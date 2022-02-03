ARG VERSION=3.9
FROM rabbitmq:${VERSION}-management-alpine
LABEL org.opencontainers.image.source https://github.com/aivero/contrib

RUN rabbitmq-plugins enable rabbitmq_mqtt
RUN rabbitmq-plugins enable rabbitmq_web_mqtt

ENV RABBITMQ_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

ADD rabbitmq-init.sh /init.sh
RUN chmod +x /init.sh
# MQTT-over-WebSockets (see https://www.rabbitmq.com/networking.html#ports)
EXPOSE 15675
EXPOSE 15672

# Define default command
CMD ["/init.sh"]
