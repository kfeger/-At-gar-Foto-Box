#!/usr/bin/python
#  -*- coding: utf-8 -*-
#
# ottO's Twitter-CeBIT-Box
# based on....
# tweetpic.py take a photo with the Pi camera and tweet it
# by Alex Eames http://raspi.tv/?p=5918

#
#
import tweepy
import time
import picamera
import RPi.GPIO as GPIO
from subprocess import call
from datetime import datetime
import Adafruit_SSD1306
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
import atexit
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import random

# 24" SMI LG
#HDMIwidth = 1680
#HDMIheight = 1050
# 22" Acer zuhause
HDMIwidth = 1440
HDMIheight = 900
# Der kleine
#HDMIwidth = 1024
#HDMIheight = 768
PrevMsgIndex = 99


def Set_Trigger(channel):
	global Trigger
	TriggerCounter=0
	while GPIO.input(channel) == GPIO.LOW :
		TriggerCounter=TriggerCounter+1
		time.sleep(0.1)
		if (TriggerCounter > 1):
			break
	if (TriggerCounter >= 1):
		print("TriggerCounter = " + str(TriggerCounter))
		Trigger = 1

def exit_handler(channel):
	time.sleep(0.5)
	ExitCounter=0
	while GPIO.input(channel) == GPIO.LOW :
		ExitCounter=ExitCounter+1
		time.sleep(0.1)
		if (ExitCounter > 20):
			break
	if (ExitCounter >= 20):
		print("ExitCounter = " + str(ExitCounter))
		print('Programm beendet')
		draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
		draw.text((0, 12), "tweet.py:",  font=font, fill=255)
		draw.text((0, 32), "Ende....",  font=font, fill=255)
		OLED.image(OLEDimage)
		OLED.display()
		RGBLed.set_pixel_rgb(0, 0, 0, 0)
		RGBLed.show()
		GPIO.cleanup()
		sys.exit()

def Shoot_Photo(channel):
	global Trigger
	Trigger = 1
	print("Trigger = " + str(Trigger))
	
def Shaking(channel):
	if (Trigger == 0):
		print("Es wackelt")
		BeepBuzzer(1)
	
def BeepBuzzer(BeepTime):
	GPIO.output(BuzzerPin, GPIO.HIGH)
	time.sleep(BeepTime)
	GPIO.output(BuzzerPin, GPIO.LOW)

def Tweet_It(PhotPath):
	global PrevMsgIndex
	if PickAccount == 0:
		# first Account
		consumer_key = 'very long token'
		consumer_secret = 'even longer secret'
		access_token = 'very long token'
		access_token_secret = 'even longer secret'
	else:
		# second Account
		consumer_key = 'very long token'
		consumer_secret = 'even longer secret'
		access_token = 'very long token'
		access_token_secret = 'even longer secret'

		# OAuth process, using the keys and tokens
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	MsgIndex = random.randint(0, MsgNum-1)
	#keine zwei gleichen Messages hintereinander
	while MsgIndex == PrevMsgIndex:
		MsgIndex = random.randint(0, MsgNum-1)
	PrevMsgIndex = MsgIndex
	print ('MsgNum = ' + str(MsgNum))
	print ('MsgIndex = ' + str(MsgIndex))

	# Creation of the actual interface, using authentication
	api = tweepy.API(auth)

	# Send the tweet with photo
	#photo_path = '/home/pi/twitter.png'
	#status = 'Besucher-Tweet von der CeBIT 2017 am ' + i.strftime('%d.%m.%Y um %H:%M:%S')
	status = Message[MsgIndex]
	api.update_with_media(PhotPath, status=status)

def shut_it_down(channel):
	time.sleep(0.5)
	counter=0
	while GPIO.input(channel) == GPIO.LOW :
		counter=counter+1
		time.sleep(0.1)
		if (counter > 50):
			break

	if (counter >= 50): 
		print("counter = " + str(counter))
		print("Fahre runter...") 
		GPIO.remove_event_detect(ShutDownPin)
		draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
		draw.text((0, 12), "Raspberry:",  font=font, fill=255)
		draw.text((0, 32), "Shutdown",  font=font, fill=255)
		OLED.image(OLEDimage)
		OLED.display()
		RGBLed.set_pixel_rgb(0, 255, 255, 255)
		RGBLed.show()
		time.sleep(3)
		BeepBuzzer(0.05)
		RGBLed.set_pixel_rgb(0, 0, 0, 0)
		RGBLed.show()
		os.system("sudo shutdown now -h")
    	
	else:
		print("Press longer to shutdown!")
		print(str(counter) + "counter")
		reset_event_detection_shutdown()

def reset_event_detection_shutdown():
	time.sleep(0.5)
	GPIO.remove_event_detect(ShutDownPin)
	time.sleep(0.1)
	GPIO.add_event_detect(ShutDownPin, GPIO.FALLING, callback=shut_it_down, bouncetime=300)
	
def Movement(channel):
	global Moving
	if GPIO.input(PIRPin) == GPIO.HIGH :
		Moving = 1
	else :
		Moving = 0

#IO-Ports definieren
BuzzerPin = 4
BannerPin = 24
RemotePin = 18
SparePin = 23
ShutDownPin = 27
ProgEndPin = 12
AccountPin = 17
ShakerPin = 22
PIRPin = 8

Trigger = 0	
PickAccount = 0
PickBanner = 0

# Texte
Greet0 = 'Willkommen auf dem Stand des'
Greet1 = 'IT-Planungsrats der CeBIT 2017!'
Greet2 = 'Wenn Sie den roten Knopf drücken,'
Greet3 = 'wird Ihr Bild auf dem Twitter-Account'
Greet4 = '@eGovSachsen veröffentlicht'
TwText0 = 'Willkommen auf dem Stand'
TwText1 = 'des IT-Planungsrats'
TwText2 = 'in Halle 7 der CeBIT 2017!'

# Fonts
GreetFontpath = '/home/pi/fonts/Days.ttf'
TwFontpath = '/home/pi/fonts/Days.ttf'

# Bilder gehe nach ,,,,
BildPfad = '/home/pi/CeBIT/'
#PIR
PIRFlag = 0
Moving = 0
MovingPre = 1

# Programm Ende definieren
atexit.register(exit_handler, 1)

# 128x64 display with hardware I2C:
RST = 26
OLED = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# WS2801-LED
Bright = 32
SPI_PORT   = 0
SPI_DEVICE = 0
RGBLed_COUNT = 1
RGBLed = Adafruit_WS2801.WS2801Pixels(RGBLed_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Overlay Format
OFormat = 'rgba'
# Image Format
IFormat = 'RGBA'
# Alpha-Wert
AlphaSet = 0

#display initialisieren
OLED.begin()
#GPIO initialisieren
GPIO.setup(BannerPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(RemotePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(SparePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ShutDownPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ProgEndPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(ShakerPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(AccountPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PIRPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BuzzerPin, GPIO.OUT)
GPIO.add_event_detect(RemotePin, GPIO.RISING, callback = Shoot_Photo, bouncetime = 50)
GPIO.add_event_detect(ProgEndPin, GPIO.FALLING, callback = Set_Trigger, bouncetime = 2000)
GPIO.add_event_detect(ShutDownPin, GPIO.FALLING, callback=shut_it_down, bouncetime=300)
GPIO.add_event_detect(ShakerPin, GPIO.FALLING, callback = Shaking, bouncetime = 100)
GPIO.add_event_detect(PIRPin, GPIO.BOTH, callback = Movement, bouncetime = 100)

#Twitter-Texte

with open("texte", "r") as ins:
	Message = []
	for line in ins:
		Message.append(line)
		
MsgNum=len(Message)
print ('Es gibt ' + str(MsgNum) + ' Nachrichten')

MsgNum=len(Message)



# Clear display.
OLED.clear()
OLED.display()
# Image zum Schreiben erzeugen
OLEDimage = Image.new('1', (OLED.width, OLED.height))
draw = ImageDraw.Draw(OLEDimage)
font = ImageFont.truetype('fonts/Arial.ttf', 20)

# Bilder
TwitterName = '/home/pi/twitter.png'
FotoName = '/home/pi/cam.png'
photo_name_2 = '/home/pi/cam1.png'
sign_name = '/home/pi/sn.png'


# LED aus
RGBLed.clear()
RGBLed.show()  # Make sure to call show() after changing any RGBLeds!

# Account anzeigen
draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
draw.text((0, 12), "Account:",  font=font, fill=255)
if (GPIO.input(AccountPin) == 0):
	draw.text((0, 32), "ottOCebit",  font=font, fill=255)
	print ("Account: ottOCebit")
	PickAccount = 0
else:
	draw.text((0, 32), "eGovSachsen",  font=font, fill=255)
	print ("Account: eGovSachsen")
	PickAccount = 1
OLED.image(OLEDimage)
OLED.display()
time.sleep(2)

# Banner anzeigen
draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
draw.text((0, 12), "Banner:",  font=font, fill=255)
if (GPIO.input(BannerPin) == 0):
	draw.text((0, 32), "@gar",  font=font, fill=255)
	print ("Banner: @gar")
	PickBanner = 0
else:
	draw.text((0, 32), "SN Only",  font=font, fill=255)
	print ("Banner: SN Only")
	PickBanner = 1
OLED.image(OLEDimage)
OLED.display()
time.sleep(2)

with picamera.PiCamera() as camera:
	camera.hflip = True
	camera.vflip = True
	camera.resolution = (HDMIwidth, HDMIheight)
	camera.framerate = 30
	print (camera.awb_mode)
	camera.start_preview()
	
	# Logo-Handling für Display
	HDMIimage = Image.new(IFormat, (HDMIwidth, HDMIheight))
	if PickBanner == 1:
		logoNotAus = Image.open('/home/pi/SachsenUnten.png')
		logoNotAusWidth, logoNotAusHeight = logoNotAus.size
		MainHeight = HDMIheight - logoNotAusHeight
		HDMIimage.paste(logoNotAus, (0, 750), logoNotAus)
	else:
		logoNotAus = Image.open('/home/pi/SachsenUnten.png')
		Banner = Image.open("/home/pi/Banner.png")
		logoNotAusWidth = 1440
		logoNotAusHeight = 380
		MainHeight = HDMIheight - logoNotAusHeight
		HDMIimage.paste(Banner, (0, 0), Banner)
	overlay_renderer = None
	if not overlay_renderer:
		overlay_renderer = camera.add_overlay(HDMIimage.tobytes(),
		layer=3,
		size=HDMIimage.size,
		format = OFormat,
		alpha = AlphaSet);
	
	# Overlays vorbereiten
	# Taz
	logoTaz = Image.open('/home/pi/Taz.png')
	TazWidth, TazHeight = logoTaz.size
	TazImage = Image.new(IFormat, (TazWidth, TazHeight))
	TazImage.paste(logoTaz, (0, 0), logoTaz)
	# Arni
	logoArni = Image.open('/home/pi/Arni.png')
	ArniWidth, ArniHeight = logoArni.size
	ArniImage = Image.new(IFormat, (ArniWidth, ArniHeight))
	ArniImage.paste(logoArni, (0, 0), logoArni)
	# Thumbs-Up
	logoThumbs = Image.open('/home/pi/Thumbs.png')
	Thumbswidth, Thumbsheight = logoThumbs.size	
	THUMBimage = Image.new(IFormat, (Thumbswidth, Thumbsheight))
	THUMBimage.paste(logoThumbs, (0, 0), logoThumbs)
	#Twitter
	logoTwitter = Image.open('/home/pi/TwitterBird.png')
	Twitterwidth, Twitterheight = logoTwitter.size	
	TWITTERimage = Image.new(IFormat, (Twitterwidth, Twitterheight))
	TWITTERimage.paste(logoTwitter, (0, 0), logoTwitter)
	# Auge auf
	logoAuf = Image.open('/home/pi/AugeAuf.png')
	AufWidth, AufHeight = logoAuf.size	
	AufImage = Image.new(IFormat, (AufWidth, AufHeight))
	AufImage.paste(logoAuf, (0, 0), logoAuf)
	# Auge zu
	logoZu = Image.open('/home/pi/AugeZu.png')
	ZuWidth, ZuHeight = logoZu.size	
	ZuImage = Image.new(IFormat, (ZuWidth, ZuHeight))
	ZuImage.paste(logoZu, (0, 0), logoZu)

	EyeRenderer = camera.add_overlay(AufImage.tobytes(),
		layer=5,
		size=AufImage.size,
		format = OFormat,
		fullscreen = False,
		window = (0, 0, AufWidth, AufHeight),
		alpha = AlphaSet);

	
	
	while(1):
		print ("Bereit...")
		draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
		draw.text((0, 12), "tweet.py:",  font=font, fill=255)
		draw.text((0, 32), "Bereit...",  font=font, fill=255)
		OLED.image(OLEDimage)
		OLED.display()
		RGBLed.set_pixel_rgb(0, 0, 16, 0)
		RGBLed.show()

		# auf Klick warten
		LastMove = 0
		while Trigger == 0:
			if ((time.time() - LastMove) > 0.5):
				LastMove = time.time()
				if (Moving == 1):
					if (MovingPre == 0):
						MovingPre = 1
						EyeRenderer.update(AufImage.tobytes())
				else:
					if (MovingPre == 1):
						MovingPre = 0
						EyeRenderer.update(ZuImage.tobytes())
			time.sleep(0.01)

		i = datetime.now() #take time and date for filename
		now = i.strftime('%Y%m%d-%H%M%S')

		#Foto
		EyeRenderer = camera.add_overlay(AufImage.tobytes(),
			layer=5,
			size=AufImage.size,
			format = OFormat,
			fullscreen = False,
			window = (0, 0, AufWidth, AufHeight),
			alpha = AlphaSet);
		draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
		draw.text((0, 12), "picamera:",  font=font, fill=255)
		draw.text((0, 32), "Foto",  font=font, fill=255)
		OLED.image(OLEDimage)
		OLED.display()
		RGBLed.set_pixel_rgb(0, 16, 0, 0)
		RGBLed.show()
		print ("Foto aufnehmen")
		
		# Countdown Overlay
		DownCounter = 3
		while DownCounter > 0 :
			print (DownCounter)
			CountdownWidth = 32 * 5
			CountdownHeight = 16 * 15
			Countdown = Image.new(IFormat, (CountdownWidth, CountdownHeight))
			CountdownText = ImageDraw.Draw(Countdown)
			CountdownText.font = ImageFont.truetype(GreetFontpath, 200)
			Numwidth, Numheight = CountdownText.textsize(str(DownCounter), font=CountdownText.font)
			CountdownText.text((0, 0), (str(DownCounter)).decode('utf-8'), (255, 255, 255))
			DownCounter = DownCounter - 1
			NumRenderer = camera.add_overlay(Countdown.tobytes(),
				layer=4,
				size=Countdown.size,
				format = OFormat,
				fullscreen = False,
				window = (HDMIwidth - CountdownWidth, MainHeight/2 - CountdownHeight/2, CountdownWidth, CountdownHeight),
				alpha = 128);
			time.sleep(1)
			camera.remove_overlay(NumRenderer)
			
		# Foto machen und Foto-Overlay anzeigen
		# Blitz an
		print ('Click!')
		RGBLed.set_pixel_rgb(0, 255, 255, 255)
		RGBLed.show()
		camera.capture(FotoName, "png")
		# Blitz aus
		RGBLed.set_pixel_rgb(0, 10, 0, 6)
		RGBLed.show()
		if PickBanner == 1:
			ThumbRenderer = camera.add_overlay(ArniImage.tobytes(),
				layer=4,
				size=ArniImage.size,
				format = OFormat,
				fullscreen = False,
				window = (HDMIwidth/2, MainHeight/2, ArniWidth, ArniHeight),
				alpha = AlphaSet);
		else:
			ThumbRenderer = camera.add_overlay(THUMBimage.tobytes(),
				layer=4,
				size=THUMBimage.size,
				format = OFormat,
				fullscreen = False,
				window = (HDMIwidth/2 - 100, MainHeight/2 + 100 - Thumbsheight/2, Thumbswidth, Thumbsheight),
				alpha = AlphaSet);
		# Text
		# Branding
		print ("Banner aufbringen")
		draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
		draw.text((0, 12), "Branding:",  font=font, fill=255)
		draw.text((0, 32), "Banner",  font=font, fill=255)
		OLED.image(OLEDimage)
		OLED.display()

		TwitterImg = Image.open(FotoName).convert('RGBA')

		# make a blank image for the text, initialized to transparent text color
		TwTxt = Image.new('RGBA', TwitterImg.size, (255,255,255,0))
		width, height = TwitterImg.size
		if PickBanner == 1:
			BildUnten = Image.open('/home/pi/FotoUnten.png')
			BildUntenwidth, BildUntenheight = BildUnten.size
			TwitterImg.paste(BildUnten, (0, height - BildUntenheight), BildUnten)
		else:
			BildUnten = Image.open('/home/pi/BannerFoto.png')
			TwitterImg.paste(BildUnten, (0, 0), BildUnten)
			

		TwOut = Image.alpha_composite(TwitterImg, TwTxt)

		TwOut.save(TwitterName)
		TwOut.save(BildPfad + now + '_Gast.png', 'png')
		
		# Twitter
		# Twitter Overlay anzeigen
		camera.remove_overlay(ThumbRenderer)
		if PickBanner == 1:
			TwitterRenderer = camera.add_overlay(TazImage.tobytes(),
				layer=4,
				size=TazImage.size,
				format = OFormat,
				fullscreen = False,
				window = (HDMIwidth/2, MainHeight/2, TazWidth, TazHeight),
				alpha = AlphaSet);
		else:
			TwitterRenderer = camera.add_overlay(TWITTERimage.tobytes(),
				layer=4,
				size=TWITTERimage.size,
				format = OFormat,
				fullscreen = False,
				window = (HDMIwidth/2, MainHeight/2, Twitterwidth, Twitterheight),
				alpha = AlphaSet);

		print ("An Twitter senden")
		draw.rectangle((0,0,OLED.width, OLED.height), outline=0, fill=0)
		draw.text((0, 12), "Tweepy:",  font=font, fill=255)
		draw.text((0, 32), "Twitter!",  font=font, fill=255)
		OLED.image(OLEDimage)
		OLED.display()
		RGBLed.set_pixel_rgb(0, 0, 0, 16)
		RGBLed.show()
		Tweet_It(TwitterName)

		# Normales Overlay anzeigen
		camera.remove_overlay(TwitterRenderer),
		Trigger = 0
