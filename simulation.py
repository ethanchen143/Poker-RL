from rl_bot import QLearningBot
from honest_bot import HonestBot
from poker_game import PokerGame
import json
import matplotlib.pyplot as plt

def main():
    # Load Q Table
    q_table_filename = "./outputs/q_table.json"
    shared_q_table = {}
    try:
        with open(q_table_filename, 'r') as q_table_file:
            q_table = json.load(q_table_file)
            shared_q_table = {eval(k): v for k, v in q_table.items()}
            print(f"Q-table loaded, length: {len(shared_q_table)}")
    except:
        print('No starting Q-table.')

    num_rounds = 1000000

    # 3 Handed Training
    players = [
        QLearningBot(name="Bot_Hannah", chips=1000, shared_q_table=shared_q_table),
        QLearningBot(name="Bot_Ricky", chips=1000, shared_q_table=shared_q_table),
        QLearningBot(name="Bot_Bob", chips=1000, shared_q_table=shared_q_table),
    ]
    
    # 6 Handed Training
    # players = [
    #     QLearningBot(name="Bot_Hannah", chips=300, shared_q_table=shared_q_table),
    #     QLearningBot(name="Bot_Henry", chips=300, shared_q_table=shared_q_table),
    #     QLearningBot(name="Bot_Ricky", chips=300, shared_q_table=shared_q_table),
    #     QLearningBot(name="Bot_Julian", chips=300, shared_q_table=shared_q_table),
    #     QLearningBot(name="Bot_Bubbles", chips=300, shared_q_table=shared_q_table),
    #     QLearningBot(name="Bot_Bob", chips=300, shared_q_table=shared_q_table),
    # ]

    # 6 Handed Testing
    # players = [
    #     HonestBot(name="Honest_Hannah", chips=300),
    #     QLearningBot(name="Honest_Henry", chips=300),
    #     QLearningBot(name="Honest_Ricky", chips=300),
    #     QLearningBot(name="Honest_Julian", chips=300),
    #     QLearningBot(name="Honest_Bubbles", chips=300),
    #     QLearningBot(name="Bot_Bob", chips=300, shared_q_table=shared_q_table, 
    #                  initial_exploration_rate=0, initial_learning_rate=0.2),
    # ]

    game = PokerGame(players)
    game.play_game(num_rounds=num_rounds)
    # Export Q Table
    with open(q_table_filename, 'w') as q_table_file:
        json.dump({str(k): v for k, v in shared_q_table.items()}, q_table_file, indent=2)
    game.log_message(f"Shared Q-table exported to {q_table_filename}")
    game.write_score_log_to_file()
    visualize_scores('./outputs/score_log.json')
    game.write_log_to_file() 

def visualize_scores(score_log_filename):
    # Load the score log from the JSON file
    with open(score_log_filename, 'r') as f:
        score_log = json.load(f)

    plt.figure(figsize=(10, 6))

    for player, scores in score_log.items():
        rounds = [i * 10000 for i in range(len(scores))]
        plt.plot(rounds, scores, marker='o', label=player) 

    plt.xlabel('Rounds')
    plt.ylabel('Chips')
    plt.title('Player Score Tracker')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('./outputs/score_plot.png')  
    plt.show()

if __name__ == "__main__":
    main()