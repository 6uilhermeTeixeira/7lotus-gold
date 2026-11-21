FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV WINEPREFIX=/data/mt5-prefix
ENV WINEARCH=win64

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates curl wget xvfb xauth xdotool x11vnc openbox novnc websockify cabextract unzip \
    && mkdir -p /etc/apt/keyrings \
    && wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key \
    && wget -qO /etc/apt/sources.list.d/winehq-noble.sources https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources \
    && apt-get update \
    && apt-get install -y --install-recommends winehq-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/fusion-history
COPY infra/fusion-history-mt5/ /opt/fusion-history/
RUN chmod +x /opt/fusion-history/*.sh \
    && mkdir -p /data/downloads /data/mt5-prefix /data/home /data/logs

CMD ["/opt/fusion-history/start-remote-desktop.sh"]
