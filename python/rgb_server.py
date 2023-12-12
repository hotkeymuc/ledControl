#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGB Server
==========

Bridge script from UDP to WS2812 RGB.
This is a simple script that listens to UDP data and outputs it through RPi hardware PWM.
Depending on your permissions, you might want/need to run this script as root (or grant GPIO hardware access rights).

The user-land client only needs to do this:
	RGB_SERVER_ADDRESS = ('127.0.0.1', 61234)
	
	rgb_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	
	data = bytes([r,g,b, r,g,b, ... ])
	rgb_socket.sendto(data, RGB_SERVER_ADDRESS)


2023-11-30 Bernhard "HotKey" Slawik
"""

import time
import argparse
#from rpi_ws281x import PixelStrip, Color

# Defaults (can be set via arguments)
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
	parser = argparse.ArgumentParser(description='Receive RGB data through UDP and output it via RPi GPIO/PWM')
	parser.add_argument('-n', '--num', type=int, default=LED_COUNT, help='Number of LEDs')
	parser.add_argument('-g', '--gpio', type=int, default=LED_PIN, help='GPIO to use')
	parser.add_argument('-f', '--frq', type=int, default=LED_FREQ_HZ, help='Frequency (Hz)')
	parser.add_argument('-d', '--dma', type=int, default=LED_DMA, help='DMA to use')
	parser.add_argument('-i', '--invert', action='store_true', help='Inverted data (e.g. NPN-transistor)')
	parser.add_argument('-c', '--chan', type=int, default=LED_CHANNEL, help='PWM channel to use')
	parser.add_argument('-b', '--brightness', type=int, default=LED_BRIGHTNESS, help='Brightness (0..255)')
	parser.add_argument('-a', '--address', type=str, default=RGB_SERVER_ADDRESS[0], help='Address to bind to')
	parser.add_argument('-p', '--port', type=int, default=RGB_SERVER_ADDRESS[1], help='Port to bind to')
	parser.add_argument('-v', '--verbose', action='store_true', help='Show when data is incoming')
	#parser.add_argument('-x', '--clear', action='store_true', help='Clear the strip on exit')
	args = parser.parse_args()
	
	# Copy args over to vars
	LED_COUNT = args.num
	LED_PIN = args.gpio
	LED_FREQ_HZ = args.frq
	LED_DMA = args.dma
	LED_INVERT = args.invert
	LED_CHANNEL = args.chan
	LED_BRIGHTNESS = args.brightness
	RGB_SERVER_ADDRESS = (args.address, args.port)
	VERBOSE = args.verbose
	
	# Create NeoPixel object with appropriate configuration.
	put('Creating RGB strip (num=%d)...' % LED_COUNT)
	from rpi_ws281x import PixelStrip, Color
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
			if VERBOSE: put('RX from %s: (%d) bytes' % (address, len(data)))
			
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
	
