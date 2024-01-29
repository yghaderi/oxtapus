import unittest
from oxtapus.utils.normalize import json_normalize, word_normalize


class TestNormalize(unittest.TestCase):
    def test_json_normalize(self):
        raw_data = [
            {"a": 1, "records": [{"s": 2}, {"s": 3}]},
            {"a": -2, "records": [{"s": 4}, {"s": 0}]},
        ]
        norm_data_without_prefix = [
            {"a": 1, "s": 2},
            {"a": 1, "s": 3},
            {"a": -2, "s": 4},
            {"a": -2, "s": 0},
        ]
        norm_data_wit_prefix = [
            {"a": 1, "sub_s": 2},
            {"a": 1, "sub_s": 3},
            {"a": -2, "sub_s": 4},
            {"a": -2, "sub_s": 0},
        ]
        self.assertEqual(
            json_normalize(raw_data, record_path="records"), norm_data_without_prefix
        )
        self.assertEqual(
            json_normalize(raw_data, record_path="records", prefix="sub_"),
            norm_data_wit_prefix,
        )

    def test_word_normalize(self):
        self.assertEqual(word_normalize("شپديس‌ و ‌ كرماشا"), "شپدیسوکرماشا")


if __name__ == "__main__":
    unittest.main()
