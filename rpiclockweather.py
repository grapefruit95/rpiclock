from threading import Thread
import requests
import pyowm
import datetime
import time
import RPi.GPIO as GPIO
import time
GPIO.cleanup()
userDayDelta = 0
userHourDelta = 0
currentTime = (datetime.datetime.now()+datetime.timedelta(days=userDayDelta, hours=userHourDelta))

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

# Toggle 'Enable' pin
# Define GPIO to LCD mapping
LCD_RS = 25
LCD_E  = 24
LCD_D4 = 23
LCD_D5 = 17
LCD_D6 = 18
LCD_D7 = 22
HOURPLUS = 5
HOURMINUS = 6
DAYPLUS = 27
DAYMINUS = 13
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.001
E_DELAY = 0.001

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(HOURPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(HOURMINUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DAYPLUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DAYMINUS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lcd_toggle_enable()

lcd_init()

location = "Spring Branch, Texas"
outputText = ""

def updateWeather():
    owm = pyowm.OWM("a51b8b1104bc88753d99c08008b0717a")
    mgr = owm.weather_manager()
    try:
        observation = mgr.weather_at_coords(29.82, -98.3)
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

def clockLine():
    global userDayDelta
    global userHourDelta
    global currentTime
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

        time_str = datetime.datetime.strftime(currentTime, "%I:%M%p    %m/%d")

        print(time_str)
        lcd_string(time_str,LCD_LINE_1)
        time.sleep(0.1)

def formatOutText(maxMinTemp, currentTemp):
  numOfSpaces = 0
  numOfSpaces = 16-(2+len(maxMinTemp[0])+len(maxMinTemp[1])+len(currentTemp))
  return (maxMinTemp[0]+'/'+maxMinTemp[1]+(" "*numOfSpaces)+currentTemp+u'\N{DEGREE SIGN}'+"                ")[0:16]


def weatherLine():
    global userDayDelta
    global userHourDelta
    global currentTime
    currentTemp = updateWeather()
    maxMinTemp = updateForecast()
    if int(currentTemp) > int(maxMinTemp[0]):
      maxMinTemp[0] = currentTemp
    elif int(currentTemp) < int(maxMinTemp[1]):
      maxMinTemp[1] = currentTemp
    outputText = formatOutText(maxMinTemp, currentTemp)

    while True: 
        if currentTemp > maxMinTemp[0]:
          maxMinTemp[0] = currentTemp
        elif currentTemp < maxMinTemp[1]:
          maxMinTemp[1] = currentTemp
        print(outputText)
        #lcd_string(outputText,LCD_LINE_2)
        currentTemp = updateWeather()
        if currentTemp == "API Request Fail":
            outputText = "API Request Fail"
        else:
            outputText = formatOutText(maxMinTemp, currentTemp)
        if (currentTime.hour == 0 and currentTime.minute in range(0,5)) or (maxMinTemp[0]+'/'+maxMinTemp[1] == "N/A"):
            maxMinTemp = updateForecast()

        time.sleep(120)

Thread(target=clockLine).start()
Thread(target=weatherLine).start()


