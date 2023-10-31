def json_normalize(data: list[dict], record_path: str, prefix: str):
    normalized = []
    for dict_ in data:
        for record in dict_.pop(record_path):
            normalized.append({**dict_, **{f"{prefix}{k}": v for k, v in record.items()}})
    return normalized


def word_normalize(x: str):
    return x.translate(str.maketrans(
        {
            "ي": "ی",
            "ك": "ک",
            "‌": "",
            " ": ""
        }
    ))
