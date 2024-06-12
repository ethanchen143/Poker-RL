import random
from utils import evaluate_hand_strength 
from player import Player
import json

class QLearningBot(Player):
    def __init__(self, name, chips, discount_factor=1, initial_learning_rate=0.1, final_learning_rate=0.5, initial_exploration_rate=0.5, final_exploration_rate=0.1, shared_q_table = {}):
        super().__init__(name, chips)
        self.initial_chips = chips
        self.q_table = shared_q_table  # State-action value table
        self.gamma = discount_factor
        self.initial_alpha = initial_learning_rate
        self.final_alpha = final_learning_rate
        self.initial_epsilon = initial_exploration_rate
        self.final_epsilon = final_exploration_rate
        self.alpha = initial_learning_rate
        self.epsilon = initial_exploration_rate
        self.states_actions = []

    def get_state(self, game, current_position):
        """ Convert the game state to a tuple that can be used as a dictionary key. """
        position = game.get_player_position(current_position)
        hand_strength = 0
        for pair in self.states_actions:
            if pair[0][0] == game.stage:
                hand_strength = pair[0][2]
        if hand_strength == 0:
            hand_strength = evaluate_hand_strength(game,self,1000)
        past_actions = game.actions
        return (
            game.stage,
            position,
            hand_strength,
            tuple(past_actions),
        )
        
    def choose_action(self, state, legal_actions, game):
        """ Choose an action based on the Q-Table, with exploration. """
        if random.random() < self.epsilon:
            return random.choice(legal_actions)  # Explore
        else:
            q_values = [self.q_table.get((state, action), 0) for action in legal_actions]
            game.log_message(str(state[2]))
            game.log_message(str(legal_actions))
            game.log_message(str(q_values))
            max_q = max(q_values)
            return legal_actions[q_values.index(max_q)]  # Exploit
    
    def is_valid_raise(self, raise_action, pot, effective_stack, call_amount):
        percentage = int(raise_action.split('_')[1])
        amount = (percentage / 100) * pot
        return amount <= (effective_stack - call_amount)

    def get_legal_actions(self, game, effective_stack):
        legal_actions = []
        game.pot = sum(game.pots)
        call_amount = game.current_bet - self.current_bet

        if self.chips <= 0:
            return ['check']
        
        if self.current_bet < game.current_bet:
            legal_actions.append('fold')
        
        if self.current_bet == game.current_bet:
            legal_actions.append('check')
        else:
            if self.chips > 0:
                legal_actions.append('call')
        
        if self.chips > game.current_bet:
            if game.community_cards:
                # Post-Flop
                pot_fraction_raises = ['raise_50','raise_100']
            else:
                # Pre-Flop
                pot_fraction_raises = ['raise_100']

            # Calculate the actual raise amounts and filter out invalid ones
            valid_raises = [
                raise_action for raise_action in pot_fraction_raises
                if self.is_valid_raise(raise_action, game.pot, effective_stack, call_amount)
            ]

            legal_actions.extend(valid_raises)
            legal_actions.append('all_in')

        return legal_actions

    def get_action(self, game, current_position, effective_stack):
        state = self.get_state(game, current_position)
        legal_actions = self.get_legal_actions(game, effective_stack)
        action = self.choose_action(state, legal_actions, game)
        self.states_actions.append((state,action))
        return action

    def receive_reward(self, reward):
        for state, action in self.states_actions:
            old_q_value = self.q_table.get((state, action), 0)
            new_q_value = old_q_value + self.alpha * reward
            self.q_table[(state, action)] = new_q_value
        self.states_actions = []

    def check_rebuy(self,game):
        if self.chips <= game.big_blind:
            # take chips from the deepest stack
            deep_player = max(game.players, key= lambda x: x.chips)
            if deep_player.chips > 3*self.initial_chips:
                deep_player.chips = self.initial_chips
                deep_player.score += 2
                
            game.log_message(f"{self.name} rebuys for {self.initial_chips} chips.")
            self.chips = self.initial_chips
            self.score -= 1
            
    def adjust_learning_rate(self, round_number, total_rounds):
        self.alpha = self.initial_alpha + (self.final_alpha - self.initial_alpha) * (round_number / total_rounds)

    def adjust_exploration_rate(self, round_number, total_rounds):
        self.epsilon = self.initial_epsilon - (self.initial_epsilon - self.final_epsilon) * (round_number / total_rounds)