# metafid

## install 
```bash
python3 -m pip install metafid-data
```

## data
### ise (Iran Stock Exchange)
#### TSETMC (tsetmc.com)
```python
from mf_data.ise import TSETMC
tsetmc = TSETMC()
# market watch
stock_mw = tsetmc.market_watch(stock=True)
# option market watch
tsetmc.option_market_watch()
# instrument info 
tsetmc.stock_info()
tsetmc.option_info()
tsetmc.etf_info()
# adjust history price
tsetmc.adj_hist_price("10210670847057957") 
```

### Rahavard
```python
from mf_data.ise import Rahavard
rah = Rahavard()
# get balance-sheet
rah.balance_sheet("فولاد")

```
### tgju
