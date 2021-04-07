#ifndef __IF_MQTT_H__
#define __IF_MQTT_H__

// MQTT stuff (PubSubClient)
#include <PubSubClient.h>
String mqtt_host = "192.168.4.114";
int mqtt_port = 1883;
String mqtt_client_id = "ESP32LED";
String mqtt_topic = "house/announce";

WiFiClient espClient; // For connecting to MQTT
PubSubClient mqttClient(espClient);


void mqtt_init() {
  mqttClient.setServer(mqtt_host.c_str(), mqtt_port);
  mqttClient.setCallback(mqttCallback);

  mqtt_reconnect();
}

void mqtt_reconnect() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    
    put("if_mqtt: Connecting to " + String(mqtt_host) + ":" + String(mqtt_port) + "..."); //putFlush();
    
    // Attempt to connect
    //boolean connect (clientID, willTopic, willQoS, willRetain, willMessage)
    if (mqttClient.connect(mqtt_client_id.c_str())) {
      //put("connected"); //putFlush();
      
      mqttClient.publish("house/log", "Hello from ledControl!");
      mqttClient.subscribe("house/log");
      
      mqttClient.subscribe(mqtt_topic.c_str());
      
    } else {
      //put("failed, rc="); //putFlush();
      //Serial.print(mqttClient.state());
      //delay(5000);
      //state = INTERFACE_STATE_ERROR / INACTIVE / ACTIVATING
      return;
    }
  }
}

void mqtt_update() {
  // MQTT stuff
  if (!mqttClient.connected()) {
    mqtt_reconnect();
  }
  mqttClient.loop();
}

void mqtt_send() {
  // Actually send payload over the interface
  char payload[sizeof(msg->payload)];
  msg->payload.toCharArray(payload, sizeof(payload));
  
  mqttClient.publish(mqtt_topic.c_str(), payload);
}


#endif