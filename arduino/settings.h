#ifndef __SETTINGS_H__
#define __SETTINGS_H__

// Settings
#include "EEPROM.h"


#define SETTINGS_SIGNATURE 0x55AA
#define SETTINGS_VERSION 0x02 // Increase to force factory reset

typedef struct {
  uint16_t signature; // Should be SETTINGS_SIGNATURE
  uint8_t version;

  int preset;
  uint8_t brightness;
  int frameDelay;
  
} Settings;

Settings settings;

void settings_reset() {
  settings.signature = SETTINGS_SIGNATURE;
  settings.version = SETTINGS_VERSION;
  
  settings.preset = DEFAULT_PRESET;
  settings.brightness = DEFAULT_BRIGHTNESS;
  settings.frameDelay = DEFAULT_FRAMEDELAY;
}


#define EEADDR 0 // Start location to write EEPROM data.

void settings_load() {
  EEPROM.get(EEADDR, settings);
  /*
  int address = EEADDR;
  for(int i = 0; i < sizeof(settings); i++) {
    *((uint8_t *)&settings + i) = EEPROM.readByte(address++);
  }
  */
}
void settings_save() {
  // See also the general purpose writeBytes() and readBytes() for BLOB in EEPROM library
  //int address = 0;
  
  //EEPROM.writeBytes(&settings, sizeof(settings));
  //EEPROM.writeByte(address, -128)
  
  EEPROM.put(EEADDR, settings);
  /*
  int address = EEADDR;
  for(int i = 0; i < sizeof(settings); i++) {
    EEPROM.writeByte(address++, *((uint8_t *)&settings + i));
  }
  */
  delay(200);
  #ifdef ESP8266
    Serial.print(F("EEPROM.commit..."));
    if (EEPROM.commit()) {
      Serial.println(F("OK"));
    } else {
      Serial.println(F("failed"));
    }
    delay(200);
  #endif
}


void settings_setup() {
  Serial.println(F("settings_setup"));
  
  settings_reset();
  
  // EEPROM begin
  #ifdef ESP8266
  Serial.print(F("settings_setup: EEPROM.begin..."));
  EEPROM.begin(sizeof(settings));
  
  /*
  if (!EEPROM.begin(sizeof(settings))) {
    putln("failed!");
    return;
  }
  */
  #endif
  Serial.println(F("OK"));
  delay(200); // Problems when not waiting a bit!
  
  settings_load();
  
  // Check if signature is valid
  if ((settings.signature != SETTINGS_SIGNATURE) || (settings.version != SETTINGS_VERSION)) {
    
    // If signature invalid: Restore defaults
    Serial.println(F("settings: Signature/version invalid. resetting to defaults..."));
    /*
    for(int i = 0; i < sizeof(settings); i++) {
      putln(*((uint8_t *)&settings + i));
    }
    */
    settings_reset();
    settings_save();
  }

}
#endif
