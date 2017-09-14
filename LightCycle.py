try:
    import DasSpiel as BAPI
except ImportError:
    import DasSpielSimulation as BAPI

import keyboard
import math
import time
from GameHelper import limitToUInt8

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
        self._possibleDrivingAnglesRad = []
        self._possibleDrivingAnglesRad.append(math.radians(0))
        self._possibleDrivingAnglesRad.append(math.radians(90))
        self._possibleDrivingAnglesRad.append(math.radians(180))
        self._possibleDrivingAnglesRad.append(math.radians(270))
        self._actualDrivingAngleId = startAngleId
        self._car.angle = self._possibleDrivingAnglesRad[self._actualDrivingAngleId]

        # Steering control parameters
        self._feedbackControlFactorP = 5.0
        self.KEYBOARD_RELEASE_LIMIT = 20
        self._keyboardReleasedCounter = self.KEYBOARD_RELEASE_LIMIT
        self.STEERING_LIMIT_ABS = 100

        self._maxThrottle = 100
        self._minThrottle = 30
        self._car.throttle = 0
        self.PIXEL_PER_METER = 400
        self._tangentialSpeedKph = 0.0
        self._calculationStepDistanceMeters = 0.0
        self._lastPosition = self._car.position
        self._lastCallTimeSeconds = 0

        # self._transmitters = self._remoteControl.get_connected_transmitter_ips()

    def getPosition(self):
        return self._car.position

    def getAngle(self):
        return self._car.angle

    def getDistanceDrivenMetersInLastStep(self):
        return self._calculationStepDistanceMeters

    def getCarObject(self):
        return self._car

    def destroy(self):
        self._car.throttle = 0
        self._minThrottle = 0
        self._maxThrottle = 0

    def handleSteeringInputs(self):
        useRemote = True
        if (useRemote):
            if self._carId == 0:
                ip = "192.168.0.100"
            else:
                ip = "192.168.0.101"

            actual_throttle = self._remoteControl.get_in_throttle(ip) - 128
            actual_steer = self._remoteControl.get_in_steer(ip) - 128

            if actual_throttle > self._minThrottle:
                self._car.throttle = actual_throttle
            elif actual_throttle > self._maxThrottle:
                actual_throttle = self._maxThrottle
            else:
                self._car.throttle = self._minThrottle

            if self._keyboardReleasedCounter >= self.KEYBOARD_RELEASE_LIMIT and actual_steer < -100:
                self._actualDrivingAngleId = (self._actualDrivingAngleId + self.DRIVING_AGLE_COUNT - 1) % self.DRIVING_AGLE_COUNT
                self._keyboardReleasedCounter = 0
            elif self._keyboardReleasedCounter >= self.KEYBOARD_RELEASE_LIMIT and actual_steer > 100:
                self._actualDrivingAngleId = (self._actualDrivingAngleId + self.DRIVING_AGLE_COUNT + 1) % self.DRIVING_AGLE_COUNT
                self._keyboardReleasedCounter = 0
            else:
                self._keyboardReleasedCounter += 1
                if self._keyboardReleasedCounter > self.KEYBOARD_RELEASE_LIMIT:
                    self._keyboardReleasedCounter = self.KEYBOARD_RELEASE_LIMIT

        else:
            # control by keyboard
            if keyboard.is_pressed(self._forwardKey):
                self._car.throttle = self._maxThrottle
            else:
                self._car.throttle = self._minThrottle
            # Limit keyboard repetition speed
            if self._keyboardReleasedCounter >= self.KEYBOARD_RELEASE_LIMIT and keyboard.is_pressed(self._turnLeftKey):
                self._actualDrivingAngleId = (self._actualDrivingAngleId + self.DRIVING_AGLE_COUNT - 1) % self.DRIVING_AGLE_COUNT
                self._keyboardReleasedCounter = 0
            elif self._keyboardReleasedCounter >= self.KEYBOARD_RELEASE_LIMIT and keyboard.is_pressed(self._turnRightKey):
                self._actualDrivingAngleId = (self._actualDrivingAngleId + self.DRIVING_AGLE_COUNT + 1) % self.DRIVING_AGLE_COUNT
                self._keyboardReleasedCounter = 0
            else:
                self._keyboardReleasedCounter += 1
                if self._keyboardReleasedCounter > self.KEYBOARD_RELEASE_LIMIT:
                    self._keyboardReleasedCounter = self.KEYBOARD_RELEASE_LIMIT


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
        deltaRad = desiredAngleRad - self._car.angle
        if deltaRad > math.pi:
            deltaRad -= 2 * math.pi
        elif deltaRad < -math.pi:
            deltaRad += 2 * math.pi

        steering = int(math.degrees(deltaRad) * self._feedbackControlFactorP)
        if steering < -self.STEERING_LIMIT_ABS:
            steering = -self.STEERING_LIMIT_ABS
        elif steering > self.STEERING_LIMIT_ABS:
            steering = self.STEERING_LIMIT_ABS
        self._car.steeringAngle = steering
        if self._carId == 0:
            ip = "192.168.0.100"
        else:
            ip = "192.168.0.101"
        steer_override = limitToUInt8((steering * 128 // 100) + 128)
        throttle_override = limitToUInt8((self._car.throttle * 128 // 100) + 128)
        self._remoteControl.set_override_out_both(ip, steer_override, throttle_override)
        if self._carId == 0:
            print("%s  %f  %d  %d" % (ip, self._car.angleInDegree, throttle_override, steer_override))

