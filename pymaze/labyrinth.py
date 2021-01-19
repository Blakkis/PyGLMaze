import pygame
from pygame.locals import *
import sys
import os
import glm
import numpy as np
import ctypes

from OpenGL.GL import * 

import random
#random.seed(0xdeadbeef)

from constants import *
from textures import *
from shaders import *
from debug import *
from entities import *


# ----------------------------------------------------------------

CELL_SIZE = 32  # Dont change!
CELL_FREE = 0   # Dont change!
CELL_DONE = 1   # Dont change!
CELL_VIST = 2   # Dont change!

# http://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm
class PWMazeGenerator(PWConstants):
    def __init__(self, width, height, output_data = False):
        self.width = width
        self.height = height
        self.output = output_data

        # -------- If output_data is enabled, these get filled with data.

        self.o_walls = []
        self.o_trims = []

        # --------

        self.surface = pygame.Surface((512, 512))
        pygame.draw.rect(self.surface, (0xff, 0xff, 0xff), (0, 0, 512, 512), 1)

        #
        self.p_grid = [[CELL_FREE for x in range(self.width)] for y in range(self.height)]
        self.p_done = []
        self.p_cand = []

        #
        self.dirs = [glm.ivec2(0, -1), glm.ivec2(0, 1), glm.ivec2(-1, 0), glm.ivec2(1, 0)]

        #
        self.stepMaze(True)


    def __withIn(self, v, v_min, v_max):
        return True if (v > v_min and v < v_max) else False


    def __withInGrid(self, p, v):
        if self.__withIn(p.y, -1, self.height) and self.__withIn(p.x, -1, self.width) and self.p_grid[p.y][p.x] == v:
            return True
        
        return False


    def __advance(self, p):
        self.p_grid[p.y][p.x] = CELL_DONE
        self.p_done.append(p)

        for direction in self.dirs:
            ofs = p + direction
            if self.__withInGrid(ofs, CELL_FREE):
                self.p_grid[ofs.y][ofs.x] = CELL_VIST
                self.p_cand.append(ofs)


    def __getMidPointCorr(self, _from, _to):
        mx = (((_from.x + _to.x) / 2.0) / CELL_SIZE) * 2.2
        my = (((_from.y + _to.y) / 2.0) / CELL_SIZE) * 2.2
        return glm.vec2(-mx, my)

    def __getMidPoint(self, _from, _to):
        mx = (_from.x + _to.x) / 2.0
        my = (_from.y + _to.y) / 2.0
        return glm.vec2(mx, my)

    def __buildWall(self, _from, _to, direction):
        pygame.draw.line(self.surface, (0xff, 0xff, 0xff), _from, _to, 1)

        if (self.output):
            mid = self.__getMidPointCorr(_from, _to)
            self.o_walls.extend([mid.y - 1.1, direction, mid.x + 1.1])


    def __buildTrim(self, _from, _to):
        direction = abs(_from.x - _to.x)

        _from *= CELL_SIZE
        _to   *= CELL_SIZE

        mid = self.__getMidPoint(_from, _to) + CELL_SIZE / 2
        #pygame.draw.circle(self.surface, (0xff, 0x0, 0x0), (int(mid.x), int(mid.y)), 2, 1)

        if (self.output):
            self.o_trims.extend([(mid.y / CELL_SIZE * 2.2) - 1.1, direction, -((mid.x / CELL_SIZE * 2.2) - 1.1)])


    def __advanceDraw(self, _to, _from):
        max_x = self.width
        max_y = self.height

        x2, y2 = _to

        x2_m = x2 * CELL_SIZE
        y2_m = y2 * CELL_SIZE

        if (self.__withIn(y2 - 1, -1, max_y) and self.p_grid[y2 - 1][x2] == 1 and y2 - 1 != _from.y):
            t1 = glm.ivec2(x2_m,             y2_m)
            t2 = glm.ivec2(x2_m + CELL_SIZE, y2_m)
            self.__buildWall(t1, t2, 1.0)

        
        if (self.__withIn(y2 + 1, -1, max_y) and self.p_grid[y2 + 1][x2] == 1 and y2 + 1 != _from.y):
            t1 = glm.ivec2(x2_m,             y2_m + CELL_SIZE)
            t2 = glm.ivec2(x2_m + CELL_SIZE, y2_m + CELL_SIZE)
            self.__buildWall(t1, t2, 1.0)

        
        if (self.__withIn(x2 - 1, -1, max_x) and self.p_grid[y2][x2 - 1] == 1 and x2 - 1 != _from.x):
            t1 = glm.ivec2(x2_m, y2_m)
            t2 = glm.ivec2(x2_m, y2_m + CELL_SIZE)
            self.__buildWall(t1, t2, 0.0)

        
        if (self.__withIn(x2 + 1, -1, max_x) and self.p_grid[y2][x2 + 1] == 1 and x2 + 1 != _from.x):
            t1 = glm.ivec2(x2_m + CELL_SIZE, y2_m)
            t2 = glm.ivec2(x2_m + CELL_SIZE, y2_m + CELL_SIZE)
            self.__buildWall(t1, t2, 0.0)


    def __getNextValidCell(self, p):
        mov = []

        for direction in self.dirs:
            ofs = p + direction
            if self.__withInGrid(ofs, CELL_DONE):
                mov.append(ofs)

        rdir = random.randrange(0, len(mov))
        return mov[rdir]


    def stepMaze(self, set_spawn = False):
        if set_spawn:
            #x = random.randrange(0, self.width)
            #y = random.randrange(0, self.height)

            self.__advance(glm.ivec2(0, 0))
        else:
            if not self.p_cand:
                return True  

            rcand = random.randrange(0, len(self.p_cand))

            candidate = self.p_cand[rcand] 
            direction = self.__getNextValidCell(candidate)

            self.__advance(candidate)
            self.__advanceDraw(candidate, direction)

            visited = self.p_cand.pop(rcand)
            self.__buildTrim(direction, visited)

        return False


    def render(self, surface):
        surface.blit(self.surface, (0, 0))


# ----------------------------------------------------------------


class PWMaze(PWConstants):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # -------- Generate maze

        self.maze = PWMazeGenerator(width, height, True)
        while(not self.maze.stepMaze()):
            pass

        # -------- Setup Floor Geometry

        self.floors = PWVaoData()
        self.__createFloorGeom()

        # -------- Setup Wall Geometry

        self.aabb_walls = []    # Add collision for the walls
        self.walls = PWVaoData()
        self.__createWallsGeom()

        # -------- Setup Trim Geometry

        self.trims= PWVaoData()
        self.__createTrimsGeom()


    def __createFloorGeom(self):
        self.floors.vao = glGenVertexArrays(1)
        glBindVertexArray(self.floors.vao)

        # Position(3), Normal(3), Texture(2) == stride
        vertices = np.array([-1.0,  0.0,  1.0,    0.0,  1.0,  0.0,    0.0,  0.0,
                              1.0,  0.0, -1.0,    0.0,  1.0,  0.0,    1.0,  1.0,
                             -1.0,  0.0, -1.0,    0.0,  1.0,  0.0,    0.0,  1.0,

                             -1.0,  0.0,  1.0,    0.0,  1.0,  0.0,    0.0,  0.0,
                              1.0,  0.0,  1.0,    0.0,  1.0,  0.0,    1.0,  0.0,
                              1.0,  0.0, -1.0,    0.0,  1.0,  0.0,    1.0,  1.0], dtype='float32')

        self.floors.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.floors.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 8
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        n_offset = 3
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * n_offset, ctypes.c_void_p))

        uv_offset = 6
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * uv_offset, ctypes.c_void_p))

        #
        glVertexAttribDivisor(0, 0)
        glVertexAttribDivisor(1, 0)
        glVertexAttribDivisor(2, 0)

        # -------- Build instance matrix (not mat4!)
        
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                positions.extend([(float(x) * 2.2), 0.0, -(float(y) * 2.2)])

        positions = np.array(positions, dtype='float32')

        # Store instance count
        self.floors.count = int(len(positions) / 3)

        # -------- Feed data to instance buffer

        self.floors.data = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.floors.data)
        glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)

        stride = 3
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        #
        glVertexAttribDivisor(3, 1)


    def __createWallsGeom(self):
        self.walls.vao = glGenVertexArrays(1)
        glBindVertexArray(self.walls.vao)

        # Position(3), Normal(3), Texture(2) == stride
        vertices = np.array([-1.0,  0.0,  0.1,    0.0,  0.0,  1.0,    0.0,  0.0,    # Front
                              1.0,  2.0,  0.1,    0.0,  0.0,  1.0,    1.0,  1.0,
                             -1.0,  2.0,  0.1,    0.0,  0.0,  1.0,    0.0,  1.0,

                             -1.0,  0.0,  0.1,    0.0,  0.0,  1.0,    0.0,  0.0,
                              1.0,  0.0,  0.1,    0.0,  0.0,  1.0,    1.0,  0.0,
                              1.0,  2.0,  0.1,    0.0,  0.0,  1.0,    1.0,  1.0,


                             -1.0,  0.0, -0.1,    0.0,  0.0, -1.0,    0.0,  0.0,    # Back
                             -1.0,  2.0, -0.1,    0.0,  0.0, -1.0,    0.0,  1.0,
                              1.0,  2.0, -0.1,    0.0,  0.0, -1.0,    1.0,  1.0,

                             -1.0,  0.0, -0.1,    0.0,  0.0, -1.0,    0.0,  0.0,
                              1.0,  2.0, -0.1,    0.0,  0.0, -1.0,    1.0,  1.0,
                              1.0,  0.0, -0.1,    0.0,  0.0, -1.0,    1.0,  0.0], dtype='float32')

        self.walls.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.walls.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 8
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        n_offset = 3
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * n_offset, ctypes.c_void_p))

        uv_offset = 6
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * uv_offset, ctypes.c_void_p))

        #
        glVertexAttribDivisor(0, 0)
        glVertexAttribDivisor(1, 0)
        glVertexAttribDivisor(2, 0)

        # -------- Build instance matrix (not mat4!)

        # Add outer perimiter walls
        for y in range(self.height):
            self.maze.o_walls.extend([float(y) * 2.2, 0.0, 1.1])
            self.maze.o_walls.extend([float(y) * 2.2, 0.0, -self.height * 2.2 + 1.1])

        for x in range(self.width):
            self.maze.o_walls.extend([-1.1, 1.0, -float(x) * 2.2])
            self.maze.o_walls.extend([self.width * 2.2 - 1.1, 1.0, -float(x) * 2.2])

        positions = np.array(self.maze.o_walls, dtype='float32')

        tolerance = 0.01    # Gap between walls forming cross sections to stop getting stuck when sliding against
        for i in range(0, len(positions), 3):
            x = positions[i + 0]
            y = positions[i + 1] 
            z = positions[i + 2] 

            direction = int(y)
            if direction:
                self.aabb_walls.append(PWWall(glm.vec2(x - 0.1, z - 1.2 + tolerance), glm.vec2(0.2, 2.4 - tolerance * 2.0)))
            else:
                self.aabb_walls.append(PWWall(glm.vec2(x - 1.2 + tolerance, z - 0.1), glm.vec2(2.4 - tolerance * 2.0, 0.2)))

        # Store instance count
        self.walls.count = int(len(positions) / 3)

        # -------- Feed data to instance buffer

        self.walls.data = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.walls.data)
        glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)

        stride = 3
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        #
        glVertexAttribDivisor(3, 1)


    def __createTrimsGeom(self):
        self.trims.vao = glGenVertexArrays(1)
        glBindVertexArray(self.trims.vao)

        # Position(3), Normal(3), Texture(2) == stride
        vertices = np.array([-0.1,  0.0, -1.0,    0.0,  0.0,  1.0,    0.0,  0.0, 
                              0.1,  2.0, -1.0,    0.0,  0.0,  1.0,    1.0,  1.0,
                             -0.1,  2.0, -1.0,    0.0,  0.0,  1.0,    0.0,  1.0,

                             -0.1,  0.0, -1.0,    0.0,  0.0,  1.0,    0.0,  0.0,
                              0.1,  0.0, -1.0,    0.0,  0.0,  1.0,    1.0,  0.0,
                              0.1,  2.0, -1.0,    0.0,  0.0,  1.0,    1.0,  1.0,


                             -0.1,  0.0,  1.0,    0.0,  0.0, -1.0,    0.0,  0.0, 
                             -0.1,  2.0,  1.0,    0.0,  0.0, -1.0,    0.0,  1.0,
                              0.1,  2.0,  1.0,    0.0,  0.0, -1.0,    1.0,  1.0,

                             -0.1,  0.0,  1.0,    0.0,  0.0, -1.0,    0.0,  0.0,
                              0.1,  2.0,  1.0,    0.0,  0.0, -1.0,    1.0,  1.0,
                              0.1,  0.0,  1.0,    0.0,  0.0, -1.0,    1.0,  0.0,


                             -0.1,  0.0,  1.0,    0.0,  1.0,  0.0,    0.0,  0.0, 
                              0.1,  0.0, -1.0,    0.0,  1.0,  0.0,    1.0,  1.0,
                             -0.1,  0.0, -1.0,    0.0,  1.0,  0.0,    0.0,  1.0,

                             -0.1,  0.0,  1.0,    0.0,  1.0,  0.0,    0.0,  0.0,
                              0.1,  0.0,  1.0,    0.0,  1.0,  0.0,    1.0,  0.0,
                              0.1,  0.0, -1.0,    0.0,  1.0,  0.0,    1.0,  1.0], dtype='float32')


        self.trims.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.trims.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        stride = 8
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        n_offset = 3
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * n_offset, ctypes.c_void_p))

        uv_offset = 6
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, self.d_fsize * stride, ctypes.cast(self.d_fsize * uv_offset, ctypes.c_void_p))

        #
        glVertexAttribDivisor(0, 0)
        glVertexAttribDivisor(1, 0)
        glVertexAttribDivisor(2, 0)

        # -------- Build instance matrix (not mat4!)

        positions = np.array(self.maze.o_trims, dtype='float32')

        # Store instance count
        self.trims.count = int(len(positions) / 3)

        # -------- Feed data to instance buffer

        self.trims.data = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.trims.data)
        glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)

        stride = 3
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, self.d_fsize * stride, None)

        #
        glVertexAttribDivisor(3, 1)


    def __renderFloor(self, shader, depth_only):
        if not depth_only:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, PWTextures.getTexture2D("floor_01").getTexture())

            glUniform2f(shader.texture_scale, 2.0, 2.0)

        glBindVertexArray(self.floors.vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 3 * 2, self.floors.count)


    def __renderWalls(self, shader, depth_only):
        if not depth_only:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, PWTextures.getTexture2D("wall_01").getTexture())

            glUniform2f(shader.texture_scale, 1.5, 1.5)

        glBindVertexArray(self.walls.vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 3 * 4, self.walls.count)

        # -------- Debug stuff

        #for wall in self.aabb_walls:
        #    wall.debugDraw()


    def __renderTrims(self, shader, depth_only):
        if not depth_only:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, PWTextures.getTexture2D("trim_01").getTexture())

            glUniform2f(shader.texture_scale, 1.0, 2.5)

        glBindVertexArray(self.trims.vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, 3 * 6, self.trims.count)


    def renderMaze(self, camera, depth_only=False, shadow_mapper=None):
        shader = None
        
        # depth shader should be active before making this call
        if not depth_only:
            shader = PWShaders.getShader(ShaderTypes.WORLD_SHADER)
            glUseProgram(shader.shader)
            
            glUniformMatrix4fv(shader.proj_view, 1, GL_FALSE, camera.getProjectionView())
            glUniformMatrix4fv(shader.light_proj_view, 1, GL_FALSE, shadow_mapper.getProjectionView())

            light_direction = shadow_mapper.getLightDirection()
            glUniform3f(shader.light_direction, light_direction.x, light_direction.y, light_direction.z)

            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, shadow_mapper.getDepthMap())

        # --------

        self.__renderFloor(shader, depth_only)
        self.__renderWalls(shader, depth_only)
        self.__renderTrims(shader, depth_only)


# Generate 2D debug view of the maze
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.init()
    screen = pygame.display.set_mode((512, 512))

    clock = pygame.time.Clock()

    # --------

    generator = PWMazeGenerator(16, 16)
    while(not generator.stepMaze()):
        pass

    while 1:
        delta = clock.tick(8192) / 1000.0
        seconds = pygame.time.get_ticks() / 1000.0

        screen.fill((0x0, 0x0, 0x0))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        generator.render(screen)

        pygame.display.flip()
    

