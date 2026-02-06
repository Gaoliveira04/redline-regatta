#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import src.interface.menu as menu
from config import SRC_DIR

def initialize_project():
    """Ensures all necessary folders exist before the app starts."""
    for folder in [SRC_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[!] Created missing directory: {folder}")

def main():
    initialize_project()
    
    try:
        menu.run_menu()
        
    except KeyboardInterrupt:
        print("\n\n[!] Program closed by user. Goodbye!")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR]: {e}")
        input("Press Enter to exit...")
        
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()