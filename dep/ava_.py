import os
import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import requests
import json
from formulas import *

with open('.secrets/token.json') as f:
    token = json.load(f)

TOKEN = token['token']
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{client.user} has connected.')

@bot.command()
async def test(ctx):
    await ctx.send('Hello!')

@bot.command()
async def weather(ctx, location = '07024'):
    #Retrieve API key
    with open('.secrets/APIs.json') as f:
        APIs = json.load(f)
    API_KEY = APIs['weather']
    #Format url with key, optional zipcode argument
    url = 'http://api.weatherapi.com/v1/forecast.json?key='+API_KEY+'&q='+location+'&days=3&aqi=no'
    response = requests.get(url)
    #Return response as json
    data = response.json()
    
    #Set json variables
    current_weather = data['current']
    daily_weather = data['forecast']['forecastday'][0]['day']
    
    #Instantiate variable for current UV index note
    uv_index_now = ''
    #Set UV index note
    if current_weather['uv'] < 3:
        uv_index_now = 'low'
    elif current_weather['uv'] in list(range(3,6)):
        uv_index_now = 'moderate'
    elif current_weather['uv'] in list(range(6,9)):
        uv_index_now = 'high'
    elif current_weather['uv'] in list(range(9,11)):
        uv_index_now = 'very high'
    else:
        uv_index_now = 'extremely high'

    #Duplicate above process for daily forecast
    uv_index_day = ''
    if daily_weather['uv'] < 3:
        uv_index_day = 'low'
    elif daily_weather['uv'] in list(range(3,6)):
        uv_index_day = 'moderate'
    elif daily_weather['uv'] in list(range(6,9)):
        uv_index_day = 'high'
    elif daily_weather['uv'] in list(range(9,11)):
        uv_index_day = 'very high'
    else:
        uv_index_day = 'extremely high'
    
    #Check for rain or snow
    weather_event = ''
    if daily_weather['daily_will_it_rain'] == 1 and daily_weather['daily_will_it_snow'] == 1:
        weather_event = 'Be careful today! Rain and Snow expected!'
    elif daily_weather['daily_will_it_rain'] == 1:
        weather_event = f"{daily_weather['daily_chance_of_rain']}% chance of rain"
    elif daily_weather['daily_will_it_snow'] == 1:
        weather_event = f"{daily_weather['daily_chance_of_snow']}% chance of snow"
    else:
        weather_event = 'No rain or snow expected today'
    
    #Send all weather data
    await ctx.send(f'''Here's today's forecast for {data['location']['name']}, {data['location']['region']}:
    
Right now it is {current_weather['condition']['text'].lower()} with:
    Temperature: {current_weather['temp_f']}F / {current_weather['temp_c']}C
    Feels like: {current_weather['feelslike_f']}F / {current_weather['feelslike_c']}C
    Humidity is: {current_weather['humidity']}%
    
    UV index is {uv_index_now} at: {current_weather['uv']}
    Cloud coverage is {current_weather['cloud']}%
    Wind Speed is {current_weather['wind_mph']}mph with {current_weather['gust_mph']}mph gusts
        
Overall, {daily_weather['condition']['text'].lower()} today with:
    {weather_event}
    High of: {daily_weather['maxtemp_f']}F / {daily_weather['maxtemp_c']}C
    Low of: {daily_weather['mintemp_f']}F / {daily_weather['mintemp_c']}C
    UV index is {uv_index_day} at: {daily_weather['uv']}
    Avg humidity will be: {daily_weather['avghumidity']}

Here is your hourly forecast:''')
    
    #Graph hourly weather data
    columns = ['time', 'temp_f', 'feelslike_f', 'chance_of_rain', 'chance_of_snow']
    hourly_forecast = pd.DataFrame(data['forecast']['forecastday'][0]['hour'])[columns]
    #Alter data to only display hour
    hourly_forecast['time'] = hourly_forecast['time'].map(lambda x: x[-5:-3])
    #Change percent chance of rain or snow from string to float
    hourly_forecast = hourly_forecast.astype({'chance_of_rain': np.float,
                                              'chance_of_snow': np.float})
    #Set seaborn theme and stacked graphs
    sns.set_theme()
    fig, ax = plt.subplots(figsize = (10,5))
    ax.plot(hourly_forecast['time'],
            hourly_forecast['temp_f']
           )
    ax.plot(hourly_forecast['time'],
            hourly_forecast['feelslike_f']
           )

    ax.plot(hourly_forecast['time'],
            hourly_forecast['chance_of_rain'],
            '--',
            color = 'c'
           )
    ax.plot(hourly_forecast['time'],
            hourly_forecast['chance_of_snow'],
            '-.',
            color = 'slategrey'
           )

    ax.set_yticks(list(range(0,100,10)))
    ax.legend(['Actual Temp', 'Feels Like', 'Chance of Rain', 'Chance of Snow'])
    plt.suptitle(f'Hourly Forecast for {data["forecast"]["forecastday"][0]["date"]}')
    #Save graph
    plt.savefig('plot.jpg')
    file = discord.File('plot.jpg')
    #Send graph
    await ctx.send(file = file)

#client.run(TOKEN)
bot.run(TOKEN)