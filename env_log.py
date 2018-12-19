import sqlite3
import sys
import Adafruit_DHT

def log_values(sensor_id, temp, hum):
    connection = sqlite3.connect('/var/www/weatherStation/weatherStation.db')

    cursor = connection.cursor()
    # wrtie the current temperature to the temperatures table
    cursor.execute("""INSERT INTO temperatures values (datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id, temp))

    # write the current humidity to the humidities table
    cursor.execute("""INSERT INTO humidities values (datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (sensor_id, hum))

    connection.commit()
    connection.close()


# try to get a temp, hum reading
humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)

if humidity is not None and temperature is not None:
    log_values("1", temperature, humidity)
else:
    # if there is no ready, an unlikely number is entered for troubleshooting
    log_values("1", -999, -999)


