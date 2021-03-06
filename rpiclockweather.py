import requests
import pyowm
import datetime
import time
import RPi.GPIO as GPIO
import sys
sys.path.append('/home/pi/lcd')
import lcd

userDayDelta = 0
userHourDelta = 0
currentTime = (datetime.datetime.now()+datetime.timedelta(days=userDayDelta, hours=userHourDelta))
maxMinTemp = []

def lcd_init():
  lcd.lcd_init()
  lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
  lcd.lcd_string("Rocco's Clock", 2)
  lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
  lcd.lcd_string("Summer 2020", 2)
  #lcd.GPIO.cleanup()

location = "Spring Branch, Texas"
outputText = ""

def updateWeather():
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        observation = mgr.weather_at_coords(29.8899, -98.4253)
    except:
        return "API Request Fail"
    temp_data = observation.to_dict()['weather']['temperature']
    return str(round(pyowm.utils.measurables.kelvin_to_fahrenheit(temp_data['temp'])))

def updateForecast():
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        forecast = mgr.one_call(29.82, -98.3)
    except:
        return "NA"

    return [str(round(forecast.forecast_daily[0].temperature('fahrenheit').get('max', None))), str(round(forecast.forecast_daily[0].temperature('fahrenheit').get('min', None)))]

def clock():
    global userDayDelta
    global userHourDelta
    global currentTime
    global maxMinTemp
    maxMinTemp = updateForecast()
    weatherLine()

    HOURPLUS = 4
    HOURMINUS = 17
    DAYPLUS = 18
    DAYMINUS = 27

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

    GPIO.setup(HOURPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(HOURMINUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DAYPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DAYMINUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    while True:
        if GPIO.input(HOURPLUS) == False:
          userHourDelta = userHourDelta + 1
          time.sleep(0.2)
        if GPIO.input(HOURMINUS) == False:
          userHourDelta = userHourDelta - 1
          time.sleep(0.2)
        if GPIO.input(DAYPLUS) == False:
          userDayDelta = userDayDelta + 1
          time.sleep(0.2)
        if GPIO.input(DAYMINUS) == False:
          userDayDelta = userDayDelta - 1
          time.sleep(0.2)
        currentTime = (datetime.datetime.now()+datetime.timedelta(days=userDayDelta, hours=userHourDelta))

        time_str = datetime.datetime.strftime(currentTime, "%I:%M%p   %b %d")

        print(time_str)
        lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
        lcd.lcd_string(time_str, 2)
        if(currentTime.minute % 2 == 0 and currentTime.second == 1):
          weatherLine()
        time.sleep(0.1)

def formatOutText(maxMinTemp, currentTemp):
  numOfSpaces = 0
  numOfSpaces = 16-(2+len(maxMinTemp[0])+len(maxMinTemp[1])+len(currentTemp))
  return (maxMinTemp[0]+'/'+maxMinTemp[1]+(" "*numOfSpaces)+currentTemp+"F"+"                ")[0:16]


def weatherLine():
    global userDayDelta
    global userHourDelta
    global currentTime
    global maxMinTemp
    currentTemp = updateWeather()
    
    if currentTemp == "API Request Fail":
      outputText = "API Request Fail"
    else:
      outputText = formatOutText(maxMinTemp, currentTemp)
      if maxMinTemp != "NA":
        if int(currentTemp) > int(maxMinTemp[0]):
          maxMinTemp[0] = currentTemp
        elif int(currentTemp) < int(maxMinTemp[1]):
          maxMinTemp[1] = currentTemp

      if (currentTime.hour == 0 and currentTime.minute in range(0,5)) or (maxMinTemp[0]+'/'+maxMinTemp[1] == "N/A"):
        maxMinTemp = updateForecast()
    
      outputText = formatOutText(maxMinTemp, currentTemp)
    print(outputText)

    lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
    lcd.lcd_string(outputText, 2)

lcd.lcd_init()
clock()

