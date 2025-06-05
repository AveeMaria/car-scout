import json

def enumerate_items(data):
    try:
        with open("log.json", "r", encoding="utf-8") as f:
            log_items = json.load(f)
    except FileNotFoundError:
        log_items = []
    last_id = log_items[-1]["id"] if log_items else 0

    for item in data:
        last_id += 1
        item["id"] = last_id

    return data
