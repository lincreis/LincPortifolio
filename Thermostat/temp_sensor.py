import time
import board
import adafruit_dht
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

# Initialize DHT11 sensor
dht11 = adafruit_dht.DHT11(board.D17)

# Initialize I2C LCD (make sure the address is correct)
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)

# Set up GPIO for PIR motion sensor
PIR_PIN = 12  # GPIO pin for the PIR sensor
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(PIR_PIN, GPIO.IN)  # Set PIR pin as input

# Custom characters for happy face, sad face, right arrow, up arrow, down arrow, and OK sign
happy_face = [
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b00000,
    0b10001,
    0b01110,
    0b00000,
]

sad_face = [
    0b00000,
    0b01010,
    0b01010,
    0b00000,
    0b00000,
    0b01110,
    0b10001,
    0b00000,
]

right_arrow = [
    0b00000,
    0b00000,
    0b00100,
    0b00010,
    0b11101,
    0b00010,
    0b00100,
    0b00000
]

up_arrow = [
    0b01111,
    0b00011,
    0b00101,
    0b01001,
    0b10000,
    0b00111,
    0b00010,
    0b00010,
]

down_arrow = [
    0b00111,
    0b00010,
    0b00010,
    0b10000,
    0b01001,
    0b00101,
    0b00011,
    0b01111
]

ok_sign = [
    0b01000,
    0b10100,
    0b10100,
    0b01000,
    0b00000,
    0b00101,
    0b00110,
    0b00101
]

# Load custom characters into LCD memory
lcd.create_char(0, happy_face)
lcd.create_char(1, sad_face)
lcd.create_char(2, right_arrow)
lcd.create_char(3, up_arrow)
lcd.create_char(4, down_arrow)
lcd.create_char(5, ok_sign)

# Function to display test characters
def test_characters():
    lcd.backlight_enabled = True
    lcd.clear()
    
    # Show "Reading" on top row and "Temp..." on bottom row
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Reading")
    lcd.cursor_pos = (1, 0)
    lcd.write_string("Temperature...")
    
    time.sleep(1)

    # Show all custom characters
    for i in range(6):
        lcd.cursor_pos = (1, 15)  # Show arrows on the last column
        lcd.write_string(chr(i))  # Display custom character
        time.sleep(0.5)

# Initialize last valid readings and trend tracking
last_temp = None
last_hum = None
last_trend_check_time = time.time()
previous_temp = None  # Initialize previous_temp
trend = 'stable'  # Default trend

# Variables to store the last displayed values to avoid unnecessary LCD updates
last_displayed_temp = None
last_displayed_hum = None
last_displayed_trend = None

def display_on_lcd(temp, hum, trend):
    global last_displayed_temp, last_displayed_hum, last_displayed_trend

    # Only update the LCD if the values or trend changed
    if temp != last_displayed_temp or hum != last_displayed_hum or trend != last_displayed_trend:
        lcd.clear()

        # Display temperature on the first row
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f'Temp: {temp:.1f}F')

        # Display humidity on the second row with abbreviation
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f'Humi: {hum:.1f}%')

        # Display trend arrow in the fourth column from the right
        lcd.cursor_pos = (0, 12)  # Adjust column for trend arrow
        if trend == 'stable':
            lcd.write_string(chr(2))  # Right arrow
        elif trend == 'rising':
            lcd.write_string(chr(3))  # Up arrow
        elif trend == 'lowering':
            lcd.write_string(chr(4))  # Down arrow

        # Show happy or sad face based on humidity range
        if 40 <= hum <= 60:
            lcd.cursor_pos = (1, 12)  # Bottom-right position
            lcd.write_string(chr(0))  # Happy face
        else:
            lcd.cursor_pos = (1, 12)  # Bottom-right position
            lcd.write_string(chr(1))  # Sad face

        # Update the last displayed values
        last_displayed_temp = temp
        last_displayed_hum = hum
        last_displayed_trend = trend

# Function to get readings
def get_readings():
    global last_temp, last_hum, last_trend_check_time, trend, previous_temp

    try:
        temperature = (dht11.temperature * 9/5) + 32  # Convert to Fahrenheit
        humidity = dht11.humidity

        if temperature is not None and humidity is not None:
            # Update last valid readings
            last_temp = temperature
            last_hum = humidity
            
            print(f'Readings: Temp: {temperature:.1f}F, Humidity: {humidity:.1f}%, Trend: {trend}')

            # Check trend every 10 minutes (600 seconds)
            if time.time() - last_trend_check_time >= 600:
                if previous_temp is not None:  # Use previous_temp for comparison
                    if temperature > previous_temp:
                        trend = 'rising'
                    elif temperature < previous_temp:
                        trend = 'lowering'
                    else:
                        trend = 'stable'
                
                previous_temp = last_temp  # Update previous_temp with the last valid reading
                last_trend_check_time = time.time()  # Update last trend check time

        else:
            print("Invalid data received; using last valid readings.")

    except RuntimeError as error:
        print(f"Error reading data: {error.args[0]}. Using last valid readings.")

    # Use last valid readings if the current readings are invalid
    if last_temp is not None and last_hum is not None:
        display_on_lcd(last_temp, last_hum, trend)

# Main loop
test_characters()  # Test characters at start

lcd.backlight_enabled = False  # Start with backlight off

try:
    while True:
        get_readings()
        
        if GPIO.input(PIR_PIN):  # Check if motion is detected
            lcd.backlight_enabled = True  # Turn on backlight
            print("Motion detected! Turning on LCD backlight.")
            time.sleep(60)  # Keep the backlight on for 60 seconds
        else:
            lcd.backlight_enabled = False  # Turn off backlight
            print("No motion detected. Turning off LCD backlight.")

        time.sleep(1)  # Wait before the next cycle
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()  # Clean up GPIO on exit
