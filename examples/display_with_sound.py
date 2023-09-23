#!/usr/bin/env python3
import sys
import time
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#import RPi.GPIO as GPIO
import os
 
phrase = 'Проигрывание'
p01 = subprocess.Popen(['espeak','--voices=[ru]' ,'-ven-m1', '-a50', phrase])

import ST7789
from netifaces import interfaces, ifaddresses, AF_INET
ipLine = '' 
for ifaceName in interfaces():
    if ifaceName == 'eth0' or ifaceName == 'wlan0':
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        ipLine += ' ' + ifaceName + ':' + ' '.join(addresses)
print (ipLine)

display_type = "square"
    
#below 5 lines are moved to independent module
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(26, GPIO.OUT)
#GPIO.output(26, GPIO.LOW)
# time.sleep(0.1)
#GPIO.output(26, GPIO.HIGH)

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

WIDTH = disp.width
HEIGHT = disp.height


# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
# Get a PIL Draw object to start drawing on the display buffer.
#img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 0, 0))
# img_Ha = Image.open('Ha_240_240_2.png')
# img_I = Image.open('I_240_240_2.png')
img_A_H = Image.open('/home/pi/Desktop/ST7789/examples/Emo/A-H.jpeg')
img_C_I = Image.open('/home/pi/Desktop/ST7789/examples/Emo/C-I.jpeg')
img_E_G_J = Image.open('/home/pi/Desktop/ST7789/examples/Emo/E-G-J.jpeg')
img_F_V_W_S_Z = Image.open('/home/pi/Desktop/ST7789/examples/Emo/F-V-W-S-Z.jpeg')
img_K_R_X = Image.open('/home/pi/Desktop/ST7789/examples/Emo/K-R-X.jpeg')
img_M_P_B = Image.open('/home/pi/Desktop/ST7789/examples/Emo/M-P-B.jpeg')
img_N_L_D_T = Image.open('/home/pi/Desktop/ST7789/examples/Emo/N-L-D-T.jpeg')
img_O = Image.open('/home/pi/Desktop/ST7789/examples/Emo/O.jpeg')
img_U_Y = Image.open('/home/pi/Desktop/ST7789/examples/Emo/U-Y.jpeg')

#draw = ImageDraw.Draw(img)

# Draw a purple rectangle with yellow outline.
#draw.rectangle((10, 10, WIDTH - 10, HEIGHT - 10), outline=(255, 255, 0), fill=(255, 0, 255))

# Draw some shapes.
# Draw a blue ellipse with a green outline.
#draw.ellipse((10, 10, WIDTH - 10, HEIGHT - 10), outline=(0, 255, 0), fill=(0, 0, 255))

# Draw a white X.
#draw.line((10, 10, WIDTH - 10, HEIGHT - 10), fill=(255, 255, 255))
#draw.line((10, HEIGHT - 10, WIDTH - 10, 10), fill=(255, 255, 255))

# Draw a cyan triangle with a black outline.
#draw.polygon([(WIDTH / 2, 10), (WIDTH - 10, HEIGHT - 10), (10, HEIGHT - 10)], outline=(0, 0, 0), fill=(0, 255, 255))

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 16)
# Define a function to create rotated text.  Unfortunately PIL doesn't have good
# native support for rotated fonts, but this function can be used to make a
# text image and rotate it so it's easy to paste in the buffer.
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


# Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
#draw_rotated_text(img, 'Hello World!', (0, 0), 90, font, fill=(0, 0, 0))
for i in range(len(phrase)):
    time.sleep(0.015)
    img = img_A_H
    if 'CI'.find(phrase[i].upper()) >=0 : img = img_C_I
    if 'EGJ'.find(phrase[i].upper()) >=0 : img = img_E_G_J
    if 'FVWSZ'.find(phrase[i].upper()) >=0 : img = img_F_V_W_S_Z
    if 'KRX'.find(phrase[i].upper()) >=0 : img = img_K_R_X
    if 'MPB'.find(phrase[i].upper()) >=0 : img = img_M_P_B
    if 'NLDT'.find(phrase[i].upper()) >=0 : img = img_N_L_D_T
    if 'O'.find(phrase[i].upper()) >=0 : img = img_O
    if 'UY'.find(phrase[i].upper()) >=0 : img = img_U_Y
    #draw_rotated_text(img, ipLine, (10, HEIGHT - 10), 0, font, fill=(255, 255, 255))
    # Write buffer to display hardware, must be called to make things visible on the
    # display!
    disp.display(img)

img = img_K_R_X
draw_rotated_text(img, ipLine, (10, HEIGHT - 10), 0, font, fill=(255, 255, 255))
disp.display(img)