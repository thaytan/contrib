FROM alpine:3.15
RUN apk add --no-cache chrony=4.1-r0

RUN mkdir -p /var/lib/chrony/drift && chown -R chrony:chrony /var/lib/chrony/drift
VOLUME /var/lib/chrony/drift

COPY chrony/chrony.conf /etc/chrony/chrony.conf

EXPOSE 123/udp

ENTRYPOINT [ "/usr/sbin/chronyd", "-d", "-s"]