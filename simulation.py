from rl_bot import QLearningBot
from honest_bot import HonestBot
from poker_game import PokerGame
from utils import card_to_tuple

def main():
    players = [
        HonestBot(name="Honest_Hannah", chips=300),
        HonestBot(name="Honest_Henry", chips=300),
        # HonestBot(name="Honest_Jacob", chips=300),
        # HonestBot(name="Honest_Cory", chips=300),
        QLearningBot(name="Bot_Bob", chips=300),
    ]

    game = PokerGame(players)
    game.play_game(num_rounds=10000)

    for player in players:
        # num of time with +1500 - num of time busts
        print(f"\n{player.name}'s score: {player.score}")
    
    # Display the Q Tables
    # for player in players:
    #     if isinstance(player,QLearningBot):
    #         print(f"\n{player.name}'s Q-table:")
    #         for state_action, value in player.q_table.items():
    #             print(f"State: {state_action[0]}, Action: {state_action[1]} -> Value: {value}")

if __name__ == "__main__":
    main()