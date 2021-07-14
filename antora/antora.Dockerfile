FROM antora/antora
RUN apk add --no-cache openssh
LABEL org.opencontainers.image.source https://github.com/aivero/contrib