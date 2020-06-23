from threading import Thread
import requests
import pyowm
import datetime
import time
import geocoder
def updateWeather(g):
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        observation = mgr.weather_at_coords(g.latlng[0],g.latlng[1])
    except:
        return "API Request Fail"
    temp_data = observation.to_dict()['weather']['temperature']
    return str(round(pyowm.utils.measurables.kelvin_to_fahrenheit(temp_data['temp'])))

def updateForecast(g):
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        forecast = mgr.forecast_at_coords(g.latlng[0],g.latlng[1], "3h", limit=8)
    except:
        return "NA"
    maxTemp = 0
    minTemp = 1000
    for x in forecast.forecast.to_dict()['weathers']:
        if x['temperature']['temp_max'] > maxTemp:
            maxTemp = x['temperature']['temp_max']

    for x in forecast.forecast.to_dict()['weathers']:
        if x['temperature']['temp_min'] < minTemp:
            minTemp = x['temperature']['temp_min']
    return [str(round(pyowm.utils.measurables.kelvin_to_fahrenheit(maxTemp))), str(round(pyowm.utils.measurables.kelvin_to_fahrenheit(minTemp)))]

def clockLine():
    userDayDelta = 0
    userHourDelta = 0
    while True:
        currentTime = (datetime.datetime.now()+datetime.timedelta(days=userDayDelta, hours=userHourDelta))

        time_str = datetime.datetime.strftime(currentTime, "%I:%M%p    %m/%d")

        print(time_str)
        time.sleep(2)

def weatherLine():
    try:
        g = geocoder.ip('me')
    except:
        g = "No Connection"
    currentTemp = updateWeather(g)
    maxMinTemp = updateForecast(g)
    outputText = (currentTemp+u'\N{DEGREE SIGN}'+"        "+maxMinTemp[0]+'/'+maxMinTemp[1]+"                ")[0:16]

    while True: 
        try:
            g = geocoder.ip('me')
        except:
            g = "No Connection"
        print(outputText)
        currentTemp = updateWeather(g)
        if currentTemp == "API Request Fail":
            outputText = "API Request Fail"
        else:
            outputText = (currentTemp+u'\N{DEGREE SIGN}'+"        "+maxMinTemp[0]+'/'+maxMinTemp[1]+"                ")[0:16]
        if (datetime.datetime.now().hour == 0 and datetime.datetime.now().minute in range(0,5)) or (maxMinTemp[0]+'/'+maxMinTemp[1] == "N/A"):
            maxMinTemp = updateForecast(g)

        time.sleep(2)

Thread(target=clockLine).start()
Thread(target=weatherLine).start()
