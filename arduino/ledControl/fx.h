#ifndef __INC_FX_H
#define __INC_FX_H

//#include <deadbeef_rand.c>
static uint32_t deadbeef_seed;
static uint32_t deadbeef_beef = 0xdeadbeef;

uint32_t deadbeef_rand() {
	deadbeef_seed = (deadbeef_seed << 7) ^ ((deadbeef_seed >> 25) + deadbeef_beef);
	deadbeef_beef = (deadbeef_beef << 7) ^ ((deadbeef_beef >> 25) + 0xdeadbeef);
	return deadbeef_seed;
}

void deadbeef_srand(uint32_t x) {
	deadbeef_seed = x;
	deadbeef_beef = 0xdeadbeef;
}


int xrandint(int imin, int imax) {
  int span = (imax - imin);
  return imin + (deadbeef_rand() % span);
}
int randmax(int span) {
  return (deadbeef_rand() % span);
}

// End of fast random



enum FxType {
  FX_BLACK,  //0
  FX_SOLID,  //1
  FX_RANDOM_DOTS,  //2
  FX_SCROLL,  //3
  FX_BLUR,  //4
  FX_BLUR_DOWN,  //5
  FX_RAINBOW_FILL,  //6
  FX_NOISE_ADD,  //7
};



uint32_t Color(byte r, byte g, byte b)  {
  // Takes care of RGB mode
  uint32_t c;
  c = b;  //r;
  c <<= 8;
  c |= r;  //g;
  c <<= 8;
  c |= g;  //b;
  return c;
}

uint32_t Wheel(byte WheelPos) {
  if (WheelPos < 85) {
   return Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if (WheelPos < 170) {
   WheelPos -= 85;
   return Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
   WheelPos -= 170; 
   return Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}


void fx_black(struct CRGB leds[], int numStart, int numCount, byte val) {
  memset(&leds[numStart], val, numCount * 3);
}

void fx_solid(struct CRGB leds[], int numStart, int numCount, byte r, byte g, byte b) {
  for(int i = numStart; i < numStart+numCount; i++ ) {
    leds[i].r = g;  //r;
    leds[i].g = r;  //is R!;
    leds[i].b = b;  //b;
  }
}

void fx_randomDots(struct CRGB leds[], int numStart, int numCount, int count) {
  for (int i = 0; i < count; i++) {
    int j = random(0, numCount) + numStart;
    leds[j].r = randmax(256);
    leds[j].g = randmax(256);
    leds[j].b = randmax(256);
  }
}

void fx_scroll(struct CRGB leds[], int numStart, int numCount, byte dir) {
  // memcpy can not use overlapping regions...
  if (dir == 0)
    memmove(&leds[numStart+1], &leds[numStart], (numCount-1) * 3);
  else
    memmove(&leds[numStart], &leds[numStart+1], (numCount-1) * 3);
}


void fx_noiseAdd(struct CRGB leds[], int numStart, int numCount, int amountDown, int amountUp) {
  int amount = amountDown + amountUp;
  for (int i = numStart; i < numStart+numCount; i++) {

    /*
    uint8_t v, vDown, vUp;
    v = leds[i].r;
    vDown = (v >= amountDown) ? (v-amountDown) : 0;
    vUp = (255-v) > amountUp ? (v+amountUp) : 255;
    leds[i].r = random(vDown, vUp);
    
    v = leds[i].g;
    vDown = (v >= amountDown) ? (v-amountDown) : 0;
    vUp = (255-v) > amountUp ? (v+amountUp) : 255;
    leds[i].g = random(vDown, vUp);

    v = leds[i].b;
    vDown = (v >= amountDown) ? (v-amountDown) : 0;
    vUp = (255-v) > amountUp ? (v+amountUp) : 255;
    leds[i].b = random(vDown, vUp);
    */
    
    short v;
    short r;
    r = -amountDown + randmax(amount);
    
    v = leds[i].r + r;
    //v = randint(v - amountDown, v + amountUp);
    //v = v - amountDown + randmax(amount);
    if (v < 0) v = 0;
    else if (v > 255) v = 255;
    leds[i].r = v;

    //r = -amountDown + randmax(amount);
    v = leds[i].g + r;
    //v = randint(v - amountDown, v + amountUp);
    //v = v - amountDown + randmax(amount);
    if (v < 0) v = 0;
    else if (v > 255) v = 255;
    leds[i].g = v;

    //r = -amountDown + randmax(amount);
    v = leds[i].b + r;
    //v = randint(v - amountDown, v + amountUp);
    //v = v - amountDown + randmax(amount);
    if (v < 0) v = 0;
    else if (v > 255) v = 255;
    leds[i].b = v;
    
    //int r = random(-amountDown, amountUp);

  }
}


void fx_blur(struct CRGB leds[], int numStart, int numCount) {
  int j = 0;

  j = numStart + numCount-1;
  byte colLr = leds[j].r;
  byte colLg = leds[j].g;
  byte colLb = leds[j].b;

  j = numStart;
  byte colMr = leds[j].r;
  byte colMg = leds[j].g;
  byte colMb = leds[j].b;

  j = numStart+1;
  byte colRr = leds[j].r;
  byte colRg = leds[j].g;
  byte colRb = leds[j].b;

  for(int i = 0; i < numCount; i++ ) {
    j = numStart + (i + 1) % numCount;

    colLr = colMr; colLg = colMg; colLb = colMb;
    colMr = colRr; colMg = colRg; colMb = colRb;
    colRr = leds[j].r; colRg = leds[j].g; colRb = leds[j].b;

    // normal
    leds[i].r = (colLr + colMr + colRr) / 3;
    leds[i].g = (colLg + colMg + colRg) / 3;
    leds[i].b = (colLb + colMb + colRb) / 3;

  }
}

void fx_blurDown(struct CRGB leds[], int numStart, int numCount) {
  int j;
  
  j = numStart + numCount-1;
  byte colLr = leds[j].r;
  byte colLg = leds[j].g;
  byte colLb = leds[j].b;

  j = numStart;
  byte colMr = leds[j].r;
  byte colMg = leds[j].g;
  byte colMb = leds[j].b;

  j = numStart+1;
  byte colRr = leds[j].r;
  byte colRg = leds[j].g;
  byte colRb = leds[j].b;

  for(int i = 0; i < numCount; i++ ) {
    j = numStart + (i + 1) % numCount;
    
    colLr = colMr; colLg = colMg; colLb = colMb;
    colMr = colRr; colMg = colRg; colMb = colRb;
    colRr = leds[j].r; colRg = leds[j].g; colRb = leds[j].b;

    // fast and dark
    leds[i].r = (((int)(colLr + colMr + colRr)) *7) >> 3;
    leds[i].g = (((int)(colLg + colMg + colRg)) *7) >> 3;
    leds[i].b = (((int)(colLb + colMb + colRb)) *7) >> 3;
  }
}


void fx_rainbowFill(struct CRGB leds[], int numStart, int numCount, int rainbowStart, int rainbowScale) {
  long v = rainbowStart;
  v = v << 8;
  for(int i = numStart; i < numStart+numCount; i++ ) {
    //leds[i] = Wheel((i + rainbowStart) % 256);
    
    leds[i] = Wheel((v >> 8) & 0xff);
    v += rainbowScale;
  }
}


/*

#define pats 5
#define patLen 8
uint32_t pat[pats][patLen] = {
	// Germany
	{
		Color(0x20, 0x20, 0x20),
		Color(0x20, 0x20, 0x20),
		Color(0xff, 0x00, 0x00),
		Color(0xff, 0x00, 0x00),
		Color(0xff, 0xff, 0x00),
		Color(0xff, 0xff, 0x00),
		Color(0x00, 0x00, 0x00),
		Color(0x00, 0x00, 0x00),
	},

	// Stripes
	{
		0x00ffffff,
		0x00000000,
		0x00ffffff,
		0x00000000,
		0x00ffffff,
		0x00ffffff,
		0x00ffffff,
		0x00000000,
	},

	// Bavaria
	{
		Color(0xff, 0xff, 0xff),
		Color(0x20, 0x20, 0xff),
		Color(0xff, 0xff, 0xff),
		Color(0x20, 0x20, 0xff),
		Color(0xff, 0xff, 0xff),
		Color(0x20, 0x20, 0xff),
		Color(0xff, 0xff, 0xff),
		Color(0x20, 0x20, 0xff),
	},


	// full color
	{
		0x00ff0000,
		0x0000ff00,
		0x000000ff,
		0x00ff00ff,
		0x0000ffff,
		0x00ffff00,
		0x00ffffff,
		0x00000000,
	},


	// purple
	{
		0x00ffffff,
		0x00ff80ff,
		0x00ff00ff,
		0x00800080,
		0x00400040,
		0x00200020,
		0x00100010,
		0x00000000,
	},
};
void animation_patternScroll(int frame) {
  fx_scroll();

  int thickness = 4;
  
  int p = (frame / NUM_LEDS) % pats;
  int row = ((frame / thickness) % patLen);
  leds[0].r = pat[p][row] & 0xff;
  leds[0].g = (pat[p][row] >> 8) & 0xff;
  leds[0].b = (pat[p][row] >> 16) & 0xff;
}



void animation_police(int f) {
  int thickness = 32;
  int thickHalf = thickness >> 1;
  int ff = f / 5;
  int fblink = f % 4;
  uint32_t c = Color(0x00, 0xff, 0x00);  //Color(0x00, 0x00, 0xff);
  
  // Black out  
  memset(leds, 0x00, NUM_LEDS * 3);

  for(int i = 0; i < NUM_LEDS; i++ ) {
    if (((fblink == 0) && (((i + ff) % thickness) >> 2 == 0))
    ||  ((fblink == 2) && (((i + ff) % thickness) >> 2 == 1)))
      leds[i] = c;
  }
}
*/

#endif
