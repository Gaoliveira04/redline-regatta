from src.interface.interaction import interactive_selection
from src.interface.draw import clear_screen, draw_header
from src.engine.constants import COLORS
from src.engine.content import ContentManager

class MenuController:
    @staticmethod
    def select_colors():
        """
        Handles the loop for players to choose their boat colors.
        Returns a list of selected color names.
        """
        available_colors = list(COLORS.keys())
        chosen_colors = []
        for i in range(6):
            options = available_colors + ["Start race"]
            title_msg = f"Player {i+1} Select Color:"
            choice_idx = interactive_selection(options, "vertical", title_msg)
            selection = options[choice_idx]
            
            if selection == "Start race":
                break
            
            chosen_colors.append(selection)
            available_colors.remove(selection)
        return chosen_colors
    
    @staticmethod
    def show_rules(rules: dict):
        """
        Display an interactive menu of the rules.
        """
        options = list(rules.keys()) + ["Done"]
        while True:
            choice_idx = interactive_selection(options, "vertical", "Redline Regatta Rules:")
            selection = options[choice_idx]
            
            if selection == "Done":
                break

            clear_screen()
            draw_header(f"Rule: {selection}")
            print("\n" + rules[selection])
            print("\n" + ("-" * 30))
            input("Enter to return...")

    @staticmethod
    def show_credits(credits):
        """
        Display credits.
        """
        clear_screen()
        draw_header("Credits")
        
        if credits:
            print(credits)
        else:
            print("\n[Error] Credits file (assets/credits.txt) not found.")
        
        print("\n" + ("-" * 30))
        input("Enter to return...")

    @staticmethod
    def run_menu():
        """
        Main Menu Loop.
        """
        while True:
            options = ["Start Race", "Rules", "Credits", "Exit"]
            choice_idx = interactive_selection(options, "vertical", "Redline Regatta")
            selection = options[choice_idx]

            if selection == "Start Race":
                colors = MenuController.select_colors()
                return "Start", colors
            elif selection == "Rules":
                rules = ContentManager.get_rules()
                MenuController.show_rules(rules)
            elif selection == "Credits":
                credits = ContentManager.get_credits()
                MenuController.show_credits(credits)
            elif selection == "Exit":
                return "Exit", []