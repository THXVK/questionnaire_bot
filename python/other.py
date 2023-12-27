import json

filename = '../data.json'


def load() -> dict:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return {}


def save(data: dict):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
