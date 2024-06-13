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
                pot_fraction_raises = ['raise_50', 'raise_100']
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
        legal_actions = self.get_legal_actions(game, effective_stack)
        rand = random.random()
        hand_strength = evaluate_hand_strength(game,self,100) #get rough evaluation
        
        game.log_message(f'hand_strength: {hand_strength}')        
        game.log_message(f'legal_actions: {legal_actions}')
        
        if 'check' in legal_actions and hand_strength < 10:
            return 'check' #check 50% of the hands
        
        if game.stage == 'Pre-Flop' and hand_strength < 10:
            return 'fold' #fold 50% of the hands preflop
        
        if game.actions.count('raise') == 1:
            if hand_strength <= 10:
                return 'fold'
            if hand_strength <= 15:
                return 'call'
            
        if game.actions.count('raise') == 2:
            if hand_strength <= 15:
                return 'fold'
            if hand_strength <= 18:
                return 'call'

        if game.actions.count('raise') == 3:
            if hand_strength <= 18:
                return 'fold'
        
        # if not enough raise, dont go all in
        if 'raise_100' in legal_actions and game.actions.count('raise') <= 3:
            legal_actions = legal_actions[:-1]
        
        index = round((hand_strength / 20) * (len(legal_actions) - 1))        
        action = legal_actions[index]
        
        return action
        
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