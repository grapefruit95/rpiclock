import requests

locations = ["Spring Branch,Texas", "San Antonio,Texas", "New Braunfels,Texas"]
locationLatLongs = {}
locationWeather = {}
for location in locations:
    url = "https://community-open-weather-map.p.rapidapi.com/weather"

    querystring = {"callback":"test","id":"2172797","units":"%22metric%22 or %22imperial%22","mode":"xml%2C html","q":location}

    headers = {
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
        'x-rapidapi-key': "42d1462079mshead0e3cee7cec9fp130467jsnadc27d29ba00"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    locationWeather[location] = response.text

print(locationWeather)
