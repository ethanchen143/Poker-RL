from player import Player
from utils import evaluate_hand_strength
import random

class HonestBot(Player):
    def __init__(self, name, chips):
        super().__init__(name, chips)
        self.initial_chips = chips

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
                pot_fraction_raises = ['raise_33', 'raise_66', 'raise_100', 'raise_150']
            else:
                # Pre-Flop
                pot_fraction_raises = ['raise_100', 'raise_150']

            # Calculate the actual raise amounts and filter out invalid ones
            valid_raises = [
                raise_action for raise_action in pot_fraction_raises
                if self.is_valid_raise(raise_action, game.pot, effective_stack, call_amount)
            ]
            legal_actions.extend(valid_raises)
            legal_actions.append('all_in')

        return legal_actions
    
    def get_action(self, game, current_position, effective_stack):
        legal_actions = self.get_legal_actions(game, effective_stack)
        rand = random.random()
        if 'call' in legal_actions and rand <= 0.5:
            return 'call'
        hand_strength = evaluate_hand_strength(game,self,100)
        index = int((hand_strength / 20) * (len(legal_actions) - 1))        
        action = legal_actions[index]
        return action
        
    def check_rebuy(self,game):
        if self.chips <= 3:
            # take chips from the deepest stack
            deep_player = max(game.players, key= lambda x: x.chips)
            if deep_player.chips > 1500:
                deep_player.chips = 300
                deep_player.score += 4
            
            game.log_message(f"{self.name} rebuys for {self.initial_chips} chips.")
            self.chips = self.initial_chips
            self.score -= 1