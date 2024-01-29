import polars as pl
from typing import List, Dict, Literal
from pydantic import (
    validate_call,
    ValidationError,
)

from oxtapus.utils.codal.models import IncomeStatements
from oxtapus.utils.codal.utils import norm_char, translate
from oxtapus.utils.codal.items import is_production, is_bank

Category = Literal["p", "i", "b"]


class HandleIncomeStatement:
    def __init__(self, category: Category, json_list: List[str]) -> None:
        self._category = category
        self._json_list = json_list

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value: Category):
        self._category = value

    @property
    def json_list(self):
        return self._json_list

    @json_list.setter
    def json_list(self, value: Category):
        self._json_list = value

    def production(self):
        data = []
        validate_json_log = []
        for i in self.json_list:
            try:
                data.append(IncomeStatements.model_validate_json(norm_char(i)))
            except ValidationError as e:
                validate_json_log.append(
                    ("نتونستم این جیسون رو اعتبار سنجی کنم.", i, e)
                )
        select = [
            "sales",
            "cost_of_goods_sold",
            "gross_profit",
            "marketing_general_and_administrative_expenses",
            "special_items",
            "other_operating_income",
            "other_operating_expense",
            "operating_income",
            "interest_expense",
            "other_income",
            "income_from_continuing_operations_before_taxes",
            "income_tax",
            "net_income_from_continuing_operations",
            "income_from_discontinued_operations_net_of_tax",
            "net_income",
            "eps",
            "listed_capital",
        ]
        if not isinstance(data, list):
            data = [data]
        df = pl.DataFrame()

        for i in data:
            if i.sheets[0].tables[0].alias_name == "IncomeStatement":
                cells = i.sheets[0].tables[0].cells
            elif i.sheets[0].tables[1].alias_name == "IncomeStatement":
                cells = i.sheets[0].tables[1].cells
            cells = [(i.column_sequence, i.row_sequence, i.value) for i in cells]
            df_ = pl.from_records(cells, schema=["col", "row", "value"])
            df_ = (
                df_.pivot(values="value", columns="col", index="row")
                .rename({"1": "item", "2": "value"})
                .select(["item", "value"])
            )
            df_ = df_.with_columns(
                pl.struct(["item"]).map_elements(
                    lambda x: translate(x["item"], is_production)
                )
            )
            df_ = df_.filter(pl.col("item").is_in(select))
            df_ = df_.with_columns(
                [
                    pl.col("value").cast(pl.Int64, strict=False).fill_null(0),
                    pl.lit(1).alias("row"),
                ]
            )

            net_income = df_.filter(pl.col("item") == "net_income")["value"]

            df_ = df_.pivot(
                values="value", columns="item", index="row", aggregate_function="sum"
            )
            df_ = df_.with_columns(pl.lit(net_income.max()).alias("net_income"))
            if "special_items" not in df_.columns:
                df_ = df_.with_columns(pl.lit(0).cast(pl.Int64).alias("special_items"))
            df_ = df_.select(select)
            df_ = df_.with_columns(
                [
                    pl.lit(i.is_audited).alias("is_audited"),
                    pl.lit(i.period_end_to_date if i.period_end_to_date else "").alias(
                        "period_end_to_date"
                    ),
                    pl.lit(i.year_end_to_date if i.year_end_to_date else "").alias(
                        "year_end_to_date"
                    ),
                    pl.lit(i.register_date_time if i.register_date_time else "").alias(
                        "register_date_time"
                    ),
                    pl.lit(i.sent_date_time if i.sent_date_time else "").alias(
                        "sent_date_time"
                    ),
                ]
            )
            df = pl.concat([df, df_])
        return df, validate_json_log

    def bank(self):
        data = []
        validate_json_log = []
        for i in self.json_list:
            try:
                data.append(IncomeStatements.model_validate_json(norm_char(i)))
            except ValidationError as e:
                validate_json_log.append(
                    ("نتونستم این جیسون رو اعتبار سنجی کنم.", i, e)
                )
        select = [
            "income_on_credit_facilities",
            "depositors_interest_share",
            "net_facility_and_deposit_income",
            "commission_income",
            "commission_expense",
            "net_commission_income",
            "income_on_investments_and_deposits",
            "foreign_exchange_transaction_gain",
            "other_operating_income_and_expenses",
            "total_operating_income",
            "net_other_income_and_expenses",
            "corporate_and_administrative_expenses",
            "doubtful_debts_expense",
            "finance_expense",
            "depreciation_expense",
            "earning_before_tax",
            "tax",
            "net_income_from_continuing_operation",
            "discontinued_operations_profit",
            "net_income",
            "eps",
            "listed_capital",
        ]
        if not isinstance(data, list):
            data = [data]
        df = pl.DataFrame()

        for i in data:
            if i.sheets[0].tables[0].alias_name == "IncomeStatement":
                cells = i.sheets[0].tables[0].cells
            elif i.sheets[0].tables[1].alias_name == "IncomeStatement":
                cells = i.sheets[0].tables[1].cells
            cells = [(i.column_sequence, i.row_sequence, i.value) for i in cells]
            df_ = pl.from_records(cells, schema=["col", "row", "value"])
            df_ = (
                df_.pivot(values="value", columns="col", index="row")
                .rename({"1": "item", "2": "value"})
                .select(["item", "value"])
            )
            df_ = df_.with_columns(
                pl.struct(["item"]).map_elements(
                    lambda x: translate(x["item"], is_bank)
                )
            )
            df_ = df_.filter(pl.col("item").is_in(select))
            df_ = df_.with_columns(
                [
                    pl.col("value").cast(pl.Int64, strict=False).fill_null(0),
                    pl.lit(1).alias("row"),
                ]
            )

            net_income = df_.filter(pl.col("item") == "net_income")["value"]

            df_ = df_.pivot(
                values="value", columns="item", index="row", aggregate_function="sum"
            )
            df_ = df_.with_columns(pl.lit(net_income.max()).alias("net_income"))
            if "special_items" not in df_.columns:
                df_ = df_.with_columns(pl.lit(0).cast(pl.Int64).alias("special_items"))
            mising_cols = ["net_other_income_and_expenses", "depreciation_expense"]
            for item in mising_cols:
                if not item in df_.columns:
                    df_ = df_.with_columns(pl.lit(0).cast(pl.Int64).alias(item))
            if not "net_facility_and_deposit_income" in df_.columns:
                df_ = df_.with_columns(
                    (
                        pl.col("income_on_credit_facilities")
                        + pl.col("depositors_interest_share")
                    ).alias("net_facility_and_deposit_income")
                )

            if not "net_commission_income" in df_.columns:
                df_ = df_.with_columns(
                    (pl.col("commission_income") + pl.col("commission_expense")).alias(
                        "net_commission_income"
                    )
                )

            if not "total_operating_income" in df_.columns:
                df_ = df_.with_columns(
                    (
                        pl.col("net_facility_and_deposit_income")
                        + pl.col("net_commission_income")
                        + pl.col("income_on_investments_and_deposits")
                        + pl.col("foreign_exchange_transaction_gain")
                        + pl.col("other_operating_income_and_expenses")
                    ).alias("total_operating_income")
                )
            df_ = df_.with_columns(
                (
                    pl.col("total_operating_income")
                    + pl.col("net_other_income_and_expenses")
                    + pl.col("corporate_and_administrative_expenses")
                    + pl.col("doubtful_debts_expense")
                    + pl.col("finance_expense")
                    + pl.col("depreciation_expense")
                ).alias("earning_before_tax")
            )
            df_ = df_.with_columns(
                (pl.col("earning_before_tax") + pl.col("tax")).alias(
                    "net_income_from_continuing_operation"
                )
            )
            df_ = df_.with_columns(
                (
                    pl.col("net_income_from_continuing_operation")
                    + pl.col("discontinued_operations_profit")
                ).alias("net_income")
            )
            df_ = df_.with_columns(
                pl.when(pl.col("eps") == 0)
                .then((pl.col("net_income") / pl.col("listed_capital") * 1000).round(0))
                .otherwise(pl.col("eps"))
                .alias("eps")
            )
            df_ = df_.select(select)
            df_ = df_.with_columns(
                [
                    pl.lit(i.is_audited).alias("is_audited"),
                    pl.lit(i.period_end_to_date if i.period_end_to_date else "").alias(
                        "period_end_to_date"
                    ),
                    pl.lit(i.year_end_to_date if i.year_end_to_date else "").alias(
                        "year_end_to_date"
                    ),
                    pl.lit(i.register_date_time if i.register_date_time else "").alias(
                        "register_date_time"
                    ),
                    pl.lit(i.sent_date_time if i.sent_date_time else "").alias(
                        "sent_date_time"
                    ),
                ]
            )
            df = pl.concat([df, df_])
        return df, validate_json_log

    def insurance(self):
        pass

    def income_statements(self):
        match self._category:
            case "p":
                return self.production()
            case "i":
                return self.insurance()
            case "b":
                return self.bank()
