import numpy as np

from constants import *
from shaders import *

class PWDebug(PWConstants):
    MAX_LINES = 8192

    # Draw commands
    __draw_list = []

    # Data
    __vao = None
    __stride = 0
    __data = None


    @classmethod
    def initDebugger(cls):
        cls.__stride = (cls.d_fsize * 4) * 2
        cls.__data = np.array([0] * 8 * cls.MAX_LINES, dtype='float32')

        # --------

        cls.__vao = PWVaoData()
        cls.__vao.count = 1

        cls.__vao.vao = glGenVertexArrays(1)
        glBindVertexArray(cls.__vao.vao)

        cls.__vao.data = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, cls.__vao.data)
        glBufferData(GL_ARRAY_BUFFER, cls.__data, GL_STREAM_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, cls.d_fsize * 4, None)


    @classmethod
    def drawLine(cls, _from, _to, grey = 1.0):
        if cls.__vao.count >= cls.MAX_LINES - 1:
            return

        ofs = cls.__vao.count * 8
        cls.__data[ofs + 0] = _from.x
        cls.__data[ofs + 1] = _from.y
        cls.__data[ofs + 2] = _from.z
        cls.__data[ofs + 3] = grey

        cls.__data[ofs + 4] = _to.x
        cls.__data[ofs + 5] = _to.y
        cls.__data[ofs + 6] = _to.z
        cls.__data[ofs + 7] = grey

        # Update line count
        cls.__vao.count += 1


    @classmethod
    def drawDebug(cls, camera):
        if not cls.__vao.count:
            return

        #glDisable(GL_DEPTH_TEST)
        #glDisable(GL_MULTISAMPLE)
        glLineWidth(2.0)

        shader = PWShaders.getShader(ShaderTypes.DEBUG_SHADER)
        glUseProgram(shader.shader)
        glUniformMatrix4fv(shader.proj_view, 1, GL_FALSE, camera.getProjectionView())

        # --------

        glBindBuffer(GL_ARRAY_BUFFER, cls.__vao.data)
        glBufferData(GL_ARRAY_BUFFER, cls.__data, GL_STREAM_DRAW)
        #glBufferSubData could work here better if more lines are needed

        glBindVertexArray(cls.__vao.vao)
        glDrawArrays(GL_LINES, 0, 2 * cls.__vao.count)

        # Reset line count
        cls.__vao.count = 0

        #glEnable(GL_DEPTH_TEST)
        #glEnable(GL_MULTISAMPLE)
        glLineWidth(1.0)


if __name__ == "__main__":
    pass
