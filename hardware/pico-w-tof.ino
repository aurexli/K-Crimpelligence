#include "tof.h"
#include "motor.h"
#include "secrets.h"
#include "wifi_helper.h"

#include <WiFi.h>

WifiHelper wh; // use wh(123) to set EEPROM offset
// Set web server port number to 80
WiFiServer server(80);

// Variable to store the HTTP request
String header;

// Previous time
unsigned long previousMillis = 0; 
// Define timeout for server client in milliseconds (example: 2000ms = 2s)
const long clientTimeout = 2000;

int pidx = -1;

ToFSensor tof_sensor;
Motor motor;
// Duration of the motor in ms
int motorInterval = 1000;
int current_distance = -1;
int current_direction = -1; // forward = 0, backward = 1, left = 2, right = 3

void setup() {
  // Initialize serial for output.
  Serial.begin(115200);
  Serial.println("Starting...");

  uint32_t ts_start = millis();
  bool res = wh.connect(WIFI_SSID, WIFI_AUTH);
  Serial.print("Timing connect(): "); Serial.print(millis()-ts_start); Serial.println("ms");
  Serial.print("Result="); Serial.println(res);

  tof_sensor.initialize();
  motor.initialize();

  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Start server
  server.begin();
}

void loop() {
  unsigned long currentMillis = millis();
  WiFiClient client = server.accept();      // Listen for incoming clients
  current_distance = tof_sensor.read_distance();
  tof_sensor.show_measurement();

  // stop motors if motorInterval is reached
  if (motorInterval > -1 && currentMillis - previousMillis >= motorInterval) {
    previousMillis = currentMillis;
    motor.stop();
    motorInterval = -1;
    current_direction = -1;
  } else {
    if(motorInterval > -1 && current_direction == 0){
      // Check if we are running into an obstacle
      if(current_distance <= 100 && current_distance != -1){
        Serial.println("Emergency stop.");
        motor.stop();
        motorInterval = -1;
        current_direction = -1;
      }
    }
  }

  // check requests
  if (client) {                             // If a new client connects,
    previousMillis = currentMillis;
    Serial.println("New Client.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected() && currentMillis - previousMillis <= clientTimeout) {  // loop while the client's connected
      currentMillis = millis();
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        header += c;
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            
            Serial.println(header);
            if (header.indexOf("GET /drive") >= 0) {
              // GET /drive?direction=forward&duration=1000 HTTP/1.1
              pidx = header.indexOf("?direction=");
              int pidx2 = header.indexOf("&duration=");
              String direction = header.substring(pidx + 11, pidx2);
              pidx = header.indexOf(" HTTP/", pidx2);
              String duration = header.substring(pidx2 + 10, pidx);

              Serial.println("Drive");
              Serial.println(direction);
              Serial.println(duration);
              if(direction == "forward"){
                current_direction = 0;
                motor.goForward();
              } else if(direction == "backward"){
                current_direction = 1;
                motor.goBackward();
              }
              if(atoi(duration.c_str())){
                motorInterval = atoi(duration.c_str());
              } else {
                motorInterval = 1000;
              }
            } else if (header.indexOf("GET /turn") >= 0) {
              // GET /turn?direction=left&degree=90 HTTP/1.1
              pidx = header.indexOf("?direction=");
              int pidx2 = header.indexOf("&degree=");
              String direction = header.substring(pidx + 11, pidx2);
              pidx = header.indexOf(" HTTP/", pidx2);
              String degree = header.substring(pidx2 + 8, pidx);

              Serial.println("Turn");
              Serial.println(direction);
              Serial.println(degree);
              if(direction == "left"){
                current_direction = 2;
                motor.goLeft();
              } else if(direction == "right"){
                current_direction = 3;
                motor.goRight();
              }
              if(atoi(degree.c_str())){
                // 90 degree == 500 duration
                motorInterval = atoi(degree.c_str())*50/9;
              } else {
                motorInterval = 1000;
              }
            } else if (header.indexOf("GET /spin") >= 0) {
              Serial.println("Spin");
              motor.goLeft();
              motorInterval = 2000;
              current_direction = 2;
            } else if (header.indexOf("GET /stop") >= 0) {
              Serial.println("Stop");
              motor.stop();
              motorInterval = -1;
              current_direction = -1;
            } 
            
            // Display the HTML web page
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // CSS to style the on/off buttons 
            // Feel free to change the background-color and font-size attributes to fit your preferences
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".greenbutton { background-color: #4CAF50; border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".greybutton {background-color: #555555;}");
            client.println(".redbutton {background-color: #ff6666;}</style></head>");

            // Web Page Heading
            client.println("<body><h1>Race car</h1>");
            // Buttons
            client.println("<p><a href=\"/drive?direction=forward&duration=2000\"><button class=\"greenbutton redbutton\">Go!</button></a></p>");
            client.println("<p><a href=\"/drive?direction=backward&duration=2000\"><button class=\"greenbutton\">Go backward</button></a></p>");
            client.println("<p><a href=\"/turn?direction=left&degree=90\"><button class=\"greenbutton\">To the left</button></a></p>");
            client.println("<p><a href=\"/turn?direction=right&degree=90\"><button class=\"greenbutton\">To the right</button></a></p>");
            client.println("<p><a href=\"/spin\"><button class=\"greenbutton\">Spin</button></a></p>");
            client.println("<p><a href=\"/stop\"><button class=\"greenbutton greybutton\">Stop!</button></a></p>");
 
            client.println("</body></html>");
            
            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
}
