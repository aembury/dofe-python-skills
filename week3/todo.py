tasks = []

while True:
    action = input("Do you want to (add) a task, (view) tasks, or (quit)? ").lower()

    if action == "add":
        task = input("Enter task: ")
        tasks.append(task)
        print("Task added!")
    elif action == "view":
        print("\nYour To-Do List:")
        for task in tasks:
            print(f"- {task}")
        print("")
    elif action == "quit":
        break
    else:
        print("Invalid option.")