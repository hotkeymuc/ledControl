#ifndef __LED_H__
#define __LED_H__


#include <FastLED.h>
//#include <Adafruit_NeoPixel.h>


#include "fx.h"



// Define the array of leds
//CRGB leds[NUM_LEDS];
//Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);
CRGB leds[NUM_LEDS];  // Leave some head room for accidental spillage from dirty code which would corrupt local variables

unsigned int frame = 0;  // load next preset at beginning
uint8_t brightness = DEFAULT_BRIGHTNESS;

#define FADE_FRAMES 512
//#define FPS 60
//#define DEFAULT_FRAMEDELAY (1000 / FPS)

#define DISPLAY_MODE_AUTO 0
#define DISPLAY_MODE_RAW 1
byte mode = DISPLAY_MODE_AUTO;

int frameDelay = DEFAULT_FRAMEDELAY;

// Raw image states
int rNum = 0;
byte rC = 0;


#define FLASH_MILLIS 3000L
#define FLASH_PRESET 0


// Effect sub system
#define MAX_FXS 10  //16
#define MAX_FX_PARAMS 4


typedef struct {
  FxType fx;
  
  unsigned int frame;
  int frameEach;
  int frameOfs;
  
  int numStart;
  int numCount;
  
  int params[MAX_FX_PARAMS];
} FxLayer;

FxLayer fxLayers[MAX_FXS];

int fxLayerCount = 0;


void fxLayerSet(FxLayer *fxl,
  FxType fx,
  //unsigned int frame,
  int frameEach,
  int frameOfs,
  
  int numStart,
  int numCount,
  //int params[]  //[MAX_FX_PARAMS]
  int params0, int params1, int params2, int params3
) {
  fxl->fx = fx;
  fxl->frame = 0;  //frame;
  fxl->frameEach = frameEach;
  fxl->frameOfs = frameOfs;
  fxl->numStart = numStart;
  fxl->numCount = numCount;
  //for (int i = 0; i < MAX_FX_PARAMS; i++) fxl->params[i] = params[i];
  fxl->params[0] = params0;
  fxl->params[1] = params1;
  fxl->params[2] = params2;
  fxl->params[3] = params3;
}

int presets = 13;
int preset = DEFAULT_PRESET;  // Default preset

void fxLoadPreset(int p) {
  Serial.print(F("#Preset "));
  Serial.println(preset);
  
  // Load next preset!
  fxLayerCount = 0;
  
  switch(p) {
    case 0:
      // Warm white
      fxLayerSet(&fxLayers[fxLayerCount++], FX_SOLID,  1,0,  -1,-1,  0xa0,0x80,0x30,0);
      break;
      
    case 1: // RGB single pixel chase
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	1,0,	0,1,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	NUM_LEDS,0*(NUM_LEDS/3),	0,1,	0xff,0x00,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	NUM_LEDS,1*(NUM_LEDS/3),	0,1,	0x00,0xff,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	NUM_LEDS,2*(NUM_LEDS/3),	0,1,	0x00,0x00,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	1,0,	-1,-1,	0,0,0,0);
      break;

    case 2: // Standard full solid RGB fade
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	4,0,	-1,-1,	1,16,0,0);
      break;
      
    case 3: // Glitter
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	2,0,	-999,1,	0xff,0xff,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	2,1,	-1,-1,	0x0a,0x14,0x14,0);
      break;
      
    case 4:  // RGB Strobo
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	3,0,	-1,-1,	0xff,0x00,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	3,1,	-1,-1,	0x00,0xff,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	3,2,	-1,-1,	0x00,0x00,0xff,0);
      break;
      
    case 5: // Scroller
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	4,0,	0,1,	0x00,0x00,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	4,1,	0,1,	0xff,0x00,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	4,2,	0,1,	0x00,0xff,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	4,3,	0,1,	0x00,0x00,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	1,0,	-1,-1,	0,0,0,0);
      break;
      
    case 6: // RGB camp fire
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	4,0,	-1,-1,	1,256,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_NOISE_ADD,	1,0,	-1,-1,	20,20,0,0);
      break;
      
    case 7: // Camp fire
      // Some red, yellow and white flashes
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	7,0,	0,4,	0xff,0x00,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	5,4,	0,4,	0xff,0xff,0x00,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	23,2,	0,4,	0xff,0xff,0xff,0);
      // Quick lower move
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	1,0,	-1,-3,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_NOISE_ADD,	1,0,	0,4,	30,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	4,0,	-999,2,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++], FX_BLUR,	1,0,	0,-1,	0,0,0,0);
      
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_NOISE_ADD,	1,0,	0,-1,	8,3,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	3,0,	-1,-1,	0,0,0,0);
      // Spark
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	6,0,	-999,1,	0xff,0xff,0x00,0);
      break;
      
    case 8: // Inverse waves
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	40,0,	-999,1,	10,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	40,20,	-999,1,	20,0,128,0);
      fxLayerSet(&fxLayers[fxLayerCount++], FX_BLUR,	1,0,	-1,-1,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	4,0,	-1,-1,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	4,1,	0,4,	0,0,0,0);
      break;
    
    case 9: // Rainbow clean scroller
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	1,0,	-1,-1,	1,256*4,0,0);
      //fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	1,0,	-1,-1,	3,256,0,0);
      //fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	1,0,	-1,-1,	1,2048,0,0);
      break;
    
    case 10: // Blur/scroll
      //fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	1000,0,	-1,-1,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RANDOM_DOTS,	20,0,	-1,-1,	1,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLUR_DOWN,	1,0,	-1,-1,	1,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	4,0,	-1,-1,	0,0,0,0);
      break;
    
    case 11: // Police
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	1000,0,	-1,-1,	0,0,0,0);
      
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	20,0,	0,-2,	0x00,0x00,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	20,1,	0,-2,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	20,6,	0,-2,	0x00,0x00,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	20,7,	0,-2,	0,0,0,0);

      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	20,10,	-2,-2,	0x00,0x00,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	20,11,	-2,-2,	0,0,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SOLID,	20,16,	-2,-2,	0x00,0x00,0xff,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_BLACK,	20,17,	-2,-2,	0,0,0,0);
      break;
      
    case 12:  // Rainbow shock
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_RAINBOW_FILL,	200,0,	-1,-1,	11,256,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_NOISE_ADD,	1,0,	-1,-1,	5,3,0,0);
      fxLayerSet(&fxLayers[fxLayerCount++],	FX_SCROLL,	1,0,	-1,-1,	1,0,0,0);
      break;

  }
}

// For some reason esp32 sources re-define "max()"... *sigh!*
int mymax(int x1, int x2) {
  if (x1 > x2) return x1;
  return x2;
}

int hexCharToInt(char c) {
  if ((c >= '0') && (c <= '9')) return (c - '0');
  else if ((c >= 'a') && (c <= 'f')) return (10 + c - 'a');
  else if ((c >= 'A') && (c <= 'F')) return (10 + c - 'A');
  return 0;
}

unsigned long millis_last = millis();

long frameGlobal = 0;

void led_show() {
  FastLED.show();
}

void led_setup() {
  /*
  //FastLED.addLeds<WS2812B, DATA_PIN>(leds, NUM_LEDS);
  strip.setBrightness(BRIGHTNESS);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  */
  
  //pinMode(DATA_PIN, OUTPUT);
  //LEDS.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
  //LEDS.addLeds<WS2811Controller400Khz, LED_PIN, RGB>(leds, NUM_LEDS);
  //LEDS.addLeds<WS2812Controller800Khz, LED_PIN, GRB>(leds, NUM_LEDS);
  LEDS.addLeds<WS2812Controller800Khz, LED_PIN, RGB>(leds, NUM_LEDS);
  LEDS.setBrightness(brightness);
  delay(100);
  memset(leds, 0x04, NUM_LEDS * 3); // Init color...
  
  FastLED.show();
  delay(100);

}

void led_loop() {
  int d;
  int i, j;
  FxLayer *fx;
  uint32_t col;

  
  
  if (mode == 0) {
    // Auto mode
    
    /*
    if ((frame % 500) >= 499) {
      frame = 0;
      presets = 12;
      preset = (preset + 1) % presets;
      
      fxLoadPreset(preset);
      
    } else {
    */
    //frame = (frame + 1) % frames;
    frame++;
    //Serial.println(frame);
    //}
    
    
    // Apply effects
   
    for (i = 0; i < fxLayerCount; i++) {

      fx = &fxLayers[i];
      
      if ((frame % fx->frameEach) == fx->frameOfs) {
        // Trigger the effect
        
        int numStart = fx->numStart;
        switch(numStart) {
          case -1:  numStart = 0;  break;
          
          case -2:  numStart = NUM_LEDS >> 1;  break;
          case -20: numStart = 0*NUM_LEDS >> 1;  break;
          case -21: numStart = 1*NUM_LEDS >> 1;  break;
          case -22: numStart = 2*NUM_LEDS >> 1;  break;
          
          case -3: numStart = NUM_LEDS / 3;  break;
          case -30: numStart = 0*NUM_LEDS / 3;  break;
          case -31: numStart = 1*NUM_LEDS / 3;  break;
          case -32: numStart = 2*NUM_LEDS / 3;  break;
          case -33: numStart = 3*NUM_LEDS / 3;  break;
          
          case -4: numStart = NUM_LEDS >> 2;  break;
          case -40: numStart = 0*NUM_LEDS >> 2;  break;
          case -41: numStart = 1*NUM_LEDS >> 2;  break;
          case -42: numStart = 2*NUM_LEDS >> 2;  break;
          case -43: numStart = 3*NUM_LEDS >> 2;  break;
          case -44: numStart = 4*NUM_LEDS >> 2;  break;
          
          case -999: numStart = random(0, NUM_LEDS); break;
        }
        
        int numCount = fx->numCount;
        switch(numCount) {
          case -1:  numCount = NUM_LEDS;  break;
          case -2:  numCount = NUM_LEDS >> 1;  break;
          
          case -3:  numCount = NUM_LEDS / 3;  break;
          case -31: numCount = 1*NUM_LEDS / 3;  break;
          case -32: numCount = 2*NUM_LEDS / 3;  break;
          
          case -4:  numCount = NUM_LEDS >> 2;  break;
          case -41: numCount = 1*NUM_LEDS >> 2;  break;
          case -42: numCount = 2*NUM_LEDS >> 2;  break;
          case -43: numCount = 3*NUM_LEDS >> 2;  break;
        }
        if (numStart+numCount > NUM_LEDS) numCount = NUM_LEDS - numStart;
        if (numCount < 0) numCount = 0;
        
        switch(fx->fx) {
          case FX_BLACK:
            col = fx->params[0];
            fx_black(leds, numStart, numCount, col);
            break;
          
          case FX_SOLID:
            //col = fx->params[0];
            //fx_solid(leds, numStart, numCount, (col >> 16) & 0xff, (col >> 8) & 0xff, (col) & 0xff);
            fx_solid(leds, numStart, numCount, fx->params[0], fx->params[1], fx->params[2]);
            break;
            
          case FX_RANDOM_DOTS:
            fx_randomDots(leds, numStart, numCount, fx->params[0]);
            break;
            
          case FX_SCROLL:
            fx_scroll(leds, numStart, numCount, fx->params[0]);
            break;
            
          case FX_BLUR:
            fx_blur(leds, numStart, numCount);
            break;

          case FX_BLUR_DOWN:
            fx_blur(leds, numStart, numCount);
            break;
            
          case FX_RAINBOW_FILL:
            fx_rainbowFill(leds, numStart, numCount, (fx->frame * fx->params[0] + fx->params[2]) % 256, fx->params[1]);
            break;
          
          case FX_NOISE_ADD:
            fx_noiseAdd(leds, numStart, numCount, fx->params[0], fx->params[1]);
            break;
        }
        fx->frame++;
        
      }

    }


    
    // Fade in
    if (frameGlobal < FADE_FRAMES) {
      //d = FADE_FRAMES - (frameGlobal / (FADE_FRAMES/256));
      d = frameGlobal / (FADE_FRAMES/256);
      for (i = 0; i < NUM_LEDS; i++) {
        CRGB *l = &leds[i];
        
        if (l->r > d) l->r = d;
        if (l->g > d) l->g = d;
        if (l->b > d) l->b = d;
      }
    }
    frameGlobal++;
    
    
    
    /*
    for (i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, leds[i].r * 0x010000 + leds[i].g * 0x000100 + leds[i].b * 0x000001);
    }
    strip.show(); // Initialize all pixels to 'off'
    */
    led_show();

    
    unsigned long millis_now = millis();
    d = millis_now - millis_last;

    //@TODO: Use ESP light/modem sleep
    delay(mymax(frameDelay, frameDelay - d));
    
    millis_last = millis_now;
  }
}

void flash() {
  frame = 0;
  frameGlobal = 0;
  fxLoadPreset(FLASH_PRESET);
  
  unsigned long endMillis = millis() + FLASH_MILLIS;
  while (millis() < endMillis) {
    //delay(frameDelay);
    led_loop();
    yield;
  }
  
  fxLoadPreset(preset);
  frame = 0;
  frameGlobal = 0;
}

#endif
