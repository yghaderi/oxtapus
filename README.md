# metafid
## oxtapus
این پکیج برای پوششِ بخشی از داده‌های موردِ نیاز در تصمیم‌هایِ مالی-اقتصادی توسعه داده شده است
## install 
#### mac , linux
```bash
python3 -m pip install oxtapus
```
#### windows
```bash
python -m pip install oxtapus
```

## data

### ise (Iran Stock Exchange)
#### TSETMC (tsetmc.com)
```python
from oxtapus.ise import TSETMC
tsetmc = TSETMC()

# ------------- market watch -------------
tsetmc.market_watch(stock=True) #stoock
tsetmc.market_watch(ifb_paye=True) # پایه‌یٍ فرابورس
tsetmc.market_watch(mortgage=True) # اوراقٍ مسکن
# cum_right, bond, option, futures, etf, commodity دیگر پارامترها شامل اینها است که می‌توان با-هم هم افزوده شوند 
tsetmc.market_watch(stock=True, cum_right=True,etf=True )

# ------------- option market watch -------------
tsetmc.option_market_watch()

# ------------- instrument info -------------
tsetmc.stock_info()
tsetmc.option_info()
tsetmc.etf_info()

# ------------- history price -------------
tsetmc.hist_price(symbol_far= "شبندر") 
# اگر میخواهید بر اساس کد نماد داده دریافت کنید
tsetmc.hist_price(ins_code= "35366681030756042") 

# ------------- adjust history price -------------
tsetmc.adj_hist_price(symbol_far= "شبندر") 
# اگر میخواهید بر اساس کد نماد داده دریافت کنید
tsetmc.adj_hist_price(ins_code= "35366681030756042") 

# ------------- share change -------------
tsetmc.share_change(symbol_far= "شبندر") 
# اگر میخواهید بر اساس کد نماد داده دریافت کنید
tsetmc.share_change(ins_code= "35366681030756042") 

# ------------- index  -------------
tsetmc.all_index() # همه‌یِ شاخص‌ها-شاملِ نام، کد، و مقدار
tsetmc.index_ticker_symbols(index_code=13235969998952202) # نمادهایی که شاخصِ *** دنبال می‌کند
tsetmc.index_hist(index_code=13235969998952202)

```
### Codal(codal.ir)
###### beta version!
```python
from oxtapus.ise import Codal
codal = Codal()
codal.symbol = "شبندر"

# ------------- income-statements -------------
codal.income_statements() # صورتِ سود یا زیان
codal.balance_sheet() # صورت-وضعیتِ مالی
```

### Rahavard
```python
from oxtapus.ise import Rahavard
rah = Rahavard()

# ------------- balance-sheet -------------
rah.balance_sheet("شبندر")

```
### econ 
### TGJU (tgju.org)
```python
from oxtapus.econ import TGJU
tgju = TGJU()

# ------------- sekke -------------
tgju.sekke_emami() # امامی
tgju.nim_sekke() # نیم
tgju.rob_sekke() # رُبع
tgju.ons() # xauusd (اُنس جهانی)

# ------------- currency -------------
tgju.usd_irr()
```
### ICB (Iran Central Bank)