from ledControl import LEDControl, LED, LEDS, FxType, FxLayer, FxPreset
import time
import math



import pygame
from pygame.locals import *

VERSION = 'ledControl'
screenSize = (1024, 600)

lastPut = ''
def put(txt):
	print(VERSION + ':	' + txt)
	global lastPut
	lastPut = txt


lc = LEDControl()

# Position LEDs
sx = 3
sy = 5
p = [screenSize[0]/2 - LEDS*sx/2, screenSize[1]/2, 0.0]
for i in xrange(LEDS):
	lc.leds[i].pos = [(p[j]) for j in xrange(3)]
	#p[0] += 10
	p[0] += sx
	if (p[0] > screenSize[0]):
		p[0] = 0
		p[1] += sy

def wheel8(h):
	if (h < 85):
		return [h * 3, 255 - h * 3, 0]
	elif (h < 170):
		h -= 85
		return [255 - h * 3, 0, h * 3]
	else:
		h -= 170
		return [0, h * 3, 255 - h * 3]

def wheel(h):
	#while (h >= 1.0):
	#	h -= 1.0
	
	if (h < 0.333):
		return [h * 3.0, 1.0 - h * 3.0, 0]
	elif (h < 0.667):
		h -= 0.333
		return [1.0 - h * 3.0, 0, h * 3.0]
	else:
		h -= 0.667
		return [0, h * 3.0, 1.0 - h * 3.0]


"""
p = FxPreset("Test")
p.addLayer(FxLayer(
	fx=FxType.FX_RAINBOW_FILL,
	frameEach=1, frameOfs=0,
	numStart=0, numCount=300,
	params0=1, params1=256*4, params2=0, params3=0
	))
"""

# Rainbow tests
#p.addLayer(FxLayer(FxType.FX_RAINBOW_FILL,	1,0,	-1,-1,	-10, 256*16,0,0))
#p.addLayer(FxLayer(FxType.FX_RAINBOW_FILL,	1,0,	-1,-1,	-10, 256*16,0,0))
#p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	0,300,	0x33,0xcc,0x99,0))

# Init game
pygame.init()
screen = pygame.display.set_mode(screenSize, 0, 32)
#screen.fill((0x00, 0x00, 0x00))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 48, True)
pygame.display.set_caption(VERSION)
#pygame.mouse.set_visible(False)


#img = pygame.image.load('img/test1.png')
img = pygame.image.load('img/weihnachtsmarkt1.jpg')
#img = pygame.image.load('img/weihnachtsmarkt2.jpg')
#img = pygame.image.load('img/weihnachtsmarkt3.png')
img = img.convert()
#screen.blit(img, (0, 0))
#pygame.display.update()




running = True
put('Running...')

while running:
	time.sleep(0.2)
	tick = clock.tick()
	changed = False
	
	screen.fill((0x00, 0x00, 0x00))
	screen.blit(img, (0, 0))
	
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()
		
		if event.type == MOUSEBUTTONDOWN:
			lc.transmit()
			pass
		
		if event.type == MOUSEMOTION:
			
			i = 0
			x = event.pos[0]
			y = event.pos[1]
			r = img.get_rect()
			for led in lc.leds:
				if x >= 0 and y >= 0 and x < r.w and y < r.h:
					c = img.get_at((x, y))
					#led.color = (c[0]*b, c[1]*b, c[2]*b)
					led.setReal(c)
				
				x += 1
				y += 1
				
				i += 1
			
			if event.buttons[0]:
				lc.transmit()
			
			"""
			i = 0
			for led in lc.leds:
				#d = math.sqrt((led.pos[0]-event.pos[0])**2 + (led.pos[1]-event.pos[1])**2)
				#led.color = [min(1.0, max(0.0, 1.0-(d/200))) for i in xrange(3)]
				
				#w = wheel(min(1.0, max(0.0, d/200)))
				#led.color = [min(1.0, max(0.0, w[i])) for i in xrange(3)]
				led.color = wheel((float(i)/LEDS  - float(event.pos[0]*4.0)/screenSize[0] + 2.0 )*(float(event.pos[1]*2)/screenSize[1]))
				changed = True
				
				i += 1
			"""
			changed = True
			
		if event.type == KEYDOWN:
			if (event.key == 282):	#F1	#ord('0')):
				p = FxPreset('Black Out')
				p.addLayer(FxLayer(FxType.FX_BLACK,	1,0,	-1,-1,	0,0,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 283):	#F2	# == ord('1')):
				p = FxPreset('RGB campfire')
				p.addLayer(FxLayer(FxType.FX_RAINBOW_FILL,	4,0,	-1,-1,	1, 256,0,0))
				p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	1,0,	-1,-1,	20,20,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 284):	#F3	# == ord('2')):
				p = FxPreset('RGB campfire 2')
				p.addLayer(FxLayer(FxType.FX_RAINBOW_FILL,	4,0,	-1,-1,	1, 256/3,0,0))
				p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	1,0,	-1,-1,	15,15,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 285):	#F4	# == ord('3')):
				p = FxPreset('Warm light')
				#p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	-1,-1,	0xff,0xd8,0x60,0))
				#p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	-1,-1,	0xff,0xd0,0x40,0))
				p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	-1,-1,	0xa0,0x80,0x30,0))
				#p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	1,0,	-1,-1,	10,10,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 286):	#F5	# == ord('4')):
				p = FxPreset('City Lights')
				#p.addLayer(FxLayer(FxType.FX_SOLID,	40,0,	-1,-1,	0x10,0x18,0x40,0))
				p.addLayer(FxLayer(FxType.FX_SOLID,	10,0,	-20,-2,	0x10,0x18,0x40,0))
				p.addLayer(FxLayer(FxType.FX_SOLID,	10,2,	-21,-2,	0x10,0x18,0x40,0))
				
				#p.addLayer(FxLayer(FxType.FX_SOLID,	200,0,	-40,-4,	0x10,0x18,0x40,0))
				#p.addLayer(FxLayer(FxType.FX_SOLID,	200,50,	-41,-4,	0x10,0x18,0x40,0))
				#p.addLayer(FxLayer(FxType.FX_SOLID,	200,100,	-42,-4,	0x10,0x18,0x40,0))
				#p.addLayer(FxLayer(FxType.FX_SOLID,	200,150,	-43,-4,	0x10,0x18,0x40,0))
				
				#p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	4,0,	-1,-1,	20,20,0,0))
				p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	1,0,	-1,-1,	5,5,0,0))
				p.addLayer(FxLayer(FxType.FX_RANDOM_DOTS,	17,0,	-1,-1,	4,0,0,0))
				#p.addLayer(FxLayer(FxType.FX_BLUR_DOWN,	1,0,	-1,-1,	0,0,0,0))
				p.addLayer(FxLayer(FxType.FX_BLUR,	1,0,	-1,-1,	0,0,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 287):	#F6	# == ord('5')):
				p = FxPreset('Something')
				p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	-1,-1,	0xff,0xe0,0x60,0))
				p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	4,0,	-1,-1,	80,80,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 288):	#F7	# == ord('6')):
				p = FxPreset('Glitter')
				p.addLayer(FxLayer(FxType.FX_SOLID,	2,0,	-999,1,	0xff,0xff,0xff,0))
				p.addLayer(FxLayer(FxType.FX_SOLID,	2,1,	-1,-1,	0x0a,0x14,0x14,0))
				lc.send(p.getCommands())
				
			elif (event.key == 289):	#F8	# == ord('8')):
				p = FxPreset('Random')
				p.addLayer(FxLayer(FxType.FX_RANDOM_DOTS,	8,0,	-1,-1,	1,0,0,0))
				#p.addLayer(FxLayer(FxType.FX_BLUR_DOWN,	1,0,	-1,-1,	0,0,0,0))
				p.addLayer(FxLayer(FxType.FX_BLUR,	2,0,	-1,-1,	0,0,0,0))
				p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	1,0,	-1,-1,	4,4,0,0))
				lc.send(p.getCommands())
				
			elif (event.key == 290):	#F9	# == ord('9')):
				p = FxPreset('Rainbow Shock')
				p.addLayer(FxLayer(FxType.FX_RAINBOW_FILL,	200,0,	-1,-1,	11,256,0,0))
				p.addLayer(FxLayer(FxType.FX_NOISE_ADD,	1,0,	-1,-1,	5,3,0,0))
				p.addLayer(FxLayer(FxType.FX_SCROLL,	1,0,	-1,-1,	1,0,0,0))
				lc.send(p.getCommands())
				
			#elif (event.key == 291):	#F10	# == ord('b')):
			#elif (event.key == 292):	#F11	# == ord('b')):
				
			elif (event.key == 293):	#F12	# == ord('b')):
				p = FxPreset('Black Out')
				w = 268
				w2 = int(w/2)
				p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	0,1,	0x00,0x00,0x00,0))
				p.addLayer(FxLayer(FxType.FX_SCROLL,	1,0,	0,w2,	0,0,0,0))
				p.addLayer(FxLayer(FxType.FX_SOLID,	1,0,	w-2,2,	0x00,0x00,0x00,0))
				p.addLayer(FxLayer(FxType.FX_SCROLL,	1,0,	w2,w2,	1,0,0,0))
				lc.send(p.getCommands())
				
				
			elif (event.key == ord('0')):
				
				#colHex = 0x33cc99
				colHex = 0x0000f0
				colPygame = (colHex >> 16, (colHex >> 8) & 0xff, colHex & 0xff)
				put(str(colPygame))
				#colLed = [math.pow(c / 255.0, correction) for c in colPygame]
				colLed = [
					math.pow(colPygame[0] / 255.0, 4),
					math.pow(colPygame[1] / 255.0, 4.5),
					math.pow(colPygame[2] / 255.0, 6)
				]
				
				screen.fill(
					color = colPygame,
					rect=(0, 0, screenSize[0], 20)
				)
				
				for led in lc.leds:
					led.color = colLed
				
				lc.transmit()
				changed = True
				
			elif (event.key == ord('x')):
				lc.send('x')
			elif (event.key == ord('a')):
				lc.send('a')
			elif (event.key == ord('p')):
				lc.send('p')
			elif (event.key == ord('s')):
				lc.send('s')
				
			elif (event.key == 32):
				# Transmit image
				lc.transmit()
				
			elif (event.key == 27):
				running = False
			
			else:
				put('Unknown key: ' + str(event.key))
			
		if event.type == KEYUP:
			pass
			
		# end of event loop
	
	if changed:
		# Visualise and send
		lc.draw(screen)
		pygame.display.update()
		
	"""
	if changed:
		lc.transmit()
		
		# Don't send too fast!
		time.sleep(1.0/30)
	
	lc.drawLast(screen)
	"""
	
	
	
	
	"""
	#col = (0x00, 0x00, 0x00)
	#pygame.draw.circle(screen, col, (int((i+0.5) * 160), screenSize[1]/2), 80, 0)
	putImage = font.render(lastPut, True, (255,255,255))
	rect = putImage.get_rect()
	rect[0] = 32
	rect[1] = 32
	screen.blit(putImage, rect)
	"""
	
	
	
put('Finished.')

