# metafid
این پکیج برای پوشش بخشی از داده‌های موردِ نیاز در تصمیم‌هایِ مالی-اقتصادی توسعه داده شده است
## install 
#### mac , linux
```bash
python3 -m pip install metafid-data
```
#### windows
```bash
python -m pip install metafid-data
```

## data
### ise (Iran Stock Exchange)
#### TSETMC (tsetmc.com)
```python
from mf_data.ise import TSETMC
tsetmc = TSETMC()
# ------------- market watch -------------
stock_mw = tsetmc.market_watch(stock=True) #stoock
ifb_paye_mw = tsetmc.market_watch(ifb_paye=True) # پایه‌یٍ فرابورس
mortgage_mw = tsetmc.market_watch(mortgage=True) # اوراقٍ مسکن
# cum_right, bond, option, futures, etf, commodity دیگر پارامترها شامل اینها که می‌توان با هم هم افزوده شوند 
m_mw = tsetmc.market_watch(stock=True, cum_right=True,etf=True )
# ------------- option market watch -------------
tsetmc.option_market_watch()
# ------------- instrument info -------------
tsetmc.stock_info()
tsetmc.option_info()
tsetmc.etf_info()
# ------------- history price -------------
tsetmc.hist_price(symbol_far= "فولاد") 
# اگر میخواهید بر اساس کد نماد داده دریافت کنید
tsetmc.hist_price(ins_code= "46348559193224090") 
# ------------- adjust history price -------------
tsetmc.adj_hist_price(symbol_far= "فولاد") 
# اگر میخواهید بر اساس کد نماد داده دریافت کنید
tsetmc.adj_hist_price("46348559193224090") 
```

### Rahavard
```python
from mf_data.ise import Rahavard
rah = Rahavard()
# ------------- balance-sheet -------------
rah.balance_sheet("فولاد")

```
### econ 
### TGJU (tgju.org)
```python
from mf_data.econ import TGJU
tgju = TGJU()
# ------------- sekke -------------
sekke_emami = tgju.sekke_emami() # امامی
nim_sekke = tgju.nim_sekke() # نیم
rob_sekke = tgju.rob_sekke() # رُبع
ons = tgju.ons() # xauusd (اُنس جهانی)
# ------------- currency -------------
usd_irr = tgju.usd_irr()
```
### ICB (Iran Central Bank)