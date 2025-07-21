import tkinter as tk
import pandas as pd

test_df = pd.DataFrame({'a': [[1,2,3],[3,4,5],[5,6,7]], 'b':[4,5,6]})
myseries = pd.Series([1,4,0,7,5], index=['0','1','2','bruh','4'])
print(pd.Index(myseries).get_loc(7))