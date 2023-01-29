import logging

import pandas as pd

from date_matching.config import DATA_DIR
from date_matching.matching.matchmaker import MatchMaker

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Specify the csv file that has information about the participants
data = pd.read_csv(f"date_matching/{DATA_DIR}/romantic_dates.csv", header=0)

LIMIT = None  # Or None

if LIMIT is not None:
    data = data[:LIMIT]

mm = MatchMaker(data)
mm.solve()
