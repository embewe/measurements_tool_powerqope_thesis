
# 10x10 pageload difference plot
python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc-grid --pageload_diffs

# Pageload difference subset plots for each provider
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_cf
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_google
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_quad9
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_cleanb_sec
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_cleanb_fam
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_cleanb_adt
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_adguard_default
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_adguard_family
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_securedns_default
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_securedns_adblock

#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_diffs_doh
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --cf_pageloads
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --pageload_resources
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --timing_cf

# DNS timings
#python3 plots.py ../../data/.pgpass ../../data/domains.txt --matplotlibrc matplotlibrc --timing
