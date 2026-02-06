import os
import sys
import subprocess
from src.interface.interaction import interactive_selection
from src.interface.draw import clear_screen
from config import BASE_DIR, ASSETS_DIR

def handle_launch():
    """
    Starts the game for both singles and multiplyer options.
    """
    options = ["Single Player", "Pass & Play", "Back"]
    choice_idx = interactive_selection(options, "vertical", "Row: Past the Burn")
    selection = options[choice_idx]

    if selection == "Back":
        return
     
    # Run game
    clear_screen()
    subprocess.run([sys.executable, "-m", "src.engine.game"], cwd = BASE_DIR)
    input("\nReturn to menu...")

def handle_rules():
    """
    Read the rules files and outputs it.
    """
    try:
        path = os.path.join(ASSETS_DIR, "rules.txt")
        with open(path, "r", encoding = 'utf-8') as f:
            clear_screen()
            print(f.read())
            input("\nReturn to menu...")
    except FileNotFoundError:
        print("Rules file not found")

def handle_credits():
    """
    Read the credits files and outputs it.
    """
    try:
        path = os.path.join(ASSETS_DIR, "credits.txt")
        with open(path, "r", encoding = 'utf-8') as f:
            clear_screen()
            print(f.read())
            input("\nReturn to menu...")
    except FileNotFoundError:
        print("Credits file not found")

def run_menu():
    """
    Control and execute the menu options.
    """
    clear_screen()
    while True:
        options = ["Play Game", "Rules", "Credits", "Exit"]
        choice_idx = interactive_selection(options, "vertical", "Row: Past the Burn")
        selection = options[choice_idx]

        if selection == "Play Game":
            handle_launch()
        elif selection == "Rules":
            handle_rules()
        elif selection == "Credits":
            handle_credits()
        elif selection == "Exit":
            clear_screen()
            print("Thanks for playing!")
            break
