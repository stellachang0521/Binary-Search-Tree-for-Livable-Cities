import requests
import json


######################### Data Pre-Manipulation #########################

# Numbeo API key
numbeo_key = '2ff4reqbl6x2y3'

# Weather API key
weather_key = '565db931607fb2edf86194645edef709'


# obtain city list

## Numbeo cities (accessible with Numbeo API)
ncity_url = f'https://www.numbeo.com/api/cities?country=USA&api_key={numbeo_key}'
ncity_response = requests.get(ncity_url)
ncity_json = ncity_response.text
ncity_dicts = json.loads(ncity_json)

numbeo_cities = []
for i in ncity_dicts['cities']:
    numbeo_cities.append((i['city_id'], i['city']))

## Weather cities (downloadable from the OpenWeather website)
wcity_dicts = json.load(open('weather_city.list.json'))

weather_cities = []
wcity_ids = {}
wcity_coors = {}
for dic in wcity_dicts:
    if dic['country'] == 'US':
        weather_cities.append(dic['name'] + ', ' + dic['state'])
        wcity_ids[dic['name'] + ', ' + dic['state']] = dic['id']
        wcity_coors[dic['name'] + ', ' + dic['state']] = (dic['coord']['lon'], dic['coord']['lat'])

# finding mutual cities
cities = []
city_names = []
city_coors = {}
for city in numbeo_cities:
    if city[1] in weather_cities:
        # format: city_name, numbeo_id, weather_id
        cities.append((city[1], city[0], wcity_ids[city[1]]))
        city_names.append(city[1])
        # format: longitude, latitude
        city_coors[city[1]] = wcity_coors[city[1]]


# Numbeo city indices data
#indice_url = f'https://www.numbeo.com/api/indices?city_id={city_id}&api_key={numbeo_key}'

indice_dicts = []
for city in cities:
    city_id = city[1]
    indice_response = requests.get(f'https://www.numbeo.com/api/indices?city_id={city_id}&api_key={numbeo_key}')
    indice_json = indice_response.text
    indice_dicts.append(json.loads(indice_json))
    

# month list
### will only focus on two months within the year (July for the summer and December for the winter)
#weather_url = f'http://history.openweathermap.org/data/2.5/aggregated/month?id={city_id}&month={month}&appid={weather_key}'

July = []
month = 7
for city in cities:
    city_id = city[2]
    weather_response = requests.get(f'http://history.openweathermap.org/data/2.5/aggregated/month?id={city_id}&month={month}&appid={weather_key}')
    weather_json = weather_response.text
    July.append((json.loads(weather_json))['result'])
    
December = []
month = 12
for city in cities:
    city_id = city[2]
    weather_response = requests.get(f'http://history.openweathermap.org/data/2.5/aggregated/month?id={city_id}&month={month}&appid={weather_key}')
    weather_json = weather_response.text
    December.append((json.loads(weather_json))['result'])
    
# create a comprehensive list
dataDict = {}
dataDict['city'] = city_names
dataDict['living costs'] = indice_dicts
dataDict['July weather'] = July
dataDict['December weather'] = December

# downloading dataDict into a local json file
dataDict_json = json.dumps(dataDict)
with open('dataDict.json', 'w') as f:
    f.write(dataDict_json)
    
# downloading city_coors into a local json file
city_coors_json = json.dumps(city_coors)
with open('city_coors.json', 'w') as f:
    f.write(city_coors_json)
