import time
import board
import adafruit_dht

# Set up the DHT11 sensor
dht11 = adafruit_dht.DHT11(board.D4)

while True:
    try:
        # Read temperature and humidity
        temperature = dht11.temperature
        humidity = dht11.humidity
        
        # Print the results
        print(f"Temp: {temperature} °C, Humidity: {humidity}%")
        
    except RuntimeError as error:
        # Errors happen fairly often with DHT sensors, just retry after a while
        print(f"Error reading data: {error.args[0]}")
        time.sleep(2.0)
        continue
        
    time.sleep(2.0)
