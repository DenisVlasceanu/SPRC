#!/bin/sh

check_service() {
    service=$1
    port=$2
    timeout=${3:-30}
    while ! nc -z "$service" "$port" 2>/dev/null; do
        sleep 1
        timeout=$((timeout-1))
        if [ "$timeout" -le 0 ]; then
            echo "Timeout waiting for $service on port $port"
            exit 1
        fi
    done
    echo "$service is up on port $port"
}

check_service "sprc3_mqtt-broker" 1883 30
check_service "sprc3_influxdb" 8086 30

python3 -u adapter.py
