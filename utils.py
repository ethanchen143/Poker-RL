import time
import random
from hand_rank_monte_carlo import monte_carlo_simulation

class Card:
    SUITS = ['h', 'd', 'c', 's']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    def __repr__(self):
        return f"{self.rank}{self.suit}"
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

def card_to_tuple(card):
    """Convert a Card object to a tuple of (suit, rank) for Cython processing"""
    return (card.suit, card.rank)

def rank_to_value(rank):
    return '@@23456789TJQKA'.index(rank)

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Card.SUITS for rank in Card.RANKS]
        self.shuffle()
    def deal(self):
        return self.cards.pop()
    def shuffle(self):
        random.shuffle(self.cards)
    def reset(self):
        self.__init__()

def describe_hand(hand_rank):
    rank_type, rank_values = hand_rank
    card_names = {10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    def card_value_to_name(value):
        return card_names.get(value, str(value))
    if rank_type == 8:  # Straight Flush
        return f"Straight Flush, {card_value_to_name(rank_values[0])} high"
    elif rank_type == 7:  # Four of a Kind
        return f"Four of a Kind, {card_value_to_name(rank_values[0])}s"
    elif rank_type == 6:  # Full House
        return f"Full House, {card_value_to_name(rank_values[0])}s full of {card_value_to_name(rank_values[1])}s"
    elif rank_type == 5:  # Flush
        return f"Flush, {card_value_to_name(rank_values[0])} high"
    elif rank_type == 4:  # Straight
        return f"Straight, {card_value_to_name(rank_values[0])} high"
    elif rank_type == 3:  # Three of a Kind
        return f"Three of a Kind, {card_value_to_name(rank_values[0])}s"
    elif rank_type == 2:  # Two Pair
        return f"Two Pair, {card_value_to_name(rank_values[0])}s and {card_value_to_name(rank_values[1])}s"
    elif rank_type == 1:  # Pair
        return f"Pair, {card_value_to_name(rank_values[0])}s"
    else:  # High Card
        return f"High Card, {card_value_to_name(rank_values[0])}"

# pre flop winning rate map
starting_hands = {
    # Pairs
    'AA': 85.0, 'KK': 82.1, 'QQ': 79.3, 'JJ': 77.2, 'TT': 75.0,
    '99': 72.8, '88': 69.2, '77': 66.5, '66': 63.4, '55': 59.8,
    '44': 57.0, '33': 53.8, '22': 50.2,

    # Suited Hands
    'AKs': 66.0, 'AQs': 65.3, 'AJs': 63.4, 'ATs': 62.0, 'A9s': 60.7,
    'A8s': 59.1, 'A7s': 57.7, 'A6s': 56.1, 'A5s': 54.9, 'A4s': 53.6,
    'A3s': 52.3, 'A2s': 51.0, 'KQs': 64.1, 'KJs': 62.3, 'KTs': 60.4,
    'K9s': 58.7, 'K8s': 56.9, 'K7s': 55.1, 'K6s': 53.6, 'K5s': 51.9,
    'K4s': 50.4, 'K3s': 49.0, 'K2s': 47.6, 'QJs': 61.4, 'QTs': 59.5,
    'Q9s': 57.8, 'Q8s': 55.9, 'Q7s': 54.2, 'Q6s': 52.6, 'Q5s': 50.9,
    'Q4s': 49.5, 'Q3s': 48.1, 'Q2s': 46.7, 'JTs': 58.5, 'J9s': 56.9,
    'J8s': 54.9, 'J7s': 53.3, 'J6s': 51.6, 'J5s': 50.1, 'J4s': 48.7,
    'J3s': 47.3, 'J2s': 45.8, 'T9s': 56.1, 'T8s': 54.2, 'T7s': 52.5,
    'T6s': 50.8, 'T5s': 49.2, 'T4s': 47.8, 'T3s': 46.3, 'T2s': 44.8,
    '98s': 53.6, '97s': 51.9, '96s': 50.3, '95s': 48.7, '94s': 47.2,
    '93s': 45.6, '92s': 44.1, '87s': 51.2, '86s': 49.7, '85s': 48.0,
    '84s': 46.4, '83s': 44.9, '82s': 43.4, '76s': 49.0, '75s': 47.4,
    '74s': 45.9, '73s': 44.3, '72s': 42.8, '65s': 46.7, '64s': 45.2,
    '63s': 43.7, '62s': 42.2, '54s': 44.5, '53s': 43.0, '52s': 41.5,
    '43s': 41.4, '42s': 40.0, '32s': 38.6,

    # Off-suit Hands
    'AK': 64.1, 'AQ': 62.4, 'AJ': 60.6, 'AT': 58.8, 'A9': 56.6,
    'A8': 54.8, 'A7': 53.0, 'A6': 51.1, 'A5': 49.7, 'A4': 48.2,
    'A3': 46.7, 'A2': 45.1, 'KQ': 61.7, 'KJ': 59.8, 'KT': 58.1,
    'K9': 55.9, 'K8': 53.9, 'K7': 52.1, 'K6': 50.4, 'K5': 48.5,
    'K4': 46.9, 'K3': 45.4, 'K2': 43.9, 'QJ': 58.4, 'QT': 56.6,
    'Q9': 54.3, 'Q8': 52.2, 'Q7': 50.3, 'Q6': 48.7, 'Q5': 47.0,
    'Q4': 45.5, 'Q3': 44.0, 'Q2': 42.4, 'JT': 55.2, 'J9': 53.1,
    'J8': 51.1, 'J7': 49.1, 'J6': 47.5, 'J5': 45.9, 'J4': 44.3,
    'J3': 42.7, 'J2': 41.2, 'T9': 52.8, 'T8': 50.8, 'T7': 48.9,
    'T6': 47.0, 'T5': 45.4, 'T4': 43.8, 'T3': 42.3, 'T2': 40.8,
    '98': 50.6, '97': 48.6, '96': 46.8, '95': 45.1, '94': 43.5,
    '93': 41.9, '92': 40.4, '87': 48.1, '86': 46.3, '85': 44.5,
    '84': 42.8, '83': 41.3, '82': 39.8, '76': 45.9, '75': 44.2,
    '74': 42.6, '73': 41.0, '72': 39.4, '65': 43.6, '64': 42.0,
    '63': 40.5, '62': 39.0, '54': 41.3, '53': 39.8, '52': 38.3,
    '43': 39.0, '42': 37.6, '32': 36.2
}

def evaluate_hand_strength(game,player,num_sim):
    # evaluate situation and give a score between 0 and 20
    if not game.community_cards:
        card1, card2 = player.hand
        ranks = sorted([card1.rank, card2.rank], reverse=True, key=rank_to_value)
        suits = [card1.suit, card2.suit]
        if suits[0] == suits[1]:
            hand_key = f"{ranks[0]}{ranks[1]}s"
        else:
            hand_key = f"{ranks[0]}{ranks[1]}"
        return int(starting_hands[hand_key]/5)
    else:
        # simulate game out to estimate the win rate / value
        return int(monte_carlo_simulation([card_to_tuple(card) for card in player.hand], [card_to_tuple(card) for card in game.community_cards],num_sim)*20)

# Test
def test_monte_carlo():
    hand = [Card('h','A'), Card('d','Q')]
    community_cards = [Card('h', 'Q'), Card('s', 'J'), Card('d', '5')]
    print(f"Hand: {hand}, Community Cards: {community_cards}")
    start_time = time.time()
    strength = monte_carlo_simulation([card_to_tuple(card) for card in hand], [card_to_tuple(card) for card in community_cards], num_simulations = 1000)
    print(f"Estimated Strength: {strength:.2f} (win rate)")
    elapsed_time = time.time() - start_time
    print(f"Time Taken: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    test_monte_carlo()