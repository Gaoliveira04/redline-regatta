import random
import time
from src.engine.race_logic import GameLogic

def create_pace_limits():
    """
    Create random pace limits to test 
    """
    paces = [5,6,7,8]
    meters = [25,50,75,85]
    limit = {}
    for meter in meters:
        pace = random.choice(paces)
        limit[meter] = pace
    return limit

def test_game_crabs(limit, interactions):
    """
    Test game with only NPCs with the random limits.
    """
    batch_results = {}
    for loc in limit.keys():
        batch_results[loc] = 0

    failed_tracker = {}
    for loc in limit.keys():
        failed_tracker[loc] = set()

    for _ in range(interactions) :
        boats = GameLogic.create_boat(["No more players"])
        game_running = True

        while game_running:
            for b in boats:
                if b.finished:
                    continue

                GameLogic.draw_cards(b)

                # Stroke rate change
                # Identify playbel cards
                playable_cards = sorted(
                    [c for c in b.hand if c != 's'], 
                    key=lambda x: (x if isinstance(x, int) else 2), 
                    reverse=True
                )
                
                # Determine best Stroke Rate for this round
                best_rate = "35 spm"
                rate_map = {2: 4, 1: 2, 0: 1}

                for rate in [2,1,0]:
                        needed = rate_map[rate]

                        # Check if npc has enough playble cards for the Stroke Rate
                        if len(playable_cards) < needed:
                            continue

                        # Calculate estimated speed
                        cards_to_play = playable_cards[:needed]
                        est_speed = sum([(c if isinstance(c, int) else 2) for c in cards_to_play])

                        # Check Split Limits
                        next_pos = b.position + est_speed
                        next_limit_pace = None
                        next_limit_loc = None
                        for limit_loc, limit_pace in limit.items():
                            if b.position < limit_loc <= next_pos:
                                next_limit_loc = limit_loc
                                next_limit_pace = limit_pace
                                break
                            
                        # If no split to be crossed or estimated speed inferior or equal to pace limit,
                        # pick best Stroke Rate and stop checking
                        if next_limit_pace is None or est_speed <= next_limit_pace:
                            best_rate = rate
                            break

                        #  Use random decision to decide if NPC exceeds pace limit
                        aggressive_prob = (next_limit_loc / 100) * 0.60
                        if random.random() < aggressive_prob:
                            exhaustion_cost = max(1, int(est_speed - next_limit_pace))

                            # See if stamina is sufficient
                            if len(b.stamina_pile) >= exhaustion_cost:
                                best_rate = rate
                                break
                            else:
                                gamble_prob = (next_limit_loc / 100) * 0.40
                                if random.random() < gamble_prob:
                                    best_rate = rate
                                    break

                # If hand full with Stamina Cards, reduce Stroke Rate to 35 spm
                if b.hand.count("s") >= 2:
                    best_rate = 0

                GameLogic.change_stroke_rate(b, best_rate)

                # Play cards
                available_cards, cards_needed = GameLogic.get_playable_cards(b)
                available_cards.sort(
                    key=lambda x: (x if isinstance(x, int) else 2),
                    reverse=True
                )
                cards_selected = available_cards[:cards_needed]

                # Movement and Split Limit
                movement= GameLogic.calculate_movement(b, cards_selected)

                active_loc = None
                for loc in limit:
                    if b.position < loc <= (b.position + movement):
                        active_loc = loc
                        break

                status = GameLogic.check_split_limit(b, movement, limit)

                if status in ["Passed", "Tired"]:
                    GameLogic.apply_movement(b, movement)
                elif status == "Crab" and active_loc:
                    if b.name not in failed_tracker[active_loc]:
                        batch_results[active_loc] += 1
                        failed_tracker[active_loc].add(b.name)
                
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
                    if not b.caught_crab or not b.finished:
                        GameLogic.change_tides_bonus(b)            

                for idx in range(1, len(sorted_boats)):
                    current_boat = sorted_boats[idx]
                    boat_ahead = sorted_boats[idx-1]

                    if boat_ahead.finished or current_boat.finished or current_boat.caught_crab:
                        continue
                    
                    if GameLogic.can_use_motivation(current_boat, boat_ahead):
                        if len(current_boat.stamina_pile) > 0:
                            GameLogic.pay_stamina_cards(current_boat, 1)
                            GameLogic.motivation_bonus(current_boat)

            for b in boats:
                if b.position >= 100:
                    b.finished = True
        
            if all(b.finished for b in boats):
                game_running = False

    return batch_results

if __name__ == "__main__":
    start_time = time.time()
    total_tests = 1000
    batch_interactions = 10

    results = {
        25: {5:0, 6:0, 7:0, 8:0},
        50: {5:0, 6:0, 7:0, 8:0},
        75: {5:0, 6:0, 7:0, 8:0},
        85: {5:0, 6:0, 7:0, 8:0}
    }
    
    attempts = {
        25: {5:0, 6:0, 7:0, 8:0},
        50: {5:0, 6:0, 7:0, 8:0},
        75: {5:0, 6:0, 7:0, 8:0},
        85: {5:0, 6:0, 7:0, 8:0}
    }

    for t in range(total_tests):
        # Create pace limits
        limit = create_pace_limits()
        
        # Add number of races for the specific pace limits in the attempts 
        for pace_loc, pace_limit in limit.items():
            # Count boats exposures per race, not races
            attempts[pace_loc][pace_limit] += (batch_interactions * 6)

        # Run the simulation
        crabs_found = test_game_crabs(limit, interactions=batch_interactions)

        # Add number of crabs for the specific pace limits in the results 
        for loc, count in crabs_found.items():
            current_pace = limit[loc]
            results[loc][current_pace] += count

    # Report Results
    print(f"Simulation Complete: {total_tests * batch_interactions * 6} boat races in {time.time() - start_time:.2f} seconds.")

    print("\nFinal Results")
    print("=" * 75)
    print(f"{'SPLIT':<8} | {'PACE':<6} | {'CRABS':<8} | {'TOTAL':<8} | {'CRAB %'}")
    print("-" * 75)

    for loc in sorted(results.keys()):
        for pace in sorted(results[loc].keys()):
            count = results[loc][pace]
            total = attempts[loc][pace]
            percentage = (count / total * 100) if total > 0 else 0
            
            risk = ""
            if percentage > 35:
                risk = " [!] HIGH RISK"
            elif percentage > 15:
                risk = " [!] RISKED"
               
            print(f"{loc:<8} | {pace:<6} | {count:<8} | {total:<8} | {percentage:>6.2f}%{risk}")
        print("-" * 75)