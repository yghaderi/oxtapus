from typing import Callable
from dataclasses import dataclass


@dataclass
class Ced:
    ins_info: Callable[[dict], dict]


def ins_info(ins_info_: dict):
    return {
        "ins_code": ins_info_["insCode"],
        "ins_id": ins_info_["instrumentID"],
        "symbol": ins_info_["cIsin"][4:8],
        "name": ins_info_["lVal18"],
        "symbol_far": ins_info_["lVal18AFC"],
        "name_far": ins_info_["lVal30"],
        "capital": ins_info_["zTitad"],
        "sector_name": ins_info_["sector"]["lSecVal"],
        "sector_code": ins_info_["sector"]["cSecVal"].replace(" ", ""),
        "group_type": ins_info_["cgrValCot"],
        "market_name": ins_info_["flowTitle"],
        "market_code": ins_info_["flow"],
        "market_type": ins_info_["cgrValCotTitle"],
        "base_vol": ins_info_["baseVol"],
        "eps": ins_info_["eps"]["estimatedEPS"],
        "float_shares_pct": ins_info_["kAjCapValCpsIdx"],
        "contract_size": ins_info_["contractSize"],
    }


ced = Ced(
    ins_info=ins_info
)
