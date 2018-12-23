from flask import Flask, request, render_template
import sys
import Adafruit_DHT
import sqlite3
import time
import datetime
import arrow

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
    temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

    print(temperatures, humidities)

    # create new arrays with times converted back to user's timezone
    time_adjusted_temperatures = []
    time_adjusted_humidities = []

    for record in temperatures:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
        time_adjusted_temperatures.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])

    for record in humidities:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
        time_adjusted_humidities.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2], 2)])

    return render_template("env_db.html", timezone = timezone, temp=time_adjusted_temperatures, hum=time_adjusted_humidities, temp_items=len(temperatures), hum_items= len(humidities), from_date = from_date_str, to_date = to_date_str)

def get_records():
    from_date_str = request.args.get('from', time.strftime("%Y-%m-%d %H:%M"))
    to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
    range_h_form = request.args.get('range_h', '')
    range_h_int = "nan"
    timezone = request.args.get('timezone', 'Etc/UTC');
    
    try:
        range_h_int = int(range_h_form)
    except:
        print("range_h_form is not a number")

    ## validate the date from and to before sending the query to the database
    if not validate_date(from_date_str):
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m%d %H:%M")
    
    # create datetime object so that we can convert to UTC from the brower's local time
    from_date_obj = datetime.datetime.strptime(from_date_str, '%Y-%m-%d %H:%M')
    to_date_obj = datetime.datetime.strptime(to_date_str, '%Y-%m-%d %H:%M')
    
    
    # If range_h_from is defined it takes precendece over the 'from' and 'to' params
    if isinstance(range_h_int, int):
        arrow_time_from = arrow.utcnow().replace(hours=-range_h_int)
        arrow_time_to = arrow.utcnow()
        from_date_utc = arrow_time_from.strftime("%Y-%m-%d %H:%M")
        to_date_utc = arrow_time_to.strftime("%Y-%m-%d %H:%M")
        from_date_str = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
        to_date_str = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
    else:
        from_date_utc = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")
        to_date_utc = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

    connection = sqlite3.connect('/var/www/weatherStation/weatherStation.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    temperatures = cursor.fetchall()
    cursor.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    humidities = cursor.fetchall()
    connection.close()
    return [temperatures, humidities, timezone, from_date_str, to_date_str]

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
