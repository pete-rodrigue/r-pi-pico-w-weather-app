
# This script was written for CircuitPython, rather than MicroPython.

# Below, we load all the modules we'll need
# I try to just load the specific functions we'll use, not the whole module.
# This can help save memory on the pico.
import board
from digitalio import DigitalInOut, Direction
from audiomp3 import MP3Decoder
from audiopwmio import PWMAudioOut
from adafruit_requests import Session
from wifi import radio
from socketpool import SocketPool
from ssl import create_default_context
import busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
import gc
from os import getenv
from time import sleep


myzip = YOUR_ZIPCODE_GOES_HERE
EPA_api_key = 'YOUR AIRNOW.GOV API KEY GOES HERE!'

# configure the lcd screen; you'll need to put in whatever GPIO pins you plan to use
i2c = busio.I2C(board.GP7, board.GP6)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=2, num_cols=16)   # if you use a larger screen, you may need to change these values

# function to play mp3. The only arguement to the function is the name of the mp3 file.
def play_clip(mp3=''):
    decoder = MP3Decoder(open("/audio_clips/" + mp3 + ".mp3", "rb"))
    audio.play(decoder)
    while audio.playing:
        pass

# this function visits the worldtime API and returns a tuple w/ the hour and date
def getTime():
    time_request = request.get("http://worldtimeapi.org/api/timezone/America/New_York")
    data = time_request.json()
    hour = int(data['datetime'][11:13])
    date = data['datetime'][0:10]
    gc.collect()
    
    return (hour, date)


# this function visits the NOAA API and gets the current weather (in "period 0")
# the LWX and 96,73 bits refer to the grid I'm in. You'll need to replace those values with the grid
# values for your location. See the NOAA weather API for more details. 
def getWeather(url='https://api.weather.gov/gridpoints/LWX/96,73/forecast'):
    current_weather = request.get(url).json()['properties']['periods'][0]
    current_temp = current_weather['temperature']
    current_chance_rain = current_weather['probabilityOfPrecipitation']['value']
    current_wind_speed = current_weather['windSpeed']
    current_wind_direction = current_weather['windDirection']
    
    # "garbage collection" is a function i try to use throughout the code to free up memory
    gc.collect()
    
    return {'t': current_temp, 'cr': current_chance_rain, 'ws': current_wind_speed, 'wd':current_wind_direction}


# visit the AirNow.gov API and get the current AQI value. Return "good", "moderate", or "bad", depending on the value
# note that unlike the NOAA API, this API has a key. So you need to visit the AirNow.gov API website, sign up, and get a key.
def getAQI(myzip, date, EPA_api_key):
    url = 'https://www.airnowapi.org/aq/forecast/zipCode/?format=application/json&zipCode={}&date={}&distance=1&API_KEY={}'.format(myzip, date, EPA_api_key)
    aqi = request.get(url).json()[0]['AQI']
    if aqi <= 50:
        return 'good'
    elif 50 < aqi <= 100:
        return 'moderate'
    else:
        return 'bad'

## try/catch statement to connect to your wifi
# note that we don't store our wifi password in the actual code; we store it in settings.toml
try:
    print("Attemping to connect to WiFi named " + getenv('CIRCUITPY_WIFI_SSID'))
    radio.connect(getenv('CIRCUITPY_WIFI_SSID'), getenv('CIRCUITPY_WIFI_PASSWORD'))
    print('success')
except Exception as e:
    print("Error:\n", str(e))
    print("Failed to connect to WiFi; Resetting microcontroller in 10 seconds")
    sleep(10)
    microcontroller.reset()
    
    
# configure the motion sensor pins and LED pins.
# the LED will turn on when the pir sensor notices movement.
pir = DigitalInOut(board.GP18)
pir.direction = Direction.INPUT
led = DigitalInOut(board.GP15)
led.direction = Direction.OUTPUT
# configure the audio output
audio = PWMAudioOut(board.GP13)

# start with the backlight on the LCD set to off
lcd.set_backlight(0)

while True:
    if pir.value:                                 # if we notice movement...
        print("Motion detected. Hello there!")
        led.value = True                          # turn on the LED
        lcd.set_backlight(1)                      # turn on the LCD backlight
        # start a new http session:
        pool = SocketPool(radio)
        request = Session(pool, create_default_context())
        
        # get the current hour of the day:
        #print('getting time...')
        hour, date = getTime()
        gc.collect()
        
        if hour > 23 or hour < 5:
            pass  # do nothing if it's just the middle of the night. Don't want to wake the neighbors with talking microchips
        else:
            # get the current weather, using NOAA weather API
            #print('getting weather from NOAA API...')
            weather_data = getWeather()
            gc.collect()
            
            # depending on the % chance of rain and temperature, play 1 of 4 audio clips that says the forecast:
            if int(weather_data['t']) < 50 and int(0 if weather_data['cr'] is None else weather_data['cr']) < 20:
                play_clip('cold and dry')   
            elif int(weather_data['t']) < 50 and int(0 if weather_data['cr'] is None else weather_data['cr']) >= 20:
                play_clip('cold and rainy')  
            elif int(weather_data['t']) >= 50 and int(0 if weather_data['cr'] is None else weather_data['cr']) < 20:
                play_clip('warm and dry') 
            else:
                play_clip('warm and rainy') 
             
            
            gc.collect()
                
            # get the AQI
            #print('getting AQI from AirNow.gov API...')
            aqi = getAQI(myzip, date, EPA_api_key)
            gc.collect()
            
            
            # on the LCD screen, loop through the different weather facts a few times, so we can read them:
            for i in range(6):
                lcd.print('Temp: ' + str(weather_data['t']) + 'F')
                sleep(6)
                lcd.clear()
                lcd.print('Wind:' + str(weather_data['ws']) + str(weather_data['wd']))
                sleep(6)
                lcd.clear()
                lcd.print('Rain:' + str(0 if weather_data['cr'] is None else weather_data['cr']) + '%\nAQI:' + str(aqi))
                sleep(6)
                lcd.clear()
                
            # then turn off the LED...    
            led.value = False
            
        # and go to sleep for 20 minutes!
        print('\nProvided the data, now sleeping for 20 minutes')
        sleep(5)
        lcd.clear()
        lcd.set_backlight(0)
        sleep(20*60)
        




