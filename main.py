#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from src.controllers.menu import MenuController
from src.controllers.game import GameController

def main():
    try:
        while True:
            signal, chosen_colors = MenuController.run_menu()

            if signal == "Start":
                game = GameController(chosen_colors)
                game.run_game()
            elif signal == "Exit":
                print("\nThanks for playing! See you at the next starting line.")
                break

        sys.exit(0)
    except KeyboardInterrupt:
        print("\n[!] Game closed manually. See you on the water!")
        sys.exit(0)

if __name__ == "__main__":
    main()