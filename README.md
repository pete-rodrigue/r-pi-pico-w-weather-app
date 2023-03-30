# r-pi-pico-w-weather-app
Little project that lets a raspberry pi pico W tell you the weather using both a speaker and an LCD screen when you walk by and trip a PIR sensor. Grabs the weather data from some free API services.

## About this little project

This little project was just a way for me to learn more about using Raspberry Pi boards. Here's what this project does:

* Hooks up a raspberry pi pico W to:
  * A pir motion sensor
  * an led (which turns on when the motion sensor has been tripped, just so we can tell when that's happened)
  * a 16 by 2 LCD screen
  * a small speaker with external power. 
* When the pi is powered on, it connects to the local WiFi network.
* When someone walks by the motion sensor, the pi turns on the LED.
* Then the pi visits http://worldtimeapi.org/ and grabs the current time in our timezone
* If it's not after midnight and before 5am, the pi visits the NOAA weather API (https://www.weather.gov/documentation/services-web-api) and the AirNow.gov API (https://docs.airnowapi.org/) to get the local weather forecast and the local Air Quality Index (AQI), respectively. 
* Then, depending on the weather forecast, the pi plays 1 of 4 audio mp3 files using the speaker. For example "Forecast: warm and rainy." There are only 4 simple forecast summaries, because the pi has limited storage space for mp3 files:
  * warm and rainy
  * warm and dry
  * cold and rainy
  * cold and dry
* Finally, the pi prints the weather and AQI to the LCD screen, and then goes to sleep for 20 minutes.

## What you will need
* a raspberry pi pico W
* a pir motion sensor
* an led (which turns on when the motion sensor has been tripped, just so we can tell when that's happened)
* a resistor that's about 300ohms (ish)
* a 16 by 2 LCD screen
* a small speaker with external power. 
