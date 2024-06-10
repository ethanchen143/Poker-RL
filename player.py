class Player:
    def __init__(self, name, chips):
        self.name = name
        self.score = 0
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        # decides which pot player is playing for
        self.playpot = 0
        
    def place_bet(self, amount):
        if amount > self.chips:
            raise ValueError(f"{self.name} does not have enough chips to bet {amount}")
        self.chips -= amount
        self.current_bet += amount

    def reset_for_round(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.playpot = 0

    def __repr__(self):
        return f"{self.name}: {self.chips} chips"