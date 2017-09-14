try:
    import DasSpiel as BAPI
except ImportError:
    import DasSpielSimulation as BAPI

from GameHelper import calcDistance

# This class represents the trail of a LightCycle, that is generated in the back of the bike,
# while it is driving.
# It handles the graphics of the bike trails.
# It reacts to movement of a bike.
# It handles objects, that represent the trail of the field.
class LightCycleTrail():

    TRAIL_STANDARD_IMAGES = (BAPI.loadImage(".\\Bilder\\TronTrailRed.png").createRotatedCopyWithAngleInDegree(270),
                             BAPI.loadImage(".\\Bilder\\TronTrailBlue.png").createRotatedCopyWithAngleInDegree(270))

    def __init__(self, graphicsObjectManager, bike):
        self._graphicsObjectManager = graphicsObjectManager
        self._image = self.TRAIL_STANDARD_IMAGES[bike._carId]
        self._trailObjects = []
        self.MIN_OBJECT_DISTANCE = 0.09
        self._metersSinceLastObject = 0.0
        self._lengthLimit = 120
        self._lastBikePositions = []
        self._delayedTrailObjects = 2


    def generate(self, tronBike):
        self._metersSinceLastObject += tronBike.getDistanceDrivenMetersInLastStep()
        if self._metersSinceLastObject >= self.MIN_OBJECT_DISTANCE:
            rotatedImage = self._image.createRotatedCopyWithAngleInRadian(tronBike.getAngle() * -1)
            self._lastBikePositions.append(tronBike.getPosition())
            if len(self._lastBikePositions) >= self._delayedTrailObjects:
                self._addNewObject(self._lastBikePositions.pop(0), rotatedImage)
            self._metersSinceLastObject = 0.0


    def _addNewObject(self, bikePosition, image):
        self._trailObjects.append(self._graphicsObjectManager.createAndAddItem(image, bikePosition))
        if len(self._trailObjects) >= self._lengthLimit:
            self._graphicsObjectManager.removeItem(self._trailObjects.pop(0))


    def getCollidedObjects(self, otherObjects, distanceLimitPx):
        result = []
        for i, trailObject in enumerate(reversed(self._trailObjects)):
            if i > 0:
                for otherObject in otherObjects:
                    distance = calcDistance(trailObject.position, otherObject.getPosition())
                    if distance < distanceLimitPx:
                        result.append((otherObject, trailObject))
        return result