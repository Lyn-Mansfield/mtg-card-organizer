import tkinter as tk
import pandas as pd


test_pd = pd.DataFrame({1: [1,2], 2:[3,4], 4:[6,7]})
print(test_pd.T)

test_series = pd.Series([1,2,3,4])
x = test_series.to_frame()
print(x.T)