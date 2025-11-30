#include "vl53lx_class.h"
#include "tof.h"

ToFSensor::ToFSensor()
{
  sensor = std::make_unique<VL53LX>(&Wire, xshut);
}

void ToFSensor::initialize() {
  Wire.setSDA(sda);
  Wire.setSCL(scl);
  // Initialize I2C bus.
  Wire.begin();

  // Configure VL53LX satellite component.
  sensor->begin();

  // Switch off VL53LX satellite component.
  sensor->VL53LX_Off();

  //Initialize VL53LX satellite component.
  sensor->InitSensor(0x12);

  // Start Measurements
  sensor->VL53LX_StartMeasurement();
}

int ToFSensor::read_distance() {
  VL53LX_MultiRangingData_t MultiRangingData;
  VL53LX_MultiRangingData_t *pMultiRangingData = &MultiRangingData;
  uint8_t NewDataReady = 0;
  int no_of_object_found = 0;
  int status;

  do {
    status = sensor->VL53LX_GetMeasurementDataReady(&NewDataReady);
  } while (!NewDataReady);

  if ((!status) && (NewDataReady != 0)) {
    status = sensor->VL53LX_GetMultiRangingData(pMultiRangingData);
    no_of_object_found = pMultiRangingData->NumberOfObjectsFound;
    
    if(no_of_object_found >= 1){
      return pMultiRangingData->RangeData[0].RangeMilliMeter;
    }
    if (status == 0) {
      status = sensor->VL53LX_ClearInterruptAndStartMeasurement();
    }
  }
  return -1;
}

void ToFSensor::show_measurement() {
  VL53LX_MultiRangingData_t MultiRangingData;
  VL53LX_MultiRangingData_t *pMultiRangingData = &MultiRangingData;
  uint8_t NewDataReady = 0;
  int no_of_object_found = 0, j;
  char report[64];
  int status;

  do {
    status = sensor->VL53LX_GetMeasurementDataReady(&NewDataReady);
  } while (!NewDataReady);

  if ((!status) && (NewDataReady != 0)) {
    status = sensor->VL53LX_GetMultiRangingData(pMultiRangingData);
    no_of_object_found = pMultiRangingData->NumberOfObjectsFound;
    snprintf(report, sizeof(report), "VL53LX Satellite: Count=%d, #Objs=%1d ", pMultiRangingData->StreamCount, no_of_object_found);
    Serial.print(report);
    for (j = 0; j < no_of_object_found; j++) {
      if (j != 0) Serial.print("\r\n                               ");
      Serial.print("status=");
      Serial.print(pMultiRangingData->RangeData[j].RangeStatus);
      Serial.print(", D=");
      Serial.print(pMultiRangingData->RangeData[j].RangeMilliMeter);
      Serial.print("mm");
      Serial.print(", Signal=");
      Serial.print((float)pMultiRangingData->RangeData[j].SignalRateRtnMegaCps / 65536.0);
      Serial.print(" Mcps, Ambient=");
      Serial.print((float)pMultiRangingData->RangeData[j].AmbientRateRtnMegaCps / 65536.0);
      Serial.print(" Mcps");
    }
    Serial.println("");
    if (status == 0) {
      status = sensor->VL53LX_ClearInterruptAndStartMeasurement();
    }
  }
}

bool ToFSensor::read_measurement(VL53LX_MultiRangingData_t *data) {
  uint8_t ready = 0;
  int status;
  do {
    status = sensor->VL53LX_GetMeasurementDataReady(&ready);
  } while (!ready);

  if (status != 0) return false;

  sensor->VL53LX_GetMultiRangingData(data);
  return true;
}
