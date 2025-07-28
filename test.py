import tkinter as tk
import pandas as pd
import numpy as np

test_df = pd.DataFrame({'a': [[1,2,3],[3,4,5],[5,6,7]], 'b':[4,5,6]})
test_series = pd.Series([1,2,3], index=['a','b','c'])
myseries = pd.Series([1,4,0,7,5], index=['0','1','2','bruh','4'])
