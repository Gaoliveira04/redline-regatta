import sys
from src.interface.draw import draw_header, draw_options, draw_cards

# Detect OS for key handling
try:
    import msvcrt # Windows
    WINDOWS = True
except ImportError:
    import tty, termios # Mac/Linux
    WINDOWS = False

def get_key(mode):
    """
    Captures a single key press and filter based on mode
    mode = "vertical": up, down and enter keys.
    mode = "horizontal": left, right and enter keys.
    """
    key_pressed = None

    if WINDOWS:
        key = msvcrt.getch()
        if key in [b'\x00', b'\xe0']:
            key = msvcrt.getch()
            mapping = {
                b'H': 'up', 
                b'P': 'down', 
                b'K': 'left', 
                b'M': 'right'
            }
            key_pressed = mapping.get(key)
        elif key in [b'\r', b'\n']:
            key_pressed = 'enter'
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            
            # Check for escape sequences (start of an arrow key)
            if ch == '\x1b':
                seq = sys.stdin.read(2)
                mapping = {
                    '[A': 'up', 
                    '[B': 'down', 
                    '[C': 'right', 
                    '[D': 'left'
                }
                key_pressed = mapping.get(seq)
            # Check for Enter/Return
            elif ch in ('\r', '\n'):
                key_pressed = 'enter'
            
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Filter by mode
    if mode == "vertical":
        if key_pressed in ['up', 'down', 'enter']:
            return key_pressed 
        else:
            None
    if mode == "horizontal":
        if key_pressed in ['left', 'right', 'enter']:
            return key_pressed 
        else:
            None
    return key_pressed

def interactive_selection(options, type, title, color=None):
    """
    Allows interactive selection by capturing allowed keys entered. 
    Return the index of the selected element.
    """
    current_idx = 0
    sys.stdout.write("\033[?25l") 
    sys.stdout.flush()

    try:
        while True:
            sys.stdout.write("\033[H\033[J") 
            draw_header(title)

            if type == "vertical": 
                draw_options(options, current_idx, color)
                key = get_key(type)
                if key == 'up':
                    current_idx = (current_idx - 1) % len(options)
                elif key == 'down':
                    current_idx = (current_idx + 1) % len(options)
                elif key == 'enter':
                    return current_idx
                
            elif type == "horizontal":
                draw_cards(options, current_idx, color)
                key = get_key(type)
                if key == 'left':
                    current_idx = (current_idx - 1) % len(options)
                elif key == 'right':
                    current_idx = (current_idx + 1) % len(options)
                elif key == 'enter':
                    return current_idx
            
            sys.stdout.flush()

    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()