"""
This module contains constants to configure elementary game settings
related to the game field, the camera, the game controls or the game play.
"""

MAIN_WINDOW_WIDTH_PX = 1920
MAIN_WINDOW_HEIGHT_PX = 1200

# game field size parameters, need to be same size as camera resolution!!!
FIELD_WIDTH_PX = 1800
FIELD_HEIGHT_PX = 1200

USE_CARRERA_REMOTE_CONTROL = False

LIGHTCYCLES_PERMANENTLY_DRIVING = True

COLLISION_DISTANCE_LIMIT_LIGHTCYCLES_PX = 40
COLLISION_DISTANCE_LIMIT_TRAILS_PX = 40
COLLISION_DISTANCE_LIMIT_FIELD_BOUNDARIES_PX = 20

CARRERA_REMOTE_ZERO_OFFSET = 128

# steering input needs to be released for xx seconds
STEERING_INPUT_RELEASE_TIME_SEC = 0.50