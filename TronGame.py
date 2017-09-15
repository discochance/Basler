import keyboard

try:
    import DasSpiel as BAPI
except ImportError:
    import DasSpielSimulation as BAPI
# BAPI may stand for Basler API :-)

import GameSounds
from GameHelper import calcDistance
from LightCycle import LightCycle
from LightCycleTrail import LightCycleTrail


# Script entry function.
# It runs a Basler version of the classic computer game TRON.
def main():
    # Window renderer resolution parameters
    MAIN_WINDOW_WIDTH_PX = 1920
    MAIN_WINDOW_HEIGHT_PX = 1200
    # BAPI.doCalibrationToFile(2, "C:\\Hackathon\\workspace\\Tron\\Calib\\")
    mainWindow = initMainWindow("Tron", MAIN_WINDOW_WIDTH_PX, MAIN_WINDOW_HEIGHT_PX)

    # standingItems = mainWindow.standingItemsManager
    lyingItems = mainWindow.lyingItemsManager

    frontItems = mainWindow.frontItemsManager
    frontItems.createAndAddItem(BAPI.loadImage(".\\Bilder\\Basler_Tron.png"), BAPI.Point(320, 5))

    # game field size parameters
    FIELD_WIDTH_PX = 1880
    FIELD_HEIGHT_PX = 1200

    bikes = initBikes()
    img = BAPI.grabFromCamera()
    mainWindow.asyncHandleCarsAndBackground(img)
    mainWindow.wait4Asyncs()
    for bike in bikes:
        bike.setAngleIdToNearestMatch()

    bikeTrails = initBikeTrails(lyingItems, bikes)

    views = initViews(mainWindow, bikes)

    COLLISION_DISTANCE_LIMIT_PX = 40

    GameSounds.playGridIsLiveSound()

    while True:
        # Basic game API code
        img = BAPI.grabFromCamera()
        mainWindow.asyncHandleCarsAndBackground(img)
        mainWindow.wait4Asyncs()

        # Views need to be adapted here to create a smooth animation!
        adaptViewsToFollowBikes(bikes, views)

        # Basic game API code
        mainWindow.asyncCalcViews()
        mainWindow.wait4Asyncs()
        mainWindow.calcFront()
        mainWindow.display()

        if keyboard.is_pressed('q'):
            # quit the game!
            mainWindow.close()
            GameSounds.uninit()
            break;
        elif keyboard.is_pressed('r'):
            # reset the game!
            for item in lyingItems.getListOfItems():
                lyingItems.removeItem(item)
            bikes = initBikes()
            bikeTrails = initBikeTrails(lyingItems, bikes)
            GameSounds.stopSoundPlayback()
            GameSounds.playGridIsLiveSound()

        # bike ans biketrail behaviour
        for bike, bikeTrail in zip(bikes, bikeTrails):
            bike.handleSteeringInputs()
            bike.controlSteeringAngle()
            bikeTrail.generate(bike)

        handleCollisions(COLLISION_DISTANCE_LIMIT_PX, FIELD_WIDTH_PX, FIELD_HEIGHT_PX, bikes, bikeTrails)


def initMainWindow(name, fieldWidthPx, fieldHeightPx):
    mainWindow = BAPI.getWindow()
    mainWindow.setSize(fieldWidthPx, fieldHeightPx)
    mainWindow.name = name
    return mainWindow


def initBikes():
    bike0Keys = {'forwardKey':'w',
             'backwardKey':'s',
             'turnLeftKey':'a',
             'turnRightKey':'d',
             'specialAbilityKey':'e' }

    bike0 = LightCycle(0, bike0Keys, BAPI.Point(1500, 300))

    bike1Keys = {'forwardKey':'i',
                 'backwardKey':'k',
                 'turnLeftKey':'j',
                 'turnRightKey':'l',
                 'specialAbilityKey':'o' }

    bike1 = LightCycle(1, bike1Keys, BAPI.Point(100, 300))

    bikes = (bike0, bike1)

    return bikes


def initBikeTrails(graphicsObjectManager, bikes):
    bike0trail = LightCycleTrail(graphicsObjectManager, bikes[0])
    bike1trail = LightCycleTrail(graphicsObjectManager, bikes[1])
    return (bike0trail, bike1trail)


def handleCollisions(distanceLimitPx, fieldWidthPx, fieldHeightPx, bikes, bikeTrails):

    # collision with bike trails
    for bikeTrail in bikeTrails:
        collisions = bikeTrail.getCollidedObjects(bikes, distanceLimitPx)
        if len(collisions) > 0:
            for collision in collisions:
                bikes[collision[0]._carId].destroy()

    # collision bikes with each other
    if calcDistance(bikes[0].getPosition(), bikes[1].getPosition()) < distanceLimitPx:
        for bike in bikes:
            bike.destroy()

    # collision with field boundaries
    distanceLimitForFieldLimitsPx = distanceLimitPx // 4
    for bike in bikes:
        position = bike.getPosition()
        if (position.x < distanceLimitForFieldLimitsPx
            or position.x > (fieldWidthPx - distanceLimitForFieldLimitsPx)
            or position.y < distanceLimitForFieldLimitsPx
            or position.y > (fieldHeightPx - distanceLimitForFieldLimitsPx)):
            bike.destroy()


def adaptViewsToFollowBikes(bikes, views):
    for bike, view in zip(bikes, views):
        view.setViewFromCar(bike.getCarObject())


def initViews(mainWindow, bikes):
    views = []
    view = mainWindow.createView(mainWindow.width // 2, mainWindow.height, 0, 0)
    views.append(view)
    view = mainWindow.createView(mainWindow.width // 2, mainWindow.height, mainWindow.width // 2, 0)
    views.append(view)
    for bike, view in zip(bikes, views):
        view.showLyingItems = True
        view.showStandingItems = True
        view.setViewFromCar(bike.getCarObject())  # attach view to the diretion/angle of a bike
    return views




###########################################
###########################################
###########################################
if __name__ == '__main__':
    main()


