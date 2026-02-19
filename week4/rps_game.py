import random

def get_computer_choice():
    choices = ["rock", "paper", "scissors"]
    return random.choice(choices)

def get_winner(player, computer):
    if player == computer:
        return "It's a tie!"
    elif (player == "rock" and computer == "scissors") or \
         (player == "paper" and computer == "rock") or \
         (player == "scissors" and computer == "paper"):
        return "You win!"
    else:
        return "Computer wins!"

# Main Game Loop
while True:
    player_choice = input("Rock, Paper, or Scissors? (or 'quit'): ").lower()
    if player_choice == "quit":
        break
    
    computer_choice = get_computer_choice()
    print(f"Computer chose: {computer_choice}")
    
    result = get_winner(player_choice, computer_choice)
    print(result)