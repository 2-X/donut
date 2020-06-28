import json

def load_json_file(file_name):
    """ Return a dict representing the JSON in the given filepath """
    with open(file_name) as json_file:
        return json.load(json_file)


def save_json_file(dictionary, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)
