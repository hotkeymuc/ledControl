#ifndef __IF_SERIAL_H__
#define __IF_SERIAL_H__
void serial_loop() {
  int d;
  int i, j;
  FxLayer *fx;
  uint32_t col;
  uint16_t num_leds;
  
  // Check serial
  while (Serial.available() > 0) {
    uint8_t c = Serial.read();

    switch(c) {
      case '\n':
        Serial.print('#');
        break;
      case '?':
        Serial.println(F("p/P = next/previous preset"));
        Serial.println(F("b/B = brighter/dimmer"));
        Serial.println(F("d/D = slower/faster"));
        Serial.println(F("r = show raw image"));
        Serial.println(F("l = list FX layers"));
        Serial.println(F("f = define a new FX"));
        Serial.println(F("x = clear current FX layers"));
        break;

      case 'b':
        // Brighter
        if (brightness < 0xff) brightness++;
        LEDS.setBrightness(brightness);
        break;
      case 'B':
        // Dimmer
        if (brightness > 0) brightness--;
        LEDS.setBrightness(brightness);
        break;
    
      case 'x':
        fxLayerCount = 0;
        Serial.println(F("#Cleared"));
        break;
    
    
      case 'f':
        // Add/set FX Layer
        mode = 0;
        i = Serial.parseInt();
        if (i >= MAX_FXS) {
          Serial.println(F("#OOR"));
          continue;
        }
        
        fxLayerSet(
          &fxLayers[i],
          (FxType)(Serial.parseInt() & 0xff),
          Serial.parseInt(), Serial.parseInt(),  // frame set up
          Serial.parseInt(), Serial.parseInt(),  // size set up
          Serial.parseInt(), Serial.parseInt(), Serial.parseInt(), Serial.parseInt()  // params
        );
        Serial.println("#FxLayer added.");
        if (i >= fxLayerCount) fxLayerCount = i+1;
        c = 'l';  // List!
        break;
    
      case 'l':
        // List layers
        for (i = 0; i < fxLayerCount; i++) {
          fx = &fxLayers[i];
          Serial.print(F("#FxLayer ")); Serial.println(i);
          Serial.print(F("#  fx=")); Serial.println(fx->fx);
          Serial.print(F("#  frameEach=")); Serial.println(fx->frameEach);
          Serial.print(F("#  frameOfs=")); Serial.println(fx->frameOfs);
          Serial.print(F("#  numStart=")); Serial.println(fx->numStart);
          Serial.print(F("#  numCount=")); Serial.println(fx->numCount);
        }
        break;
    
      case 'p':
        // Next preset
        frame = 0;
        preset = (preset + 1) % presets;
        fxLoadPreset(preset);
        break;
    
      case 'P':
        // preset #
        frame = 0;
        preset = Serial.parseInt();
        fxLoadPreset(preset);
        break;

      case 'D':
        if (frameDelay > 1) frameDelay --;
        break;
    
      case 'd':
        frameDelay++;
        break;
    
      case 'r':
        // Display raw image
        
        mode = DISPLAY_MODE_RAW;
        int v;
        
        // Read start and size
        while (Serial.available() < 4) {}
        i = ((uint16_t)Serial.read() << 8) | (uint16_t)Serial.read();
        num_leds = ((uint16_t)Serial.read() << 8) | (uint16_t)Serial.read();
        
        // Black out  
        //memset(leds, 0x00, NUM_LEDS * 3);
  
        int timeOut = 5000;
        // Start over
        rC = 0;
        while ((num_leds > 0) && (timeOut > 0)) {
          v = Serial.read();
          
          if (v < 0) {
            timeOut--;
            if (timeOut <= 0) {
              Serial.println(F("TO"));
              break;
            }
            delayMicroseconds(10);
            continue;
          }
        
          switch (rC) {
            case 0:  leds[i].r = v;  break;
            case 1:  leds[i].g = v;  break;
            case 2:  leds[i].b = v;  break;
          }
          
          rC++;
          if (rC > 2) {
            rC = 0;
            i++;
            num_leds--;
          }
        }
        
        Serial.println(F("Displaying..."));
        /*
        for (i = 0; i < NUM_LEDS; i++) {
          strip.setPixelColor(i, leds[i].r * 0x010000 + leds[i].g * 0x000100 + leds[i].b * 0x000001);
        }
        strip.show(); // Initialize all pixels to 'off'
        */
        FastLED.show();
  
        
        //delay(1000);
        //Serial.println("Back to auto...");
        //mode = 0;      
        break;
    }

  }
}

#endif
