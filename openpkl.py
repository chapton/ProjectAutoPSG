import pandas as pd
from pprint import pprint

object = pd.read_pickle(r'edfx/sleepdata.pkl')
pprint(locals())