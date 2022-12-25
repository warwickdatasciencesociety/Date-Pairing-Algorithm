

from matchmaker import MatchMaker
import pandas as pd
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level = logging.INFO)

dfr = pd.read_csv('data/romantic_dates.csv', header=0)


mm = MatchMaker(dfr[:5])
mm.solve()