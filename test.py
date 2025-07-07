import tkinter as tk
import re

test_str = 'bruh x10'
res = re.search(r'x(\d+)$', test_str)
if res:
	print(int(res.group(1)))
else:
	print(0)