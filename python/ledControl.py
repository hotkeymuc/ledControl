#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
LED Control
===========

Python companion library to communicate with an Arduino/ESP running the ledControl sketch.

There are three means of communication available:
	* serial
	* udp
	* http
	
	+ ethernet (NetIO)
	+ mqtt

2014/2021 Bernhard "HotKey" Slawik
"""

import math
import time

#DEFAULT_NUM_LEDS = 30*9 + 1
DEFAULT_NUM_LEDS = 8

#USE_SERIAL = False
#DEFAULT_SERIAL_PORT = 'COM59'
DEFAULT_SERIAL_PORT = '/dev/ttyUSB0'
DEFAULT_SERIAL_BAUD = 115200	#1000000

#USE_UDP = False
#DEFAULT_UDP_HOST = '255.255.255.255' # :-D
DEFAULT_UDP_HOST = '192.168.4.137'
DEFAULT_UDP_PORT = 1329

#USE_HTTP = True
#http://192.168.4.138/raw?010101020202040404080808101010202020404040808080
DEFAULT_HTTP_URL = 'http://esp32led.fritz.box'
#DEFAULT_HTTP_URL = 'http://192.168.4.138'

import serial	# for serial communication
import socket	# for UDP communication
import requests	# for HTTP communication


# Transfer encoding
ENCODING_RAW = 0
ENCODING_BIT_MASK = 1
ENCODING_RLE = 2
ENCODING_DELTA = 3
ENCODING_PACK8 = 4


def put(txt):
	print('ledControl: ' + txt)


### FX Layers
DELIMITER = ','
class FxType:
	FX_BLACK = 0
	FX_SOLID = 1
	FX_RANDOM_DOTS = 2
	FX_SCROLL = 3
	FX_BLUR = 4
	FX_BLUR_DOWN = 5
	FX_RAINBOW_FILL = 6
	FX_NOISE_ADD = 7
	
class FxLayer:
	def __init__(self,
		fx=FxType.FX_BLACK,
		frameEach=1,
		frameOfs=0,
		
		numStart=-1,
		numCount=-1,
		
		params0=0, params1=0, params2=0, params3=0
		):
		self.fx = int(fx)
		self.frameEach = int(frameEach)
		self.frameOfs = int(frameOfs)
		
		self.numStart = int(numStart)
		self.numCount = int(numCount)
		
		self.params = [int(params0), int(params1), int(params2), int(params3)]
		
	def get_command(self, num):
		d = DELIMITER
		return 'f'\
			+ str(num) +d\
			+ str(self.fx) +d\
			+ str(self.frameEach) +d+ str(self.frameOfs) +d\
			+ str(self.numStart) +d+ str(self.numCount) +d\
			+ str(self.params[0]) +d+ str(self.params[1]) +d+ str(self.params[2]) +d+ str(self.params[3])\
			+ '\n'

class FxPreset:
	def __init__(self, name):
		self.name = name
		self.layers = []
		
	def addLayer(self, l):
		self.layers.append(l)
	
	def get_commands(self):
		d = DELIMITER
		r = 'x\n'
		i = 0
		for l in self.layers:
			r += l.get_command(i)
			
			# Just to be sure (UDP may fuck things up)
			r += ',0,0,0,0\n'
			i += 1
		return r

def generate_gradient(keys):
	g = []
	i0 = -1
	c0 = (0x00, 0x00, 0x00)
	for i1,c1 in keys.items():
		#put('from i=%d, c=%s	to	i=%d, c=%s' % (i0, c0, i1, c1))
		
		# Deltas
		id = i1 - i0
		cd = (
			c1[0]-c0[0],
			c1[1]-c0[1],
			c1[2]-c0[2]
		)
		
		# Go through
		for ii in range(id):
			i = i0 + 1 + ii
			c = (
				int(c0[0] + (ii+1)*(cd[0]/id)),
				int(c0[1] + (ii+1)*(cd[1]/id)),
				int(c0[2] + (ii+1)*(cd[2]/id))
			)
			#put('i=%d	c=%s' % (i, c))
			g.append(c)
		
		i0 = i1
		c0 = c1
		
	return g

### Communication

ORDER_RGB = 0
ORDER_RBG = 1
ORDER_GRB = 2
ORDER_GBR = 3
ORDER_BRG = 4
ORDER_BGR = 5
DEFAULT_ORDER = ORDER_RGB

class LED:
	def __init__(self, order=DEFAULT_ORDER):
		self.order = order
		self.color = [0.0, 0.0, 0.0]
		
		#self.last = [0.0, 0.0, 0.0]	# Store last INTERNAL value
		self.lastOut = [0,0,0]	# Store last OUTPUT value
		
		self.pos = [0.0, 0.0, 0.0]
	
	def set_direct_int(self, ints):
		self.color = (
			ints[0] / 255.0,
			ints[1] / 255.0,
			ints[2] / 255.0
		)
	
	def set_real(self, colPygame):
		"""Set using color-correction"""
		#correction = 3.0	#4.0
		#self.color = [math.pow(c / 255.0, correction) for c in colPygame]
		
		
		# 1:1
		self.color = (
			colPygame[0] / 255.0,
			colPygame[1] / 255.0,
			colPygame[2] / 255.0
		)
		
		"""
		# Nice and warm
		self.color = [
			math.pow(colPygame[0] / 255.0, 4.1),	#4),
			math.pow(colPygame[1] / 255.0, 4.5),	#3.5),
			math.pow(colPygame[2] / 255.0, 5)	# 5
		]
		"""
		
		"""
		self.color = [
			math.pow(colPygame[0] / 255.0, 0.4),
			math.pow(colPygame[1] / 255.0, 0.35),
			math.pow(colPygame[2] / 255.0, 0.6)
		]
		"""
	
	def get_bytes(self):
		
		#return [ int(max(0, min(255, math.floor(v * 255)))) for v in self.colors ]
		
		if self.order == ORDER_RGB:
			values = self.color
		elif self.order == ORDER_RBG:
			values = (self.color[0], self.color[2], self.color[1])
		elif self.order == ORDER_GRB:
			values = (self.color[1], self.color[0], self.color[2])
		elif self.order == ORDER_GBR:
			values = (self.color[1], self.color[2], self.color[0])
		elif self.order == ORDER_BRG:
			values = (self.color[2], self.color[0], self.color[1])
		elif self.order == ORDER_BGR:
			values = (self.color[2], self.color[1], self.color[0])
		
		return [ int(max(0, min(255, math.floor(v * 255)))) for v in values ]



class LEDControl:
	def __init__(self, num_leds=DEFAULT_NUM_LEDS, order=DEFAULT_ORDER, encoding=ENCODING_RAW):
		self.num_leds = num_leds
		self.encoding = encoding
		
		self.leds = []
		for i in range(self.num_leds):
			led = LED(order=order)
			self.leds.append(led)
		
	def send(self, data):
		#put('Sending command "' + data[:80] + '..."...')
		#put('Sending command (%d bytes)...' % len(data))
		
		put('No communication layer selected')
		
		if USE_HTTP:
			u = HTTP_URL + '/raw?'
			for d in data:
				#u += '%02x' % (ord(d))
				u += '%02x' % (d)
			put('HTTP: "%s"' % (u))
			try:
				r = requests.get(u)
			except Exception as e:
				put('Exception while transmitting via HTTP: %s' % str(e))
	
	def draw(self, screen):
		for led in self.leds:
			screen.fill(
				#color = led.get_bytes(),	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)],
				color = [ int(c*255) for c in led.color ],
				rect=(led.pos[0], led.pos[1], 4, 4)
			)
			
	def draw_last(self, screen):
		for led in self.leds:
			screen.fill(
				color = [led.lastOut[i] for i in range(3)],
				rect=(led.pos[0], led.pos[1] + screenSize[1]/2, 4, 4)
			)
	
	def transmit(self):
		"""Encode and send"""
		r = bytearray()
		
		# Header
		
		#r.append(ord('r'))	# command: RAW
		
		#r.append(self.num_leds >> 8)
		#r.append(self.num_leds % 256)
		#r.append(self.encoding)
		
		if self.encoding == ENCODING_RAW:
			### Encoding: RAW
			for led in self.leds:
				# Calculate output value(s)
				color = led.get_bytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
				for i,c in enumerate(color):	#range(3):
					#r.append(color[i])
					#r.append(color[i] + 1)
					#r.append(min(255, c))
					r.append(c)
					
					led.lastOut[i] = c	# Not needed for raw
				"""
				if (len(r) > 48):
					self.send(r)
					r = bytearray()
					#r.append(ord('r'))
				"""
		
		elif self.encoding == ENCODING_BIT_MASK:
			### Encoding: Transmit a bit mask for each pixel, telling which component changed
			
			for led in self.leds:
				# Calculate output value(s)
				color = led.get_bytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
				last = led.lastOut
				
				# Determine component bit mask for changes
				c = 0
				for i in range(3):
					if not (color[i] == last[i]):
						c += (1 << i)
				
				# Output
				r.append(c)
				
				for i in range(3):
					if not (color[i] == last[i]):
						r.append(color[i])
						led.lastOut[i] = color[i]
			#
		
		elif self.encoding == ENCODING_RLE:
			### Encoding: Use RLE (only for areas of no change)
			c = 0
			for li in range(len(self.leds)):
				led = self.leds[li]
				# Calculate output value(s)
				color = led.get_bytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
				
				# Check for change
				if (color[0] == led.lastOut[0]) and (color[1] == led.lastOut[1]) and (color[2] == led.lastOut[2]):
					# Nothing changed, keep counting...
					c += 1
					
				else:
					# Found a change
					
					# Transmit RLE-number
					while c >= 255:
						r.append(255)	# the same
						c -= 255
					r.append(c)
					
					#r.append(1)	# 1 new color
					for i in range(3):
						r.append(color[i])
						led.lastOut[i] = color[i]
					c = 0
			#
			if (c > 0):
				# Still something left?
				
				# Transmit RLE-number
				while c >= 255:
					r.append(255)	# the same
					c -= 255
				r.append(c)
				
		elif self.encoding == ENCODING_DELTA:
			### Encoding: 8 bit delta: Encode 1 byte per pixel, containing delta values. This leads to motion blur
			for led in self.leds:
				color = led.get_bytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
				#delta = [color[i] - led.lastOut[i] for i in range(3)]
				
				c = 0
				for i in range(3):
					delta = color[i] - led.lastOut[i]
					
					if delta > 0:
						dir = 0
					else:
						dir = 1
						delta = -delta
					
					data = min(delta, 2**1)
					
					c += (dir * 2 + data * 1) << ((2**1)*i)
					
					if dir == 0:
						led.lastOut[i] += data
					else:
						led.lastOut[i] -= data
					
					
				r.append(c)
				
		elif self.encoding == ENCODING_PACK8:
			### Encoding: Pack of 8 - send one 8-bit-mask indicating which of the 8 pixels has changed
			li = 0
			colorBuf = [0,0,0,0,0,0,0,0]
			while (li < len(self.leds)):
				
				c = 255
				for j in range(8):
					if (li+j) >= self.num_leds:
						colorBuf[j] = None
					else:
						led = self.leds[li+j]
						color = led.get_bytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
						
						# Check for change, update bitmask
						if (color[0] == led.lastOut[0]) and (color[1] == led.lastOut[1]) and (color[2] == led.lastOut[2]):
							c -= (1 << j)
							colorBuf[j] = None
						else:
							colorBuf[j] = color
				
				r.append(c)
				# Output what has changed
				for j in range(8):
					if not colorBuf[j] == None:
						led = self.leds[li+j]
						
						for k in range(3):
							r.append(colorBuf[j][k])
							led.lastOut[k] = colorBuf[j][k]
				li += 8
		else:
			put('Unknown encoding selected (%d)!' % self.encoding)
		
		#put('Total ' + str(len(r)) + ' bytes encoded')
		#put(str(len(r)) + ' bytes')
		self.send_raw(r)
	
	def fill(self, col):
		for led in self.leds:
			led.set_real(col)
		self.transmit()
	def set_all(self, cols):
		"Set all values at once"
		l = min(len(cols), self.num_leds)
		for i in range(l):
			#for led in self.leds:
			#led.set_real(col)
			self.leds[i].set_real(cols[i])

class LEDControl_serial(LEDControl):
	def __init__(self, serial_port=DEFAULT_SERIAL_PORT, serial_baud=DEFAULT_SERIAL_BAUD, *args, **kwargs):
		LEDControl.__init__(self, *args, **kwargs)
		
		self.serial_port = serial_port
		self.serial_baud = serial_baud
		self.handle = None
		
		put('Opening %s...' % self.serial_port)
		self.handle = serial.Serial(port=self.serial_port, baudrate=self.serial_baud, timeout=1)
		
		put('Waiting for Arduino to boot...')
		t_stop = time.monotonic() + 1.75
		while time.monotonic() < t_stop:
			d = self.handle.read()
			if len(d) > 0:
				#put('<<< %s' % d)
				pass
			else:
				time.sleep(.01)
		put('Should be ready now.')
	
	def send_raw(self, data):
		#put('Sending raw data (%d bytes for %d leds)...' % (len(data), self.num_leds))
		self.handle.write(b'r')
		
		# Write start
		start = 0
		self.handle.write(bytes([start >> 8, start & 0xff]))
		# Write size
		self.handle.write(bytes([self.num_leds >> 8, self.num_leds & 0xff]))
		
		# Write data
		self.handle.write(data)
	
	def send(self, data):
		#put('Sending command "' + data[:80] + '..."...')
		if type(data) is str:
			data = bytes(data, 'ascii')
		
		#put('Sending command (%d bytes)...' % len(data))
		#put(str(data))
		
		# Send data
		self.handle.write(data)
		
		# Throttle!
		#time.sleep((len(data) * 9) / self.serial_baud)
		#self.handle.flushOutput()
	
	def __del__(self):
		if not self.handle == None:
			self.handle.close()
			self.handle = None
	

class LEDControl_udp(LEDControl):
	def __init__(self, udp_host=DEFAULT_UDP_HOST, udp_port=DEFAULT_UDP_PORT, chunk_size=64, *args, **kwargs):
		LEDControl.__init__(self, *args, **kwargs)
		
		self.udp_host = udp_host
		self.udp_port = udp_port
		self.chunk_size = chunk_size	# Use 64 for standard ESP sketch
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	
	def send_raw(self, data):
		#put('Sending command "' + data[:80] + '..."...')
		#put('Sending command (%d bytes)...' % len(data))
		
		### UDP connection
		#self.sock.sendto(data, (UDP_HOST, UDP_PORT))
		#for retry in range(retries):
			#if (retry > 0): time.sleep(0.1)
		s = self.chunk_size
		o = 0
		l = len(data)
		while (o < l):
			put('chunk...')
			if (o > 0): time.sleep(0.002)
			self.sock.sendto(data[o:o+s], (self.udp_host, self.udp_port))
			o += s
		

class LEDControl_http(LEDControl):
	def __init__(self, http_url=DEFAULT_HTTP_URL, *args, **kwargs):
		LEDControl.__init__(self, *args, **kwargs)
		self.http_url = http_url
	
	def send_raw(self, data):
		#put('Sending command "' + data[:80] + '..."...')
		#put('Sending command (%d bytes)...' % len(data))
		
		
		u = self.http_url + '/raw?'
		for d in data:
			#u += '%02x' % (ord(d))
			u += '%02x' % (d)
		put('HTTP: "%s"' % (u))
		try:
			r = requests.get(u)
		except Exception as e:
			put('Exception while transmitting via HTTP: %s' % str(e))


if __name__ == '__main__':
	#r = requests.get(HTTP_URL)
	#print(str(r.text))
	
	
	lc = LEDControl_serial()
	#lc = LEDControl_udp()
	#lc = LEDControl_http()
	
	#lc.fill((0x33, 0xcc, 0x99))	# spr.at
	#lc.fill((0xf0, 0x00, 0xc2))	# pretty in pink
	#lc.fill((0xf8, 0xe0, 0xd0))	# warm white
	
	COUNT_PRE = 1
	COUNT_WALL_S = 105
	COUNT_WALL_W = 165
	COUNT_ALL = COUNT_PRE + COUNT_WALL_S + COUNT_WALL_W
	
	# The corner index is the first index in the "next" strip/wall
	INDEX_CORNER_SE = COUNT_PRE
	INDEX_CORNER_SW = COUNT_PRE + COUNT_WALL_S
	INDEX_CORNER_NW = COUNT_PRE + COUNT_WALL_S + COUNT_WALL_W	# index of the first non-visible LED
	
	
	# Gradients
	"""
	# RGB
	data = generate_gradient({
		#0              : (0xff, 0x00, 0x00),
		INDEX_CORNER_SE: (0xff, 0x00, 0x00),
		INDEX_CORNER_SW: (0x00, 0xff, 0x00),
		INDEX_CORNER_NW: (0x00, 0x00, 0xff),
		#COUNT_ALL      : (0xff, 0xff, 0x00)
	})
	"""
	
	# Instagram-ish
	data = generate_gradient({
		0              : (0xff, 0xc0, 0xa0),
		#INDEX_CORNER_SE: (0xf0, 0x00, 0xc2),
		#INDEX_CORNER_SE: (0xf0, 0x00, 0xc2),
		#INDEX_CORNER_SE + 30: (0xf0, 0x00, 0xc2),
		INDEX_CORNER_SE + 30: (0xf0, 0xc0, 0x00),
		
		INDEX_CORNER_SW: (0xf0, 0x40, 0xf0),
		
		INDEX_CORNER_NW - 30: (0xf0, 0xc0, 0x00),
		COUNT_ALL      : (0xf0, 0xd0, 0xf0)
	})
	
	
	"""
	# Bold colors
	c1 = (0x00, 0x20, 0xf0)
	c2 = (0xff, 0x40, 0x40)
	c3 = (0xff, 0x40, 0x40)
	
	data = generate_gradient({
		0              : c1,
		INDEX_CORNER_SW: c1,
		
		INDEX_CORNER_SW+1: c2,
		COUNT_ALL      : c2
	})
	"""
	
	"""
	# Theater mode
	data = []
	BORDER = 20
	FADE_EXP = 1.8
	COLOR = (0xff, 0xe0, 0xca)
	DOT_INDICES = [
		COUNT_PRE,
		#COUNT_PRE + COUNT_WALL_S // 2,
		COUNT_PRE + COUNT_WALL_S,
		COUNT_PRE + COUNT_WALL_S + COUNT_WALL_W // 2,
		COUNT_PRE + COUNT_WALL_S + COUNT_WALL_W,
	]
	
	for i in range(len(lc.leds)):
		led = lc.leds[i]
		
		#if (i < (COUNT_PRE + COUNT_S)):
		d = COUNT_ALL
		for idx in DOT_INDICES:
			d = min(d, abs(i - idx))
		
		if (d <= BORDER):
			#c = (0xff, 0xe8, 0xca)
			c = [ min(0xff, int(v * (1.0 - (d / BORDER)**FADE_EXP  ))) for v in COLOR ]
			#c = (0x10, 0xd0, 0xf0)
		else:
			c = (0x00, 0x00, 0x00)
			
		data.append(c)
		#led.set_real(c)
	"""
	
	put(str(data))
	lc.set_all(data)
	lc.transmit()
	
