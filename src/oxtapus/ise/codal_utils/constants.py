from urllib.parse import urlencode


class QueryParameters:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._symbol = "فملی"
        self._audited = "true"
        self._category = 1
        self._childes = "false"
        self._length = -1
        self._mains = "true"
        self._page_number = 1

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol

    @property
    def audited(self):
        return self._audited

    @audited.setter
    def audited(self, audited: bool):
        if audited:
            self._audited = "true"
        elif not audited:
            self._audited = "false"

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category: int):
        match category:
            case 1:
                self._category = category
            case 2:
                self._category = category
            case 3:
                self._category = category
            case _:
                self._category = -1

    @property
    def childes(self):
        return self._childes

    @childes.setter
    def childes(self, childes: bool):
        if childes:
            self._childes = "true"
        elif not childes:
            self._childes = "false"

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length: int):
        if self._category == 1:
            match length:
                case 3:
                    self._length = length
                case 6:
                    self._length = length
                case 12:
                    self._length = length
                case _:
                    self._length = -1
        elif length in range(1, 13):
            self._length = length
        else:
            self._length = -1

    @property
    def mains(self):
        return self._mains

    @mains.setter
    def mains(self, mains: bool):
        if mains:
            self._mains = "true"
        elif not mains:
            self._mains = "false"

    @property
    def page_number(self):
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        self._page_number = page_number

    @property
    def parameters(self):
        return {
            "Audited": self._audited,  # حسابرسی شده
            "AuditorRef": -1,  #
            "Category": self._category,  #
            "Childs": self._childes,  # زیرمجموعه
            "CompanyState": 0,  #
            "CompanyType": 1,  #
            "Consolidatable": "true",  # تلفیقی
            "FromDate": "1395/01/01",
            "IsNotAudited": "false",  # حسابرسی نشده
            "Isic": 271018,  #
            "Length": self._length,  # طولِ دوره
            "LetterType": 6,  # نوعِ اطلاعیه
            "Mains": self._mains,  # اصلی
            "NotAudited": "false",  #
            "NotConsolidatable": "true",  #
            "PageNumber": self._page_number,  #
            "Publisher": "false",  #
            "Symbol": self._symbol,  # نماد
            # "ToDate": "1402/05/03",
            "TracingNo": -1,  #
            "search": "true",
        }

    @property
    def query_parameters(self):
        return urlencode(self.parameters)


class URL(QueryParameters):
    def __init__(
        self,
        base_url="https://codal.ir",
        api="https://search.codal.ir/api/search/v2/q?",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.api = api

    @property
    def search_url(self):
        return self.api + self.query_parameters

    def financial_statements(self, letter_url, sheet_id):
        return self.base_url + f"{letter_url}&sheetId={sheet_id}"
