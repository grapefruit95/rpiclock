from threading import Thread
import requests
import pyowm
import datetime
import time
import RPi.GPIO as GPIO
import time
 
# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
 
def main():
  # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
 
  # Initialise display
  lcd_init()
 
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
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
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
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
 
if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()

location = "Spring Branch, Texas"
outputText = ""

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
        lcd_string(time_str,LCD_LINE_1)
        time.sleep(0.1)

def weatherLine():
    currentTemp = updateWeather()
    maxMinTemp = updateForecast()
    outputText = (currentTemp+u'\N{DEGREE SIGN}'+"        "+maxMinTemp[0]+'/'+maxMinTemp[1]+"                ")[0:16]

    while True: 
        print(outputText)
        lcd_string(outputText,LCD_LINE_2)
        currentTemp = updateWeather()
        if currentTemp == "API Request Fail":
            outputText = "API Request Fail"
        else:
            outputText = (maxMinTemp[0]+'/'+maxMinTemp[1]+"        "+currentTemp+u'\N{DEGREE SIGN}'+"                ")[0:16]
        if (datetime.datetime.now().hour == 0 and datetime.datetime.now().minute in range(0,5)) or (maxMinTemp[0]+'/'+maxMinTemp[1] == "N/A"):
            maxMinTemp = updateForecast()

        time.sleep(120)

Thread(target=clockLine).start()
Thread(target=weatherLine).start()

