import numpy as np

from OpenGL.GL import * 

from constants import *
from shaders import *
from textures import *


class PPostTypes:
    PPOST_DEFAULT = 512
    PPOST_FISHEYE = 513
    PPOST_RADIALB = 514
    PPOST_CROSSHA = 515
    PPOST_THIRD3D = 516

    #
    current_shader = 0

    @classmethod
    def changeShader(cls, key_change):
        all_count = len(cls.all_shaders)
        cls.current_shader += key_change
        cls.current_shader %= all_count

        print(cls.getCurrentShaderID())

    @classmethod
    def getCurrentShaderID(cls):
        return cls.PPOST_DEFAULT + cls.current_shader
        

# Build list ordered list of all shaders and feed it back to the class
__filtered = {k:v for k, v in PPostTypes.__dict__.items() if k.startswith("PPOST")}
PPostTypes.all_shaders = sorted([x for x in __filtered.values()])


#
class PWPostProcessing(PWConstants):
    def __init__(self):
        self.buffer = 0
        self.color_texture = 0
        self.depth_texture = 0
        self.__createPassBuffer()

        # --------

        self.quad = PWVaoData()
        self.__createPassQuad()


    def getColorAttachment(self):
        return self.color_texture;


    def getDepthAttachment(self):
        return self.depth_texture;


    def __createPassBuffer(self):
        self.buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.buffer)

        # -------- Add color attachment

        self.color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.color_texture)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.d_resolution.x, self.d_resolution.y, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_texture, 0)

        # -------- Add depth attachment

        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.d_resolution.x, self.d_resolution.y, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_texture, 0)

        # --------

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Framebuffer Error!")
            # TODO: Make GL utility functions


    def __createPassQuad(self):
        self.quad.vao = glGenVertexArrays(1)
        glBindVertexArray(self.quad.vao)

        # Position(3), Texture(2)
        vertices = np.array([-1.0,  1.0,    0.0,  1.0,
                             -1.0, -1.0,    0.0,  0.0,
                              1.0, -1.0,    1.0,  0.0,

                             -1.0,  1.0,    0.0,  1.0,
                              1.0, -1.0,    1.0,  0.0,
                              1.0,  1.0,    1.0,  1.0], dtype='float32')

        self.quad.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.quad.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 4
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        uv_offset = 2
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * uv_offset, ctypes.c_void_p))


    def begin(self):
        # Bind out framebuffer to write all color/depth info into to it
        glBindFramebuffer(GL_FRAMEBUFFER, self.buffer)

        # Clear it
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    def end(self, seconds, camera):
        # Reset back to default buffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Render the fullscreen quad with the frame buffer attachments
        self.renderQuad(seconds, camera)


    def setExtraUniforms(self, shader, shader_type, seconds):
        if shader_type == PPostTypes.PPOST_THIRD3D:
            proj = glm.perspective(glm.radians(self.c_fov), self.c_aspect, self.c_near, self.c_far)
            view = glm.lookAt(glm.vec3(0.0, 0.0, 1.0), glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))

            proj_view = np.array(proj * view, dtype='float32')
            glUniformMatrix4fv(shader.proj_view, 1, GL_FALSE, proj_view)
            
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(0.0, 0.0, -3.0))
            model = glm.rotate(model, glm.radians(60.0), glm.vec3(0.0, 1.0, 0.0))

            glUniformMatrix4fv(shader.model, 1, GL_FALSE, np.array(model, dtype='float32'))

        # Add more if/elifs if needed



    def renderQuad(self, seconds, camera):
        shader_type = PPostTypes.getCurrentShaderID()

        shader = PWShaders.getShader(shader_type)
        glUseProgram(shader.shader)

        self.setExtraUniforms(shader, shader_type, seconds)

        # Feed some funky stuff for the shaders
        glUniform1f(shader.seconds, seconds)
        glUniform2f(shader.resolution, self.d_resolution.x, self.d_resolution.y)

        # --------

        glDisable(GL_DEPTH_TEST)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.color_texture)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        
        glBindVertexArray(self.quad.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        glEnable(GL_DEPTH_TEST)


    # All post processing shaders share the same common uniforms
    @classmethod
    def __fetchUniformLocations(cls, shader):
        glUseProgram(shader.shader)
        
        #
        shader.seconds = glGetUniformLocation(shader.shader, "uSeconds")
        shader.resolution = glGetUniformLocation(shader.shader, "uResolution")
        
        # 
        glUniform1i(glGetUniformLocation(shader.shader, "colorTexture"), 0)
        glUniform1i(glGetUniformLocation(shader.shader, "depthTexture"), 1)


    @classmethod
    def parseShaders(cls):
        root_path = "shaders/post_processing/"

        # -------- Default passthrough

        PWShaders.loadShader(PPostTypes.PPOST_DEFAULT, root_path + "post_default.vert", root_path + "post_default.frag")
        cls.__fetchUniformLocations(PWShaders.getShader(PPostTypes.PPOST_DEFAULT))

        # -------- 

        PWShaders.loadShader(PPostTypes.PPOST_FISHEYE, root_path + "post_fisheye.vert", root_path + "post_fisheye.frag")
        cls.__fetchUniformLocations(PWShaders.getShader(PPostTypes.PPOST_FISHEYE))

        # -------- 

        PWShaders.loadShader(PPostTypes.PPOST_RADIALB, root_path + "post_radialb.vert", root_path + "post_radialb.frag")
        cls.__fetchUniformLocations(PWShaders.getShader(PPostTypes.PPOST_RADIALB))

        # -------- 

        PWShaders.loadShader(PPostTypes.PPOST_CROSSHA, root_path + "post_crossha.vert", root_path + "post_crossha.frag")
        cls.__fetchUniformLocations(PWShaders.getShader(PPostTypes.PPOST_CROSSHA))

        # -------- 

        PWShaders.loadShader(PPostTypes.PPOST_THIRD3D, root_path + "post_third3d.vert", root_path + "post_third3d.frag")
        shader = PWShaders.getShader(PPostTypes.PPOST_THIRD3D)
        cls.__fetchUniformLocations(shader)
        shader.proj_view = glGetUniformLocation(shader.shader, "projView")
        shader.model = glGetUniformLocation(shader.shader, "model")

        # -------- 

