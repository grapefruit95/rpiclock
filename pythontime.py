import datetime
import time

while True:
    currentTime = (datetime.datetime.now())
    day = str(currentTime.day)
    month = str(currentTime.month)
    hour = str(currentTime.strftime("%I"))
    minute = str(currentTime.strftime("%M"))
    second = str(currentTime.strftime("%S"))
