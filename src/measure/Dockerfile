FROM debian:stable-slim

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get -y update && \
    apt-get -y install apt-utils && \
    apt-get -y install --no-install-recommends \
        sudo python3-pip vim wget bzip2 libgtk-3-0 libdbus-glib-1-2 \
        libxt6 procps dnsutils libssl-dev openssl libyaml-dev git libtool m4 autoconf build-essential automake libunbound-dev \
        libcurl4-openssl-dev libssl-dev libev4 libev-dev libevent-2.1.6 libevent-core-2.1.6 libevent-openssl-2.1.6 libevent-dev libuv1 cmake check 

#ADD requirements.txt /tmp/
#RUN pip3 install -r /tmp/requirements.txt && \
#   rm /tmp/requirements.txt

RUN useradd -ms /bin/bash seluser
RUN adduser seluser sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ADD ../../../dotdoh /home/seluser/
RUN sudo chown seluser:seluser -R /home/seluser/dotdoh/
USER seluser
WORKDIR /home/seluser/dotdoh/src/measure/
ENTRYPOINT ["/home/seluser/dotdoh/src/measure/measure.sh"]
