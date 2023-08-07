from collections import namedtuple


Cols = namedtuple(
    "Cols", ["bs",]
)
Property = namedtuple("Property", ["rename", "drop", "rep"])

_bs = {"rename":{"date_time":"issue_date", "jalali_date_time":"j_issue_date"}}

bs = Property(rename=_bs.get("rename"), drop=_bs.get("drop"), rep=_bs.get("rep"))

cols = Cols(bs=bs)
