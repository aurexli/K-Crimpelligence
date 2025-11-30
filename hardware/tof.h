#ifndef TOFSENSOR_H
#define TOFSENSOR_H

#include <Wire.h>
#include <vl53lx_class.h>
#include <memory>

class ToFSensor {
public:
  ToFSensor();
  void initialize();
  int read_distance();
  void show_measurement();
  bool read_measurement(VL53LX_MultiRangingData_t *data);


private:
  int xshut = 19;  // This is not important for now.
  uint8_t sda = 20;
  uint8_t scl =  21;
  // Just declare; do not call default constructor.
  std::unique_ptr<VL53LX> sensor;
};


#endif