import glm
import ctypes

from OpenGL.GL import * 
from OpenGL.GL import shaders

class PWConstants(object):
    # Common
    d_max_fps = 2048
    d_resolution = glm.ivec2(1280, 720)
    d_fsize = ctypes.sizeof(ctypes.c_float)
    d_gravity = 9.81

    # Camera
    c_fov = 45.0
    c_aspect = float(d_resolution.x) / float(d_resolution.y)
    c_near = 0.01
    c_far = 100.0
    c_sensitivity = 5.0

    # Player
    p_height = 0.8
    p_speed = 3.0
    p_jump_vel = 3.5

    # Shadows
    s_shadow_width = 4096 * 2
    s_shadow_height = 4096 * 2
    s_shadow_near = 0.01
    s_shadow_far = 64.0


class PWVaoData(object):
    def __init__(self):
        self.vao = 0
        self.vbo = 0
        self.data = 0
        self.count = 0


if __name__ == "__main__":
    pass
