#!/usr/bin/env python3
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import RPi.GPIO as GPIO
import ST7789
from netifaces import interfaces, ifaddresses, AF_INET
ipLine = '' 
for ifaceName in interfaces():
    if ifaceName == 'eth0' or ifaceName == 'wlan0':
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        ipLine += ' ' + ifaceName + ':' + ' '.join(addresses)
print (ipLine)

display_type = "square"
    
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, GPIO.LOW)
GPIO.output(26, GPIO.HIGH)

# Create ST7789 LCD display class.


disp = ST7789.ST7789(
    height= 240,
    rotation= 90,
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
#         cs=ST7789.BG_SPI_CS_BACK,
    dc=25,
    backlight=24,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz= 80 * 1000 * 1000,
    offset_left = 0,
    offset_top = 0
)

# Initialize display.
disp.begin()

HEIGHT = 240

img = Image.open('I_240_240_2.png')
# Load default font.
font = ImageFont.load_default()

def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)


draw_rotated_text(img, ipLine, (10, HEIGHT - 10), 0, font, fill=(255, 255, 255))
# Write buffer to display hardware, must be called to make things visible on the
# display!
disp.display(img)

