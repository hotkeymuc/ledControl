
/*
#ifdef __AVR__
  #include <avr/power.h>
#endif
*/


/*

USAGE:
  * Press button short to switch preset
  * Press button long (3 seconds) to store current settings

SERIAL COMMANDS:
  * p/P = next/previous preset
  * b/B = brighter/dimmer
  * d/D = slower/faster
  * ? = help
  * r = show raw image
  * l = list FX layers
  * f = define a new FX
  * x = clear current FX layers

TODO:
  OK Store presets in EEPROM
  * Use &CRGB[] instead of passing the whole struct (fx_XXX use struct as argument?!)
  * Store network config in EEPROM
  + UDP receiver
*/  

#define USE_ARDUINO
//#define USE_NETIO
//#define USE_ESP32


#define CONTROL_BAUD 115200
#define DEBOUNCE_MILLIS 100


// Less LEDs for testing
//#define NUM_LEDS 9
//#define NUM_LEDS 150  // 5m, 30/m
#define NUM_LEDS 300  // 5m, 60/m
//#define NUM_LEDS 512
//#define NUM_LEDS 600  // 5m, 120/m
//#define NUM_LEDS 720  // 5m, 144/m
//#define NUM_LEDS 1024


#define BRIGHTNESS_STEP 8
#define DEFAULT_BRIGHTNESS 128
#define FPS 60
#define DEFAULT_FRAMEDELAY (1000 / FPS)
#define DEFAULT_PRESET  9 //6





//////////////////// Arduino Uno
#ifdef USE_ARDUINO
  #define BUTTON_PIN 12
  #define LED_PIN 6  // 3,5,6,9,10,11
#endif


//////////////////// ESP32
#ifdef USE_ESP32
  #define BUTTON_PIN 0  //18
  #define LED_PIN 19 // 19, 23
  
  // 1000000 (1MBaud) works fine!
  //#define CONTROL_BAUD 115200
  //#define CONTROL_BAUD 250000
  //#define CONTROL_BAUD 1000000
  //#define CONTROL_BAUD 2000000
  
  #define USE_WIFI
  //#define USE_NTP
  //#define USE_MQTT
#endif


//////////////////// Net IO
#ifdef USE_NETIO
  /*
  NetIO free pins:
    Ardui. Chip NetIO
    
    PIN16  PC0  D-SUB-25 Pin 2 "Ausgang 1"
    PIN17  PC1  D-SUB-25 Pin 3 "Ausgang 2"
    PIN18  PC2  D-SUB-25 Pin 4 "Ausgang 3"
    PIN19  PC3  D-SUB-25 Pin 5 "Ausgang 4"
    PIN20  PC4  D-SUB-25 Pin 6 "Ausgang 5"
    PIN21  PC5  D-SUB-25 Pin 7 "Ausgang 6"
    PIN22  PC6  D-SUB-25 Pin 8 "Ausgang 7"
    PIN23  PC7  D-SUB-25 Pin 9 "Ausgang 8"
  
    ADC0   PA0  D-SUB-25 Pin 10 "Eingang 1"
    ADC1   PA1  D-SUB-25 Pin 11 "Eingang 2"
    ADC2   PA2  D-SUB-25 Pin 12 "Eingang 3"
    ADC3   PA3  D-SUB-25 Pin 13 "Eingang 4"
    ADC4   PA4  Terminal "ADC1"
    ADC5   PA5  Terminal "ADC2"
    ADC6   PA6  Terminal "ADC3"
    ADC7   PA7  Terminal "ADC4"
  
  
    
    PIN12  PD4  EXT Pin 3
    PIN13  PD5  EXT Pin 4
    PIN14  PD6  EXT Pin 5
    PIN15  PD7  EXT Pin 6
  */
  
  // Hardware button (10)
  #define BUTTON_PIN A0
  
  // WS2812 data pin (usually PIN13)
  // PD5 = EXT-4
  // PC0 = J3-AUSGANG-1
  // PC7 = J3-AUSGANG-8
  //#define LED_PIN 13
  #define LED_PIN 6  // NetIO / Uno

  #define USE_NETIO
#endif

#ifdef USE_NETIO
  #include "if_netio.h"
#endif


//////////////////// ESP32
#ifdef USE_ESP32
  const char* ssid     = "htkair";
  const char* password = "facedefecd";

  #define USE_WIFI
#endif


#ifdef USE_WIFI
  #include "if_wifi.h"
#endif


#ifdef USE_NTP
  // NTP
  const char* ntpServer = "pool.ntp.org";
  const long  gmtOffset_sec = 3600;
  const int   daylightOffset_sec = 3600;
#endif


#ifdef USE_MQTT
  void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    // Handle incoming MQTT message
    
    /*
    mqtt_incoming.topic = String(topic);
    
    mqtt_incoming.payload = "";
    for (int i = 0; i < length; i++) {
      mqtt_incoming.payload.concat((char)payload[i]);
    }
  
    // Callback must be static - we have no way of accessing on_message_received, so we need a global data structure...
    //if (on_message_received != NULL) on_message_received(&m);
    mqtt_incoming.valid = true;
    */
  }
  #include "if_mqtt.h"
#endif

#include "settings.h"

#include "led.h"

#include "if_button.h"

#include "if_serial.h"


void setup() {
  Serial.begin(CONTROL_BAUD);
  
  Serial.print(F("#ledControl "));
  Serial.println(__DATE__);

  //delay(500);

  // Init button
  button_setup();
  
  
  settings_setup();
  // Apply settings
  preset = settings.preset % presets;
  brightness = settings.brightness;
  frameDelay = settings.frameDelay;
  
  //Serial.print(F("#LEDs..."));
  led_setup();

  
  // Init effects...
  fxLoadPreset(preset);

  
  #ifdef USE_WIFI
    // Network
    Serial.println(F("# Network..."));
    wifi_setup();
    Serial.println(F("OK"));
  #endif
  #ifdef USE_NETIO
    netio_setup();
  #endif
}


void loop() {
  
  button_loop();
  
  serial_loop();

  led_loop();
  
  // Check network
  #ifdef USE_WIFI
    wifi_loop();
  #endif
  #ifdef USE_NETIO
    netio_loop();
  #endif
  

}
