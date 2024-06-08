#! /bin/bash

sudo apt-get install -y mosquitto-clients
docker-compose -f stack.yml build
docker stack deploy -c stack.yml sprc3