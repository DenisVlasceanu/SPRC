import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import logging
import os
from datetime import datetime
from json import loads
from re import match


debug_data_flow = os.getenv('DEBUG_DATA_FLOW')
topic_str_pattern = r'^[^/]+/[^/]+$'
date_format = '%Y-%m-%d %H:%M:%S'
timestamp_format = '%Y-%m-%dT%H:%M:%S%z'

# Setting up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt=date_format)


def subscribe(mqtt_client, client_data, flags, rc):
    logging.info(f"Connected with result code {rc}")
    mqtt_client.subscribe("#")


def publish(mqtt_client, client_data, message):
    # logging.info(f"Received message on topic: {message.topic}")
    # logging.info(f"Message payload: {message.payload.decode('utf-8')}")

    if match(topic_str_pattern, message.topic):
        if debug_data_flow == 'true':
            logging.info(f'Received a message by topic [{message.topic}]')
        in_message(message, client_data)


def in_message(message, db_client):
    def parse_timestamp(payload):
        try:
            return datetime.strptime(payload['timestamp'], timestamp_format)
        except (KeyError, ValueError):
            if debug_data_flow == 'true':
                logging.info('Data timestamp is NOW')
            return datetime.now()

    def create_influxdb_point(station, key, value, location, timestamp):
        return {
            'measurement': f'{station}.{key}',
            'tags': {'location': location, 'station': station},
            'time': timestamp.strftime(timestamp_format),
            'fields': {'value': value}
        }

    if not match(topic_str_pattern, message.topic):
        return

    device_location, device_station = message.topic.split('/')
    try:
        message_payload = loads(message.payload.decode('utf-8'))
    except ValueError as json_error:
        logging.error(f"Error parsing payload: {json_error}")
        return

    data_timestamp = parse_timestamp(message_payload)
    influxdb_data = [
        create_influxdb_point(device_station, key, value, device_location, data_timestamp)
        for key, value in message_payload.items() if isinstance(value, (int, float))
    ]

    if influxdb_data:
        db_client.write_points(influxdb_data)
        if debug_data_flow == 'true':
            for data in influxdb_data:
                logging.info(f"{data['tags']['location']}.{data['tags']['station']}.{data['measurement'].split('.')[1]} {data['fields']['value']}")


if __name__ == "__main__":
    db_name = os.getenv('DB_NAME', 'sprc3DB')
    mqtt_service_name = os.getenv('MQTT_HOST', 'sprc3_mqtt-broker')
    influx_service_name = os.getenv('INFLUX_HOST', 'sprc3_influxdb')
    influx_client = InfluxDBClient(influx_service_name, database=db_name)
    influx_client.create_database(db_name)
    influx_client.create_retention_policy('unlimited', 'INF', 2, default=True)

    mqtt_client = mqtt.Client(userdata=influx_client)
    mqtt_client.on_connect = subscribe
    mqtt_client.on_message = publish
    mqtt_client.connect(mqtt_service_name)
    mqtt_client.loop_forever()
