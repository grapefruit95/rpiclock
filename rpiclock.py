import datetime
import time
userDayDelta = 0
userHourDelta = 0
while True:
    currentTime = (datetime.datetime.now()+datetime.timedelta(days=userDayDelta, hours=userHourDelta))
    day = str(currentTime.day)
    month = str(currentTime.month)
    hour = str(currentTime.strftime("%I"))
    minute = str(currentTime.strftime("%M"))
    second = str(currentTime.strftime("%S"))
    time.sleep(0.1)
    print(month, day, hour, minute, second)
