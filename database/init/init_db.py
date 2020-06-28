import os

from utils.json_utils import load_json_file
from tinydb import TinyDB, Query

drinks_db_path = "./database/drinks_db.json"
cuisines_db_path = "./database/cuisines_db.json"
restaurants_db_path = "./database/restaurants_db.json"

# insert all drinks
if os.path.exists(drinks_db_path):
    os.remove(drinks_db_path)
    open(drinks_db_path, "a").close()

drinks_db = TinyDB('./database/drinks_db.json')
drinks = load_json_file("./database/init/drinks.json")
for index, drink in enumerate(drinks):
    drink["index"] = index + 1
    drinks_db.insert(drink)

# insert all cuisines
if os.path.exists(cuisines_db_path):
    os.remove(cuisines_db_path)
    open(cuisines_db_path, "a").close()

cuisines_db = TinyDB('./database/cuisines_db.json')
cuisines = load_json_file("./database/init/cuisines.json")
for cuisine in cuisines:
    cuisines_db.insert(cuisine)

# empty file for restaurants
if os.path.exists(restaurants_db_path):
    os.remove(restaurants_db_path)
open(restaurants_db_path, "a").close()
