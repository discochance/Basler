import pygame as pg


pg.mixer.init()

__GRID_LIVE_SOUND = pg.mixer.Sound("Sounds\grid_is_live.wav")
__LIGHTCYCLE_SOUND = pg.mixer.Sound("Sounds\lightcycle.wav")

def playGridIsLiveSound():
    __GRID_LIVE_SOUND.play()


def playLightCycleSound():
    __LIGHTCYCLE_SOUND.play()

def uninit():
    pg.mixer.quit()

def stopSoundPlayback():
    pg.mixer.stop()

