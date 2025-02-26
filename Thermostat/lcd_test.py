import smbus2
from RPLCD.i2c import CharLCD

# Configure the LCD
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)

# Clear any previous content
lcd.clear()

# Display text on the LCD
lcd.write_string('Welcome Laerson!')

# Move to the second row
lcd.cursor_pos = (1, 0)
lcd.write_string('Seja bem vindo!!')
