import ctypes
import sys
import os
import datetime


# TODO
#   - Optimize collision check (Right now it just tests the collisions against all walls)
#   - Code could use some refactoring



# Check to make sure user has the all necessary libraries
# and install instructions

try:
    import pygame
    from pygame.locals import *
except ImportError:
    print("Run 'pip install pygame'")
    exit()

try:
    from OpenGL.GL import * 
except ImportError:
    print("Run 'pip install PyOpenGL PyOpenGL_accelerate'")
    exit()

try:
    import glm
except ImportError:
    print("Run 'pip install PyGLM'")
    exit()

try:
    import numpy as np
except ImportError:
    print("Run 'pip install numpy'")
    exit()

# End of check

from constants import *
from camera import *
from textures import *
from shaders import *
from labyrinth import *
from player import *
from debug import *
from skybox import *
from post_processing import *
from end_portal import *


class PWMain(PWConstants):
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        pygame.init()

        # TODO: Need to add support for multisamplebuffers in the framebuffer texture attachments
        #       otherwise the msaa wont work
        #pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        #pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 2)   # MSAA 

        pygame.display.set_mode(self.d_resolution, DOUBLEBUF | OPENGL)

        self.clock = pygame.time.Clock()

        # -------- GL Stuff

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        glEnable(GL_MULTISAMPLE)
        glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS);

        # -------- Data
        
        PWShaders.parseShaders()
        PWTextures.parseTextures()
        PWDebug.initDebugger()
        PWPostProcessing.parseShaders()

        # -------- Common

        self.maze = PWMaze(16, 16)
        self.skybox = PWSkybox()
        self.camera = PWCamera()
        self.player = PWPlayer(glm.vec2(0, 0))
        self.post = PWPostProcessing()
        self.portal = PWPortal()


        # -------- Render world to shadow map

        # Since the world is mostly static, we can render the shadow map once
        # If you want to render the shadow map every frame, move this in to the loop
        # and set all functions that render something between the begin/end functions
        
        self.skybox.skybox_shadow.begin()

        self.maze.renderMaze(self.camera, True)

        self.skybox.skybox_shadow.end()

        # --------

        found_portal = False
        self.time_start = pygame.time.get_ticks()
        self.final_time = 0


    def mainloop(self):
        while 1:
            delta = self.clock.tick(self.d_max_fps) / 1000.0
            seconds = pygame.time.get_ticks() / 1000.0

            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            for event in pygame.event.get():
                if (event.type == QUIT) or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()

                if (event.type == KEYUP) and (event.key == K_LEFT):
                    PPostTypes.changeShader(-1)

                if (event.type == KEYUP) and (event.key == K_RIGHT):
                    PPostTypes.changeShader(1)

            # --------

            self.player.update(delta, self.camera, self.maze.aabb_walls)
            self.camera.updateCamera(delta, self.player.getPosition())
            
            # --------

            # All draw commands should go between the begin/end clause for them to appear on the framebuffer textures

            self.post.begin()

            self.maze.renderMaze(self.camera, False, self.skybox.skybox_shadow)
            self.skybox.renderSkybox(self.camera)

             # Draw all debug lines last
            PWDebug.drawDebug(self.camera) 

            self.post.end(seconds, self.camera)

            found_portal = self.portal.render(self.camera, seconds, self.post.getColorAttachment(), self.post.getDepthAttachment())
            
            if found_portal and not self.final_time:
                self.final_time = pygame.time.get_ticks() - self.time_start
                seconds = int(self.final_time / 1000.0)
                print("Solved in: ({0})!".format(str(datetime.timedelta(seconds=seconds))))

            pygame.display.set_caption("FPS: {0:.2f}".format(self.clock.get_fps()))
            pygame.display.flip()


if __name__ == "__main__":
    PWMain().mainloop()
