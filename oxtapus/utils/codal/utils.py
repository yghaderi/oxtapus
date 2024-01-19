from tarix import Date


def norm_char(w: str):
    dict_ = {
        "ي": "ی",
        "ك": "ک",
        "\u200c": " ",
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "/": "-",
    }
    return w.translate(str.maketrans(dict_))


def normalize_fs_item(w: str):
    dict_ = {
        " ": "",
        "–": "",
        "(": "",
        ")": "",
        "،": "",
        "ي": "ی",
        "ى": "ی",
        "آ": "ا",
        "\u200f": "",
        "\u200c": "",
    }
    return w.translate(str.maketrans(dict_))


def translate(item: str, dict_: dict):
    for k, v in dict_.items():
        if item and normalize_fs_item(k) == normalize_fs_item(item):
            return v
    return item


def jalali_to_gregorian(dtstr: str):
    """1402-05-12 12:20:42"""
    date = Date(dtstr[:10]).jalali_to_gregorian().strftime("%Y-%m-%d")
    time = dtstr[-8:]
    return f"{date} {time}"
