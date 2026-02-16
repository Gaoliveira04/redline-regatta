import os
from config import ASSETS_DIR

class ContentManager:
    def get_rules():
        """
        Obtain the rules in topics from the rules file.
        """
        rules = {}
        path = os.path.join(ASSETS_DIR, "rules.txt")
        try:
            with open(path, "r", encoding = 'utf-8') as f:
                rules_sections = f.read().split("\n\n\n")
                for section in rules_sections:
                    section = section.strip()
                    lines = section.split("\n")
                    title= lines[0].replace(":","").strip()
                    rules[title] = section
            return rules
        except FileNotFoundError:
            print(f"Error: Rules file not found at {path}")
            return None
    
    def get_credits():
        """
        Obtain the credits from the credits file.
        """
        path = os.path.join(ASSETS_DIR, "credits.txt")
        try:
            with open(path, "r", encoding = 'utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Credits file not found at {path}")
            return None