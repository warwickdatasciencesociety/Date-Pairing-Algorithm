PROBLEM_NAME = "date_matching"
DATA_DIR = "data"
LOG_LP_FILE_PATH = f"date_matching/{DATA_DIR}/{PROBLEM_NAME}.lp"


# IMPORTANT, this is the penalty multiplier for when a soft constraint is violated
# See _initialse_problem._initialse_problem() for usage
# If 0, no penalty for violating the soft constraint, so constraint isn't enforced
# The closer it is to 1, the more of a hard constraint it becomes
# Realistically, keep it small, and below 0.9
PENALTY_MULTIPLIER = 0.1