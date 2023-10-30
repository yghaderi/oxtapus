
def json_normalize(data: list[dict], record_path: str):
    normalized = []
    for dict_ in data:
        for record in dict_.pop(record_path):
            normalized.append({**dict_, **record})
    return normalized
