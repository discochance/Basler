from DasSpielSimulation import VirtualCar
try:
    import DasSpiel as BAPI
except ImportError:
    import DasSpielSimulation as BAPI

import keyboard
import math
import time
from GameHelper import limitToUInt8, calcDeltaOnShortestTurnAngle
import Config as Cfg

# This class represents a bike/car that behaves similar to the bikes from the game/movie TRON.
# It handles the graphics of the bike.
# It reacts to steering inputs by keyboard or remote control.
# It controlls the bike to drive only in right angles.
class LightCycle():

    BIKE_STANDARD_IMAGES = (BAPI.loadImage(".\\Bilder\\Pfeil_orange-2.png").createResizedCopy(30, 64).createRotatedCopyWithAngleInDegree(270),
                            BAPI.loadImage(".\\Bilder\\Pfeil_hellblau-2.png").createResizedCopy(30, 64).createRotatedCopyWithAngleInDegree(270))

    def __init__(self, carId, dictOfKeys, startPosition, startAngleId):
        self._carId = carId
        self._car = BAPI.getWindow().carManager.getListOfCars()[carId]

        self._car.dispImage = self.BIKE_STANDARD_IMAGES[carId]
        self._remoteControl = BAPI.getWindow().getCommTransmitter()

        # Input keys
        self._forwardKey = dictOfKeys['forwardKey']
        self._backwardKey = dictOfKeys['backwardKey']
        self._turnLeftKey = dictOfKeys['turnLeftKey']
        self._turnRightKey = dictOfKeys['turnRightKey']
        self._specialAbilityKey = dictOfKeys['specialAbilityKey']

        self._car.position = startPosition

        # Simulation or real world car?
        self._isVirtual = isinstance(self._car, BAPI.VirtualCar)

        # Steering parameters
        self.DRIVING_AGLE_COUNT = 4
        self._actualDrivingAngleId = startAngleId
        self._possibleDrivingAnglesRad = [math.radians(0),
                                          math.radians(90),
                                          math.radians(180),
                                          math.radians(270)]

        # Steering control parameters
        self._feedbackControlFactorP = 4.0

        self._steeringLastPressedTime = Cfg.STEERING_INPUT_RELEASE_TIME_SEC
        self.STEERING_LIMIT_ABS = 100

        self._maxThrottle = 40
        if Cfg.LIGHTCYCLES_PERMANENTLY_DRIVING:
            self._minThrottle = 28
        else:
            self._minThrottle = 0
        
        self._car.throttle = 0
        self.PIXEL_PER_METER = 400
        self._tangentialSpeedKph = 0.0
        self._calculationStepDistanceMeters = 0.0
        self._lastPosition = self._car.position
        self._lastCallTimeSeconds = 0

        if (self._isVirtual):
            # initialize angle of virtual car
            self._car.angle = math.radians(self._possibleDrivingAnglesRad[self._actualDrivingAngleId])
        else:
            # synchronize car angle id with real car orientation
            self.setAngleIdToClosestMatchingAngle()

        if self._carId == 0:
                self._remoteIp = "192.168.0.100"
        else:
                self._remoteIp = "192.168.0.101"


    def getPosition(self):
        return self._car.position

    def getAngle(self):
        return self._car.angle

    def getDistanceDrivenMetersInLastStep(self):
        return self._calculationStepDistanceMeters

    def getCarObject(self):
        return self._car

    # Things to do when the car crashes an objects and gets "destroyed"
    def destroy(self):
        self._car.throttle = 0
        self._minThrottle = 0
        self._maxThrottle = 0

    # The actual car angle is used to calculate the angle and its angle id
    # that are closest to the actual car orientation angle.
    def setAngleIdToClosestMatchingAngle(self):
        carAngleRad = self._car.angle
        minDeltaRad = math.pi
        newAngleId = 0
        for i, angleRad in enumerate(self._possibleDrivingAnglesRad):
            absDeltaRad = abs(calcDeltaOnShortestTurnAngle(angleRad, carAngleRad))
            if absDeltaRad < minDeltaRad:
                minDeltaRad = absDeltaRad
                newAngleId = i
        self._actualDrivingAngleId = newAngleId


    def handleSteeringInputs(self):
        LEFT_THRESHOLD = -100
        RIGHT_THRESHOLD = +100
        actual_steer = 0
        actual_throttle = 0
        
        if (Cfg.USE_CARRERA_REMOTE_CONTROL):
            # control by carrera wireless remote control
            actual_throttle = self._remoteControl.get_in_throttle(self._remoteIp)
            actual_steer = self._remoteControl.get_in_steer(self._remoteIp)
            
            # valid values from remote control are always positive
            if actual_steer >= 0 and actual_throttle >=0:
                actual_steer -= Cfg.CARRERA_REMOTE_ZERO_OFFSET
                actual_throttle -= Cfg.CARRERA_REMOTE_ZERO_OFFSET
                if actual_throttle > self._minThrottle and actual_throttle < self._maxThrottle:
                    self._car.throttle
                elif actual_throttle >= self._maxThrottle:
                    self._car.throttle = self._maxThrottle
                else:
                    self._car.throttle = self._minThrottle
            else:
                print("Invalid values from remote with IP: " + self._remoteIp)
        else:
            # control by keyboard
            if keyboard.is_pressed(self._forwardKey):
                self._car.throttle = self._maxThrottle
            else:
                self._car.throttle = self._minThrottle
            if keyboard.is_pressed(self._turnLeftKey):
                actual_steer = LEFT_THRESHOLD
            elif keyboard.is_pressed(self._turnRightKey):
                actual_steer = RIGHT_THRESHOLD

        # limit steering repetition
        if time.clock() - self._steeringLastPressedTime >= Cfg.STEERING_INPUT_RELEASE_TIME_SEC:
            if actual_steer <= LEFT_THRESHOLD:
                self._actualDrivingAngleId = (self._actualDrivingAngleId + self.DRIVING_AGLE_COUNT - 1) % self.DRIVING_AGLE_COUNT
                self._steeringLastPressedTime = time.clock()
            elif actual_steer >= RIGHT_THRESHOLD:
                self._actualDrivingAngleId = (self._actualDrivingAngleId + self.DRIVING_AGLE_COUNT + 1) % self.DRIVING_AGLE_COUNT
                self._steeringLastPressedTime = time.clock()



    def controlSteeringAngle(self):
        actualTimeSeconds = time.clock()
        deltaTimeSeconds = actualTimeSeconds - self._lastCallTimeSeconds
        self._lastCallTimeSeconds = actualTimeSeconds

        distancePixels = math.sqrt((self._lastPosition.x - self._car.position.x) ** 2 + (self._lastPosition.y - self._car.position.y) ** 2)
        FACTOR_MPS_TO_KPH = 3.6
        if deltaTimeSeconds > 0.0:
            self._tangentialSpeedKph = distancePixels * FACTOR_MPS_TO_KPH / (self.PIXEL_PER_METER * deltaTimeSeconds)
            self._calculationStepDistanceMeters = distancePixels / self.PIXEL_PER_METER
        self._lastPosition = self._car.position

        desiredAngleRad = self._possibleDrivingAnglesRad[self._actualDrivingAngleId]
        deltaRad = calcDeltaOnShortestTurnAngle(desiredAngleRad, self._car.angle)

        steering = int(math.degrees(deltaRad) * self._feedbackControlFactorP)
        if steering < -self.STEERING_LIMIT_ABS:
            steering = -self.STEERING_LIMIT_ABS
        elif steering > self.STEERING_LIMIT_ABS:
            steering = self.STEERING_LIMIT_ABS
        self._car.steeringAngle = steering

        steer_override = limitToUInt8((steering * 128 // 100) + Cfg.CARRERA_REMOTE_ZERO_OFFSET)
        throttle_override = limitToUInt8((self._car.throttle * 128 // 100) + Cfg.CARRERA_REMOTE_ZERO_OFFSET)
        self._remoteControl.set_override_out_both(self._remoteIp, steer_override, throttle_override)

