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

# pre flop starting hand map
starting_hands = {
    # Pairs
    'AA': 100, 'KK': 100, 'QQ': 95, 'JJ': 90, 'TT': 85,
    '99': 80, '88': 75, '77': 70, '66': 65, '55': 60,
    '44': 60, '33': 60, '22': 60,

    # Suited Hands
    'AKs': 95, 'AQs': 90, 'AJs': 85, 'ATs': 80, 'A9s': 70,
    'A8s': 70, 'A7s': 60, 'A6s': 60, 'A5s': 70, 'A4s': 60,
    'A3s': 50, 'A2s': 50, 'KQs': 85, 'KJs': 80, 'KTs': 75,
    'K9s': 70, 'K8s': 65, 'K7s': 60, 'K6s': 55, 'K5s': 50,
    'K4s': 45, 'K3s': 40, 'K2s': 35, 'QJs': 75, 'QTs': 70,
    'Q9s': 65, 'Q8s': 60, 'Q7s': 55, 'Q6s': 50, 'Q5s': 45,
    'Q4s': 40, 'Q3s': 35, 'Q2s': 30, 'JTs': 65, 'J9s': 60,
    'J8s': 55, 'J7s': 50, 'J6s': 45, 'J5s': 40, 'J4s': 35,
    'J3s': 30, 'J2s': 25, 'T9s': 55, 'T8s': 50, 'T7s': 45,
    'T6s': 40, 'T5s': 35, 'T4s': 30, 'T3s': 25, 'T2s': 20,
    '98s': 50, '97s': 45, '96s': 40, '95s': 35, '94s': 30,
    '93s': 25, '92s': 20, '87s': 45, '86s': 40, '85s': 35,
    '84s': 30, '83s': 25, '82s': 20, '76s': 30, '75s': 25,
    '74s': 20, '73s': 15, '72s': 10, '65s': 25, '64s': 20,
    '63s': 15, '62s': 10, '54s': 20, '53s': 15, '52s': 10,
    '43s': 15, '42s': 10, '32s': 5,

    # Off-suit Hands
    'AK': 90, 'AQ': 85, 'AJ': 80, 'AT': 75, 'A9': 65,
    'A8': 65, 'A7': 55, 'A6': 55, 'A5': 65, 'A4': 55,
    'A3': 45, 'A2': 45, 'KQ': 80, 'KJ': 75, 'KT': 70,
    'K9': 65, 'K8': 60, 'K7': 55, 'K6': 50, 'K5': 45,
    'K4': 40, 'K3': 35, 'K2': 30, 'QJ': 70, 'QT': 65,
    'Q9': 60, 'Q8': 55, 'Q7': 50, 'Q6': 45, 'Q5': 40,
    'Q4': 35, 'Q3': 30, 'Q2': 25, 'JT': 60, 'J9': 55,
    'J8': 50, 'J7': 45, 'J6': 40, 'J5': 35, 'J4': 30,
    'J3': 25, 'J2': 20, 'T9': 50, 'T8': 45, 'T7': 40,
    'T6': 35, 'T5': 30, 'T4': 25, 'T3': 20, 'T2': 15,
    '98': 45, '97': 40, '96': 35, '95': 30, '94': 25,
    '93': 20, '92': 15, '87': 40, '86': 35, '85': 30,
    '84': 25, '83': 20, '82': 15, '76': 25, '75': 20,
    '74': 15, '73': 10, '72': 5, '65': 20, '64': 15,
    '63': 10, '62': 5, '54': 15, '53': 10, '52': 5,
    '43': 10, '42': 5, '32': 0
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
# def test_monte_carlo():
#     hand = [Card('h','2'), Card('d','2')]
#     community_cards = [Card('s', '9'), Card('s', '2'), Card('d', '8')]
#     print(f"Hand: {hand}, Community Cards: {community_cards}")
#     start_time = time.time()
#     strength = monte_carlo_simulation([card_to_tuple(card) for card in hand], [card_to_tuple(card) for card in community_cards], num_simulations = 20)
#     print(f"Estimated Strength: {strength:.2f} (win rate)")
#     elapsed_time = time.time() - start_time
#     print(f"Time Taken: {elapsed_time:.2f} seconds")

import json
from ast import literal_eval
from operator import itemgetter

if __name__ == '__main__':
    # test_monte_carlo()
    
    shared_q_table = {}
    q_table_filename = "./outputs/q_table.json"
    with open(q_table_filename, 'r') as q_table_file:
        q_table = json.load(q_table_file)
        shared_q_table = {eval(k): v for k, v in q_table.items()}
    with open('./outputs/scaled_q_table.json', 'w') as q_table_file:
        json.dump({str(k): v/100 for k, v in shared_q_table.items()}, q_table_file, indent=2)
        
    # sorted_q_table_dict = {}
    # for entry in sorted_q_table:
    #     stage, position, pot_ratio, strength, _, actions, action, value = entry
    #     key = (stage, position, pot_ratio, strength, actions), action
    #     sorted_q_table_dict[str(key)] = value

    # # Save the sorted Q-table to a JSON file
    # with open('./outputs/sorted_q_table.json', 'w') as f:
    #     json.dump(sorted_q_table_dict, f, indent=2)