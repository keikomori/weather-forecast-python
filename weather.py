# Desenvolvido no curso:
# Aprenda Programação em Python 3 do Zero com Facilidade
#

#Bibliotecas
import requests                             #Requisições HTTP em Python
import json
from datetime                             import date
import urllib.parse

from requests.packages import urllib3

accuweatherAPIKey = 'APIKEY'
mapboxToken = 'TOKEN'
days_week = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]

def getCoords():
    # Baseado no endereço de IP reconhece a localização retornando a longitude e latitude
    # - https://www.geoplugin.com/
    r = requests.get('http://www.geoplugin.net/json.gp')

    if (r.status_code != 200):
        print('Não foi possivel obter a localização.')
        return None
    else:
        try:
            location = json.loads(r.text)    #transformado em um dicionario
            coords = {}
            coords['lat'] = location['geoplugin_latitude']
            coords['long'] = location['geoplugin_longitude']
            return coords
        except:
            return None
    
    
def getCodLocation(lat, long):
    LocationAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/" \
                     + "search?apikey=" + accuweatherAPIKey \
                     + "&q=" + lat + "%2C" + long + "&language=pt-BR"
                     
    r = requests.get(LocationAPIUrl)
    if (r.status_code != 200):
        print('Não foi possivel obter a localização.')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocation = {}
            infoLocation['nameLocation'] = locationResponse['ParentCity']['LocalizedName'] + ", " \
                        + locationResponse['AdministrativeArea']['LocalizedName'] + ". " \
                        + locationResponse['Country']['LocalizedName']
            infoLocation['codLocation'] = locationResponse['Key']
            return infoLocation
        except:
            return None


def getCurrentTime(codLocation, nameLocation):
    
    CurrentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" \
                            + codLocation + "?apikey=" + accuweatherAPIKey + "&language=pt-BR"
        
    r = requests.get(CurrentConditionsAPIUrl)
    if (r.status_code != 200):
        print('Não foi possivel obter o clima atual.')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            infoWeather = {}
            infoWeather['textWeather'] = CurrentConditionsResponse[0]['WeatherText']
            infoWeather['temperature'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            infoWeather['nameLocation'] = nameLocation
            return infoWeather
        except:
            return None


def getForecast5days(codLocation):
    
    DailyAPIUrl = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" \
                + codLocation + "?apikey=" + accuweatherAPIKey + "&language=pt-br&metric=True"
    
        
    r = requests.get(DailyAPIUrl)
    if (r.status_code != 200):
        print('Não foi possivel obter o clima atual.')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoWeather5days = []
            for day in DailyResponse['DailyForecasts']:
                weatherDay = {}
                weatherDay['max'] = day['Temperature']['Maximum']['Value']
                weatherDay['min'] = day['Temperature']['Minimum']['Value']
                weatherDay['weather'] = day['Day']['IconPhrase']
                dayweek = int(date.fromtimestamp(day['EpochDate']).strftime("%w"))
                weatherDay['day'] = days_week[dayweek]
                infoWeather5days.append(weatherDay)
            return infoWeather5days
        except:
            return None
        
def showForecast(lat, long):
    try:
        local = getCodLocation(coords['lat'], coords['long'])
        weatherCurrent = getCurrentTime(local['codLocation'], local['nameLocation'])

        print('Clima atual em: ' + weatherCurrent['nameLocation'])
        print(weatherCurrent['textWeather'])
        print('Temperatura: ' + str(weatherCurrent['temperature']) + "\xb0" + "C")
    except:
        print('\nErro ao obter o clima atual.\n')
        
    opcao= input('\nDeseja ver previsao para os proximos dias? (s ou n): ').lower()
    
    if opcao == "s":
        print('\nClima para hoje e para os próximos 5 dias:\n')
        try:
            forecast5days = getForecast5days(local['codLocation'])
            for day in forecast5days:
                print(day['day'])
                print('Mínima: ' + str(day['min']) + "\xb0" + "C")
                print('Máxima: ' + str(day['max']) + "\xb0" + "C")
                print('Clima: ' + day['weather'])
                print('---------------------------------')
        except:
            print('\nErro ao obter a previsão para os proximos dias.\n')
        
def searchLocal(local):
    _local = urllib.parse.quote(local)
    mapboxGeocodeUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/" \
                    + _local + ".json?access_token=" + mapboxToken

    r = requests.get(mapboxGeocodeUrl)
    if (r.status_code != 200):
        print('Não foi possivel obter o clima atual.')
        return None
    else:
        try:
            MapboxResponse = json.loads(r.text)
            coords = {}
            coords['long'] = str( MapboxResponse['features'][0]['geometry']['coordinates'][0] )
            coords['lat'] = str( MapboxResponse['features'][0]['geometry']['coordinates'][1] )
            return coords
        except:
            return None
            
    
try:
    coords = getCoords()
    showForecast(coords['lat'], coords['long'])
    coords = searchLocal("São Paulo")
    
    continuar = "s"
    while continuar == "s":
        continuar = input("\nDeseja consultar a previsão de outro local? (s ou n): ").lower()
        if continuar != "s":
            break
        local = input('\nDigite a cidade e o estado: ')
        try:
            coords = searchLocal(local)
            showForecast(coords['lat'], coords['long'])
        except:
            print('Não foi possivel obter previsao para este local.')
        
except:
    print('Erro ao processar a solicitação. Entre em contato com o suporte.')