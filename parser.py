import mysql.connector
import os
import re
import config

def parse_and_import(folder_path, game_type):
    """
    Parses poker hand history files and imports them with English comments.
    Now includes file tracking for better visibility.
    """
    try:
        # 1. Connect to MariaDB
        db = mysql.connector.connect(**config.DB_CONFIG)
        cursor = db.cursor()
        
        # 2. Validate folder path
        if not os.path.exists(folder_path):
            print(f"Error: Directory {folder_path} not found.")
            return

        # 3. Get all .txt files and start processing
        files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        total_hands_saved = 0

        print(f"\n--- Starting import for {game_type} ---")

        for filename in files:
            # Re-added the file tracking print
            print(f"Processing file: {filename}...")
            
            full_path = os.path.join(folder_path, filename)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 4. Split file into individual hands using lookahead
            hands = re.split(r'(?=Poker Hand #)', content)
            
            for hand_text in hands:
                if not hand_text.strip() or "Poker Hand #" not in hand_text:
                    continue
                
                try:
                    # --- IMPROVED REGEX LOGIC ---
                    
                    # Hand ID: Captures everything after # until colon (works for BR, TM, etc.)
                    hand_id_match = re.search(r'Poker Hand #([A-Z0-9]+):', hand_text)
                    hand_id = hand_id_match.group(1) if hand_id_match else None
                    
                    # Tournament ID
                    tourney_match = re.search(r'Tournament #(\d+)', hand_text)
                    tourney_id = tourney_match.group(1) if tourney_match else None
                    
                    # Date (YYYY/MM/DD)
                    date_match = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', hand_text)
                    hand_date = date_match.group(1).replace('/', '-') if date_match else None
                    
                    # Level
                    level_match = re.search(r'Level\s?(\d+)', hand_text)
                    if level_match:    
                        level_info = f"Level {level_match.group(1)}"
                    else:
                        level_info = "Unknown"
                    
                    # Hero's Cards
                    hero_match = re.search(r'Dealt to Hero \[(.*?)\]', hand_text)
                    hero_cards = hero_match.group(1) if hero_match else None

                    # Board
                    board_match = re.search(r'Board \[(.*?)\]', hand_text)
                    board = board_match.group(1) if board_match else None

                    # Pot Size
                    pot_match = re.search(r'Total pot (\d+(?:,\d+)?)', hand_text)
                    pot_size = int(pot_match.group(1).replace(',', '')) if pot_match else 0

                    if hand_id:
                        # 5. Insert or Ignore
                        sql = """
                        INSERT IGNORE INTO tournament_hands 
                        (hand_id, tournament_id, hand_date, level_info, hero_cards, pot_size, board, raw_text, game_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        val = (hand_id, tourney_id, hand_date, level_info, hero_cards, pot_size, board, hand_text, game_type)
                        cursor.execute(sql, val)
                        
                        if cursor.rowcount > 0:
                            total_hands_saved += 1

                except Exception:
                    # Silently skip individual hand parsing errors
                    continue

            # Commit after each file for stability
            db.commit()

        print(f"Done! Successfully saved {total_hands_saved} new {game_type} hands.")
        
    except Exception as e:
        print(f"Critical error in parser: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
