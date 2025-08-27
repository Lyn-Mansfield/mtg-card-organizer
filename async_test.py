import asyncio
from contextlib import asynccontextmanager
import time
import requests
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

@asynccontextmanager
async def background_task(repeating_func):
	task = asyncio.create_task(repeating_func)
	try:
		yield
	finally:
		task.cancel()
		try:
			await task
		except asyncio.CancelledError:
			pass

async def time_keeper(start_time=0):
	#print("============================================")
	print(f"! current time taken: {start_time} seconds !")
	# print("============================================")
	
	interval = 5
	await asyncio.sleep(interval)
	new_time = start_time + interval
	await time_keeper(start_time=new_time)

async def get_first_letter(word, courtesy_interval=0.1):
	print(f'fetching info for {word}')
	time.sleep(courtesy_interval)
	# mimic fetching info
	await asyncio.sleep(np.random.exponential(3))
	first_letter = word[0]
	print(f'found it! first letter of {word} is {first_letter} c:')
	global first_letter_dict
	first_letter_dict[word] = first_letter.upper()

async def async_tk_loop(tk_object, interval):
	while True:
		tk_object.update()
		await asyncio.sleep(interval)

first_letter_dict = {}
async def get_all_first_letters(word_list):
	all_first_letter_tasks = [get_first_letter(word) for word in word_list]
	await asyncio.gather(*all_first_letter_tasks)

async def main():
	root = tk.Tk()

	word_listbox = tk.Listbox(root)
	word_listbox.pack()
	
	word_list = ['hello', 'gay', 'bye', 'super', 'fragrant', 'euphony', 'banal', 'candy', 'short', 'far']
	for word in word_list:
		word_listbox.insert(tk.END, word)

	input_box = tk.Entry(root)
	input_box.pack()

	async def add_new_word():
		new_word = input_box.get().strip()
		input_box.delete(0, tk.END)

		if len(new_word) == 0:
			return

		word_list.append(new_word)
		word_listbox.insert(tk.END, new_word)
		await get_first_letter(new_word)	

	input_box.bind('<Return>', lambda event: asyncio.ensure_future(add_new_word()))

	letter_display = tk.Label()
	letter_display.pack()

	# Sets the focus on the current listbox
	def _on_click(event):
		word_listbox.update_idletasks()
		word_listbox.focus_set()

	# Displays the selected card, if there is one selected
	def _on_select(event):
		word_listbox.update_idletasks()
		selected_word = word_list[word_listbox.curselection()[0]]
		show_first_letter(selected_word)

	def show_first_letter(word):
		global first_letter_dict
		if word not in first_letter_dict.keys():
			letter_display.config(text='info not loaded in yet :c')
		else:
			letter_display.config(text=first_letter_dict[word])

	word_listbox.bind('<Button-1>', lambda event: _on_click(event))
	word_listbox.bind('<<ListboxSelect>>', lambda event: _on_select(event))


	fig, ax = plt.subplots(figsize=(1,1))
	ax.axis("off")

	canvas = FigureCanvasTkAgg(fig, master=root)
	canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	async def add_trace(interval=1):
		seed1, seed2 = np.random.uniform(), np.random.uniform()
		
		x = np.arange(0, 10, 0.1)
		rand_x_displacement, rand_y_displacement = np.random.uniform(-5, 5), np.random.uniform(-5, 5)
		rand_amplitude, rand_frequency = np.random.uniform(-1, 1), np.random.uniform(0.5, 4)
		y = rand_amplitude * np.cos(rand_frequency * x + rand_x_displacement)  + rand_y_displacement
		ax.plot(x, y)

		ax.relim()  # Recalculate limits based on new data
		ax.autoscale_view() # Adjust view to fit new data
		# fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
		canvas.draw()

		await asyncio.sleep(interval)

	async def add_traces(interval=1):
		while True:
			await add_trace(interval=interval)



	root.update_idletasks()

	all_tasks = [async_tk_loop(root, 0.01), add_traces(), get_all_first_letters(word_list)]
	
	async with background_task(time_keeper()):
		await asyncio.gather(*all_tasks)

#start = time.perf_counter()
#asyncio.run(main())
#elapsed = time.perf_counter() - start
#print(f"{os.path.basename(__file__)} executed in {elapsed:0.2f} seconds, instead of taking {total_time:0.2f} seconds.")
