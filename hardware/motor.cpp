#include "motor.h"

Motor::Motor()
{

}

void Motor::initialize() {
  pinMode(motorIN1Pin, OUTPUT);
  pinMode(motorIN2Pin, OUTPUT);
  pinMode(motorIN3Pin, OUTPUT);
  pinMode(motorIN4Pin, OUTPUT);
}

void Motor::goForward() {
  digitalWrite(motorIN1Pin, HIGH);
  digitalWrite(motorIN2Pin, LOW);
  digitalWrite(motorIN3Pin, HIGH);
  digitalWrite(motorIN4Pin, LOW);
}

void Motor::goBackward() {
  digitalWrite(motorIN1Pin, LOW);
  digitalWrite(motorIN2Pin, HIGH);
  digitalWrite(motorIN3Pin, LOW);
  digitalWrite(motorIN4Pin, HIGH);
}

void Motor::goLeft() {
  digitalWrite(motorIN1Pin, LOW);
  digitalWrite(motorIN2Pin, HIGH);
  digitalWrite(motorIN3Pin, HIGH);
  digitalWrite(motorIN4Pin, LOW);
}

void Motor::goRight() {
  digitalWrite(motorIN1Pin, HIGH);
  digitalWrite(motorIN2Pin, LOW);
  digitalWrite(motorIN3Pin, LOW);
  digitalWrite(motorIN4Pin, HIGH);
}

void Motor::stop() {
  digitalWrite(motorIN1Pin, LOW);
  digitalWrite(motorIN2Pin, LOW);
  digitalWrite(motorIN3Pin, LOW);
  digitalWrite(motorIN4Pin, LOW);
}
