# Pageload difference plot
python3 plots.py ../../data/princeton_postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc-grid --pageload_diffs

# DNS timings
python3 plots.py ../../data/princeton_postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --timing

# Query amortization
python3 plots.py ../../data/princeton_postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --amortization

