#! /bin/bash

cd ..
docker-compose exec web flask db init
docker-compose exec web flask db migrate -m "Initial migration."
docker-compose exec web flask db upgrade
cd scripts