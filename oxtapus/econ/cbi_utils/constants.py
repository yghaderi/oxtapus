class URL:
    def __init__(
        self,
        base_url="https://tsd.cbi.ir",
        **kwargs,
    ):
        self.base_url = base_url

    def query_report(self, report_url):
        """تولید(درآمد) ناخالص ملی بر حسب فعالیت های اقتصادی(به قیمت های ثابت سال 1395)"""
        # ارزش افزوده گروه کشاورزی، جنگلداری و ماهیگیری
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2017&x=568163760875930"
        # ارزش افزوده گروه نفت و گاز
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2018&x=450489330326395"

        # ارزش افزوده گروه صنایع و معادن
        # ارزش افزوده استخراج معدن #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2020&x=721704267548261"
        # ارزش افزوده صنعت #
        url = " https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2021&x=39697446023232"
        # ارزش افزوده تامین برق، گاز، بخار و تهویه هوا #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2022&x=371118760528580"
        # ارزش افزوده آبرسانی، مدیریت پسماند، فاضلاب و فعالیت های تصفیه #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2105&x=12329086472708"
        # ارزش افزوده ساختمان #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2023&x=301281323166451"

        # ارزش افزوده گروه خدمات
        # ارزش افزوده عمده فروشی، خرده فروشی و تعمیر وسایل نقلیه موتوری #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2025&x=534954229295710"
        # ارزش افزوده حمل و نقل و انبارداری #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2026&x=712552797912846"
        # ارزش افزوده فعالیت های مربوط به تامین جا و غذا #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2027&x=815178158148913"
        # ارزش افزوده اطلاعات و ارتباطات #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2029&x=711224586650532"
        # ارزش افزوده فعالیت های مالی و بیمه#
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2030&x=60194993530146"
        # ارزش افزوده فعالیت های املاک و مستغلات #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2106&x=726843256806441"
        # ارزش افزوده فعالیت های حرفه ای، علمی و فنی #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2107&x=970202880167847"
        # ارزش افزوده فعالیت های اداری و خدمات پشتیبانی #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2108&x=776285463872463"
        # ارزش افزوده اداره عمومی، دفاع و تامین اجتماعی #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2109&x=926117410587222"
        # ارزش افزوده آموزش #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2110&x=697307782575793"
        # ارزش افزوده بهداشت و مددکاری اجتماعی #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2111&x=727280862894250"
        # ارزش افزوده هنر، سرگرمی، تفریح، ورزش و سایر فعالیت های خدماتی #
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2112&x=132116139744837"

        # تولید ناخالص داخلی به قیمت پایه
        url = " https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2032&x=702116970618982"
        # تولید ناخالص داخلی به قیمت پایه بدون نفت
        url = " https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2033&x=780147826659697"
        # خالص درآمد عوامل تولید از خارج
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2034&x=583603438459463"
        # خالص مالیات بر محصول
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2035&x=160251075780820"
        # نتیجه رابطه مبادله بازرگانی
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2117&x=102144423721700"
        # تولید(درآمد) ناخالص ملی به قیمت بازار
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2037&x=618748291649296"
        # استهلاک سرمایه های ثابت
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2038&x=157074714725439"
        # درآمد ملی
        url = "https://tsd.cbi.ir/Display/ShowSelected.aspx?qsTreeCode=2039&x=524032760474755"
        return

    def get_report(self):
        return f"{self.base_url}/Display/ShowExcelReport.aspx?DT=0"
