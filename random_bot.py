from player import Player
import random

class RandomBot(Player):
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
        action = random.choice(legal_actions)
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