#ifndef __IF_BUTTON_H__
#define __IF_BUTTON_H__

#define BUTTON_DELAY_LONG 2000

void button_setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void button_loop() {
  unsigned long now, press_start;
  int d;
  
  // Check button
  if (digitalRead(BUTTON_PIN) == LOW) {
    
    Serial.println(F("#Button"));
    
    now = millis();
    
    press_start = now;
    // De-bounce
    delay(DEBOUNCE_MILLIS);
    while (digitalRead(BUTTON_PIN) == LOW) {
      delayMicroseconds(10);
    }

    now = millis();
    d = (now - press_start);
    
    // Now it's high!
    delay(DEBOUNCE_MILLIS);

    if (d >= BUTTON_DELAY_LONG) {
      // Long press
      
      // Save preset
      Serial.print(F("Saving settings..."));
      
      // Flash greeen
      //(col >> 16) & 0xff, (col >> 8) & 0xff, (col) & 0xff
      fx_solid(leds, 0, NUM_LEDS, 0x00,0x80,0x00);
      led_show();
      
      settings.preset = preset;
      settings.brightness = brightness;
      settings.frameDelay = frameDelay;
      
      settings_save();
      
      delay(500);
      
      Serial.println(F("OK"));
      
    } else {
      // Short press
      
      frame = 0;
      preset = (preset + 1) % presets;
      fxLoadPreset(preset);
    }
    
  }
}
#endif
