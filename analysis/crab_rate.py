import random
import time
from src.engine.race_logic import GameLogic
from src.engine.npc_logic import NPCLogic

def create_pace_limits():
    """
    Create random pace limits to test 
    """
    paces = [5,6,7]
    meters = [25,50,75,85]
    limit = {}
    for meter in meters:
        pace = random.choice(paces)
        limit[meter] = pace
    return limit

def test_game_crabs(limit, iterations):
    """
    Test game with only NPCs with the random limits.
    """
    crab_results = {}
    for loc in limit.keys():
        crab_results[loc] = 0

    tired_results = {}
    for loc in limit.keys():
        tired_results[loc] = 0

    for _ in range(iterations) :
        boats = GameLogic.create_boat(["No more players"])
        game_running = True

        while game_running:
            for b in boats:
                if b.finished:
                    continue
                b.caught_crab = False
                b.penalized = False
                GameLogic.draw_cards(b)

                if GameLogic.check_clustered_hand(b):
                    GameLogic.replenish_hand(b)
                    continue

                # Stroke rate change
                exhaustion_status = GameLogic.check_stamina(b)
                if exhaustion_status == "ok":
                    rate_choice = NPCLogic.choose_stroke_rate(b, limit)
                    GameLogic.change_stroke_rate(b, rate_choice)

                # Play cards
                available_cards, cards_needed = GameLogic.get_playable_cards(b)
                cards = NPCLogic.choose_cards(b)
                cards_selected = cards[:cards_needed]

                # Movement and Split Limit
                movement= GameLogic.calculate_movement(b, cards_selected)
                status, inf = GameLogic.check_split_limit(b, movement, limit)

                active_loc = None
                for loc in limit:
                    if b.position < loc <= (b.position + movement):
                        active_loc = loc
                        break

                if status == "passed":
                    GameLogic.apply_movement(b, movement)
                elif status == "tired":
                    GameLogic.apply_movement(b, movement)
                    GameLogic.pay_stamina_cards(b, inf)
                    tired_results[active_loc] += 1
                else:
                    GameLogic.apply_crab(b, inf)
                    crab_results[active_loc] += 1
                
                # Replenish hand
                GameLogic.replenish_hand(b)
                b.round += 1

            sorted_boats = sorted(
                boats, 
                key=lambda x: (x.position, x.stroke_rate), 
                reverse=True
            )

            if len(sorted_boats) >= 2:
                # Change of Tides bonus
                for b in [sorted_boats[-1], sorted_boats[-2]]:
                    if b.caught_crab or b.finished:
                        continue     
                    GameLogic.change_tides_bonus(b)

                for i in range(1, len(sorted_boats)):
                    current_boat = sorted_boats[i]
                    boat_ahead = sorted_boats[i-1]
                    
                    if boat_ahead.finished or current_boat.finished or current_boat.penalized or current_boat.caught_crab:
                        continue

                    if GameLogic.can_use_motivation(current_boat, boat_ahead):
                        use_motivation = NPCLogic.choose_motivation(current_boat)
                        if use_motivation == "use":
                            GameLogic.pay_stamina_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

            for b in boats:
                if b.position >= 100:
                    b.finished = True
        
            if all(b.finished for b in boats):
                game_running = False

    return crab_results, tired_results

if __name__ == "__main__":
    start_time = time.time()
    tests = 1000
    iterations = 10

    stats = {"crabs": {l: {p: 0 for p in [5,6,7]} for l in [25,50,75,85]},
             "tired": {l: {p: 0 for p in [5,6,7]} for l in [25,50,75,85]},
             "total": {l: {p: 0 for p in [5,6,7]} for l in [25,50,75,85]}}

    for _ in range(tests):
        limit = create_pace_limits()
        
        # Add number of boats exposures per race for the specific pace limits in the attempts 
        for pace_loc, pace_limit in limit.items():
            stats["total"][pace_loc][pace_limit] += (iterations * 6)

        # Run the simulation
        crabs_found, tired_found = test_game_crabs(limit, iterations)

        # Add number of crabs and tired returns for the specific pace limits in the results 
        for loc, count in crabs_found.items():
            stats["crabs"][loc][limit[loc]] += count

        for loc, count in tired_found.items():
            stats["tired"][loc][limit[loc]] += count

    # Report Results
    print(f"Simulated {tests * iterations * 6} boat races in {time.time() - start_time:.2f} seconds.")

    print("\nCrab Results")
    print("=" * 40)
    print(f"{'SPLIT':<8} | {'PACE':<6} | {'STATUS':<8} | {'TOTAL':<8}")
    print("-" * 40)

    for category in ["crabs", "tired"]:
        print(f"\n{category.upper()} RESULTS")
        print("="*40)
        print(f"{'SPLIT':<8} | {'PACE':<6} | {category.upper():<8} | {'%':>6}")
        for loc in [25, 50, 75, 85]:
            for pace in [5, 6, 7]:
                c = stats[category][loc][pace]
                t = stats["total"][loc][pace]
                perc = (c/t*100) if t > 0 else 0
                print(f"{loc:<8} | {pace:<6} | {c:<8} | {perc:>6.2f}%")
            print("-" * 40)