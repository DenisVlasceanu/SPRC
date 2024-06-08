#! /bin/bash

docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'sprc2_web')
docker rmi $(docker images --filter=reference='adminer' --format "{{.ID}}")
docker rmi $(docker images --filter=reference='postgres' --format "{{.ID}}")
docker volume rm sprc2_dbVolume
docker volume rm sprc2_migrationsVolume