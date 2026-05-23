import os
import sys
from helpers.nameChanger import get_half_episodes, format_new_name, fix_subtitle_language

# --- KONFIGURASJON ---
TARGET_DIRECTORY = os.environ.get("TARGET_DIR", "./items")

# Reads from environment variables, falls back to your defaults if missing
NAME_PREFIX = os.environ.get("NAME_PREFIX", "filename")
DEFAULT_SEASON = int(os.environ.get("DEFAULT_SEASON", "1"))
LANGUAGE = os.environ.get("LANGUAGE", "en")


def main():
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"Error: Directory {TARGET_DIRECTORY} not found.")
        return

    print(f"Starting processing with Prefix: '{NAME_PREFIX}', Season: {DEFAULT_SEASON}, Lang: '{LANGUAGE}'")
    half_episodes = get_half_episodes(TARGET_DIRECTORY)

    for filename in os.listdir(TARGET_DIRECTORY):
        old_path = os.path.join(TARGET_DIRECTORY, filename)
        
        if os.path.isfile(old_path):
            # 1. Finn nytt navn (Sesong/Episode logikk)
            new_name = format_new_name(filename, half_episodes, DEFAULT_SEASON, NAME_PREFIX)
            
            if new_name:
                new_path = os.path.join(TARGET_DIRECTORY, new_name)
                
                # Utfør omdøping hvis navnet er annerledes
                if filename != new_name:
                    print(f"Renaming: {filename} -> {new_name}")
                    os.rename(old_path, new_path)
                    current_file_path = new_path
                else:
                    current_file_path = old_path

                # 2. Sjekk for språktag hvis det er en .srt fil
                if current_file_path.endswith(".srt"):
                    fix_subtitle_language(current_file_path, LANGUAGE)

if __name__ == "__main__":
    main()