#ifndef __IF_NETIO_H__
#define __IF_NETIO_H__
// include networking
//#NOTdefine NETWORK
  #include <EtherCard.h>

  // #define NETWORK_MAC { 0x00,0x22,0xf9,0x01,0xaf,0x05 }  // IO1 ATMEGA644
  // #define NETWORK_IP { 192,168,4,138 }
  
  #define NETWORK_MAC { 0x00,0x22,0xf9,0x01,0x7f,0xe3 } // eFace ATMEGA32
  #define NETWORK_IP { 192,168,4,137 }


  // ethernet interface mac address, must be unique on the LAN
  static byte mymac[] = NETWORK_MAC;
  static byte myip[] = NETWORK_IP;
  
  byte Ethernet::buffer[500];
  BufferFiller bfill;


  int netio_setup() {
    //@TODO: Load/store ip and mac from eeprom!
    
    if (ether.begin(sizeof Ethernet::buffer, mymac, 28) == 0) {
      Serial.println( "# Failed to access Ethernet controller");
      return -1;
    }
    ether.staticSetup(myip);
    
    return 0;
  }

  word netio_loop() {
    word len = ether.packetReceive();
    word pos = ether.packetLoop(len);
    
    if (pos) {
      char* data = (char *) Ethernet::buffer + pos;
      if (strncmp("GET ", data, 4) == 0) {

        if (strncmp("GET /next ", data, 10) == 0) {
          frame = 0;
          preset = (preset + 1) % presets;
          fxLoadPreset(preset);
          //ether.httpServerReply(net_content());
        }
        else if (strncmp("GET /prev ", data, 10) == 0) {
          frame = 0;
          preset = (preset + presets - 1) % presets;
          fxLoadPreset(preset);
          //ether.httpServerReply(net_content());
        }
        
        // Always return page on every GET
        ether.httpServerReply(net_content());
      }
    }
    
    return pos;
  }

  static word net_content() {
    long t = millis() / 1000;
    word h = t / 3600;
    byte m = (t / 60) % 60;
    byte s = t % 60;
    bfill = ether.tcpOffset();
    bfill.emit_p(PSTR(
    "HTTP/1.0 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Pragma: no-cache\r\n"
    "\r\n"
    //"<meta http-equiv='refresh' content='1'/>"
    "<html>"
    "<head>"
    "<title>ledControl</title>" 
    "</head>"
    "<body>"
    "<h1>ledControl</h1>"
    "uptime=$D$D:$D$D:$D$D <a href=\"/\">refresh</a><br />"
    "preset=$D/$D <a href=\"/prev\">prev</a> | <a href=\"/next\">next</a><br />"
    "frame=$D"
    "</body>"
    "</html>"
    ),
      h/10, h%10, m/10, m%10, s/10, s%10,
      (byte)preset, (byte)presets,
      frame);
    return bfill.position();
  }

#endif