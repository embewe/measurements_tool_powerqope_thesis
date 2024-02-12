#!/bin/sh

# Princeton
# These experiments ran from 2019/06/24 18:52 UTC to 2019/06/30 21:45 UTC
CMDPRINCETON="pipenv run python plots.py ./princeton.ini \
    ../../data/tranco_combined.txt \
    --name=princeton \
    --experiments \
        28bce458-96b1-11e9-b77e-ffced1bf1c70 \
        40042f84-9780-11e9-b844-eb2e67efdb20 \
        9c69b15a-986a-11e9-8dcd-0785c30a5734 \
        c686cb72-993b-11e9-a31f-6f61c22a6212 \
        9c488e12-9a0e-11e9-b272-87b812950940"

# Princeton 4G
# These experiments ran from 2019/06/24 14:36 UTC to 2019/06/30 21:49 UTC
CMD4G="pipenv run python plots.py ./princeton_4g.ini \
    ../../data/tranco_combined.txt \
    --name=princeton_4g \
    --experiments \
        18776a08-9690-11e9-8204-7b657e652275 \
        63de94a8-978a-11e9-82c2-67f77b5d4b26 \
        9cb74bb4-9887-11e9-ac51-bb36fce37806 \
        04d5ab66-9985-11e9-bd39-67ad48f29752 \
        2992d384-9a84-11e9-9338-d77a8dcce0e7"

# Princeton 4G Lossy
# These experiments ran from 2019/06/17 14:45 UTC to 2019/06/24 08:19 UTC
CMD4GLOSSY="pipenv run python plots.py ./princeton_4g_lossy.ini \
    ../../data/tranco_combined.txt \
    --name=princeton_4g_lossy \
    --experiments \
        78f4fb5c-910e-11e9-85af-1749d9c6db80 \
        4e6e8c82-921b-11e9-adaa-0fd1a9675237 \
        75bedb7e-932a-11e9-8a9d-33f95562d684 \
        478b1c6e-943c-11e9-960b-57dd1eea9c72 \
        f407b296-9549-11e9-861d-9f8d899b4201"

# Princeton 3G
# These experiments ran from 2019/06/17 14:53 UTC to 2019/06/28 04:29 UTC
# They took longer than one week because 3G is slower
CMD3G="pipenv run python plots.py ./princeton_3g.ini \
    ../../data/tranco_combined.txt \
    --name=princeton_3g \
    --experiments \
        9e4ec922-910f-11e9-9e84-3f2b25902a5d \
        8738dc78-92bd-11e9-9fc9-d398e47263f6 \
        ef858042-9466-11e9-bc27-373fc12f4703 \
        32f9abfa-9610-11e9-b244-8fc3416eb9c6 \
        aacd46d4-97b7-11e9-af23-679c4502a719"

for CMD in "${CMDPRINCETON}" "${CMD4G}" "${CMD4GLOSSY}" "${CMD3G}"; do
    ${CMD} \
        --matplotlibrc matplotlibrc-grid \
        --pageload_diffs

    ${CMD} \
        --matplotlibrc matplotlibrc-grid \
        --pageload_diffs_cf

    ${CMD} \
        --matplotlibrc matplotlibrc \
        --timing

    ${CMD} \
        --matplotlibrc matplotlibrc \
        --timing_cf

    ${CMD} \
        --matplotlibrc matplotlibrc \
        --pageload_resources
done
