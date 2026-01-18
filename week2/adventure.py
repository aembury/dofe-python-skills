print("You are standing in a dark forest.")
choice1 = input("Do you go left or right? ").lower()

if choice1 == "left":
    print("You find a treasure chest!")
    choice2 = input("Do you open it? (yes/no) ").lower()
    if choice2 == "yes":
        print("It's full of gold! You win!")
    else:
        print("You walk away safely. The end.")
elif choice1 == "right":
    print("You fall into a pit. Game over.")
else:
    print("That wasn't an option. You stand there until you get hungry.")