/*
FILENAME... VirtualMotorDriver.cpp
USAGE...    Motor driver support for the virtual motor controller

Kevin Peterson
January 6, 2015

*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#include <iocsh.h>
#include <epicsThread.h>

#include <asynOctetSyncIO.h>

#include "asynMotorController.h"
#include "asynMotorAxis.h"

#include <epicsExport.h>
#include "VirtualMotorDriver.h"

#define NINT(f) (int)((f)>0 ? (f)+0.5 : (f)-0.5)

/** Creates a new VirtualMotorController object.
  * \param[in] portName          The name of the asyn port that will be created for this driver
  * \param[in] VirtualMotorPortName     The name of the drvAsynSerialPort that was created previously to connect to the VirtualMotor controller 
  * \param[in] numAxes           The number of axes that this controller supports 
  * \param[in] movingPollPeriod  The time between polls when any axis is moving 
  * \param[in] idlePollPeriod    The time between polls when no axis is moving 
  */
VirtualMotorController::VirtualMotorController(const char *portName, const char *VirtualMotorPortName, int numAxes, 
                                 double movingPollPeriod,double idlePollPeriod)
  :  asynMotorController(portName, numAxes, NUM_VIRTUAL_MOTOR_PARAMS, 
                         0, // No additional interfaces beyond those in base class
                         0, // No additional callback interfaces beyond those in base class
                         ASYN_CANBLOCK | ASYN_MULTIDEVICE, 
                         1, // autoconnect
                         0, 0)  // Default priority and stack size
{
  asynStatus status;
  int axis;
  VirtualMotorAxis *pAxis;
  static const char *functionName = "VirtualMotorController::VirtualMotorController";

  /* Connect to VirtualMotor controller */
  status = pasynOctetSyncIO->connect(VirtualMotorPortName, 0, &pasynUserController_, NULL);
  if (status) {
    asynPrint(this->pasynUserSelf, ASYN_TRACE_ERROR, 
      "%s: cannot connect to virtual motor controller\n",
      functionName);
  }

  // If additional information is required for creating axes (stepsPerUnit), comment out 
  // the following loop and make the user call VirtualMotorCreateAxis from the cmd file
  for (axis=0; axis<numAxes; axis++) {
    pAxis = new VirtualMotorAxis(this, axis);
  }

  startPoller(movingPollPeriod, idlePollPeriod, 2);
}


/** Creates a new VirtualMotorController object.
  * Configuration command, called directly or from iocsh
  * \param[in] portName          The name of the asyn port that will be created for this driver
  * \param[in] VirtualMotorPortName       The name of the drvAsynIPPPort that was created previously to connect to the VirtualMotor controller 
  * \param[in] numAxes           The number of axes that this controller supports 
  * \param[in] movingPollPeriod  The time in ms between polls when any axis is moving
  * \param[in] idlePollPeriod    The time in ms between polls when no axis is moving 
  */
extern "C" int VirtualMotorCreateController(const char *portName, const char *VirtualMotorPortName, int numAxes, 
                                   int movingPollPeriod, int idlePollPeriod)
{
  VirtualMotorController *pVirtualMotorController
    = new VirtualMotorController(portName, VirtualMotorPortName, numAxes, movingPollPeriod/1000., idlePollPeriod/1000.);
  pVirtualMotorController = NULL;
  return(asynSuccess);
}

/** Reports on status of the driver
  * \param[in] fp The file pointer on which report information will be written
  * \param[in] level The level of report detail desired
  *
  * If details > 0 then information is printed about each axis.
  * After printing controller-specific information it calls asynMotorController::report()
  */
void VirtualMotorController::report(FILE *fp, int level)
{
  fprintf(fp, "MVP 2001 motor driver %s, numAxes=%d, moving poll period=%f, idle poll period=%f\n", 
    this->portName, numAxes_, movingPollPeriod_, idlePollPeriod_);

  // Call the base class method
  asynMotorController::report(fp, level);
}

/** Returns a pointer to an VirtualMotorAxis object.
  * Returns NULL if the axis number encoded in pasynUser is invalid.
  * \param[in] pasynUser asynUser structure that encodes the axis index number. */
VirtualMotorAxis* VirtualMotorController::getAxis(asynUser *pasynUser)
{
  return static_cast<VirtualMotorAxis*>(asynMotorController::getAxis(pasynUser));
}

/** Returns a pointer to an VirtualMotorAxis object.
  * Returns NULL if the axis number encoded in pasynUser is invalid.
  * \param[in] axisNo Axis index number. */
VirtualMotorAxis* VirtualMotorController::getAxis(int axisNo)
{
  return static_cast<VirtualMotorAxis*>(asynMotorController::getAxis(axisNo));
}

//
// These are the VirtualMotorAxis methods
//

/** Creates a new VirtualMotorAxis object.
  * \param[in] pC Pointer to the VirtualMotorController to which this axis belongs. 
  * \param[in] axisNo Index number of this axis, range 0 to pC->numAxes_-1.
  * 
  * Initializes register numbers, etc.
  */
VirtualMotorAxis::VirtualMotorAxis(VirtualMotorController *pC, int axisNo)
  : asynMotorAxis(pC, axisNo),
    pC_(pC)
{
  //asynStatus status;
  
  axisIndex_ = axisNo + 1;

  // Allow CNEN to turn motor power on/off
  //setIntegerParam(pC->motorStatusGainSupport_, 1);
  //setIntegerParam(pC->motorStatusHasEncoder_, 1);

}


extern "C" int VirtualMotorCreateAxis(const char *VirtualMotorName, int axisNo)
{
  VirtualMotorController *pC;
  
  pC = (VirtualMotorController*) findAsynPortDriver(VirtualMotorName);
  if (!pC) 
  {
    printf("Error port %s not found\n", VirtualMotorName);
    return asynError;
  }

  pC->lock();
  new VirtualMotorAxis(pC, axisNo);
  pC->unlock();
  return asynSuccess;
}


/** Reports on status of the axis
  * \param[in] fp The file pointer on which report information will be written
  * \param[in] level The level of report detail desired
  *
  * After printing device-specific information calls asynMotorAxis::report()
  */
void VirtualMotorAxis::report(FILE *fp, int level)
{
  if (level > 0) {
    fprintf(fp, "  axis %d\n", axisNo_);
    fprintf(fp, "  axis index %d\n", axisIndex_);
 }

  // Call the base class method
  asynMotorAxis::report(fp, level);
}


asynStatus VirtualMotorAxis::sendAccelAndVelocity(double acceleration, double velocity, double baseVelocity) 
{
  asynStatus status;
  // static const char *functionName = "VirtualMotor::sendAccelAndVelocity";

  // Send the base velocity
  sprintf(pC_->outString_, "%d BAS %f", axisIndex_, baseVelocity);
  status = pC_->writeReadController();

  // Send the velocity
  sprintf(pC_->outString_, "%d VEL %f", axisIndex_, velocity);
  status = pC_->writeReadController();

  // Send the acceleration
  sprintf(pC_->outString_, "%d ACC %f", axisIndex_, acceleration);
  status = pC_->writeReadController();

  return status;
}


asynStatus VirtualMotorAxis::move(double position, int relative, double minVelocity, double maxVelocity, double acceleration)
{
  asynStatus status;
  // static const char *functionName = "VirtualMotorAxis::move";

  status = sendAccelAndVelocity(acceleration, maxVelocity, minVelocity);
  
  // Set the target position
  if (relative) {
    sprintf(pC_->outString_, "%d MR %d", axisIndex_, NINT(position));
  } else {
    sprintf(pC_->outString_, "%d MV %d", axisIndex_, NINT(position));
  }
  status = pC_->writeReadController();

  // If controller has a "go" command, send it here
  
  return status;
}

/*
asynStatus VirtualMotorAxis::home(double minVelocity, double maxVelocity, double acceleration, int forwards)
{
  // static const char *functionName = "VirtualMotorAxis::home";

  // Homing isn't currently implemented

  return asynSuccess;
}
*/


asynStatus VirtualMotorAxis::moveVelocity(double minVelocity, double maxVelocity, double acceleration)
{
  asynStatus status;
  //static const char *functionName = "VirtualMotorAxis::moveVelocity";

  // Call this to set the max current and acceleration
  status = sendAccelAndVelocity(acceleration, maxVelocity, minVelocity);

  sprintf(pC_->outString_, "%d JOG %f", axisIndex_, maxVelocity);
  status = pC_->writeReadController();
  return status;
}


asynStatus VirtualMotorAxis::stop(double acceleration )
{
  asynStatus status;
  //static const char *functionName = "VirtualMotorAxis::stop";

  sprintf(pC_->outString_, "%d AB", axisIndex_);
  status = pC_->writeReadController();
  return status;
}


asynStatus VirtualMotorAxis::setPosition(double position)
{
  asynStatus status;
  //static const char *functionName = "VirtualMotorAxis::setPosition";

  sprintf(pC_->outString_, "%d POS %d", axisIndex_, NINT(position));
  status = pC_->writeReadController();
  return status;
}


/*
asynStatus VirtualMotorAxis::setClosedLoop(bool closedLoop)
{
  asynStatus status;
  //static const char *functionName = "VirtualMotorAxis::setClosedLoop";
  
  if (closedLoop)
  {
    // Send an AB here for EN to work (EN fails if status ends in 8, rather than E)
    sprintf(pC_->outString_, "%d AB", axisIndex_);
    status = pC_->writeController();
    epicsThreadSleep(0.033);
    
    sprintf(pC_->outString_, "%d EN", axisIndex_);
  }
  else
  {
    sprintf(pC_->outString_, "%d DI", axisIndex_);
  }

  status = pC_->writeController();
  return status;
}
*/

/** Polls the axis.
  * This function reads the motor position, the limit status, the home status, the moving status, 
  * and the drive power-on status. 
  * It calls setIntegerParam() and setDoubleParam() for each item that it polls,
  * and then calls callParamCallbacks() at the end.
  * \param[out] moving A flag that is set indicating that the axis is moving (true) or done (false). */
asynStatus VirtualMotorAxis::poll(bool *moving)
{ 
  int position;
  int status;
  int done;
  int direction;
  int limit;
  asynStatus comStatus;

  // Read the current motor position
  sprintf(pC_->outString_, "%d POS?", axisIndex_);
  comStatus = pC_->writeReadController();
  if (comStatus) 
    goto skip;
  // The response string is of the form "0.00000"
  position = atof((const char *) &pC_->inString_);
  setDoubleParam(pC_->motorPosition_, position);

  // Read the moving status of this motor
  sprintf(pC_->outString_, "%d ST?", axisIndex_);
  comStatus = pC_->writeReadController();
  if (comStatus) 
    goto skip;
  // The response string is of the form "1"
  status = atoi((const char *) &pC_->inString_);

  // Set the direction bit in the move method instead of here since there isn't a direction bit, requires private readback position var
  // Or set the direction bit here, requires a private target position var
  direction = (status & 0x1) ? 1 : 0;
  setIntegerParam(pC_->motorStatusDirection_, direction);

  done = (status & 0x2) ? 1 : 0;
  setIntegerParam(pC_->motorStatusDone_, done);
  setIntegerParam(pC_->motorStatusMoving_, !done);
  *moving = done ? false:true;

  // Read the limit status
  limit = (status & 0x8) ? 1 : 0;
  setIntegerParam(pC_->motorStatusHighLimit_, limit);
  limit = (status & 0x10) ? 1 : 0;
  setIntegerParam(pC_->motorStatusLowLimit_, limit);

  // Read the home status--eventually
  
  // Read the drive power on status
  //driveOn = (status & 0x100) ? 0 : 1;
  //setIntegerParam(pC_->motorStatusPowerOn_, driveOn);

  skip:
  setIntegerParam(pC_->motorStatusProblem_, comStatus ? 1:0);
  callParamCallbacks();
  return comStatus ? asynError : asynSuccess;
}

/** Code for iocsh registration */
static const iocshArg VirtualMotorCreateControllerArg0 = {"Port name", iocshArgString};
static const iocshArg VirtualMotorCreateControllerArg1 = {"MVP 2001 port name", iocshArgString};
static const iocshArg VirtualMotorCreateControllerArg2 = {"Number of axes", iocshArgInt};
static const iocshArg VirtualMotorCreateControllerArg3 = {"Moving poll period (ms)", iocshArgInt};
static const iocshArg VirtualMotorCreateControllerArg4 = {"Idle poll period (ms)", iocshArgInt};
static const iocshArg * const VirtualMotorCreateControllerArgs[] = {&VirtualMotorCreateControllerArg0,
                                                             &VirtualMotorCreateControllerArg1,
                                                             &VirtualMotorCreateControllerArg2,
                                                             &VirtualMotorCreateControllerArg3,
                                                             &VirtualMotorCreateControllerArg4};
static const iocshFuncDef VirtualMotorCreateControllerDef = {"VirtualMotorCreateController", 5, VirtualMotorCreateControllerArgs};
static void VirtualMotorCreateContollerCallFunc(const iocshArgBuf *args)
{
  VirtualMotorCreateController(args[0].sval, args[1].sval, args[2].ival, args[3].ival, args[4].ival);
}


/* VirtualMotorCreateAxis */
/*
static const iocshArg VirtualMotorCreateAxisArg0 = {"Controller port name", iocshArgString};
static const iocshArg VirtualMotorCreateAxisArg1 = {"Axis number", iocshArgInt};
static const iocshArg VirtualMotorCreateAxisArg2 = {"Encoder lines per rev", iocshArgInt};
static const iocshArg VirtualMotorCreateAxisArg3 = {"Max current (ma)", iocshArgInt};
static const iocshArg VirtualMotorCreateAxisArg4 = {"Limit polarity", iocshArgInt};
static const iocshArg * const VirtualMotorCreateAxisArgs[] = {&VirtualMotorCreateAxisArg0,
                                                     &VirtualMotorCreateAxisArg1,
                                                     &VirtualMotorCreateAxisArg2,
                                                     &VirtualMotorCreateAxisArg3,
                                                     &VirtualMotorCreateAxisArg4};
static const iocshFuncDef VirtualMotorCreateAxisDef = {"VirtualMotorCreateAxis", 5, VirtualMotorCreateAxisArgs};
static void VirtualMotorCreateAxisCallFunc(const iocshArgBuf *args)
{
  VirtualMotorCreateAxis(args[0].sval, args[1].ival, args[2].ival, args[3].ival, args[4].ival);
}
*/

static void VirtualMotorRegister(void)
{
  iocshRegister(&VirtualMotorCreateControllerDef, VirtualMotorCreateContollerCallFunc);
  //iocshRegister(&VirtualMotorCreateAxisDef,       VirtualMotorCreateAxisCallFunc);
}

extern "C" {
epicsExportRegistrar(VirtualMotorRegister);
}
