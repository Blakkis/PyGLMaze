import pygame
from pygame.locals import *

import os

from OpenGL.GL import * 
from constants import *


class PWTexture2D(object):
    def __init__(self, path):
        self.texture_id = self.__createTexture(path)


    def __createTexture(self, path):
        # Load texture and convert to format OpenGL can use
        surface = pygame.image.load(path).convert()
        surface_data = pygame.image.tostring(surface, "RGB", 1)
        
        width = surface.get_width()
        height = surface.get_height()

        # Create and bind texture (Following settings apply to the currently binded texture)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, surface_data)

        # GL_REPEAT makes texture repeatable (aka. seamless*)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # There are dozen options for texture filtering (Setting things to GL_NEAREST makes textures look crispy)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        # Generate mipmaps (Reduces load on texture sampling with distant objects)
        glGenerateMipmap(GL_TEXTURE_2D)

        # TODO: Should query the max level first 
        # Make textures look smooth on different angles/distance
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY, 16)

        glBindTexture(GL_TEXTURE_2D, 0)

        return texture_id


    def getTexture(self):
        return self.texture_id


class PWTexture3D(object):
    def __init__(self, path):
        self.texture_id = self.__createTexture(path)


    def __createTexture(self, path):
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)

        for enum, texture_path in enumerate(("right.png", "left.png", "bottom.png", "top.png", "front.png", "back.png")):
            full_path = os.path.join(path, texture_path)
            
            surface = pygame.image.load(full_path).convert()
            surface_data = pygame.image.tostring(surface, "RGB", 1)

            width = surface.get_width()
            height = surface.get_height()

            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + enum, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, surface_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        return texture_id


    def getTexture(self):
        return self.texture_id
        

class PWTextures(PWConstants):
    textures2D = {}
    textures3D = {}

    @classmethod
    def loadTexture2D(cls, name, path):
        cls.textures2D[name] = PWTexture2D(path)

    @classmethod
    def getTexture2D(cls, name):
        return cls.textures2D[name]

    # --------

    @classmethod
    def loadTexture3D(cls, name, path):
        cls.textures3D[name] = PWTexture3D(path)

    @classmethod
    def getTexture3D(cls, name):
        return cls.textures3D[name]

    @classmethod
    def parseTextures(cls):
        # 2D
        cls.loadTexture2D("wall_01", "textures/wall_01.png")
        cls.loadTexture2D("floor_01", "textures/floor_01.png")
        cls.loadTexture2D("trim_01", "textures/trim_01.png")

        # 3D
        cls.loadTexture3D("skybox_01", "textures/skybox_01")
