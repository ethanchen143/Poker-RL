# NO LONGER IN USE!
# idea: use hashing to improve runtime speed of evaluation

import json
from itertools import combinations_with_replacement

hand_rank_cache = {}

# def rank_to_value(rank):
#     return '@@23456789TJQKA'.index(rank)

# def hand_rank_with_flush(hand):
#     values = sorted([rank_to_value(card.rank) for card in hand], reverse=True)
#     suits = [card.suit for card in hand]
#     value_counts = {v: values.count(v) for v in values}
#     is_flush = len(set(suits)) == 1
#     is_straight = len(set(values)) == 5 and max(values) - min(values) == 4
#     if is_flush and is_straight:
#         return (8, values) 
#     elif 4 in value_counts.values():
#         four_kind = max(value_counts, key=lambda v: value_counts[v] == 4)
#         return (7, [four_kind] + sorted(v for v in values if v != four_kind))
#     elif 3 in value_counts.values() and 2 in value_counts.values():
#         three_kind = max(value_counts, key=lambda v: value_counts[v] == 3)
#         pair = max(value_counts, key=lambda v: value_counts[v] == 2)
#         return (6, [three_kind, pair])
#     elif is_flush:
#         return (5, values)
#     elif is_straight:
#         return (4, values)
#     elif 3 in value_counts.values():
#         three_kind = max(value_counts, key=lambda v: value_counts[v] == 3)
#         return (3, [three_kind] + sorted(v for v in values if v != three_kind))
#     elif list(value_counts.values()).count(2) == 2:
#         pairs = sorted((v for v in value_counts if value_counts[v] == 2), reverse=True)
#         kicker = max(v for v in values if v not in pairs)
#         return (2, pairs + [kicker])
#     elif 2 in value_counts.values():
#         pair = max(value_counts, key=lambda v: value_counts[v] == 2)
#         return (1, [pair] + sorted(v for v in values if v != pair))
#     else:
#         return (0, values)

# def load_cache_from_file(file_path):
#     with open(file_path, 'r') as f:
#         loaded_cache = json.load(f)
#     return {key: tuple(value) for key, value in loaded_cache.items()}

# hand_rank_cache = load_cache_from_file("hand_rank_cache.json")

# def hand_rank(hand):
#     suits = [card.suit for card in hand]
#     is_flush = len(set(suits)) == 1
#     if is_flush:
#         return hand_rank_with_flush(hand)
#     else:
#         sorted_values = ''.join(sorted([card.rank for card in hand], key=rank_to_value))
#         if sorted_values in hand_rank_cache:
#             return hand_rank_cache[sorted_values]
#         else:
#             print('ERROR')
#             return hand_rank_with_flush(hand)

# def monte_carlo_simulation(player_hand, community_cards, num_simulations=250):
#     deck = Deck()
#     used_cards = player_hand + community_cards
#     for card in used_cards:
#         deck.cards.remove(card)
#     wins = 0
#     for _ in range(num_simulations):
#         sim_deck = copy.deepcopy(deck)
#         sim_deck.shuffle()
#         opponent_hand = [sim_deck.deal(), sim_deck.deal()] 
#         remaining_community_cards = list(community_cards)
#         while len(remaining_community_cards) < 5:
#             remaining_community_cards.append(sim_deck.deal())
#         player_best_hand = max(combinations(player_hand + remaining_community_cards, 5), key=hand_rank)
#         opponent_best_hand = max(combinations(opponent_hand + remaining_community_cards, 5), key=hand_rank)
#         if hand_rank(player_best_hand) > hand_rank(opponent_best_hand):
#             wins += 1
#     return wins / num_simulations

# def hand_rank_without_flush(hand):
#     values = sorted([rank_to_value(card) for card in hand], reverse=True)
#     value_counts = {v: values.count(v) for v in values}
#     is_straight = len(set(values)) == 5 and max(values) - min(values) == 4
#     if 4 in value_counts.values():
#         four_kind = max(value_counts, key=lambda v: value_counts[v] == 4)
#         return (7, [four_kind] + sorted(v for v in values if v != four_kind))
#     elif 3 in value_counts.values() and 2 in value_counts.values():
#         three_kind = max(value_counts, key=lambda v: value_counts[v] == 3)
#         pair = max(value_counts, key=lambda v: value_counts[v] == 2)
#         return (6, [three_kind, pair])
#     elif is_straight:
#         return (4, values)
#     elif 3 in value_counts.values():
#         three_kind = max(value_counts, key=lambda v: value_counts[v] == 3)
#         return (3, [three_kind] + sorted(v for v in values if v != three_kind))
#     elif list(value_counts.values()).count(2) == 2:
#         pairs = sorted((v for v in value_counts if value_counts[v] == 2), reverse=True)
#         kicker = max(v for v in values if v not in pairs)
#         return (2, pairs + [kicker])
#     elif 2 in value_counts.values():
#         pair = max(value_counts, key=lambda v: value_counts[v] == 2)
#         return (1, [pair] + sorted(v for v in values if v != pair))
#     else:
#         return (0, values)

# def generate_card_combinations():
#     ranks = '23456789TJQKA'
#     return [''.join(combo) for combo in combinations_with_replacement(ranks, 5)]

# def populate_hand_rank_cache():
#     combinations = generate_card_combinations()
#     for idx,combo in enumerate(combinations):
#         rank = hand_rank_without_flush(combo)
#         hand_rank_cache[combo] = rank

# def save_cache_to_file(file_path):
#     with open(file_path, 'w') as f:
#         json.dump(hand_rank_cache, f)

# if __name__ == "__main__":
#     populate_hand_rank_cache()
#     print(len(hand_rank_cache))
#     save_cache_to_file("hand_rank_cache.json")
    
