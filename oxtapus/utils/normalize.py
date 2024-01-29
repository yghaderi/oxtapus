def json_normalize(data: list[dict], record_path: str, prefix: str | None = None):
    normalized = []
    prefix = prefix if prefix else ""
    for dict_ in data:
        d = dict_.copy()
        records = d.pop(record_path)
        for record in records:
            normalized.append({**d, **{f"{prefix}{k}": v for k, v in record.items()}})
    return normalized


def normalize_nested_dict(
    data: list[dict], nested_dict: str, prefix: str | None = None
):
    normalized = []
    prefix = prefix if prefix else ""
    for dict_ in data:
        d = dict_.copy()
        record = d.pop(nested_dict)
        normalized.append({**d, **{f"{prefix}{k}": v for k, v in record.items()}})
    return normalized


def word_normalize(x: str):
    return x.translate(str.maketrans({"ي": "ی", "ك": "ک", "‌": "", " ": ""}))
