import pickle
import json
from pathlib import Path
from CardCatManager import CardCatManager
from CardImageManager import CardImageManager

SAVE_DIR = Path("save_info")
USER_SETTINGS_FILE_PATH = SAVE_DIR / "usersettings.json"
CARD_INFO_FILE_PATH = SAVE_DIR / "card_db.pkl"
CAT_INFO_FILE_PATH = SAVE_DIR / "cat_db.pkl"
IMAGE_INFO_FILE_PATH = SAVE_DIR / "img_db.pkl"

SAVE_DIR.mkdir(parents=True, exist_ok=True)
#----------------------------------------------------------------------------------------------------#
def save_all():
	save_user_settings() 
	save_db_info()
	save_image_info()
#----------------------------------------------------------------------------------------------------#
def load_all():
	load_user_settings() 
	load_db_info()
	load_image_info()
#----------------------------------------------------------------------------------------------------#
def save_user_settings():
	user_settings_dict = {
		'decklist_file_path': CardCatManager.decklist_file_path,
		'primary_only': CardCatManager.primary_only,
		'cat_order': CardCatManager.cat_order,
		'block_order': CardCatManager.block_order
	}
	USER_SETTINGS_FILE_PATH.write_text(json.dumps(user_settings_dict, indent=2))
#----------------------------------------------------------------------------------------------------#
def load_user_settings():
	if not USER_SETTINGS_FILE_PATH.exists():
		return

	user_settings_json_str = USER_SETTINGS_FILE_PATH.read_text(encoding='utf-8')
	user_settings_json = json.loads(user_settings_json_str)
	
	CardCatManager.decklist_file_path = user_settings_json['decklist_file_path']
	CardCatManager.primary_only = user_settings_json['primary_only']
	CardCatManager.cat_order = user_settings_json['cat_order']
	CardCatManager.block_order = user_settings_json['block_order']
#----------------------------------------------------------------------------------------------------#
def save_db_info():
	with open(CARD_INFO_FILE_PATH, 'wb') as card_info_file:
		pickle.dump(CardCatManager.cards_df, card_info_file)
	with open(CAT_INFO_FILE_PATH, 'wb') as cat_info_file:
		pickle.dump(CardCatManager.categories_df, cat_info_file)
#----------------------------------------------------------------------------------------------------#
def cat_info_saved():
	return CAT_INFO_FILE_PATH.exists()
#----------------------------------------------------------------------------------------------------#
def load_db_info():
	if not CARD_INFO_FILE_PATH.exists() or not CAT_INFO_FILE_PATH.exists():
		return

	with open(CARD_INFO_FILE_PATH, 'rb') as card_info_file:
		saved_cards_df = pickle.load(card_info_file)
		CardCatManager.cards_df = saved_cards_df
	with open(CAT_INFO_FILE_PATH, 'rb') as cat_info_file:
		saved_cats_df = pickle.load(cat_info_file)
		CardCatManager.categories_df = saved_cats_df
#----------------------------------------------------------------------------------------------------#
def save_image_info():
	with open(IMAGE_INFO_FILE_PATH, 'wb') as img_info_file:
		pickle.dump(CardImageManager.img_df, img_info_file)
#----------------------------------------------------------------------------------------------------#
def load_image_info():
	if not IMAGE_INFO_FILE_PATH.exists():
		return

	with open(IMAGE_INFO_FILE_PATH, 'rb') as img_info_file:
		saved_img_df = pickle.load(img_info_file)
		CardImageManager.img_df = saved_img_df