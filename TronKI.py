import keyboard, time

try:
    import DasSpiel as BAPI
except ImportError:
    import DasSpielSimulation as BAPI
# BAPI may stand for "Basler API" :-)

import GameSounds
from GameHelper import calcDistance
from LightCycle import LightCycle
from LightCycleTrail import LightCycleTrail
import Config as Cfg



# Script entry function.
# It runs a Basler version of the classic computer game TRON.
def main():
    
    file = open("C:/projects/Hackathon/preset.txt")
    json = file.read()
    file.close()
    preset=JSONtoDict(json)
    
    
    mainWindow = initMainWindow("Tron", Cfg.MAIN_WINDOW_WIDTH_PX, Cfg.MAIN_WINDOW_HEIGHT_PX)

    # standingItems = mainWindow.standingItemsManager
    lyingItems = mainWindow.lyingItemsManager

    # the item manager for head up displays
    frontItems = mainWindow.frontItemsManager
    frontItems.createAndAddItem(BAPI.loadImage(".\\Bilder\\Basler_Tron.png"), BAPI.Point(320, 5))

    # set the field ground image in simulation mode
    BAPI.setImage4NoCameraMode(BAPI.generateField(Cfg.FIELD_WIDTH_PX, Cfg.FIELD_HEIGHT_PX, 40))

    lightCycles = initLightCycles()

    # one grab and calculation to determine the cars positions and angles
    img = BAPI.grabFromCamera()
    mainWindow.asyncHandleCarsAndBackground(img)
    mainWindow.wait4Asyncs()
    for bike in lightCycles:
        bike.setAngleIdToClosestMatchingAngle()

    trails = initBikeTrails(lyingItems, lightCycles)

    views = initViews(mainWindow, lightCycles)

    #GameSounds.playGridIsLiveSound()
    t=0
    while True:
        # Basic game API code
        img = BAPI.grabFromCamera()
        mainWindow.asyncHandleCarsAndBackground(img)
        mainWindow.wait4Asyncs()

        # Views need to be adapted here to create a smooth animation!
        adaptViewsToFollowBikes(lightCycles, views)

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
            lightCycles = initLightCycles()
            trails = initBikeTrails(lyingItems, lightCycles)
            GameSounds.stopSoundPlayback()
            GameSounds.playGridIsLiveSound()

        # bike ans biketrail behaviour
        for bike, bikeTrail in zip(lightCycles, trails):
            bike.handleSteeringInputs()
            bike.controlSteeringAngle()
            bikeTrail.generate(bike)
        
        time.sleep(1)
        t+=1
        #handleCollisionOfLightCyclesAndTrails(Cfg.COLLISION_DISTANCE_LIMIT_TRAILS_PX, lightCycles, trails)
        #handleCollisionOfLightCyclesWithEachOther(Cfg.COLLISION_DISTANCE_LIMIT_LIGHTCYCLES_PX, lightCycles)
        #handleCollisionOfLightCyclesWithBoundaries(Cfg.COLLISION_DISTANCE_LIMIT_FIELD_BOUNDARIES_PX,
        #                                           Cfg.FIELD_WIDTH_PX,
        #                                           Cfg.FIELD_HEIGHT_PX,
        #                                           lightCycles)


def initMainWindow(name, fieldWidthPx, fieldHeightPx):
    mainWindow = BAPI.getWindow()
    mainWindow.setSize(fieldWidthPx, fieldHeightPx)
    mainWindow.name = name
    mainWindow.showFPS = False
    return mainWindow


def initLightCycles():
    bike0Keys = {'forwardKey':'w',
             'backwardKey':'s',
             'turnLeftKey':'a',
             'turnRightKey':'d',
             'specialAbilityKey':'e' }

    bike0 = LightCycle(0, bike0Keys, BAPI.Point(1500, 300), 2)

    bike1Keys = {'forwardKey':'i',
                 'backwardKey':'k',
                 'turnLeftKey':'j',
                 'turnRightKey':'l',
                 'specialAbilityKey':'o' }

    bike1 = LightCycle(1, bike1Keys, BAPI.Point(100, 300), 0)

    bikes = (bike0, bike1)

    return bikes


def initBikeTrails(graphicsObjectManager, bikes):
    bike0trail = LightCycleTrail(graphicsObjectManager, bikes[0])
    bike1trail = LightCycleTrail(graphicsObjectManager, bikes[1])
    return (bike0trail, bike1trail)


def handleCollisionOfLightCyclesAndTrails(distanceLimitPx, lightCycles, trails):
    # collision with light cycle trails trails
    for trail in trails:
        collisions = trail.getCollidedObjects(lightCycles, distanceLimitPx)
        if len(collisions) > 0:
            for collision in collisions:
                lightCycles[collision[0]._carId].destroy()
                
                
def handleCollisionOfLightCyclesWithEachOther(distanceLimitPx, lightCycles):
    # collision lightCycles with each other
    if calcDistance(lightCycles[0].getPosition(), lightCycles[1].getPosition()) < distanceLimitPx:
        for bike in lightCycles:
            bike.destroy()


def handleCollisionOfLightCyclesWithBoundaries(distanceLimitPx, fieldWidthPx, fieldHeightPx, lightCycles):
    # collision with field boundaries
    distanceLimitForFieldLimitsPx = distanceLimitPx // 4
    for bike in lightCycles:
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


def JSONtoDict(json):
    list = json.split("{")[1].split("}")[0].split(",")
    dict={}
    for pair in list:
        p=pair.split(":")
        dict[p[0]]=eval(p[1])
    return dict
    
###########################################
###########################################
###########################################
if __name__ == '__main__':
    main()


