import numpy as np
import glm

from OpenGL.GL import * 

from constants import *
from shaders import *

class PWPortal(PWConstants):
    def __init__(self):
        self.portal = PWVaoData()
        self.__createPortal()


    def __createPortal(self):
        self.portal.vao = glGenVertexArrays(1)
        glBindVertexArray(self.portal.vao)


        s = 0.5
        vertices = np.array([-s,  s,  0.0,    0.0,  0.0,
                             -s, -s,  0.0,    0.0,  1.0,
                              s, -s,  0.0,    1.0,  1.0,

                             -s,  s,  0.0,    0.0,  0.0,
                              s, -s,  0.0,    1.0,  1.0,
                              s,  s,  0.0,    1.0,  0.0], dtype='float32')

        self.portal.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.portal.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 5
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        uv_offset = 3
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * uv_offset, ctypes.c_void_p))


    def render(self, camera, seconds, color_texture, depth_texture):
        shader = PWShaders.getShader(ShaderTypes.PORTAL_SHADER)
        glUseProgram(shader.shader)
        
        glUniformMatrix4fv(shader.proj_view, 1, GL_FALSE, camera.getProjectionView())
        glUniformMatrix4fv(shader.view, 1, GL_FALSE, camera.getView())

        #glDisable(GL_CULL_FACE)

        # Player is in "center" while portal is relative to world center
        # add a little offset to get correct distance to the portal

        player_position = camera.getPosition()  # Camera and player share the same position (We can use the camera position here)
        portal_position = glm.vec3(16.5, 0.35, -16.5)

        # --------

        model = glm.mat4(1.0)
        model = glm.translate(model, portal_position)   # Set end portal at the other end of the labyrinth
        glUniformMatrix4fv(shader.model, 1, GL_FALSE, np.array(model, dtype='float32'))

        glUniform1f(shader.seconds, seconds)
        glUniform2f(shader.resolution, self.d_resolution.x, self.d_resolution.y)

        # --------

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, color_texture)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, depth_texture)

        # --------

        glBindVertexArray(self.portal.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        #glEnable(GL_CULL_FACE)

        # --------

        # Player is in "center" while portal is relative to world center
        # add a little offset to get correct distance to the portal

        portal_position_ofs = portal_position + glm.vec3(16.5, 0.0, -16.5)  # Add offset
        distance = glm.distance(player_position, portal_position_ofs)
        return distance < 1.0
