import os

def clear_screen():
    """
    Clear screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def terminal_size():
    """
    Obtain terminal size
    """
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size[0]
    return terminal_width    

def draw_header(title):
    """
    Draw a centred header using the terminal size.
    """
    width = terminal_size()
    
    # Calculate empty space needed for title
    input_length = len(title)
    padding_required = int((width - input_length) / 2)
    padding = " " * padding_required

    # Calculate empty space needed for separator
    if input_length % 2 == 0:
        bar_length = input_length * 2
        padding_required2 = int((width - bar_length) / 2)
        padding2 = " " * padding_required2
    else:
        bar_length = (input_length * 2) + 1
        padding_required2 = int((width - bar_length) / 2)
        padding2 = " " * padding_required2     

    # Print header
    print("")
    print(padding + title)
    print(padding2 + ("─" * bar_length))

def draw_options(options, selected_index, color=None):
    """
    Finds the widest option to create a 'box' and centers that box,
    ensuring all arrows and text start at the same horizontal position.
    """
    width = terminal_size()
    
    # Find the longest option to determine the width of our menu block
    max_option_len = max(len(opt) for opt in options) + 4
    
    # Calculate the starting position for all lines
    margin = (width - max_option_len) // 2
    padding = " " * margin

    if color == None:
        color = "\033[0;36m"

    for i, option in enumerate(options):
        if i == selected_index:
            text = f"➤ {option.upper()}"
            print(f"{padding}{color}{text}\033[0m")
        else:
            text = f"  {option}"
            print(f"{padding}{text}")

def draw_cards(options, selected_index, color=None):
    """
    Finds the total size of the options in the screen and center them.
    """
    width = terminal_size()

    # Build list of cards as they appear
    colored_cards = []
    visual_width = 0
    
    spacing = "  "

    if color == None:
        color = "\033[0;36m"

    for i, option in enumerate(options):
        if i == selected_index:
            card_text = f"➤[{option}]"
            colored_cards.append(f"{color}{card_text}\033[0m")
        else:
            card_text = f" [{option}]"
            colored_cards.append(card_text)
        
        # Track how many characters wide this is on screen
        visual_width += len(card_text)
    
    # Add the spacing to the cards
    visual_width += len(spacing) * (len(options) - 1)

    # Calculate the margin to center text
    margin = max(0, (width - visual_width) // 2)
    padding = " " * margin

    full_row = spacing.join(colored_cards)
    print(f"\n{padding}{full_row}\n")

def draw_venue(boats, venue_length=100):
    """
    Draws the lanes for the race and the boats in the correct position
    """
    clear_screen()
    width = terminal_size()

    if width < 40:
        print("Please widen your terminal to view the race!")
        return

    lane_size = int(width * 0.8)
    scale = lane_size / venue_length

    padding_required = (width - lane_size) // 2
    padding = " " * padding_required

    header_text = "ROWING VENUE"
    print("\n" + " " * (padding_required + (lane_size // 2) - (len(header_text) // 2)) + header_text)
    
    # Draw lanes and boat position
    for b in boats:
        print(padding + ("─" * lane_size))

        pos_index = int(b.position * scale)
        pos_index = max(0, min(pos_index, lane_size - 1))

        visual_pos = " " * pos_index
        finish_marker = "" if b.position < venue_length else " ★"

        print(f"{padding}{visual_pos}{b.color}●{finish_marker}\033[0m")
    
    # Draw final bondary
    print(padding + ("─" * lane_size))
    print(padding + (" " * ((lane_size // 4) - 1)) + "^" + (" " * ((lane_size // 4) - 1)) + "^" + (" " * ((lane_size // 4) - 1)) + "^" + (" " * ((lane_size // 8) - 1)) + "^")
    print(padding + (" " * ((lane_size // 4) - 1)) + "500m" + (" " * ((lane_size // 4) - 4)) + "1000m" + (" " * ((lane_size // 4) - 5)) + "1500m" + (" " * ((lane_size // 8) - 5)) + "1750m")
    print(padding + (" " * ((lane_size // 4) - 1)) + "SL: 4" + (" " * ((lane_size // 4) - 5)) + "SL: 5" + (" " * ((lane_size // 4) - 5)) + "SL: 6" + (" " * ((lane_size // 8) - 5)) + "SL: 8")


def draw_leaderboard(positions, title):
    """
    Draws leaderboard with positions during race and turns when the race finished if title contains "Finish" or "Final"
    """
    width = terminal_size()

    # Calculate empty space needed for title
    input_length = len(title)
    padding_required = int((width - input_length) / 2)
    padding = " " * padding_required

    # Calculate empty space needed for separator
    bar_length = input_length * 3
    padding__bar_required = int((width - bar_length) / 2)
    padding_bar = " " * padding__bar_required

    # Print header
    print("")
    print(padding_bar + ("─" * bar_length))
    print(padding + title)
    print(padding_bar + ("─" * bar_length))

    show_turns = "Finish" in title or "Final" in title

    # Calculate empty space needed for ranking
    max_option_len = max(len(f"1. {b.name}  Turns:{b.position}") for b in positions)
    margin = (width - max_option_len) // 2
    padding = " " * margin

    for i, b in enumerate(positions):
        text = f"Turns: {b.turn}" if show_turns else f"Dist: {b.position * 20}m"
        print(f"{padding}{b.color}{i+1}. {b.name:<8} {text}\033[0m")