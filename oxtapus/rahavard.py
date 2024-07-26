import requests
import datetime as dt
import polars as pl
from dataclasses import dataclass

from oxtapus.models.rahavard import Stocks, BalanceSheet, IncomeStatements

__all__ = ["Rahavard", "Rep", "BaseInfo"]

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def handel_clos(s: str):
    replace_dict = {" ": "_", "(": "", ")": "", ",": ""}
    return s.lower().translate(str.maketrans(replace_dict))


@dataclass
class BaseInfo:
    announcement_type: str
    financial_view_type: str


@dataclass
class Rep:
    data: pl.DataFrame
    base_info: BaseInfo
    field_info: pl.DataFrame


class Url:
    def __init__(self):
        self.base_url = "https://rahavard365.com/api/v2"

    def stocks(self) -> str:
        return f"{self.base_url}/market-data/stocks?last_trade=last_trading_day"

    def balance_sheet(self, ins_id, quarterly: bool) -> str:
        announcement_type_id = 1
        if quarterly:
            announcement_type_id = 3
        return f"{self.base_url}/asset/{ins_id}/balancesheets?_skip=0&_count=5&announcement_type_id={announcement_type_id}"

    def income_statements(self, ins_id, quarterly: bool) -> str:
        announcement_type_id = 1
        if quarterly:
            announcement_type_id = 3
        return f"{self.base_url}/asset/{ins_id}/profitloss?_skip=0&_count=3&announcement_type_id={announcement_type_id}"

    def cash_flow(self, ins_id) -> str:
        return f"{self.base_url}/asset/{ins_id}/cashflow?_skip=0&_count=5"


class Rahavard:
    def __init__(self):
        self.url = Url()
        self.last_get_stocks = None

    def stocks(self):
        r = requests.get(self.url.stocks(), headers=headers).json()
        d = Stocks.model_validate(r)
        self.stocks_: Stocks = d
        self.last_get_stocks = dt.datetime.now()
        return self

    def handle_get_stock(self):
        if not self.last_get_stocks:
            self.stocks()
        elif self.last_get_stocks < dt.datetime.now() - dt.timedelta(minutes=60):
            self.stocks()

    def balance_sheet(self, symbol: str, quarterly: bool = False):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ ترازنامه رو بهت می‌ده
            </div>

        Parameters
        ---------
        symbol: str
            نماد
        quarterly: bool, default False
            اگه 'فالس' باشه، داده‌هایِ سالانه می‌ده و اگه 'ترو' باشه، فصلی

        Returns
        -------
        Rep

        example
        -------
        >>> from oxtapus import Rahavard
        >>> rah = Rahavard()
        >>> bsh = rah.balance_sheet("آسیا")
        >>> bsh.data
        shape: (5, 48)
        ┌───────────┬───────────┬───────────┬───────────┬───┬───────────┬───────────┬───────────┬──────────┐
        │ date      ┆ fiscal_ye ┆ 1         ┆ 2         ┆ … ┆ 120       ┆ 8         ┆ 10        ┆ 25       │
        │ ---       ┆ ar        ┆ ---       ┆ ---       ┆   ┆ ---       ┆ ---       ┆ ---       ┆ ---      │
        │ date      ┆ ---       ┆ f64       ┆ f64       ┆   ┆ f64       ┆ f64       ┆ f64       ┆ f64      │
        │           ┆ date      ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        ╞═══════════╪═══════════╪═══════════╪═══════════╪═══╪═══════════╪═══════════╪═══════════╪══════════╡
        │ 2023-07-1 ┆ 2023-03-2 ┆ 1.6475e12 ┆ 9.4735e13 ┆ … ┆ 0.0       ┆ 0.0       ┆ 0.0       ┆ 0.0      │
        │ 7         ┆ 0         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        │ 2022-07-1 ┆ 2022-03-2 ┆ 9.7369e11 ┆ 6.8886e13 ┆ … ┆ 1.3831e13 ┆ 0.0       ┆ 0.0       ┆ 0.0      │
        │ 3         ┆ 0         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        │ 2021-07-0 ┆ 2021-03-1 ┆ 1.4242e12 ┆ 5.8496e13 ┆ … ┆ 0.0       ┆ 0.0       ┆ 0.0       ┆ 0.0      │
        │ 5         ┆ 9         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        │ 2020-07-1 ┆ 2020-03-1 ┆ 7.1692e11 ┆ 0.0       ┆ … ┆ 0.0       ┆ 9.7560e11 ┆ 3.2546e13 ┆ 0.0      │
        │ 8         ┆ 9         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        │ 2019-07-1 ┆ 2019-03-2 ┆ 6.4080e11 ┆ 1.0119e13 ┆ … ┆ 0.0       ┆ 0.0       ┆ 9.8519e12 ┆ 1.5801e1 │
        │ 6         ┆ 0         ┆           ┆           ┆   ┆           ┆           ┆           ┆ 2        │
        └───────────┴───────────┴───────────┴───────────┴───┴───────────┴───────────┴───────────┴──────────┘

        >>> bsh.base_info
        BaseInfo(announcement_type='1', financial_view_type='3')

        >>> bsh.field_info
        shape: (46, 10)
        ┌─────┬─────────────┬─────────────┬────────────┬───┬────────────┬──────────┬──────────┬────────────┐
        │ id  ┆ title       ┆ english_tit ┆ account    ┆ … ┆ index_view ┆ sign_neg ┆ sign_pos ┆ neg_nature │
        │ --- ┆ ---         ┆ le          ┆ ---        ┆   ┆ ---        ┆ ---      ┆ ---      ┆ ---        │
        │ str ┆ str         ┆ ---         ┆ str        ┆   ┆ i64        ┆ bool     ┆ bool     ┆ bool       │
        │     ┆             ┆ str         ┆            ┆   ┆            ┆          ┆          ┆            │
        ╞═════╪═════════════╪═════════════╪════════════╪═══╪════════════╪══════════╪══════════╪════════════╡
        │ 120 ┆ تسهیلات     ┆ Loan        ┆ CurrentLia ┆ … ┆ 4000       ┆ false    ┆ false    ┆ false      │
        │     ┆ مالی        ┆ Payables    ┆ bilities:L ┆   ┆            ┆          ┆          ┆            │
        │     ┆ دریافتی     ┆             ┆ oanPayable ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆             ┆ s          ┆   ┆            ┆          ┆          ┆            │
        │ 89  ┆ سایر ذخائر  ┆ Other       ┆ CurrentLia ┆ … ┆ 3800       ┆ false    ┆ false    ┆ false      │
        │     ┆ فنی         ┆ Technical   ┆ bilities:O ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆ Reserves    ┆ therTechni ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆             ┆ ca…        ┆   ┆            ┆          ┆          ┆            │
        │ 17  ┆ سایر        ┆ Other       ┆ NonCurrent ┆ … ┆ 2200       ┆ false    ┆ false    ┆ false      │
        │     ┆ دارایی‌ها    ┆ Assets      ┆ Assets:Oth ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆             ┆ erAssets   ┆   ┆            ┆          ┆          ┆            │
        │ 18  ┆ اموال ماشین ┆ Equipment   ┆ NonCurrent ┆ … ┆ 2300       ┆ false    ┆ false    ┆ false      │
        │     ┆ آلات و      ┆             ┆ Assets:Fix ┆   ┆            ┆          ┆          ┆            │
        │     ┆ تجهیزات     ┆             ┆ edAssets:E ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆             ┆ qu…        ┆   ┆            ┆          ┆          ┆            │
        │ 78  ┆ مطالبات از  ┆ Receivables ┆ CurrentAss ┆ … ┆ 300        ┆ false    ┆ false    ┆ false      │
        │     ┆ بیمه‌گذاران  ┆ from        ┆ ets:Receiv ┆   ┆            ┆          ┆          ┆            │
        │     ┆ و نمایندگ…  ┆ Insured and ┆ ablesfromI ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆ Rep…        ┆ ns…        ┆   ┆            ┆          ┆          ┆            │
        │ …   ┆ …           ┆ …           ┆ …          ┆ … ┆ …          ┆ …        ┆ …        ┆ …          │
        │ 35  ┆ سرمایه      ┆ Common      ┆ Equity:Com ┆ … ┆ 4900       ┆ false    ┆ false    ┆ false      │
        │     ┆             ┆ Stock       ┆ monStock   ┆   ┆            ┆          ┆          ┆            │
        │ 46  ┆ جمع کل      ┆ Total       ┆ Liabilitie ┆ … ┆ 6500       ┆ false    ┆ false    ┆ false      │
        │     ┆ بدهی‌ها و    ┆ Liabilities ┆ sAndEquity ┆   ┆            ┆          ┆          ┆            │
        │     ┆ حقوق صاحبان ┆ and Equity  ┆            ┆   ┆            ┆          ┆          ┆            │
        │     ┆ سها…        ┆             ┆            ┆   ┆            ┆          ┆          ┆            │
        │ 33  ┆ ذخیره       ┆ Pension     ┆ NonCurrent ┆ … ┆ 4500       ┆ false    ┆ false    ┆ false      │
        │     ┆ مزایای      ┆ Reserves    ┆ Liabilitie ┆   ┆            ┆          ┆          ┆            │
        │     ┆ پایان خدمت  ┆             ┆ s:PensionR ┆   ┆            ┆          ┆          ┆            │
        │     ┆ کارکنان     ┆             ┆ es…        ┆   ┆            ┆          ┆          ┆            │
        │ 84  ┆ بدهی به     ┆ Reinsurance ┆ CurrentLia ┆ … ┆ 2700       ┆ false    ┆ false    ┆ false      │
        │     ┆ بیمه‌گذاران  ┆ Issuers     ┆ bilities:R ┆   ┆            ┆          ┆          ┆            │
        │     ┆ اتکایی      ┆ Payables    ┆ einsurance ┆   ┆            ┆          ┆          ┆            │
        │     ┆             ┆             ┆ Is…        ┆   ┆            ┆          ┆          ┆            │
        │ 9   ┆ جمع         ┆ Total       ┆ CurrentAss ┆ … ┆ 1400       ┆ false    ┆ false    ┆ false      │
        │     ┆ دارایی‌های   ┆ Current     ┆ ets        ┆   ┆            ┆          ┆          ┆            │
        │     ┆ جاری        ┆ Asset       ┆            ┆   ┆            ┆          ┆          ┆            │
        └─────┴─────────────┴─────────────┴────────────┴───┴────────────┴──────────┴──────────┴────────────┘
        """
        self.handle_get_stock()
        ins_id = [i for i in self.stocks_.data if i.name == symbol][0]
        r = requests.get(
            self.url.balance_sheet(ins_id.asset_id, quarterly), headers=headers
        ).json()
        d = BalanceSheet.model_validate(r)
        df = pl.DataFrame()
        field_info = pl.DataFrame()
        for bs in d.data:
            base = pl.from_dicts(
                [
                    {
                        **i.field.model_dump(),
                        "value": i.value,
                        "date": bs.date,
                        "fiscal_year": bs.fiscal_year,
                    }
                    for i in bs.items
                ]
            )
            bsi = base.select(["date", "fiscal_year", "id", "value"])
            df = pl.concat([df, bsi])

            f_info = base.select(
                [
                    "id",
                    "title",
                    "english_title",
                    "account",
                    "is_parent",
                    "parent",
                    "index_view",
                    "sign_neg",
                    "sign_pos",
                    "neg_nature",
                ]
            )
            field_info = pl.concat([field_info, f_info])
        df = df.pivot(
            on="id",
            values="value",
            index=["date", "fiscal_year"],
        ).fill_null(0)
        base_info = BaseInfo(
            announcement_type=d.data[0].announcement_type,
            financial_view_type=d.data[0].financial_view_type.id,
        )
        field_info = field_info.unique(subset="id")
        return Rep(data=df, base_info=base_info, field_info=field_info)

    def income_statements(self, symbol: str, quarterly: bool = False):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ سود/زیان رو بهت می‌ده
            </div>

        Parameters
        ---------
        symbol: str
            نماد
        quarterly: bool, default False
            اگه 'فالس' باشه، داده‌هایِ سالانه می‌ده و اگه 'ترو' باشه، فصلی

        Returns
        -------
        Rep

        example
        -------
        >>> from oxtapus import Rahavard
        >>> rah = Rahavard()
        >>> ist = rah.income_statements("آسیا")
        >>> ist.data
        shape: (3, 34)
        ┌───────────┬───────────┬───────────┬───────────┬───┬───────────┬───────────┬───────────┬──────────┐
        │ date      ┆ fiscal_ye ┆ 49        ┆ 51        ┆ … ┆ 33        ┆ 34        ┆ capital   ┆ pure_eps │
        │ ---       ┆ ar        ┆ ---       ┆ ---       ┆   ┆ ---       ┆ ---       ┆ ---       ┆ ---      │
        │ date      ┆ ---       ┆ f64       ┆ f64       ┆   ┆ f64       ┆ f64       ┆ f64       ┆ f64      │
        │           ┆ date      ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        ╞═══════════╪═══════════╪═══════════╪═══════════╪═══╪═══════════╪═══════════╪═══════════╪══════════╡
        │ 2023-07-1 ┆ 2023-03-2 ┆ 1.4780e14 ┆ 1.4780e14 ┆ … ┆ 5.8900e11 ┆ 4.8937e12 ┆ 3.1000e13 ┆ 1.8703e8 │
        │ 7         ┆ 0         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        │ 2022-07-1 ┆ 2022-03-2 ┆ 9.6046e13 ┆ 9.6046e13 ┆ … ┆ 2.8958e12 ┆ 7.3677e12 ┆ 2.4132e13 ┆ 2.5000e8 │
        │ 3         ┆ 0         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        │ 2021-07-0 ┆ 2021-03-1 ┆ 6.8418e13 ┆ 6.8418e13 ┆ … ┆ 2.4132e12 ┆ 5.1905e12 ┆ 2.4132e13 ┆ 3.1084e8 │
        │ 5         ┆ 9         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
        └───────────┴───────────┴───────────┴───────────┴───┴───────────┴───────────┴───────────┴──────────┘

        >>> ist.base_info
        BaseInfo(announcement_type='1', financial_view_type='3')

        >>> ist.field_info
        shape: (32, 10)
        ┌──────────┬────────────┬────────────┬───────────┬───┬───────────┬──────────┬──────────┬───────────┐
        │ id       ┆ title      ┆ english_ti ┆ account   ┆ … ┆ index_vie ┆ sign_neg ┆ sign_pos ┆ neg_natur │
        │ ---      ┆ ---        ┆ tle        ┆ ---       ┆   ┆ w         ┆ ---      ┆ ---      ┆ e         │
        │ str      ┆ str        ┆ ---        ┆ str       ┆   ┆ ---       ┆ bool     ┆ bool     ┆ ---       │
        │          ┆            ┆ str        ┆           ┆   ┆ i64       ┆          ┆          ┆ bool      │
        ╞══════════╪════════════╪════════════╪═══════════╪═══╪═══════════╪══════════╪══════════╪═══════════╡
        │ 68       ┆ سایر       ┆ Other      ┆ GrossOthe ┆ … ┆ 2400      ┆ true     ┆ false    ┆ false     │
        │          ┆ هزینه‌های   ┆ Premium    ┆ rInsuranc ┆   ┆           ┆          ┆          ┆           │
        │          ┆ بیمه‌ای     ┆ Expenses   ┆ e:OtherPr ┆   ┆           ┆          ┆          ┆           │
        │          ┆            ┆            ┆ emium…    ┆   ┆           ┆          ┆          ┆           │
        │ 78       ┆ خالص درآمد ┆ Net        ┆ Operating ┆ … ┆ 3300      ┆ true     ┆ false    ┆ false     │
        │          ┆ سرمایه‌گذار ┆ Investment ┆ :NetInves ┆   ┆           ┆          ┆          ┆           │
        │          ┆ یها از     ┆ Revenue    ┆ tmentReve ┆   ┆           ┆          ┆          ┆           │
        │          ┆ محل…       ┆ from Othe… ┆ nuefr…    ┆   ┆           ┆          ┆          ┆           │
        │ 54       ┆ هزینه حق   ┆ Reinsuranc ┆ Insurance ┆ … ┆ 600       ┆ true     ┆ false    ┆ false     │
        │          ┆ بیمه       ┆ e          ┆ Revenue:C ┆   ┆           ┆          ┆          ┆           │
        │          ┆ اتکائی     ┆ Recoveries ┆ ostPremiu ┆   ┆           ┆          ┆          ┆           │
        │          ┆ واگذاری    ┆            ┆ m         ┆   ┆           ┆          ┆          ┆           │
        │ 72       ┆ درآمد سرما ┆ Other      ┆ Operating ┆ … ┆ 3100      ┆ true     ┆ false    ┆ false     │
        │          ┆ یه‌گذاری از ┆ Investment ┆ :OtherInv ┆   ┆           ┆          ┆          ┆           │
        │          ┆ محل سایر   ┆ Revenue    ┆ estmentRe ┆   ┆           ┆          ┆          ┆           │
        │          ┆ م…         ┆            ┆ venue     ┆   ┆           ┆          ┆          ┆           │
        │ 55       ┆ درآمد حق   ┆ Insurance  ┆ Insurance ┆ … ┆ 700       ┆ true     ┆ false    ┆ false     │
        │          ┆ بیمه سهم   ┆ Revenue    ┆ Revenue   ┆   ┆           ┆          ┆          ┆           │
        │          ┆ نگهداری    ┆ (Holding   ┆           ┆   ┆           ┆          ┆          ┆           │
        │          ┆            ┆ Split…     ┆           ┆   ┆           ┆          ┆          ┆           │
        │ …        ┆ …          ┆ …          ┆ …         ┆ … ┆ …         ┆ …        ┆ …        ┆ …         │
        │ 61       ┆ خسارت سهم  ┆ Damage     ┆ ClaimExpe ┆ … ┆ 1300      ┆ true     ┆ false    ┆ false     │
        │          ┆ بیمه‌گران   ┆ Share Of   ┆ nse:Reven ┆   ┆           ┆          ┆          ┆           │
        │          ┆ اتکائی     ┆ reinsuranc ┆ ueClaim   ┆   ┆           ┆          ┆          ┆           │
        │          ┆            ┆ e insu…    ┆           ┆   ┆           ┆          ┆          ┆           │
        │ pure_eps ┆ EPS خالص   ┆ Pure EPS   ┆ -         ┆ … ┆ 100000000 ┆ true     ┆ true     ┆ false     │
        │          ┆            ┆            ┆           ┆   ┆ 02        ┆          ┆          ┆           │
        │ 19       ┆ سود قبل از ┆ Earnings   ┆ Impure    ┆ … ┆ 4100      ┆ true     ┆ true     ┆ false     │
        │          ┆ کسر مالیات ┆ Before Tax ┆           ┆   ┆           ┆          ┆          ┆           │
        │          ┆            ┆ (EBT)      ┆           ┆   ┆           ┆          ┆          ┆           │
        │ 66       ┆ کاهش       ┆ Technical  ┆ GrossOthe ┆ … ┆ 1800      ┆ true     ┆ false    ┆ false     │
        │          ┆ (افزایش)   ┆ Reserves,  ┆ rInsuranc ┆   ┆           ┆          ┆          ┆           │
        │          ┆ سایر ذخایر ┆ Net        ┆ e:Technic ┆   ┆           ┆          ┆          ┆           │
        │          ┆ فنی        ┆ Changes    ┆ alRes…    ┆   ┆           ┆          ┆          ┆           │
        │ 29       ┆ اندوخته    ┆ Legal      ┆ EarningAp ┆ … ┆ 5500      ┆ true     ┆ false    ┆ false     │
        │          ┆ قانونی     ┆ Reserves   ┆ propriate ┆   ┆           ┆          ┆          ┆           │
        │          ┆            ┆            ┆ dPlan:Leg ┆   ┆           ┆          ┆          ┆           │
        │          ┆            ┆            ┆ alRes…    ┆   ┆           ┆          ┆          ┆           │
        └──────────┴────────────┴────────────┴───────────┴───┴───────────┴──────────┴──────────┴───────────┘
        """
        self.handle_get_stock()
        ins_id = [i for i in self.stocks_.data if i.name == symbol][0]
        r = requests.get(
            self.url.income_statements(ins_id.asset_id, quarterly), headers=headers
        ).json()
        d = IncomeStatements.model_validate(r)
        df = pl.DataFrame()
        field_info = pl.DataFrame()
        for bs in d.data:
            base = pl.from_dicts(
                [
                    {
                        **i.field.model_dump(),
                        "value": i.value,
                        "date": bs.date,
                        "fiscal_year": bs.fiscal_year,
                    }
                    for i in bs.items
                ]
            )
            bsi = base.select(["date", "fiscal_year", "id", "value"])
            df = pl.concat([df, bsi])

            f_info = base.select(
                [
                    "id",
                    "title",
                    "english_title",
                    "account",
                    "is_parent",
                    "parent",
                    "index_view",
                    "sign_neg",
                    "sign_pos",
                    "neg_nature",
                ]
            )
            field_info = pl.concat([field_info, f_info])
        df = df.pivot(
            on="id", values="value", index=["date", "fiscal_year"]
        ).fill_null(0)
        df.columns = list(map(lambda x: handel_clos(x), df.columns))
        base_info = BaseInfo(
            announcement_type=d.data[0].announcement_type_id,
            financial_view_type=d.data[0].financial_view_type_id,
        )
        field_info = field_info.unique(subset="id")
        return Rep(data=df, base_info=base_info, field_info=field_info)
