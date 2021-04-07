import math
import time

USE_SERIAL = False
SERIAL_PORT = 'COM59'
SERIAL_BAUD = 115200	#1000000

USE_UDP = False
UDP_HOST = '192.168.4.137'
UDP_PORT = 1329

USE_HTTP = True
#http://192.168.4.138/raw?010101020202040404080808101010202020404040808080
HTTP_URL = 'http://esp32led.fritz.box'
#HTTP_URL = 'http://192.168.4.138'


if USE_SERIAL:
	import serial
	
if USE_UDP:
	import socket

if USE_HTTP:
	import requests


LEDS = 30*9 + 1
ENCODING = 0	# 0=raw, 1=component-bit-mask, 2=RLE-for-no-change, 3=8-bit-delta, 4=pack of 8


def put(txt):
	print('ledControl:	' + txt)



class LED:
	def __init__(self):
		self.color = [0.0, 0.0, 0.0]
		
		#self.last = [0.0, 0.0, 0.0]	# Store last INTERNAL value
		self.lastOut = [0,0,0]	# Store last OUTPUT value
		
		self.pos = [0.0, 0.0, 0.0]
	
	def setReal(self, colPygame):
		#correction = 3.0	#4.0
		#self.color = [math.pow(c / 255.0, correction) for c in colPygame]
		
		self.color = [
			math.pow(colPygame[0] / 255.0, 4),
			math.pow(colPygame[1] / 255.0, 3.5),
			math.pow(colPygame[2] / 255.0, 6)
		]
		
		"""
		self.color = [
			math.pow(colPygame[0] / 255.0, 0.4),
			math.pow(colPygame[1] / 255.0, 0.35),
			math.pow(colPygame[2] / 255.0, 0.6)
		]
		"""
	
	def getBytes(self):
		return [int(max(0, min(255, math.floor(self.color[i] * 255)))) for i in range(3)]

class LEDControl:
	def __init__(self):
		self.leds = []
		
		for i in range(LEDS):
			led = LED()
			self.leds.append(led)
			
		if USE_SERIAL:
			### Serial connection
			self.handle = None
			self.handle = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUD, timeout=1)
		
		if USE_UDP:
			### UDP connection
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		#
		
	def send(self, data):
		#put('Sending command "' + data[:80] + '..."...')
		put('Sending command (' + str(len(data)) + ' bytes)...')
		if USE_SERIAL:
			### Serial:
			self.handle.write(data)
		
		if USE_UDP:
			### UDP connection
			#self.sock.sendto(data, (UDP_HOST, UDP_PORT))
			#for retry in range(retries):
				#if (retry > 0): time.sleep(0.1)
			s = 64
			o = 0
			l = len(data)
			while (o < l):
				put('chunk...')
				if (o > 0): time.sleep(0.002)
				self.sock.sendto(data[o:o+s], (UDP_HOST, UDP_PORT))
				o += s
		
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
	
	def __del__(self):
		if USE_SERIAL:
			### Serial
			if not self.handle == None: self.handle.close()
		
	
	def draw(self, screen):
		for led in self.leds:
			screen.fill(
				color = led.getBytes(),	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)],
				rect=(led.pos[0], led.pos[1], 4, 4)
			)
			
	def drawLast(self, screen):
		for led in self.leds:
			screen.fill(
				color = [led.lastOut[i] for i in range(3)],
				rect=(led.pos[0], led.pos[1] + screenSize[1]/2, 4, 4)
			)
	
	def transmit(self):
		r = bytearray()
		
		# Header
		
		#r.append(ord('r'))	# command: RAW
		
		#r.append(LEDS >> 8)
		#r.append(LEDS % 256)
		
		#r.append(ENCODING)
		
		if ENCODING == 0:
			### Encoding: RAW
			for led in self.leds:
				# Calculate output value(s)
				color = led.getBytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
				for i in range(3):
					#r.append(color[i])
					r.append(min(255, color[i]+1))
					
					led.lastOut[i] = color[i]	# Not needed for raw
				"""
				if (len(r) > 48):
					self.send(r)
					r = bytearray()
					#r.append(ord('r'))
				"""
		
		
		elif ENCODING == 1:
			### Encoding: Transmit a bit mask for each pixel, telling which component changed
			
			for led in self.leds:
				# Calculate output value(s)
				color = led.getBytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
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
		
		elif ENCODING == 2:
			### Encoding: Use RLE (only for areas of no change)
			c = 0
			for li in range(len(self.leds)):
				led = self.leds[li]
				# Calculate output value(s)
				color = led.getBytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
				
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
				
		elif ENCODING == 3:
			### Encoding: 8 bit delta: Encode 1 byte per pixel, containing delta values. This leads to motion blur
			for led in self.leds:
				color = led.getBytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
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
				
		elif ENCODING == 4:
			### Encoding: Pack of 8 - send one 8-bit-mask indicating which of the 8 pixels has changed
			li = 0
			colorBuf = [0,0,0,0,0,0,0,0]
			while (li < len(self.leds)):
				
				c = 255
				for j in range(8):
					if (li+j) >= LEDS:
						colorBuf[j] = None
					else:
						led = self.leds[li+j]
						color = led.getBytes()	#[int(max(0, min(255, math.floor(led.color[i] * 255)))) for i in range(3)]
						
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
		#
		put('Total ' + str(len(r)) + ' bytes encoded')
		#put(str(len(r)) + ' bytes')
		self.send(r)

	def fill(self, col):
		for led in self.leds:
			led.setReal(col)
		self.transmit()
	def set(self, cols):
		"Set all values at once"
		l = min(len(cols), len(self.leds))
		for i in range(l):
			#for led in self.leds:
			#led.setReal(col)
			self.leds[i].setReal(cols[i])

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
		
	def getCommand(self, num):
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
	
	def getCommands(self):
		d = DELIMITER
		r = 'x\n'
		i = 0
		for l in self.layers:
			r += l.getCommand(i)
			
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

if __name__ == '__main__':
	#r = requests.get(HTTP_URL)
	#print(str(r.text))
	
	
	lc = LEDControl()
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
		#led.setReal(c)
	"""
	lc.set(data)
	lc.transmit()
	
