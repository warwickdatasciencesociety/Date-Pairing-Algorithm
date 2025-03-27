
import logging
import pandas as pd
from datetime import datetime

from date_matching.config import DATA_DIR
from date_matching.matching.matchmaker import MatchMaker
from data_transformer import transform_csv_for_matching

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Step 1: Transform the raw responses data
    try:
        logger.info("Starting data transformation...")
        transform_csv_for_matching(
            input_csv=f"date_matching/{DATA_DIR}/questionnaire-responses-2024-11-21.csv",
            output_csv=f"date_matching/{DATA_DIR}/transformed_romantic_dates.csv"
        )
        logger.info("Data transformation complete.")
    except Exception as e:
        logger.error(f"Error during data transformation: {e}")
        raise

    # Step 2: Read the transformed data
    try:
        logger.info("Reading transformed data...")
        data = pd.read_csv(f"date_matching/{DATA_DIR}/transformed_romantic_dates.csv", header=0)
        logger.info(f"Loaded {len(data)} responses.")
    except Exception as e:
        logger.error(f"Error reading transformed data: {e}")
        raise

    # Optional: Limit the number of entries for testing
    LIMIT = None  # Or set a number for testing
    if LIMIT is not None:
        logger.info(f"Limiting to {LIMIT} entries for testing")
        data = data[:LIMIT]

    # Step 3: Generate matches
    try:
        logger.info("Initializing matching algorithm...")
        mm = MatchMaker(data)
        
        logger.info("Solving for optimal matches...")
        mm.solve()
        
        # Step 4: Save the results (optional)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"date_matching/{DATA_DIR}/matches_{timestamp}.txt"
        
        logger.info(f"Saving results to {results_file}")
        with open(results_file, "w") as f:
            f.write("=== MATCHES ===\n\n")
            # Write scheduling info
            f.write("=== BY DAY ===\n")
            day_dict = {}
            for idx1, idx2 in mm.match_tracker.get_true_possible_matches():
                if idx1 == idx2:
                    continue
                person1, person2 = mm.persons[idx1], mm.persons[idx2]
                day = person1.day_choice if person1.day_choice != "Either" else person2.day_choice
                if day not in day_dict:
                    day_dict[day] = []
                day_dict[day].append((person1, person2))
            
            for day, pairs in day_dict.items():
                f.write(f"\n{day}:\n")
                for person1, person2 in pairs:
                    compatibility = person1.compatibility_score(person2)
                    f.write(f"{person1.student_id} - {person2.student_id} (Compatibility: {compatibility:.2%})\n")
            
            # Write gender pairing stats
            f.write("\n=== GENDER PAIRINGS ===\n")
            gender_stats = {}
            for person1, person2 in mm.match_tracker.get_matches():
                if person1 != person2:
                    g1, g2 = person1.gender.value.title(), person2.gender.value.title()
                    g1, g2 = min(g1, g2), max(g1, g2)
                    pair = f"{g1}/{g2}"
                    gender_stats[pair] = gender_stats.get(pair, 0) + 1
            
            for pair, count in gender_stats.items():
                f.write(f"{pair}: {count}\n")

        logger.info("Matching process complete!")
        
    except Exception as e:
        logger.error(f"Error during matching process: {e}")
        raise

if __name__ == "__main__":
    main()
