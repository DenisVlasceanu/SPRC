import datetime
import subprocess
from random import choice
from time import sleep


locations = ['UPB', 'UniBuc', 'ASE', 'USH', 'UAUIM', 'UTCB', 'USAMV']
stations = ['RPi_1', 'RPi_2', 'RPi_3', 'RPi_4', 'RPi_5', 'RPi_6', 'RPi_7']
bats = list(range(10, 101))
humids = list(range(20, 41))
tmps = list(range(5, 36))
alarms = list(range(0, 11))
aqis = list(range(10, 21))
rssis = list(range(1000, 2001))
odd_even = list(range(1, 11))

while True:
    location = choice(locations)
    station = choice(stations)
    timestamp = datetime.datetime.today()
    year = timestamp.year
    month = timestamp.month
    day = timestamp.day
    hour = timestamp.hour
    minute = timestamp.minute
    second = timestamp.second
    beginning = f'''mosquitto_pub -h localhost -p 1883 -t "{location}/{station}" -m '''
    end = f'''"timestamp": "{year}-{month}-{day}T{hour}:{minute}:{second}Z"''' + '''}' '''
    if choice(odd_even) % 2 == 0:
        bat = choice(bats)
        humid = choice(humids)
        tmp = choice(tmps)
        battery = ''''{"BAT": ''' + f'''{bat}, "HUMID": {humid}, "TMP": {tmp}, '''
        command = beginning + battery + end
    else:
        alarm = choice(alarms)
        aqi = choice(aqis)
        rssi = choice(rssis)
        alarm = ''''{"Alarm": ''' + f'''{alarm}, "AQI": {aqi}, "RSSI": {rssi}, '''
        command = beginning + alarm + end
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(command)
    sleep(1)
