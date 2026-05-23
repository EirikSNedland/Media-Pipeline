import re
import os

def get_file_data(filename):
    """
    Søker etter både sesong og episode.
    Støtter: s01e01, s1e1, test-1, test - 1.5, ep22
    """
    # Finn sesong (ser etter s01, s1, etc)
    season_match = re.search(r's(\d+)', filename, re.IGNORECASE)
    season = int(season_match.group(1)) if season_match else None

    # Finn episode (ser etter e, ep, eller -)
    episode_match = re.search(r'(?:e|ep|-\s*)(\d+(\.5)?)', filename, re.IGNORECASE)
    
    if episode_match:
        raw_val = episode_match.group(1)
        ep_num = int(float(raw_val))
        is_half = '.5' in raw_val
        return season, ep_num, is_half
    
    return season, None, None

def get_half_episodes(directory):
    episodes_with_half = set()
    if not os.path.isdir(directory):
        return episodes_with_half

    for f in os.listdir(directory):
        _, ep_num, is_half = get_file_data(f)
        if ep_num is not None and is_half:
            episodes_with_half.add(ep_num)
    return episodes_with_half

def format_new_name(filename, episodes_with_half, default_season, name_prefix):
    """Bygger det komplette filnavnet."""
    season_found, ep_num, is_half = get_file_data(filename)
    
    if ep_num is None:
        return None

    # Bruk funnet sesong, eller fallback til default
    season_val = season_found if season_found is not None else default_season
    
    # Formater episode-streng med part-logikk
    if ep_num in episodes_with_half:
        ep_suffix = "-part2" if is_half else "-part1"
        e_str = f"{ep_num:02d}{ep_suffix}"
    else:
        e_str = f"{ep_num:02d}"

    s_str = f"{int(season_val):02d}"
    extension = os.path.splitext(filename)[1]
    
    return f"{name_prefix} s{s_str}e{e_str}{extension}"

import re
import os

# ... (behold get_file_data, get_half_episodes og format_new_name fra forrige svar)

def fix_subtitle_language(filepath, language):
    """
    Sjekker om en .srt fil har språktag. 
    Hvis ikke, legger den til den angitte språkkoden.
    """
    directory, filename = os.path.split(filepath)
    if not filename.endswith(".srt"):
        return

    base, ext = os.path.splitext(filename)
    
    # Sjekker om filen allerede slutter på .no, .en, .eng osv.
    if re.search(r'\.[a-z]{2,3}$', base, flags=re.IGNORECASE):
        return # Har allerede språktag

    new_filename = f"{base}.{language}{ext}"
    new_path = os.path.join(directory, new_filename)
    
    print(f"Adding language tag: {filename} -> {new_filename}")
    os.rename(filepath, new_path)