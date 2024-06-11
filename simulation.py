from rl_bot import QLearningBot
from honest_bot import HonestBot
from poker_game import PokerGame
import json
import matplotlib.pyplot as plt

def main():
    players = [
        HonestBot(name="Honest_Hannah", chips=300),
        HonestBot(name="Honest_Henry", chips=300),
        # HonestBot(name="Honest_Jacob", chips=300),
        # HonestBot(name="Honest_Cory", chips=300),
        QLearningBot(name="Bot_Bob", chips=300),
    ]

    game = PokerGame(players)
    game.play_game(num_rounds=3000000)
    game.write_log_to_file()  # Write the log to file after all rounds are complete
    game.write_score_log_to_file()
    # Export Q Table for later use
    for player in players:
        if isinstance(player, QLearningBot):
            q_table_filename = f"{player.name}_Q_Table.json"
            with open(q_table_filename, 'w') as q_table_file:
                json.dump({str(k): v for k, v in player.q_table.items()}, q_table_file, indent=2)
            print(f"{player.name}'s Q-table exported to {q_table_filename}")
            
    visualize_scores('score_log.json')

def visualize_scores(score_log_filename):
    # Load the score log from the JSON file
    with open(score_log_filename, 'r') as f:
        score_log = json.load(f)

    plt.figure(figsize=(10, 6))

    for player, scores in score_log.items():
        rounds = [i * 1000 for i in range(len(scores))]
        plt.plot(rounds, scores, marker='o', label=player) 

    plt.xlabel('Rounds')
    plt.ylabel('Chips')
    plt.title('Player Score Tracker')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('score_plot.png')  
    plt.show()

if __name__ == "__main__":
    main()