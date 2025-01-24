import polars as pl
from oxtapus.utils.http import get
from oxtapus.models.fipiran import DependencyGraph
from oxtapus.utils.normalize import normalize_nested_dict


class Fipiran:
    def __init__(self) -> None:
        pass

    def funds(self):
        """
        .. raw:: html

            <div dir="rtl">
                ی سری داده‌یِ از صندوق‌هایِ سرمایه-گذاری رو بهت می‌ده.
            </div>
        """
        url = "https://fund.fipiran.ir/api/v1/fund/dependencygraph"
        r = get(url)
        items = list(filter(lambda x: self._is_gt(x["netAsset"], 0.0), r[0]["items"]))
        validated_r = DependencyGraph.model_validate({"items": items})
        norm_r = normalize_nested_dict([i.model_dump() for i in validated_r.items], "manager")
        return pl.DataFrame(norm_r)

    def _is_gt(self, x, t: float):
        try:
            number = float(x)
            if number > 0:
                return True
            return False
        except Exception as e:
            return False
