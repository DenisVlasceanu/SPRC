#!/bin/bash

docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'adapter')
docker rmi $(docker images --filter=reference='grafana/grafana' --format "{{.ID}}")
docker rmi $(docker images --filter=reference='influxdb' --format "{{.ID}}")
docker rmi $(docker images --filter=reference='eclipse-mosquitto' --format "{{.ID}}")
docker volume rm sprc3_influxdbVolume
docker volume rm sprc3_grafanaVolume