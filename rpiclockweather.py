from threading import Thread
import requests
import pyowm
import datetime
import time
import socket
location = "Spring Branch, Texas"
def updateWeather():
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        observation = mgr.weather_at_place(location)
    except:
        return "API Request Fail"
    temp_data = observation.to_dict()['weather']['temperature']
    return str(round(pyowm.utils.measurables.kelvin_to_fahrenheit(temp_data['temp'])))

def updateForecast():
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        forecast = mgr.forecast_at_place(location,"3h", limit=8)
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
    currentTemp = updateWeather()
    maxMinTemp = updateForecast()
    outputText = (currentTemp+u'\N{DEGREE SIGN}'+"        "+maxMinTemp[0]+'/'+maxMinTemp[1]+"                ")[0:16]

    while True: 
        print(outputText)
        currentTemp = updateWeather()
        if currentTemp == "API Request Fail":
            outputText = "API Request Fail"
        else:
            outputText = (currentTemp+u'\N{DEGREE SIGN}'+"        "+maxMinTemp[0]+'/'+maxMinTemp[1]+"                ")[0:16]
        if (datetime.datetime.now().hour == 0 and datetime.datetime.now().minute in range(0,5)) or (maxMinTemp[0]+'/'+maxMinTemp[1] == "N/A"):
            maxMinTemp = updateForecast()

        time.sleep(10)

Thread(target=clockLine).start()
Thread(target=weatherLine).start()
