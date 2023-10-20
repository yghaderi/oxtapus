import jdatetime
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np


class JDate:
    def __init__(self, jdate: str):
        """
        :param jdate: (1401-12-20 or 1401/12/20) تاریخِ جلالی با فرمتِ
        """
        self.jdate = jdate.replace("/", "-")

    def parse_jdate(self):
        """
        فر تبدیلِ رشته‌یِ تاریخِ جلالی به فرمتِ تاریخ
        :return: jdatetime.date
        """
        jdate = self.jdate.split("-")
        jdate = jdatetime.date(*(int(i) for i in jdate))
        return jdate

    def jalali_to_gregorian(self):
        """
        تبدیلِ تاریخِ جلالی به میلادی
        :return: datetime.date
        """
        jdate = self.parse_jdate()
        return datetime.date(
            *jdatetime.JalaliToGregorian(jyear=jdate.year, jmonth=jdate.month, jday=jdate.day).getGregorianList())

    def days_to_input_date(self):
        """
        محاسبه‌یِ تعداد‌ِ روزهایِ امروز تا تاریخِ ورودی
        :return: int
        """
        return (self.jalali_to_gregorian() - datetime.date.today()).days

    def evenly_spaced_periods(self, months: int):
        """
        محاسبه‌یِ تعداد‌ِ دوره‌هایِ xماهه تا امروز
        :param months:
        :return: تعدادِ دوره‌ی کاملِ ماه‌هایِ وارد شده و روزها‌یِ باقیمانده
        """
        if months > 0:
            today = datetime.date.today()
            date = self.jalali_to_gregorian()
            floor_division = 0
            while today <= date + relativedelta(months=-months):
                date += relativedelta(months=-months)
                floor_division += 1
            modulo = (date - today).days / (months * 30) if date > today else 0
            return int(floor_division), modulo
        return np.nan, np.nan