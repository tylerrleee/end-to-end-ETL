"""
EXPONENTIAL MOVING AVERAGE (EMA)
Context: time series analysis to smooth out data, capture underlying trends. 
- Place weights on relevant data points
- Reduce lags in data, compared to SIMPLE Moving AVG
- Respond to recent changes in Data

Flaw: 
- Inconsistency in the right time frame 
- Shorter times tend to be more volatile, so it's ambigious 

Formula:
- EMA_t = alpha * x_i + (1-alpha) * EMA_(t-1)
- d_i = |x_i - EMA_t|

"""

import numpy as np
import pandas as np


