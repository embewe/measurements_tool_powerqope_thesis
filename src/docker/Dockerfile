FROM tungs/har:firefox-67.0-stable
ADD harexporttrigger-0.6.2-fx.xpi \
    run.py \
    har_catcher.py \
    stubby-cf.yml \
    stubby-cf-security.yml \
    stubby-cf-family.yml \
    stubby-quad9.yml \
    stubby-quad9_nofilter.yml \
    quad9_security_edns.yml \
    stubby-google.yml \
    cleanb-family.yml \
    cleanb-adult.yml \
    cleanb-security.yml \
    securedns-default.yml \
    securedns-adblock.yml \
    adguard-default.yml \
    adguard-family.yml \
    adguard-nofilter.yml \
    resolv.conf \
    /home/seluser/measure/
RUN sudo chown seluser:seluser -R /home/seluser/measure/
USER seluser
WORKDIR /home/seluser/measure/
ENTRYPOINT ["sudo", "python3", "/home/seluser/measure/run.py"]
