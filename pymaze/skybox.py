import pygame
from pygame.locals import *
import glm

import numpy as np

from OpenGL.GL import * 

from constants import *
from camera import *
from shaders import *
from textures import *


class PWShadowDebugger(PWConstants):
    def __init__(self, depth_texture):
        self.debugger = PWVaoData()
        self.__createDebugger()

        # --------

        self.depth_texture = depth_texture


    def __createDebugger(self):
        self.debugger.vao = glGenVertexArrays(1)
        glBindVertexArray(self.debugger.vao)

        vertices = np.array([-0.5,  0.5,  0.0,    0.0,  1.0,
                             -0.5, -0.5,  0.0,    0.0,  0.0,
                              0.5,  0.5,  0.0,    1.0,  1.0,
                              0.5, -0.5,  0.0,    1.0,  0.0], dtype="float32")


        self.debugger.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.debugger.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 5
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        uv_offset = 3
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * uv_offset, ctypes.c_void_p))


    def renderDebugMap(self):
        shader = PWShaders.getShader(ShaderTypes.SDEBUG_SHADER)
        glUseProgram(shader.shader)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)

        glBindVertexArray(self.debugger.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)


class PWSkyboxShadow(PWConstants):
    def __init__(self):
        self.depth_buffer = 0
        self.depth_texture = 0
        self.__createDepthBuffer()

        # --------

        pitch = 55.0
        yaw = 45.0

        self.calculateViewProjection(pitch, yaw)

        self.debugger = PWShadowDebugger(self.getDepthMap())


    def calculateViewProjection(self, pitch, yaw):
        dist = 25.0
        self.projection = glm.ortho(-dist, dist, -dist, dist, self.s_shadow_near, self.s_shadow_far)

        target = glm.vec3(16.5, 0.0, -16.5)    # Center of the maze
        self.light_direction = PWCamera.createViewFront(pitch, yaw)    # Pitch, Yaw
        self.light_position = target + self.light_direction * dist
        
        #
        self.view = glm.lookAt(self.light_position, target, glm.vec3(0.0, 1.0, 0.0))
        
        #
        self.projection_view = np.array(self.projection * self.view, dtype='float32')


    def getLightDirection(self):
        return -self.light_direction


    def getDepthMap(self):
        return self.depth_texture


    def getProjectionView(self):
        return self.projection_view


    def __createDepthBuffer(self):
        self.depth_buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_buffer)

        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.s_shadow_width, self.s_shadow_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        
        border_color = np.array([1.0, 1.0, 1.0, 1.0], dtype='float32')
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border_color)
        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_texture, 0)
        
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        # Reset back to default buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def begin(self):
        shader = PWShaders.getShader(ShaderTypes.SHADOW_SHADER)
        glUseProgram(shader.shader)

        glUniformMatrix4fv(shader.proj_view, 1, GL_FALSE, self.projection_view)

        glCullFace(GL_FRONT)

        # Set viewport size to shadow map size
        glViewport(0, 0, self.s_shadow_width, self.s_shadow_height)

        # Set our new framebuffer active
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_buffer)

        # Clear the contents of the framebuffer
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_DEPTH_BUFFER_BIT)


    def end(self):
        # Reset back to default buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        glCullFace(GL_BACK)

        # Reset viewport back to default screen size
        glViewport(0, 0, self.d_resolution.x, self.d_resolution.y)


class PWSkybox(PWConstants):
    def __init__(self):
        self.skybox = PWVaoData()
        self.__createSkybox()

        self.skybox_shadow = PWSkyboxShadow()


    def __createSkybox(self):
        self.skybox.vao = glGenVertexArrays(1)
        glBindVertexArray(self.skybox.vao)

        vertices = np.array([-1.0,  1.0, -1.0,
                             -1.0, -1.0, -1.0,
                              1.0, -1.0, -1.0,
                              1.0, -1.0, -1.0,
                              1.0,  1.0, -1.0,
                             -1.0,  1.0, -1.0,

                             -1.0, -1.0,  1.0,
                             -1.0, -1.0, -1.0,
                             -1.0,  1.0, -1.0,
                             -1.0,  1.0, -1.0,
                             -1.0,  1.0,  1.0,
                             -1.0, -1.0,  1.0,

                              1.0, -1.0, -1.0,
                              1.0, -1.0,  1.0,
                              1.0,  1.0,  1.0,
                              1.0,  1.0,  1.0,
                              1.0,  1.0, -1.0,
                              1.0, -1.0, -1.0,

                             -1.0, -1.0,  1.0,
                             -1.0,  1.0,  1.0,
                              1.0,  1.0,  1.0,
                              1.0,  1.0,  1.0,
                              1.0, -1.0,  1.0,
                             -1.0, -1.0,  1.0,

                             -1.0,  1.0, -1.0,
                              1.0,  1.0, -1.0,
                              1.0,  1.0,  1.0,
                              1.0,  1.0,  1.0,
                             -1.0,  1.0,  1.0,
                             -1.0,  1.0, -1.0,

                             -1.0, -1.0, -1.0,
                             -1.0, -1.0,  1.0,
                              1.0, -1.0, -1.0,
                              1.0, -1.0, -1.0,
                             -1.0, -1.0,  1.0,
                              1.0, -1.0,  1.0], dtype='float32')

        self.skybox.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.skybox.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 3
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)


    def renderSkybox(self, camera):
        shader = PWShaders.getShader(ShaderTypes.SKYBOX_SHADER)
        glUseProgram(shader.shader)
        
        # Remove translation from the view matrix
        view = glm.mat4(glm.mat3(camera.getView()))
        projection = camera.getProjection()

        glUniformMatrix4fv(shader.proj_view, 1, GL_FALSE, np.array(projection * view))

        glDepthFunc(GL_LEQUAL)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, PWTextures.getTexture3D("skybox_01").getTexture())

        glBindVertexArray(self.skybox.vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glDepthFunc(GL_LESS)


if __name__ == "__main__":
    pass
