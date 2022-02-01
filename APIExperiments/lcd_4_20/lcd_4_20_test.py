# loading the class
import lcddriver
from time import *

# lcd start
lcd = lcddriver.lcd()

# this command clears the display (captain obvious)
lcd.lcd_clear()

# now we can display some characters (text, line)
lcd.lcd_display_string("   Hello world !", 1)
lcd.lcd_display_string("      I am", 2)
lcd.lcd_display_string("        a", 3)
lcd.lcd_display_string("   Raspberry Pi !", 4)