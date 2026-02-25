import config
import parser
import analytics

def main():
    print("--- Poker Analytics System ---")
    
    # 1. Import Freeroll hands
    # We pass the path from config and the label 'Freeroll'
    print("Checking for new Freeroll hands...")
    parser.parse_and_import(config.FREEROLL_PATH, "Freeroll")
    
    # 2. Import Mystery Bounty hands
    # We pass the path from config and the label 'Mystery'
    print("Checking for new Mystery hands...")
    parser.parse_and_import(config.MYSTERY_PATH, "Mystery")
    
    # 3. Run the analytics report
    # This will now analyze all hands (both Freeroll and Mystery)
    print("Generating analytics report...")
    analytics.get_basic_stats()
    

if __name__ == "__main__":
    main()