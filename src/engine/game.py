import time
import random
from src.interface.interaction import interactive_selection
from src.interface.draw import draw_venue, draw_leaderboard
from src.engine.constants import VENUE_LENGTH, COLORS
from src.engine.boat import Boat
from src.engine.card_logic import CardLogic
from src.engine.race_logic import RaceLogic

def select_boat():
    """
    Allows players to chose representative color and randomly assigns a lane.
    Creates npc from remaining availabel colors/lanes
    """
    lanes = [1,2,3,4,5,6]
    available_colors = list(COLORS.keys())
    boat_data = []

    # Create player
    for i in range(len(lanes)):
        options = available_colors + ["No more players"]
        choice_idx = interactive_selection(options, "vertical", f"Player {i+1} Selection:")
        selection = options[choice_idx]

        if selection == "No more players":
            break

        lane = random.choice(lanes)
        lanes.remove(lane)
        boat_data.append((selection,COLORS[selection], lane, False))
        available_colors.remove(selection)

    # Create npc
    while lanes:
        npc_lane = random.choice(lanes)
        lanes.remove(npc_lane)
        npc_color = available_colors.pop(0)
        boat_data.append((npc_color,COLORS[npc_color], npc_lane, True))

    boats = []
    for name, color, lane, is_npc in boat_data:
        new_boat = Boat(name = name, color= color, lane= lane,is_npc= is_npc)
        boats.append(new_boat)
    return boats

def game(boats):
    """
    Create a loop with the game steps until all players finish game
    """
    game_running = True
    round_number = 1
    draw_venue(boats)
    time.sleep(5)

    while game_running:

        # ------ INDIVIDUAL PHASE ------
        for b in boats:
            if b.finished:
                continue
            
            # Show next player
            options = ["continue"]
            title_msg = f"{b.name}'s Turn (Pos: {b.position * 20}m | Rate: {b.stroke_rate})"
            choice_idx = interactive_selection(options, "vertical", title_msg, b.color)
            selection = options[choice_idx]

            # 1. DRAW AND CHECK CLUSTERED CARDS
            CardLogic.draw_cards(b)

            # Show stats
            options = ["continue"]
            title_msg = f"{b.name}'s (Pos: {b.position * 20}m | Rate: {b.stroke_rate} | Hand: {b.hand} | Stamina: {b.stamina_pile})"
            choice_idx = interactive_selection(options, "vertical", title_msg, b.color)
            selection = options[choice_idx]

            clustered = CardLogic.check_clustered_hand(b)

            if clustered:
                print(f"!!! {b.name} has a CLUTTERED HAND! Stalled this turn. !!!")
                CardLogic.finish_turn(b)
                time.sleep(2)
                continue

            # 2. STROKE RATE
            rate_choice = "maintain"
            jump_choice = False

            # Detect if it's a player
            if not b.is_npc:
                options = ["maintain", "up", "down"]
                title_msg = f"Current Rate: {b.stroke_rate}. Change?"
                choice_idx = interactive_selection(options, "vertical", title_msg, b.color)
                rate_choice = options[choice_idx]

                if rate_choice != "maintain":
                    if len(b.stamina_pile) > 0:
                        options = ["Normal Shift", "Boost Jump (Cost 1 Stamina)"]
                        choice_idx = interactive_selection(options, "vertical", "Do you want to boost?", b.color)
                        jump_choice = (choice_idx == 1)
            else:
                import random
                if random.random() > 0.8 and b.stroke_rate < 3:
                    rate_choice = "up"

            CardLogic.change_stroke_rate(b, rate_choice, jump_choice)

            # 3. PLAY CARDS
            cards_selected = []
            cards_needed = b.stroke_rate + 1

            if not b.is_npc:
                for i in range(cards_needed):
                    valid_cards = [c for c in b.hand if c != "e"]

                    if not valid_cards:
                        print("Not enough playable cards!")
                        break
                    
                    title_msg = f"Select Card {i+1}/{cards_needed}:"
                    choice_idx = interactive_selection(valid_cards, "horizontal", title_msg, b.color)
                    card_value = valid_cards[choice_idx]
                    cards_selected.append(card_value)
                    b.hand.remove(card_value)
            else:
                valid_cards = [c for c in b.hand if c != "e"]
                cards_selected = valid_cards[:cards_needed]
                for c in cards_selected:
                    b.hand.remove(c)

            # 4. OPTIONAL CARDS DISCARD
            if not b.is_npc:
                options = ["Discard", "No discard"]
                choice_idx = interactive_selection(options, "vertical", "Discard any cards?", b.color) 
                selection = options[choice_idx]
                
                if selection == 0:
                    while True:
                        options = b.hand + ["Done"]
                        choice_idx = interactive_selection(options, "horizontal", "Select card to discard:", b.color)
                        selection = options[choice_idx]
                        if selection == "Done":
                            break
                        elif selection in [1,2,3]:
                            b.discard_pile.append(b.hand[choice_idx])
                            b.hand.pop(choice_idx)

            # 5. MOVEMENT
            movement= CardLogic.calculate_movement(b, cards_selected)
            caught_crab = RaceLogic.check_split_limit(b, movement)

            if not caught_crab:
                    b.position += movement
            
            # 6. REPLENISH HAND
            CardLogic.finish_turn(b)

            # Display results
            if not caught_crab:
                options = ["continue"]
                title_msg = f"{b.name} moves {movement} spaces. New Position: {b.position}"
                choice_idx = interactive_selection(options, "vertical", title_msg, b.color)
                selection = options[choice_idx]
            else:
                options = ["continue"]
                title_msg = f"CRAB! {b.name} pushed too hard and lost momentum."
                choice_idx = interactive_selection(options, "vertical", title_msg, b.color)
                selection = options[choice_idx]         
        
        # ------ VIEW BOARD ------
        draw_venue(boats)
        time.sleep(2)

        # ------ END OF ROUND BONUSES ------      
        # Sort boats based on position and stroke rate
        sorted_boats = sorted(boats, key = lambda b: (b.position, b.stroke_rate), reverse=True)

        if len(sorted_boats) >= 2:
            print("\n--- BONUSES PHASE ---")

            # Add Change of Tides bonus for last two boats
            if len(sorted_boats) > 2:
                sorted_boats[-2].position += 1
                sorted_boats[-1].position += 1

                options = ["continue"]
                title_msg = f"Change of Tides applies to {sorted_boats[-1].name} and {sorted_boats[-2].name}"
                choice_idx = interactive_selection(options, "vertical", title_msg)
                selection = options[choice_idx]
            else:
                print("")

            # Allow Motivation to be played if possibel
            for i in range(1, len(sorted_boats)):
                current_boat = sorted_boats[i]
                boat_ahead = sorted_boats[i-1]

                dist = boat_ahead.position - current_boat.position

                if dist == 0 or dist == 1:
                    can_pay = len(current_boat.stamina_pile) >= 1

                    if not current_boat.is_npc:
                        if can_pay:
                            options = ["Activate Motivation (+2 Spaces, Cost 1 Stamina)", "Hold Position"]
                            title_msg = f"MOTIVATION: {current_boat.name} is drafting {boat_ahead.name}! Activate bonus {current_boat.name}?"
                            choice_idx = interactive_selection(options, "vertical", title_msg, current_boat.color)
                            
                            if choice_idx == 0:
                                CardLogic.pay_exhaustion_cards(current_boat, 1)
                                current_boat.position += 2 
                                print("Motivation Activated!")
                        else:
                            print("Drafting possible, but not enough Stamina.")
                    else:
                        if can_pay:
                            CardLogic.pay_exhaustion_cards(current_boat, 1)
                            current_boat.position += 2
                            print(f"{current_boat.name} (NPC) uses Motivation!")
                    
                    draw_venue(boats)                        

        # ------ CHECK FINISH LINE ------
        for b in boats:
            if b.position >= VENUE_LENGTH:
                b.finished = True
                print(f"*** {b.name} HAS FINISHED! ***")
        
        # ------ FINISH GAME ------
        if all(b.finished for b in boats):
            if all(b.finished for b in boats):                
                # Return final standings
                final_standings = sorted(boats, key=lambda x: x.position, reverse=True)
                draw_leaderboard(final_standings)
                time.sleep(2)
                game_running = False
        
        round_number += 1
        time.sleep(5)

def run_game():
    boats = select_boat()
    game(boats)

run_game()