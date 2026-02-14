import os
from src.interface.interaction import interactive_selection
from src.interface.draw import clear_screen
from src.engine.constants import COLORS
from config import ASSETS_DIR

class MenuController:
    def select_colors():
        available_colors = list(COLORS.keys())
        chosen_colors = []
        for i in range(6):
            options = available_colors + ["No more players"]
            choice_idx = interactive_selection(options, "vertical", f"Player {i+1} Color:")
            selection = options[choice_idx]
            if selection == "No more players":
                break
            chosen_colors.append(selection)
            available_colors.remove(selection)
        return chosen_colors
    
    def show_rules():
        """
        Display an interactive menu to read rules by topic from the rules file.
        """
        rules = {}
        try:
            path = os.path.join(ASSETS_DIR, "rules.txt")
            with open(path, "r", encoding = 'utf-8') as f:
                rules_sections = f.read().split("\n\n\n")
                for section in rules_sections:
                    section = section.strip()
                    lines = section.split("\n")
                    title= lines[0].replace(":","").strip()
                    rules[title] = section
        except FileNotFoundError:
            print("Rules file not found")

        options = list(rules.keys()) + ["Done"]
        while True:
            choice_idx = interactive_selection(options, "vertical", "Redline Regatta Rules:")
            selection = options[choice_idx]
            if selection == "Done":
                break
            elif selection in rules:
                clear_screen()
                print("\n" + rules[selection])
                print("-" * 30)
                input("Enter to return...")
            else:
                print(f"Content for {selection} is missing.")
                input("Enter to return...")

    def show_credits():
        """
        Read the credits files and outputs it.
        """
        try:
            path = os.path.join(ASSETS_DIR, "credits.txt")
            with open(path, "r", encoding = 'utf-8') as f:
                clear_screen()
                print(f.read())
                input("\nEnter to return...")
        except FileNotFoundError:
            print("Credits file not found")

    def run_menu():
        while True:
            options = ["Start Race", "Rules", "Credits", "Exit"]
            choice_idx = interactive_selection(options, "vertical", "Redline Regatta")
            selection = options[choice_idx]

            if selection == "Start Race":
                colors = MenuController.select_colors()
                return "Start", colors
            elif selection == "Rules":
                MenuController.show_rules()
            elif selection == "Credits":
                MenuController.show_credits()
            elif selection == "Exit":
                return "Exit", []