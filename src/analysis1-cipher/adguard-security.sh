# 29x29 pageload difference plot
python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc-grid --pageload_diffs_cleanb_fam
python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc-grid --pageload_diffs_securedns_default
python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc-grid --pageload_diffs_adguard_default

