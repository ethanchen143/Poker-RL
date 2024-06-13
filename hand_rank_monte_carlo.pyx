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


# Cython code with debugging print statements
cpdef double monte_carlo_simulation(list player_hand, list community_cards, int num_simulations=1000):
    setup_module()
    cdef int i, j, wins = 0, total_community_cards = len(community_cards)
    cdef int found, k
    cdef char deck[52][2], shuffled_deck[52][2]
    cdef char our_hand[2][2]
    cdef char opponent_hand[2][2]
    cdef char board[5][2]
    cdef int num_cards = 0

    cdef char combined_cards_us[7][2]
    cdef char combined_cards_opps[7][2]
    cdef char current_hand[5][2]

    # Initialize deck
    for i in range(52):
        deck[i][0] = SUITS[i % 4]
        deck[i][1] = RANKS[i // 4]

    # Parse player cards into C array
    for i in range(2):
        our_hand[i][0] = player_hand[i][0].encode('utf-8')[0]
        our_hand[i][1] = player_hand[i][1].encode('utf-8')[0]

    # Parse community cards into C array
    for i in range(total_community_cards):
        board[i][0] = community_cards[i][0].encode('utf-8')[0]
        board[i][1] = community_cards[i][1].encode('utf-8')[0]

    # Simulation loop
    for sim_index in range(num_simulations):
        memcpy(shuffled_deck, deck, sizeof(deck))
        for i in range(52):
            j = rand() % (52 - i) + i
            shuffled_deck[i][0], shuffled_deck[j][0] = shuffled_deck[j][0], shuffled_deck[i][0]
            shuffled_deck[i][1], shuffled_deck[j][1] = shuffled_deck[j][1], shuffled_deck[i][1]

        # Deal cards not in use
        k = 0
        num_cards = total_community_cards  # Track filled community cards
        for i in range(52):
            found = 0
            for j in range(2):
                if shuffled_deck[i][0] == our_hand[j][0] and shuffled_deck[i][1] == our_hand[j][1]:
                    found = 1
                    break      
            for j in range(num_cards):
                if shuffled_deck[i][0] == board[j][0] and shuffled_deck[i][1] == board[j][1]:
                    found = 1
                    break
            if not found:
                if k < 2:
                    opponent_hand[k][0] = shuffled_deck[i][0]
                    opponent_hand[k][1] = shuffled_deck[i][1]
                    k += 1
                elif k < (7 - total_community_cards):
                    board[num_cards][0] = shuffled_deck[i][0]
                    board[num_cards][1] = shuffled_deck[i][1]
                    num_cards += 1
                    k += 1
                if k == (7 - total_community_cards):
                    break

        # Initialize the combined cards array
        for i in range(2):
            combined_cards_us[i][0] = our_hand[i][0]
            combined_cards_us[i][1] = our_hand[i][1]
            combined_cards_opps[i][0] = opponent_hand[i][0]
            combined_cards_opps[i][1] = opponent_hand[i][1]
        for i in range(5):
            combined_cards_us[i+2][0] = board[i][0]
            combined_cards_us[i+2][1] = board[i][1]
            combined_cards_opps[i+2][0] = board[i][0]
            combined_cards_opps[i+2][1] = board[i][1]

        # Initialize best rank and best hand
        best_rank_us = (-1,())
        best_rank_opps = (-1,())

        # Evaluate the best hand for us
        for combination in combinations(range(7), 5):
            for j in range(5):
                current_hand[j][0] = combined_cards_us[combination[j]][0]
                current_hand[j][1] = combined_cards_us[combination[j]][1]
            current_rank = single_hand_rank(current_hand)
            if current_rank > best_rank_us:
                best_rank_us = current_rank

        # Evaluate the best hand for opponent
        for combination in combinations(range(7), 5):
            for j in range(5):
                current_hand[j][0] = combined_cards_opps[combination[j]][0]
                current_hand[j][1] = combined_cards_opps[combination[j]][1]
            current_rank = single_hand_rank(current_hand)
            if current_rank > best_rank_opps:
                best_rank_opps = current_rank

        # Debug: Print hands and ranks
        # print("Player's best hand:", best_rank_us)
        # print("Opp's best hand:", best_rank_opps)
        
        if best_rank_us >= best_rank_opps:
            wins += 1

    return wins / float(num_simulations)


cdef void sort_array(int arr[], int n):
    cdef int i, j, tmp
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                tmp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = tmp


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
    sort_array(values, 5)
    straight = (values[0] + 1 == values[1] and values[1] + 1 == values[2] and
                values[2] + 1 == values[3] and values[3] + 1 == values[4])

    # Ace can also be high in a straight (10, J, Q, K, Ace)
    if not straight:
        if values == [10, 11, 12, 13, 14]:  # Check for Ace-high straight
            straight = 1
        elif values == [2, 3, 4, 5, 14]:  # Check for Ace-low straight
            straight = 1
            values = [1, 2, 3, 4, 5]  # Treat Ace as low for ranking purposes

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