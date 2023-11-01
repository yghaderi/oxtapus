import polars as pl
import re


class CED:
    @classmethod
    def ins_info(cls, ins_info_: dict):
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

    @classmethod
    def option_type(cls, s: str):
        return "call" if s.startswith("ض") else "put"

    @classmethod
    def expiration_date(cls, s: str):
        ex_date = re.findall("[0-9]+", s)
        ex_date = "".join(ex_date)
        match len(ex_date):
            case 8:
                return f"{ex_date[:4]}-{ex_date[4:6]}-{ex_date[6:8]}"
            case 6:
                return f"14{ex_date[:2]}-{ex_date[2:4]}-{ex_date[4:6]}"

    @classmethod
    def omw(cls, options: pl.DataFrame, ua: pl.DataFrame):
        option[["ua", "strike_price", "ex_date"]] = option.name_far.str.split(
            "-", expand=True
        )
        options = options.with_columns(
            [
                pl.col("name")
                .str.splitn("-", 3)
                .struct.rename_fields(["ua", "strike_price", "ex_date"])
                .alias("fields"),
            ]
        ).unnest("fields")

        df = df.assign(ex_date=df.ex_date.map(expiration_date))
        df = df.assign(
            t=df.ex_date.map(days_to_ex_date), type=df.symbol_far.map(option_type)
        )
        return df
