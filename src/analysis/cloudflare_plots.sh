# Pageload difference subset plots
python3 plots.py ../../data/princeton_postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_cf --name princeton
python3 plots.py ../../data/princeton_4g.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_cf --name 4g
python3 plots.py ../../data/princeton_4g_lossy.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_cf --name 4g_lossy
python3 plots.py ../../data/princeton_3g.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_cf --name 3g

# DNS timings
# python3 plots.py ../../data/princeton_4g.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --timing_cf --name 4g
# python3 plots.py ../../data/princeton_4g_lossy.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --timing_cf --name 4g_lossy
# python3 plots.py ../../data/princeton_3g.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --timing_cf --name 3g
