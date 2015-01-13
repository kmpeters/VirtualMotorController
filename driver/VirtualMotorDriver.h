/*
FILENAME...   VirtualMotorDriver.h
USAGE...      Motor driver support for the virtual motor controller.

Kevin Peterson
January 6, 2015

*/

#include "asynMotorController.h"
#include "asynMotorAxis.h"

#define MAX_VIRTUAL_MOTOR_AXES 32     /* motor.h sets the maximum number of axes */
#define BUFF_SIZE 20		/* Maximum length of string to/from VirtualMotor */

// No controller-specific parameters yet
#define NUM_VIRTUAL_MOTOR_PARAMS 0  

class epicsShareClass VirtualMotorAxis : public asynMotorAxis
{
public:
  /* These are the methods we override from the base class */
  VirtualMotorAxis(class VirtualMotorController *pC, int axisNo);
  void report(FILE *fp, int level);
  asynStatus move(double position, int relative, double min_velocity, double max_velocity, double acceleration);
  //asynStatus moveVelocity(double min_velocity, double max_velocity, double acceleration);
  //asynStatus home(double min_velocity, double max_velocity, double acceleration, int forwards);
  asynStatus stop(double acceleration);
  asynStatus poll(bool *moving);
  asynStatus setPosition(double position);
  //asynStatus setClosedLoop(bool closedLoop);

private:
  VirtualMotorController *pC_;          /**< Pointer to the asynMotorController to which this axis belongs.
                                   *   Abbreviated because it is used very frequently */
  int axisIndex_;
  //double stepsPerRev_;
  asynStatus sendAccelAndVelocity(double accel, double velocity);
  
friend class VirtualMotorController;
};

class epicsShareClass VirtualMotorController : public asynMotorController {
public:
  VirtualMotorController(const char *portName, const char *VirtualMotorPortName, int numAxes, double movingPollPeriod, double idlePollPeriod);

  void report(FILE *fp, int level);
  VirtualMotorAxis* getAxis(asynUser *pasynUser);
  VirtualMotorAxis* getAxis(int axisNo);

//private:
//  char buff_[BUFF_SIZE];
  
friend class VirtualMotorAxis;
};
