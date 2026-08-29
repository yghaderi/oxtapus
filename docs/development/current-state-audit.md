# Current-state audit

The 0.4.1 baseline passed two utility tests and built, but exposed website-shaped `TSETMC`,
`TGJU`, `Fipiran`, and `Rahavard` classes and mixed network, parsing, transformation, and
persistence concerns. Public methods included `mw`, `ins_info`, `hist_price`,
`adj_hist_price`, `client_type`, `intraday_trades`, `last_ins_data`, `options_mw`,
`search_ins_code`, `shareholder_list`, `shareholder_history`, and `order_book`.

Findings included direct `requests` and `httpx` usage, per-call clients, mutable sync/async
flags, inconsistent error behavior, source abbreviations escaping as columns, float coercion
of integral financial values, null-to-zero conversion, minimal tests, Persian-only generated
documentation, committed IDE/generated files, and no architectural enforcement.

An untracked local publishing configuration file was detected and intentionally left
untouched; it is now ignored. A tracked publishing helper contained no hard-coded value but
was removed because publishing credentials do not belong in repository utilities. Generated
documentation, IDE metadata, caches, old source, old tests, and the helper were removed.

Source review found one alternative price site technically reachable but its published terms
prohibited reuse without written permission; another historical fund source did not resolve;
the remaining historical source had no verified public-use contract. All three were excluded
from runtime architecture. The official live website's current API asset and cataloged host
were then independently discovered and probed.
