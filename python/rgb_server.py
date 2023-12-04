#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGB Server
==========

Bridge script from UDP to WS2812 RGB.
This is a simple script that listens to UDP data and outputs it through RPi hardware PWM.
Depending on your permissions, you might want/need to run this as root (or grant hardware rights).

2023-11-30 Bernhard "HotKey" Slawik
"""

import time
from rpi_ws281x import PixelStrip, Color
#import argparse

# LED strip configuration:
LED_COUNT = 16        # Number of LED pixels.
LED_PIN = 12          # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

import socket
#RGB_SERVER_ADDRESS = ('127.0.0.1', 61234)
RGB_SERVER_ADDRESS = ('0.0.0.0', 61234)

def put(t):
	print(t)

'''
# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i + q, color)
			strip.show()
			time.sleep(wait_ms / 1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i + q, 0)


def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256 * iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i + j) & 255))
		strip.show()
		time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256 * iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel(
				(int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i + q, wheel((i + j) % 255))
			strip.show()
			time.sleep(wait_ms / 1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i + q, 0)


# Main program logic follows:
if __name__ == '__main__':
	# Process arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
	args = parser.parse_args()

	# Create NeoPixel object with appropriate configuration.
	strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
	# Intialize the library (must be called once before other functions).
	strip.begin()
	print('Press Ctrl-C to quit.')
	if not args.clear:
		print('Use "-c" argument to clear LEDs on exit')
	try:
		while True:
			print('Color wipe animations.')
			colorWipe(strip, Color(255, 0, 0))  # Red wipe
			colorWipe(strip, Color(0, 255, 0))  # Green wipe
			colorWipe(strip, Color(0, 0, 255))  # Blue wipe
			print('Theater chase animations.')
			theaterChase(strip, Color(127, 127, 127))  # White theater chase
			theaterChase(strip, Color(127, 0, 0))  # Red theater chase
			theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
			print('Rainbow animations.')
			rainbow(strip)
			rainbowCycle(strip)
			theaterChaseRainbow(strip)

	except KeyboardInterrupt:
		if args.clear:
			colorWipe(strip, Color(0, 0, 0), 10)
'''

if __name__ == '__main__':
	# Process arguments
	#parser = argparse.ArgumentParser()
	#parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
	#args = parser.parse_args()
	
	# Create NeoPixel object with appropriate configuration.
	strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
	# Intialize the library (must be called once before other functions).
	strip.begin()
	
	
	# Create a UDP socket
	put('Binding server to %s...' % str(RGB_SERVER_ADDRESS))
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# Bind the socket to the port
	sock.bind(RGB_SERVER_ADDRESS)
	
	put('Press Ctrl-C to quit.')
	#if not args.clear:
	#	print('Use "-c" argument to clear LEDs on exit')
	
	try:
		while True:
			data, address = sock.recvfrom(4096)
			#put('RX from %s: (%d) %s' % (address, len(data), data))
			put('RX from %s: (%d) bytes' % (address, len(data)))
			
			# Determine number of LEDs
			n = len(data) // 3
			n = min(LED_COUNT, n)
			for i in range(n):
				ii = i * 3
				
				# Re-map RGB
				#strip.setPixelColor(i, Color(data[ii], data[ii+1], data[ii+2]))
				strip.setPixelColor(i, Color(data[ii+1], data[ii+0], data[ii+2]))	# Works for Xmas-style WS2812-chain
			strip.show()
		
	except KeyboardInterrupt:
		#colorWipe(strip, Color(0, 0, 0), 10)
		pass
	
