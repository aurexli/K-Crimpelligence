#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include <memory>

class Motor {
public:
  Motor();
  void initialize();
  void goForward();
  void goBackward();
  void goLeft();
  void goRight(); 
  void stop();

private:
  int motorIN1Pin = 10;
  int motorIN2Pin = 11;
  int motorIN3Pin = 12;
  int motorIN4Pin = 13;
};

#endif
