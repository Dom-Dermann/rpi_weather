from flask import Flask, request, render_template
import sys
import Adafruit_DHT
import sqlite3
import time
import datetime

app = Flask(__name__)
app.debug = True        #for debugging purposes only

@app.route("/")
def hello():
    return "This is the weather station reporting!"

@app.route("/weatherStation")
def weatherStation():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
    if humidity is not None and temperature is not None:
        return render_template("weatherStation.html", temp=temperature, hum=humidity)
    else:
        return render_template("no_sensor.html")

@app.route("/env_db", methods=['GET'])
def env_db():
    temperatures, humidities, from_date_str, to_date_str = get_records()
    return render_template("env_db.html", temp=temperatures, hum=humidities)

def get_records():
    from_date_str = request.args.get('from', time.strftime("%Y-%m-%d %H:%M"))
    to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))

    ## validate the date from and to before sending the query to the database
    if not validate_date(from_date_str):
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m%d %H:%M")

    connection = sqlite3.connect('/var/www/weatherStation/weatherStation.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    temperatures = cursor.fetchall()
    cursor.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    humidities = cursor.fetchall()
    connection.close()
    return [temperatures, humidities, from_date_str, to_date_str]

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
