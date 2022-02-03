#!/bin/sh

# Create Rabbitmq user
( rabbitmqctl wait --timeout 60 $RABBITMQ_PID_FILE ; \
rabbitmqctl add_user $RABBITMQ_DEEPCORE_USER $RABBITMQ_DEEPCORE_PASSWORD 2>/dev/null ; \
rabbitmqctl set_permissions -p / $RABBITMQ_DEEPCORE_USER  ".*" ".*" ".*" ; \
rabbitmqctl add_user $RABBITMQ_RENDERER_USER $RABBITMQ_RENDERER_PASSWORD 2>/dev/null ; \
rabbitmqctl set_permissions -p / $RABBITMQ_RENDERER_USER  ".*" ".*" ".*" ; \
rabbitmqctl add_user $RABBITMQ_FRONTEND_USER $RABBITMQ_FRONTEND_PASSWORD 2>/dev/null ; \
rabbitmqctl set_permissions -p / $RABBITMQ_FRONTEND_USER  ".*" ".*" ".*" ; \
rabbitmqctl add_user $RABBITMQ_ADMIN $RABBITMQ_ADMIN_PW ; \
rabbitmqctl set_permissions -p / $RABBITMQ_ADMIN  ".*" ".*" ".*" ; \
rabbitmqctl set_user_tags $RABBITMQ_ADMIN administrator ) &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
rabbitmq-server $@
