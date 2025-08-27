import asyncio
import pandas as pd
import tkinter as tk
from contextlib import asynccontextmanager
import time
import re
import aiohttp

from pathlib import Path
from PIL import Image
from PIL import ImageTk
from io import BytesIO

from CardCatManager import CardCatManager
from UpdateLabel import UpdateLabel



class CardImageManager:
	# Full-size scale is 750 x 1050, this is half that
	IDEAL_VIEWING_SIZE = (375, 525)
	# Index: name  Columns: front_side_path, back_side_path
	img_df = pd.DataFrame()

	@classmethod
	def has_images_loaded(cls, card_name):
		return card_name in cls.img_df.index

	@classmethod
	def get_image(cls, card_name, side):
		if side not in ['front', 'back']:
			raise ValueError("side must be either 'front' or 'back'")
		image_path = cls.img_df.loc[card_name, f'{side}_side_path']
		if image_path is None:
			return image_path
		image = Image.open(image_path)
		return ImageTk.PhotoImage(image)

	async def download_card_image(session, image_link, file_name, delay=0):
		# Delay to stagger them out so they're 0.1 seconds apart (politeness matters!)
		await asyncio.sleep(delay)

		current_directory = Path.cwd()
		file_path = current_directory / "card_image_files" / f"{file_name}.png"

		# If we somehow already have an image by that name, no need to fetch it again
		if file_path.exists():
			print("Already fetched! early return :D")
			return file_path

		print(f'downloading {file_name} info from: {image_link}')

		async def fetch_image_data(session, image_link):
			try:
				async with session.get(image_link) as response:
					return await response.read()
			except:
				UpdateLabel.report("Image couldn't load xc Check internet connection!")

		image_data = await fetch_image_data(session, image_link)
		print(f'finished getting image!')
		image = Image.open(BytesIO(image_data))
		resized_image = image.resize(CardImageManager.IDEAL_VIEWING_SIZE)

		print(f'saving to {file_path}')
		resized_image.save(file_path, 'PNG')

		return file_path

	@classmethod
	async def register_card_faces(cls, session, card_info_series, delay=0):
		card_name = card_info_series.name
		# If card already has image info, then can skip over
		if card_name in cls.img_df.index:
			return
		snake_case_name = re.sub(r'[^a-zA-Z0-9_]', '', card_name.lower().replace(' ', '_'))

		# If both sides are relevant, then fetch both sides
		if card_info_series['flips']:
			print(f"oh yeah, {card_name} flips")
			front_side_info_series = card_info_series['first_card_info']
			front_image_link = front_side_info_series['image_uris.png']
			print(front_image_link)
			front_side_path = await cls.download_card_image(
				session, 
				front_image_link, 
				f"{snake_case_name}_front", 
				delay=delay
			)

			back_side_info_series = card_info_series['second_card_info']
			back_image_link = back_side_info_series['image_uris.png']
			print(back_image_link)
			back_side_path = await cls.download_card_image(
				session, 
				back_image_link, 
				f"{snake_case_name}_back", 
				delay=delay
			)
		# Otherwise, just get the front side, other side is N/A
		else:
			print(f"{card_name} doesn't flip")
			front_image_link = card_info_series['image_uris.png']
			print(front_image_link)
			front_side_path = await cls.download_card_image(
				session, 
				front_image_link, 
				snake_case_name, 
				delay=delay
			)

			back_side_path = None

		new_card_img_row = pd.DataFrame({
				'name': [card_name],
				'front_side_path': [front_side_path],
				'back_side_path': [back_side_path]
			})
		new_card_img_row.set_index('name', inplace=True)

		cls.img_df = pd.concat([cls.img_df, new_card_img_row])

	@classmethod
	async def download_all_cards(cls, courtesy_interval=0.1):
		# Make the destination directory if it doesn't already exist
		current_directory = Path.cwd()
		images_directory = current_directory / "card_image_files"
		images_directory.mkdir(parents=True, exist_ok=True)

		cards_with_images = cls.img_df.index
		no_img_card_rows_df = CardCatManager.cards_df.query("name not in @cards_with_images")
		no_img_card_rows_list = [no_img_card_rows_df.iloc[i] for i in range(len(no_img_card_rows_df))]
		
		async with aiohttp.ClientSession() as session:
			all_register_tasks = [cls.register_card_faces(session, no_img_card_rows_list[i], delay=0.1*i) for i in range(len(no_img_card_rows_list))]
			await asyncio.gather(*all_register_tasks)

	async def async_tk_loop(tk_object, interval=0.05):
		while True:
			tk_object.update()
			await asyncio.sleep(interval)
