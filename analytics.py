import mysql.connector
import config
import re

def calculate_stats_for_query(cursor, filter_query=None):
    """Helper function to calculate stats based on a specific SQL filter."""
    
    # Base query for hands
    sql = "SELECT raw_text, pot_size, hero_cards, board FROM tournament_hands"
    if filter_query:
        sql += f" WHERE {filter_query}"
    
    cursor.execute(sql)
    all_hands = cursor.fetchall()
    
    total_hands = len(all_hands)
    if total_hands == 0:
        return None

    vpip_count = 0
    hands_won = 0
    played_hands_count = 0
    biggest_pot = {"size": 0, "cards": "", "board": ""}

    for row in all_hands:
        text = row['raw_text']
        
        # 1. Calculate VPIP & Win Rate
        if "*** HOLE CARDS ***" in text:
            parts = text.split("*** HOLE CARDS ***")
            preflop_section = re.split(r'\*\*\* (FLOP|SUMMARY|SHOWDOWN) \*\*\*', parts[1])[0]
            
            # Check for voluntary action
            is_vpip = re.search(r'Hero: (calls|raises)', preflop_section)
            # Check if Hero won
            is_winner = "Hero won" in text or "Hero collected" in text

            if is_vpip:
                vpip_count += 1
                played_hands_count += 1
                if is_winner:
                    hands_won += 1
            elif "Hero: posts" in text and "Hero: folds" not in preflop_section:
                # Big Blind/Small Blind special cases (checking)
                played_hands_count += 1
                if is_winner:
                    hands_won += 1

        # 2. Track Biggest Win
        if ("Hero won" in text or "Hero collected" in text) and row['pot_size'] > biggest_pot['size']:
            biggest_pot = {
                "size": row['pot_size'],
                "cards": row['hero_cards'],
                "board": row['board']
            }

    return {
        "total": total_hands,
        "vpip": (vpip_count / total_hands) * 100 if total_hands > 0 else 0,
        "win_rate": (hands_won / played_hands_count) * 100 if played_hands_count > 0 else 0,
        "biggest_pot": biggest_pot
    }

def print_report(title, stats):
    """Prints a formatted report block."""
    print(f"\n--- {title.upper()} ---")
    if not stats:
        print("No data found for this category.")
        return
        
    print(f"Total hands analyzed: {stats['total']}")
    print(f"VPIP: {stats['vpip']:.2f}%")
    print(f"Win Rate (when playing): {stats['win_rate']:.2f}%")
    
    bp = stats['biggest_pot']
    if bp['size'] > 0:
        print(f"Biggest Pot Won: {bp['size']} chips")
        print(f"Hand: [{bp['cards']}] | Board: [{bp['board']}]")
    print("-" * 30)

def get_basic_stats():
    try:
        db = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db.cursor(dictionary=True)

        print("\n" + "="*40)
        print("      POKER ANALYTICS REPORT")
        print("="*40)

        # 1. Total (Combined)
        total_stats = calculate_stats_for_query(cursor)
        print_report("Combined Results", total_stats)

        # 2. Freeroll only
        freeroll_stats = calculate_stats_for_query(cursor, "game_type = 'Freeroll'")
        print_report("Freeroll Stats", freeroll_stats)

        # 3. Mystery Bounty only
        mystery_stats = calculate_stats_for_query(cursor, "game_type = 'Mystery'")
        print_report("Mystery Bounty Stats", mystery_stats)

        print("="*40 + "\n")

        cursor.close()
        db.close()

    except Exception as e:
        print(f"Error in analytics: {e}")

if __name__ == "__main__":
    get_basic_stats()