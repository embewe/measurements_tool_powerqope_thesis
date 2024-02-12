FROM debian:stable-slim

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get update && \
    apt-get -y install gcc g++ python python-dev build-essential wget

WORKDIR /tmp

ENV NS3_VERSION=3.29
RUN wget https://www.nsnam.org/releases/ns-allinone-${NS3_VERSION}.tar.bz2 && \
    tar xf ns-allinone-${NS3_VERSION}.tar.bz2 && \
    rm -rf ns-allinone-${NS3_VERSION}.tar.bz2 && \
    mv ns-allinone-${NS3_VERSION}/ns-3.29 /ns3 && \
    cd /ns3 && \
    ./waf -d debug configure \
        --enable-modules=core,network,internet,point-to-point,applications && \
    ./waf && \
    ./waf install && \
    rm -rf /tmp/ns-allinone-${NS3_VERSION}

WORKDIR /ns3
RUN ln -sf /dnsdotdoh/applications/wscript                    /ns3/src/applications/wscript && \
    ln -sf /dnsdotdoh/applications/helper/dnsdotdoh-helper.cc /ns3/src/applications/helper/dnsdotdoh-helper.cc && \
    ln -sf /dnsdotdoh/applications/helper/dnsdotdoh-helper.h  /ns3/src/applications/helper/dnsdotdoh-helper.h && \
    ln -sf /dnsdotdoh/applications/model/dnsdotdoh-client.cc  /ns3/src/applications/model/dnsdotdoh-client.cc && \
    ln -sf /dnsdotdoh/applications/model/dnsdotdoh-client.h   /ns3/src/applications/model/dnsdotdoh-client.h && \
    ln -sf /dnsdotdoh/applications/model/dnsdotdoh-server.cc  /ns3/src/applications/model/dnsdotdoh-server.cc && \
    ln -sf /dnsdotdoh/applications/model/dnsdotdoh-server.h   /ns3/src/applications/model/dnsdotdoh-server.h && \
    ln -sf /dnsdotdoh/applications/model/dnsdotdoh-common.cc  /ns3/src/applications/model/dnsdotdoh-common.cc && \
    ln -sf /dnsdotdoh/applications/model/dnsdotdoh-common.h   /ns3/src/applications/model/dnsdotdoh-common.h && \
    ln -sf /dnsdotdoh/scratch/dnsdotdoh                       /ns3/scratch/dnsdotdoh

# TODO
# - Copy files into Docker
# - Compile
# - Delete /ns3
# - Set ENTRYPOINT
