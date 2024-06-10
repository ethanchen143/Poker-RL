from rl_bot import QLearningBot
from utils import describe_hand, Deck, card_to_tuple
from hand_rank_monte_carlo import get_best_hand

class PokerGame:
    def __init__(self, players, big_blind=3, small_blind=1):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pots = [0,0,0,0] #one mainpot and three sidepots.
        self.pot = 0
        self.pot_index = 0
        self.current_bet = 0
        self.big_blind = big_blind
        self.small_blind = small_blind
        self.dealer_position = 0
        self.stage = 'Pre-Flop'
        self.actions = [] # keep track of action history
        
    def rotate_dealer(self):
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

    def deal_hands(self):
        self.deck.reset()
        for player in self.players:
            player.hand = [self.deck.deal(), self.deck.deal()]
        print(f"Dealt hands: {[f'{p.name}: {p.hand}' for p in self.players]}")

    def post_blinds(self):
        small_blind_position = (self.dealer_position + 1) % len(self.players)
        big_blind_position = (self.dealer_position + 2) % len(self.players)
        self.players[small_blind_position].place_bet(self.small_blind)
        self.players[big_blind_position].place_bet(self.big_blind)
        self.pots[0] += self.small_blind + self.big_blind
        self.current_bet = self.big_blind
        print(f"{self.players[small_blind_position].name} posts small blind of {self.small_blind}")
        print(f"{self.players[big_blind_position].name} posts big blind of {self.big_blind}")
    
    def log_action(self, player_index, action):
        position = self.get_player_position(player_index)
        self.actions.append(position)
        self.actions.append(action)
        
    def get_player_position(self, player_index):
        position = (player_index - self.dealer_position) % len(self.players)
        position_names = ['btn', 'sb', 'bb', 'utg', 'mp', 'co']
        return position_names[position] if position < len(position_names) else f'pos_{position}'

    def call_bet(self, player):
        if player.chips < self.current_bet - player.current_bet:
            all_in_amount = player.chips
            player.place_bet(all_in_amount)
            actual_call_amount = player.current_bet
            # handling excess bets for other players and side pot creation
            for p in self.players:
                if not p.folded and p != player:
                    if p.current_bet > actual_call_amount:
                        excess_amount = p.current_bet - actual_call_amount
                        self.pots[self.pot_index] -= excess_amount
                        p.chips += excess_amount
                        p.current_bet = actual_call_amount
                    # Move to the next side pot
                    p.playpot += 1
            self.current_bet = actual_call_amount
            self.pots[self.pot_index] += actual_call_amount
        else:
            call_amount = self.current_bet - player.current_bet
            player.place_bet(call_amount)
            self.pots[self.pot_index] += call_amount
        print(f"{player.name} calls. Current bet: {player.current_bet}")
            
    def raise_bet(self, player, amount):
        player.place_bet(amount)
        self.current_bet += amount
        self.pots[self.pot_index] += amount

    def deal_flop(self):
        self.community_cards = [self.deck.deal() for _ in range(3)]
        print(f"Flop: {self.community_cards} Current Pot: {self.pots}")

    def deal_turn_or_river(self):
        self.community_cards.append(self.deck.deal())
        print(f"{self.stage}: {self.community_cards[-1]} (Community cards: {self.community_cards}) Current Pot: {self.pots}")

    def determine_winner(self, starting_chips):
        for i in range(len(self.pots)):
            if self.pots[i] == 0:
                continue
            entitled_players = [p for p in self.players if not p.folded and p.playpot >= i]
            if len(entitled_players) == 1:
                winner = entitled_players[0]
                winner.chips += self.pots[i]
                print(f"{winner.name} wins pot{i+1} of {self.pots[i]} chips.")
                self.pots[i] = 0
                continue
            best_hands = []
            for player in entitled_players:
                best_hand = get_best_hand([card_to_tuple(card) for card in player.hand], [card_to_tuple(card) for card in self.community_cards])
                best_hands.append((player, best_hand))
            best_hands.sort(key=lambda x: x[1], reverse=True)
            print(best_hands)
            best_hand_rank = best_hands[0][1]
            winners = [p for p, hand in best_hands if hand == best_hand_rank]
            split_pot = self.pots[i] // len(winners)
            # Split the Pot evenly among winner(s)
            for winner in winners:
                winner.chips += split_pot
                print(f"{winner.name} wins {split_pot} chips from pot {i + 1} with hand: {describe_hand(best_hand_rank)}")
            self.pots[i] = 0
            
        # Handle rewards for QLearningBot
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
            self.actions.append(stage)
            active_players = [player for player in self.players if not player.folded]
            if len(active_players) == 1:
                break
            if stage == 'Flop':
                self.deal_flop()
            elif stage == 'Turn':
                self.deal_turn_or_river()
            elif stage == 'River':
                self.deal_turn_or_river()
            print(f"Starting {stage} betting round.")
            self.betting_round()

        self.determine_winner(starting_chips)
        for player in self.players:
            player.check_rebuy(self)
        self.rotate_dealer()
        print(f"End of round. Players' chips: {[player for player in self.players]}")

    def play_game(self, num_rounds):
        for i in range(num_rounds):
            print(f"\n--- Round {i + 1} ---")
            self.play_round()