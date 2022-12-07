#ifndef __IF_WIFI_H__
#define __IF_WIFI_H__

#include <WiFi.h>

WiFiServer server(80);

int wifi_setup() {
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
      delay(frameDelay);
      //Serial.print(".");
      
      update(); // Continue with the LED stuff!
  }
  Serial.println("OK");
  
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  
  /*
  // NTP
  //init and get the time
  Serial.print("NTP...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Failed to obtain time");
    return;
  }
  Serial.println(&timeinfo, "OK: %A, %B %d %Y %H:%M:%S");
  */


  Serial.print("HTTP server...");
  server.begin();
  Serial.println("OK");
  
  return 0;
}

void wifi_loop() {
  int i, j;
  char c;
  
  WiFiClient client = server.available();   // listen for incoming clients

  if (client) {                             // if you get a client,
    Serial.println("New Client.");           // print a message out the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        
        if (c == '\n') {                    // if the byte is a newline character

          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();

            // the content of the HTTP response follows the header:
            client.println("<html><head><title>LED Control</title></head>");
            client.println("<body>");
            client.println("<h1><a href=\"/\">LED Control</a></h1>");
            
            client.print("NUM_LEDS="); client.print(NUM_LEDS); client.println("<br />");
            client.print("frame="); client.print(frame); client.println("<br />");

            client.print("preset="); client.print(preset);
            client.print(" <a href=\"/preset?prev\">prev</a>");
            client.print(" | <a href=\"/preset?next\">next</a>");
            client.println("<br />");

            client.print("brightness="); client.print(brightness);
            client.print(" <a href=\"/brightness?lower\">lower</a>");
            client.print(" | <a href=\"/brightness?higher\">higher</a>");
            
            client.println("<br />");


            client.print("mode="); client.print(mode);
            client.print(" <a href=\"/mode?auto\">auto</a>");
            client.println("<br />");

            client.println("<a href=\"/raw?010101020202040404080808101010202020404040808080\">test raw data</a><br />");
            client.println("<a href=\"/flash\">flash</a><br />");
            client.println("<a href=\"/restart\">restart</a><br />");
            
            client.println("</body>");
            client.println("</html>");

            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            break;
          } else {    // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }

        
        // Check to see if the client request was "GET /H" or "GET /L":
        if (currentLine.endsWith("GET /mode?auto")) {
          mode = 0;
        } else

        
        if (currentLine.endsWith("GET /flash")) {
          flash();
        } else
        if (currentLine.endsWith("GET /restart")) {
          ESP.restart();
        } else

        
        if (currentLine.endsWith("GET /brightness?lower")) {
          if (brightness >= BRIGHTNESS_STEP) brightness -= BRIGHTNESS_STEP;
          LEDS.setBrightness(brightness);
        } else
        if (currentLine.endsWith("GET /brightness?higher")) {
          if (brightness <= (255-BRIGHTNESS_STEP)) brightness += BRIGHTNESS_STEP;
          LEDS.setBrightness(brightness);
        } else

        
        if (currentLine.endsWith("GET /preset?next")) {
          // Next preset
          frameGlobal = 0;
          frame = 0;
          preset = (preset + 1) % presets;
          fxLoadPreset(preset);
        } else
        if (currentLine.endsWith("GET /preset?prev")) {
          // Next preset
          frameGlobal = 0;
          frame = 0;
          preset = (preset + presets - 1) % presets;
          fxLoadPreset(preset);
        } else
        if ((c == ' ') && (currentLine.startsWith("GET /preset?"))) {
          // Change to given preset
          int o = 12;
          //@TODO: Parse int at offset o
          
          
        } else

        
        // "GET /raw?" + HEX
        //if ((currentLine.length() == (9 + NUM_LEDS*3*2)) && (currentLine.startsWith("GET /raw?"))) {
        if ((c == ' ') && (currentLine.startsWith("GET /raw?"))) {
          int o = 9;

          // Determine the number of LEDs covered by the given hex data (2*3 bytes per LED)
          //int n = NUM_LEDS;
          int n = (currentLine.length() - o) / (3*2);
          
          memset(leds, 0x00, NUM_LEDS * 3); // Black out all
          
          for(i = 0; i < n; i++) {
            //@FIXME: For some reason R and G are swapped here...
            //leds[i].r = hexCharToInt(currentLine.charAt(o++)) * 16 + hexCharToInt(currentLine.charAt(o++));
            leds[i].g = hexCharToInt(currentLine.charAt(o++)) * 16 + hexCharToInt(currentLine.charAt(o++));
            leds[i].r = hexCharToInt(currentLine.charAt(o++)) * 16 + hexCharToInt(currentLine.charAt(o++));
            leds[i].b = hexCharToInt(currentLine.charAt(o++)) * 16 + hexCharToInt(currentLine.charAt(o++));
          }
          
          FastLED.show();
          mode = 1; // Prevent "auto"
          
        }
      }
    }
    // close the connection:
    client.stop();
    Serial.println("Client disconnected.");
  }
}



#endif