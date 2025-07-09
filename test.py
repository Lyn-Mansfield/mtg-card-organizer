import tkinter as tk
import pandas as pd


x = pd.Series([1,4,9,16], index=['a','b','c','d'])
y = pd.DataFrame(zip(['a','b','c','d'], [1,4,9,16]))
y = y.set_index(0)
z = y.iloc[0]
print(z.name)