ARG BUILD_FROM=ghcr.io/home-assistant/base:3.24
FROM ${BUILD_FROM}
RUN apk add --no-cache python3 pulseaudio-utils
COPY rootfs /
