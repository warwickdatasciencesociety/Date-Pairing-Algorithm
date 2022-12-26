
import logging
import pandas as pd
from date_matching.matching.matchmaker import MatchMaker
from date_matching.config import DATA_DIR

logging.basicConfig(format='%(levelname)s: %(message)s', level = logging.INFO)

dfr = pd.read_csv(f"date_matching/{DATA_DIR}/romantic_dates.csv", header=0)

mm = MatchMaker(dfr[:200])
mm.solve()