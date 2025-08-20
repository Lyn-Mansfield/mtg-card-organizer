from CardCatManager import CardCatManager
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def random_seven_cards():
	def number_in_deck(row):
		card_name = row['name']
		card_count = row['count']
		return  [card_name] * card_count

	count_based_series = CardCatManager.cards_df.apply(number_in_deck, axis=1)
	count_based_list = count_based_series.explode().to_list()

	return np.random.choice(count_based_list, size=7)

def generate_stats():
	cards_db = CardCatManager.cards_df.copy()
	
	average_mana = cards_db['cmc'].dropna().mean()

def generate_mana_graph(split=None):
	cards_db = CardCatManager.cards_df.copy()

	castable_cards_db = cards_db[cards_db['cmc'].notna()]
	cmc_by_count_series = castable_cards_db.apply(lambda row: [row['cmc']] * row['count'], axis=1)
	cmc_by_count_list = cmc_by_count_series.explode().to_list()

	bins = np.arange(0, max(cmc_by_count_list) + 1.5) - 0.5

	mana_fig = plt.figure()
	plt.title('Mana Curve', fontsize=14)
	plt.xlabel('Mana Value')
	plt.ylabel('Number of Cards')
	plt.grid(axis='y', alpha=0.2)
	plt.tight_layout()
	ax = mana_fig.gca()
	ax.hist(cmc_by_count_list, bins, edgecolor='black', linewidth=1.5)
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))

	return mana_fig