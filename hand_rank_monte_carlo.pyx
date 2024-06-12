#cython: language_level=3
from libc.stdlib cimport malloc, free, srand, rand, atoi
from libc.string cimport memcpy, strcpy
from libc.time cimport time
from libc.stdio cimport printf
from itertools import combinations
import cython

cdef char SUITS[4]
cdef char RANKS[13]

def initialize_constants():
    global SUITS, RANKS
    SUITS[0] = b'h'[0]
    SUITS[1] = b'd'[0]
    SUITS[2] = b'c'[0]
    SUITS[3] = b's'[0]
    RANKS[0] = b'2'[0]
    RANKS[1] = b'3'[0]
    RANKS[2] = b'4'[0]
    RANKS[3] = b'5'[0]
    RANKS[4] = b'6'[0]
    RANKS[5] = b'7'[0]
    RANKS[6] = b'8'[0]
    RANKS[7] = b'9'[0]
    RANKS[8] = b'T'[0]
    RANKS[9] = b'J'[0]
    RANKS[10] = b'Q'[0]
    RANKS[11] = b'K'[0]
    RANKS[12] = b'A'[0]

def setup_module():
    initialize_constants()
    srand(time(NULL))  # Seed the RNG once


cpdef tuple get_best_hand(list player_hand, list community_cards):
    """
    Function to evaluate the best hand for a player given their hand and community cards.
    """
    cdef char combined_cards[7][2]
    cdef char best_hand[5][2]
    cdef int i, j

    # Initialize the combined cards array
    for i in range(2):
        combined_cards[i][0] = player_hand[i][0].encode('utf-8')[0]
        combined_cards[i][1] = player_hand[i][1].encode('utf-8')[0]
    for i in range(5):
        combined_cards[i+2][0] = community_cards[i][0].encode('utf-8')[0]
        combined_cards[i+2][1] = community_cards[i][1].encode('utf-8')[0]

    # Initialize best rank and best hand
    best_rank = (-1, ())
    cdef char current_hand[5][2]

    # Evaluate the best hand
    for combination in combinations(range(7), 5):
        for j in range(5):
            current_hand[j][0] = combined_cards[combination[j]][0]
            current_hand[j][1] = combined_cards[combination[j]][1]
        current_rank = single_hand_rank(current_hand)  # Evaluate the rank of the current hand
        if current_rank > best_rank:
            best_rank = current_rank
            for j in range(5):
                best_hand[j][0] = current_hand[j][0]
                best_hand[j][1] = current_hand[j][1]

    return best_rank

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double monte_carlo_simulation(list player_hand, list community_cards, int num_simulations=1000):
    setup_module()
    cdef int i, j, wins = 0, total_community_cards = len(community_cards)
    cdef int found, k
    cdef char deck[52][2], shuffled_deck[52][2]
    cdef char cards[7][2]
    cdef char opponent_hand[2][2]
    cdef char remaining_community_cards[5][2]
    cdef int num_cards = 0

    # Initialize deck
    for i in range(52):
        deck[i][0] = SUITS[i % 4]
        deck[i][1] = RANKS[i // 4]

    # Parse player and community cards into C arrays
    for card in player_hand + community_cards:
        if num_cards < 7:
            cards[num_cards][0] = card[0].encode('utf-8')[0]
            cards[num_cards][1] = card[1].encode('utf-8')[0]
            num_cards += 1

    # Simulation loop
    for sim_index in range(num_simulations):
        memcpy(shuffled_deck, deck, sizeof(deck))
        for i in range(52):
            j = rand() % (52 - i) + i
            shuffled_deck[i][0], shuffled_deck[j][0] = shuffled_deck[j][0], shuffled_deck[i][0]
            shuffled_deck[i][1], shuffled_deck[j][1] = shuffled_deck[j][1], shuffled_deck[i][1]

        # Deal cards not in use
        k = 0
        for i in range(52):
            found = 0
            for j in range(num_cards):
                if shuffled_deck[i][0] == cards[j][0] and shuffled_deck[i][1] == cards[j][1]:
                    found = 1
                    break
            if not found:
                if k < 2:
                    opponent_hand[k][0] = shuffled_deck[i][0]
                    opponent_hand[k][1] = shuffled_deck[i][1]
                    k += 1
                elif k < (5 - total_community_cards):
                    remaining_community_cards[k][0] = shuffled_deck[i][0]
                    remaining_community_cards[k][1] = shuffled_deck[i][1]
                    k += 1
                if k == (5 - total_community_cards):
                    break

        # Convert opponent_hand and remaining_community_cards to Python lists
        py_opponent_hand = [f"{chr(opponent_hand[x][0])}{chr(opponent_hand[x][1])}" for x in range(2)]
        py_remaining_community = [f"{chr(remaining_community_cards[x][0])}{chr(remaining_community_cards[x][1])}" for x in range(5 - total_community_cards)]

        # Combine provided community cards and drawn community cards
        combined_community = community_cards + py_remaining_community

        player_best_hand = get_best_hand(player_hand, combined_community)
        opponent_best_hand = get_best_hand(py_opponent_hand, combined_community)

        if player_best_hand > opponent_best_hand:
            wins += 1

    return wins / float(num_simulations)

cdef tuple single_hand_rank(char hand[5][2]):
    cdef int values[5]
    cdef char suits[5]
    cdef int i, straight, flush
    cdef int val_count[15]  # 15 to include ranks from 2 to Ace

    # Initialize val_count to 0
    for i in range(15):
        val_count[i] = 0

    # Populate value and suit arrays
    for i in range(5):
        values[i] = card_value(hand[i][1])
        suits[i] = hand[i][0]
        val_count[values[i]] += 1

    # Check for flush
    flush = (suits[0] == suits[1] == suits[2] == suits[3] == suits[4])

    # Check for straight
    values.sort()
    straight = (values[0] + 1 == values[1] and values[1] + 1 == values[2] and
                values[2] + 1 == values[3] and values[3] + 1 == values[4])

    # Ace can also be low in a straight (Ace, 2, 3, 4, 5)
    if not straight and values[4] == 14:  # Checking if Ace is high
        straight = (values[0] == 2 and values[1] == 3 and values[2] == 4 and values[3] == 5)

    # Determine hand rank
    if straight and flush:
        return (8, tuple(values))  # Straight flush
    elif has_n_of_a_kind(val_count, 4):
        four_kind = get_n_of_a_kind(val_count, 4)
        kicker = max([v for v in values if v != four_kind])
        return (7, (four_kind, kicker))  # Four of a kind
    elif has_n_of_a_kind(val_count, 3) and has_n_of_a_kind(val_count, 2):
        three_kind = get_n_of_a_kind(val_count, 3)
        pair = get_n_of_a_kind(val_count, 2)
        return (6, (three_kind, pair))  # Full house
    elif flush:
        return (5, tuple(values))  # Flush
    elif straight:
        return (4, tuple(values))  # Straight
    elif has_n_of_a_kind(val_count, 3):
        three_kind = get_n_of_a_kind(val_count, 3)
        kicker = sorted([v for v in values if v != three_kind], reverse=True)
        return (3, (three_kind,) + tuple(kicker))  # Three of a kind
    elif count_pairs(val_count) >= 2:
        pairs = get_pairs(val_count)
        kicker = max([v for v in values if v not in pairs])
        return (2, tuple(pairs) + (kicker,))  # Two pair
    elif has_n_of_a_kind(val_count, 2):
        pair = get_n_of_a_kind(val_count, 2)
        kicker = sorted([v for v in values if v != pair], reverse=True)
        return (1, (pair,) + tuple(kicker))  # One pair
    else:
        return (0, tuple(values))  # High card
        
cdef int card_value(char rank):
    """Convert card rank characters to numerical values for sorting and comparison."""
    return {
        b'2'[0]: 2, b'3'[0]: 3, b'4'[0]: 4, b'5'[0]: 5, b'6'[0]: 6,
        b'7'[0]: 7, b'8'[0]: 8, b'9'[0]: 9, b'T'[0]: 10,
        b'J'[0]: 11, b'Q'[0]: 12, b'K'[0]: 13, b'A'[0]: 14
    }.get(rank, -1)


cdef int has_n_of_a_kind(int[15] val_count, int n):
    """Helper function to check if there is n of a kind."""
    for i in range(15):
        if val_count[i] == n:
            return 1
    return 0

cdef int get_n_of_a_kind(int[15] val_count, int n):
    """Helper function to get the rank of n of a kind."""
    for i in range(15):
        if val_count[i] == n:
            return i
    return -1  # Should never be reached

cdef list get_pairs(int[15] val_count):
    """Helper function to get all pairs."""
    pairs = []
    for i in range(15):
        if val_count[i] == 2:
            pairs.append(i)
    return pairs

cdef int count_pairs(int[15] val_count):
    """Helper function to count the number of pairs."""
    count = 0
    for i in range(15):
        if val_count[i] == 2:
            count += 1
    return count