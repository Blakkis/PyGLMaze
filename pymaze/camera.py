import pygame
from pygame.locals import *

import glm
import numpy as np

from constants import *

class PWCamera(PWConstants):
    def __init__(self):
        self.projection = glm.perspective(glm.radians(self.c_fov), self.c_aspect, self.c_near, self.c_far)

        self.position = glm.vec3(0.0, self.p_height,  0.0)
        self.front    = glm.vec3(0.0,           0.0, -1.0)
        self.up       = glm.vec3(0.0,           1.0,  0.0)

        self.yaw = 0.0
        self.pitch = 0.0

        # Center mouse (Not necessary needed)
        pygame.mouse.set_pos(self.d_resolution.x / 2, self.d_resolution.y / 2)
        
        # These 2 makes the mouse virtual (Makes the window "borderless" for the mouse)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)


    def getPosition(self):
        return self.position


    @classmethod
    def createViewFront(cls, pitch, yaw):
        pitch_r = glm.radians(pitch)
        yaw_r   = glm.radians(yaw)

        front = glm.vec3(0.0, 0.0, 1.0)
        front.x = glm.cos(yaw_r) * glm.cos(pitch_r)
        front.y = glm.sin(pitch_r)
        front.z = glm.sin(yaw_r) * glm.cos(pitch_r)
        return glm.normalize(front)

    
    def updateCamera(self, delta, position):
        self.position.xz = position.xz
        self.position.y = self.p_height + position.y


        # -------- Pitch/Yaw
        
        mouse = pygame.mouse.get_rel()

        mx = glm.clamp(mouse[0], -128, 128)
        my = glm.clamp(mouse[1], -128, 128)

        self.yaw += mx * self.c_sensitivity * delta
        self.yaw %= 360

        self.pitch -= my * self.c_sensitivity * delta
        self.pitch = glm.clamp(self.pitch, -89.0, 89.0)    # Dont go over > 90 (It'll flip the camera)

        # -------- Update camera front

        self.front = self.createViewFront(self.pitch, self.yaw);


    def __getViewRaw(self):
        return glm.lookAt(self.position, self.position + self.front, self.up) 


    def getProjectionView(self):
        return np.array(self.projection * self.__getViewRaw(), dtype='float32')


    def getView(self):
        return np.array(self.__getViewRaw(), dtype='float32')


    def getProjection(self):
        return self.projection



if __name__ == "__main__":
    pass
    
