python
import random

# Ollama models
ollama_models = ["Stealthy Spy", "Tech Guru", "Master Hacker", "Infiltration Expert"]

def main():
    print("Welcome to the Molt Agent Progression Tool!")
    print("Choose your Ollama model:")
    
    for idx, model in enumerate(ollama_models, start=1):
        print(f"{idx}. {model}")
    
    choice = int(input("Enter the number of your chosen Ollama model: "))
    
    if choice < 1 or choice > len(ollama_models):
        print("Invalid choice, please try again.")
        return
    
    ollama_model = ollama_models[choice-1]
    
    print(f"You have selected the {ollama_model} model.")
    
    while True:
        task = input("Enter a task or codebase enhancement to automate: ")
        
        if task.lower() == "exit":
            print("Exiting Molt Agent Progression Tool. Goodbye!")
            break
        
        print(f"Running {ollama_model} to automate task: {task}")
        
        if random.random() < 0.5:
            print("Task successfully completed!")
        else:
            print("Task failed. Try again.")
    
if __name__ == "__main__":
    main()