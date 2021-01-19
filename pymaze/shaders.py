import pygame
import sys
import glm

from OpenGL.GL import * 
from OpenGL.GL import shaders


from constants import *


class ShaderTypes:
    WORLD_SHADER  = 0
    DEBUG_SHADER  = 1
    SKYBOX_SHADER = 2
    SHADOW_SHADER = 3
    SDEBUG_SHADER = 4
    PORTAL_SHADER = 5


class PWShader(object):
    def __init__(self, shader):
        self.shader = shader


class PWShaders(PWConstants):
    shaders = {}

    @classmethod
    def __parseShader(cls, shader_path, shader_type):
        shader_raw = ""
        with open(shader_path, 'r') as file:
            shader_raw = file.read()

        try:
            return shaders.compileShader(shader_raw, shader_type)
        except shaders.ShaderCompilationError as e:
            # TODO: Add nicer output for error messages.
            print(e)

            pygame.quit()
            sys.exit()


    @classmethod
    def loadShader(cls, shader_id, vert, frag):
        v_shader = cls.__parseShader(vert, GL_VERTEX_SHADER)
        v_fragment = cls.__parseShader(frag, GL_FRAGMENT_SHADER)

        cls.shaders[shader_id] = PWShader(shaders.compileProgram(v_shader, v_fragment))


    @classmethod
    def getShader(cls, id):
        return cls.shaders[id]


    @classmethod
    def parseShaders(cls):
        cls.loadShader(ShaderTypes.WORLD_SHADER, "shaders/world_geom.vert", "shaders/world_geom.frag")
        shader = cls.getShader(ShaderTypes.WORLD_SHADER)
        glUseProgram(shader.shader)
        shader.proj_view = glGetUniformLocation(shader.shader, "projView")
        shader.texture_scale = glGetUniformLocation(shader.shader, "textureScale")
        shader.light_proj_view = glGetUniformLocation(shader.shader, "lightProjView")
        shader.light_direction = glGetUniformLocation(shader.shader, "lightDir")

        glUniform1i(glGetUniformLocation(shader.shader, "diffuse"  ), 0)
        glUniform1i(glGetUniformLocation(shader.shader, "shadowMap"), 1)


        # ----------------


        cls.loadShader(ShaderTypes.DEBUG_SHADER, "shaders/debug_line.vert", "shaders/debug_line.frag")
        shader = cls.getShader(ShaderTypes.DEBUG_SHADER)
        glUseProgram(shader.shader)
        shader.proj_view = glGetUniformLocation(shader.shader, "projView")


        # ----------------


        cls.loadShader(ShaderTypes.SKYBOX_SHADER, "shaders/skybox.vert", "shaders/skybox.frag")
        shader = cls.getShader(ShaderTypes.SKYBOX_SHADER)
        glUseProgram(shader.shader)
        shader.proj_view = glGetUniformLocation(shader.shader, "projView")
        glUniform1i(glGetUniformLocation(shader.shader, "skybox"), 0)
        

        # ----------------


        cls.loadShader(ShaderTypes.SHADOW_SHADER, "shaders/shadow_mapping.vert", "shaders/shadow_mapping.frag")
        shader = cls.getShader(ShaderTypes.SHADOW_SHADER)
        glUseProgram(shader.shader)
        shader.proj_view = glGetUniformLocation(shader.shader, "projView")
        

        # ----------------


        cls.loadShader(ShaderTypes.SDEBUG_SHADER, "shaders/shadow_debugger.vert", "shaders/shadow_debugger.frag")
        shader = cls.getShader(ShaderTypes.SDEBUG_SHADER)
        glUseProgram(shader.shader) 


        # ----------------


        cls.loadShader(ShaderTypes.PORTAL_SHADER, "shaders/portal.vert", "shaders/portal.frag")
        shader = cls.getShader(ShaderTypes.PORTAL_SHADER)
        glUseProgram(shader.shader)
        shader.proj_view = glGetUniformLocation(shader.shader, "projView")
        shader.model = glGetUniformLocation(shader.shader, "model")
        shader.view = glGetUniformLocation(shader.shader, "view")
        shader.seconds = glGetUniformLocation(shader.shader, "uSeconds")
        shader.resolution = glGetUniformLocation(shader.shader, "uResolution")

        glUniform1i(glGetUniformLocation(shader.shader, "colorTexture"), 0)
        glUniform1i(glGetUniformLocation(shader.shader, "depthTexture"), 1)