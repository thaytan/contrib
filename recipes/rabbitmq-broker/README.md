# rabbitmq-deployment

Deployment docker for the RabbitMQ server.

Ensure to set the environment variables to define the different users
# Define environment variables.
ENV RABBITMQ_DEEPCORE_USER some_user
ENV RABBITMQ_DEEPCORE_PASSWORD some_pw

ENV RABBITMQ_RENDERER_USER another_user
ENV RABBITMQ_RENDERER_PASSWORD another_pw

ENV RABBITMQ_FRONTEND_USER yet_another_user
ENV RABBITMQ_FRONTEND_PASSWORD yet_another_pw
