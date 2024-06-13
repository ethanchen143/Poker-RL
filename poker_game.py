from rl_bot import QLearningBot
from utils import describe_hand, Deck, card_to_tuple
from hand_rank_monte_carlo import get_best_hand
import time
import json

class PokerGame:
    def __init__(self, players, big_blind=10, small_blind=5):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pots = [0,0,0,0,0,0] # one main pot and five side pots maximum.
        self.pot = 0
        self.pot_index = 0
        self.current_bet = 0
        self.big_blind = big_blind
        self.small_blind = small_blind
        self.dealer_position = 0
        self.stage = 'Pre-Flop'
        self.actions = [] # keep track of action history of a round
        self.log = [] # log messages
        self.score_log = {player.name: [0] for player in players}

    def log_message(self, message):
        self.log.append(message)
        # print(message)

    def write_log_to_file(self, filename='./outputs/game_log.txt'):
        """Write the log messages to a text file."""
        with open(filename, 'w') as f:
            f.write('\n'.join(self.log))
        self.log_message(f"Log written to {filename}")

    def write_score_log_to_file(self, filename='./outputs/score_log.json'):
        """Write the score log to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.score_log, f, indent=2)
        self.log_message(f"Score log written to {filename}")

    def rotate_dealer(self):
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

    def deal_hands(self):
        self.deck.reset()
        for player in self.players:
            player.hand = [self.deck.deal(), self.deck.deal()]
        self.log_message(f"Dealt hands: {[f'{p.name}: {p.hand}' for p in self.players]}")

    def post_blinds(self):
        small_blind_position = (self.dealer_position + 1) % len(self.players)
        big_blind_position = (self.dealer_position + 2) % len(self.players)
        self.players[small_blind_position].place_bet(self.small_blind)
        self.players[big_blind_position].place_bet(self.big_blind)
        self.pots[0] += self.small_blind + self.big_blind
        self.current_bet = self.big_blind
        self.log_message(f"{self.players[small_blind_position].name} posts small blind of {self.small_blind}")
        self.log_message(f"{self.players[big_blind_position].name} posts big blind of {self.big_blind}")
    
    def log_action(self, player_index, action):
        position = self.get_player_position(player_index)
        self.actions.append(position)
        self.actions.append(action)
        
    def get_player_position(self, player_index):
        position = (player_index - self.dealer_position) % len(self.players)
        position_names = ['btn', 'sb', 'bb', 'utg', 'mp', 'co']
        return position_names[position] if position < len(position_names) else f'pos_{position}'

    def betting_round(self):
        if self.stage == 'Pre-Flop':
            start_position = (self.dealer_position + 3) % len(self.players)
        else:
            start_position = (self.dealer_position + 1) % len(self.players)

        current_position = start_position
        active_players = [p for p in self.players if not p.folded and p.chips > 0]
        all_in_action = False
        last_to_act = (start_position - 1) % len(self.players)

        # if only one person can act, they should not act
        if len(active_players) <= 1:
            return
        
        while True:
            player = self.players[current_position]
            if not player.folded and player.chips > 0:
                try:
                    max_opponent_stack = max(p.chips for p in active_players if p != player)
                except ValueError:
                    max_opponent_stack = 0
                effective_stack = min(player.chips, max_opponent_stack)
                action = player.get_action(self, current_position, effective_stack)
                if all_in_action:
                    action = 'call' if 'fold' not in action else 'fold'
                if action == 'fold':
                    player.folded = True
                    self.log_message(f"{player.name} folds.")
                elif action == 'call':
                    self.call_bet(player)
                    self.log_message(f"{player.name} calls. Current bet: {player.current_bet}")
                elif action == 'check':
                    self.log_message(f"{player.name} checks. Current bet: {player.current_bet}")
                elif action == 'all_in':
                    if not self.community_cards:
                        self.call_bet(player)
                        effective_stack = min(player.chips, max_opponent_stack)
                    self.raise_bet(player, effective_stack)
                    all_in_action = True
                    last_to_act = (current_position - 1) % len(self.players)
                    self.log_message(f"{player.name} goes all-in for {effective_stack}")
                elif action.startswith('raise_'):
                    percentage = int(action.split('_')[1])
                    amount = int((percentage / 100) * self.pot)
                    self.call_bet(player)
                    self.raise_bet(player, amount)
                    last_to_act = (current_position - 1) % len(self.players)
                    self.log_message(f"{player.name} raises {amount}. Current bet: {player.current_bet}")
                else:
                    self.log_message('Something went wrong, no action available.')
                self.log_action(current_position, action)
            
            if current_position == last_to_act:
                if all(p.current_bet == self.current_bet or p.chips == 0 for p in active_players if not p.folded):
                    if not (self.stage == 'Pre-Flop' and self.get_player_position(current_position) == 'sb' and self.actions.count('bb') < 1):
                        break
            
            current_position = (current_position + 1) % len(self.players)
            
            # Check if no more action needed
            live_players = [p for p in self.players if not p.folded and p.chips>0]
            if len(live_players) <= 1:
                break

        for player in self.players:
            player.current_bet = 0
        
        self.current_bet = 0
        self.actions = []

        if all_in_action:
            self.pot_index += 1 # other players gets entitled to the next sidepot
            for p in self.players:
                if not p.folded and p.chips > 0:
                    p.playpot = self.pot_index
            

    def call_bet(self, player):
        if player.chips < self.current_bet - player.current_bet:
            all_in_amount = player.chips
            player.place_bet(all_in_amount)
            actual_call_amount = player.current_bet
            for p in self.players:
                if not p.folded and p != player:
                    if p.current_bet > actual_call_amount:
                        excess_amount = p.current_bet - actual_call_amount
                        self.pots[self.pot_index] -= excess_amount
                        p.chips += excess_amount
                        p.current_bet = actual_call_amount
            self.current_bet = actual_call_amount
            self.pots[self.pot_index] += actual_call_amount
        else:
            call_amount = self.current_bet - player.current_bet
            player.place_bet(call_amount)
            self.pots[self.pot_index] += call_amount
            
    def raise_bet(self, player, amount):
        player.place_bet(amount)
        self.current_bet += amount
        self.pots[self.pot_index] += amount

    def deal_flop(self):
        self.community_cards = [self.deck.deal() for _ in range(3)]
        self.log_message(f"Flop: {self.community_cards}, Main Pot Size: {self.pots[0]}")

    def deal_turn_or_river(self):
        self.community_cards.append(self.deck.deal())
        self.log_message(f"{self.stage}: {self.community_cards[-1]} (Community cards: {self.community_cards}), Main Pot Size: {self.pots[0]}")

    def determine_winner(self, starting_chips):
        for i in range(len(self.pots)):
            if self.pots[i] == 0:
                continue
            entitled_players = [p for p in self.players if not p.folded and p.playpot >= i]
            if len(entitled_players) == 1:
                winner = entitled_players[0]
                winner.chips += self.pots[i]
                self.log_message(f"{winner.name} wins pot{i+1} of {self.pots[i]} chips.")
                self.pots[i] = 0
                continue
            best_hands = []
            for player in entitled_players:
                best_hand = get_best_hand([card_to_tuple(card) for card in player.hand], [card_to_tuple(card) for card in self.community_cards])
                best_hands.append((player, best_hand))
            if not best_hands: # safeguarding
                self.log_message('Something went wrong, no winner.')
                return
            best_hands.sort(key=lambda x: x[1], reverse=True)
            best_hand_rank = best_hands[0][1]
            winners = [p for p, hand in best_hands if hand == best_hand_rank]
            split_pot = self.pots[i] // len(winners)
            for winner in winners:
                winner.chips += split_pot
                self.log_message(f"{winner.name} wins {split_pot} chips from pot {i + 1} with hand: {describe_hand(best_hand_rank)}")
            self.pots[i] = 0
            
        for player in self.players:
            if isinstance(player, QLearningBot):
                reward = player.chips - starting_chips[player.name]
                player.receive_reward(reward)

    def reset_for_new_round(self):
        self.community_cards = []
        self.pots = [0,0,0,0,0,0]
        self.current_bet = 0
        self.pot_index = 0
        self.actions = []
        for player in self.players:
            player.reset_for_round()

    def play_round(self):
        starting_chips = {player.name: player.chips for player in self.players}
        self.reset_for_new_round()
        self.deal_hands()
        self.post_blinds()
        for stage in ['Pre-Flop', 'Flop', 'Turn', 'River']:
            self.stage = stage
            active_players = [player for player in self.players if not player.folded]
            if len(active_players) == 1:
                break
            if stage == 'Flop':
                self.deal_flop()
            elif stage == 'Turn':
                self.deal_turn_or_river()
            elif stage == 'River':
                self.deal_turn_or_river()
            self.log_message(f"Starting {stage} betting round.")
            self.betting_round()
            

        self.determine_winner(starting_chips)
        for player in self.players:
            player.check_rebuy(self)
        self.rotate_dealer()
        self.log_message(f"End of round. Players' chips: {[player for player in self.players]}")

    def play_game(self, num_rounds):
        start_time = time.time()
        for i in range(num_rounds):
            self.log_message(f"\n--- Round {i + 1} ---")
            self.play_round()
            if (i+1) % 100 == 0:
                for player in self.players:
                    if isinstance(player, QLearningBot):
                        player.adjust_learning_rate(i + 1, num_rounds)
                        player.adjust_exploration_rate(i + 1, num_rounds)
                    self.score_log[player.name].append(player.score)
                elapsed_time = time.time() - start_time
                print(f'Finished {i+1} simulations, time taken: {elapsed_time:2f} seconds')