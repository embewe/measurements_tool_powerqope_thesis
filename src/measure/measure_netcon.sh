#!/bin/bash

VENV_DIRECTORY=$(realpath venv)
DATA_DIRECTORY=$(realpath ../../data)

WORKER=3

database=${1:-${DATA_DIRECTORY}/dblocal_netcond.txt}
websites=${2:-${DATA_DIRECTORY}/test_domains.txt}
logging=${3:-${DATA_DIRECTORY}/logging.config}

UUID=$(uuid -v 1)

NUM_WEBSITES=$(wc -l ${websites} | awk '{print $1}')

BATCHSIZE=$((${NUM_WEBSITES} / ${WORKER}))

for w in $(seq 0 $((${WORKER} - 1))); do
    if [ $w -lt $((${WORKER} - 1)) ]; then
        ${VENV_DIRECTORY}/bin/python3 wrapper_net_conditions.py \
            ${database} ${websites} ${logging} \
            ${UUID} $(($w * ${BATCHSIZE})) $(( ($w + 1) * ${BATCHSIZE})) &
    else
        ${VENV_DIRECTORY}/bin/python3 wrapper_net_conditions.py \
            ${database} ${websites} ${logging} \
            ${UUID} $(($w * ${BATCHSIZE})) ${NUM_WEBSITES} &
    fi
done

wait
