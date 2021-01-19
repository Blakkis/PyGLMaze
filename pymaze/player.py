import pygame
from pygame.locals import *
import glm

from constants import *
from debug import *
from entities import *


class PWPlayerAction:
    ACTION_NONE   = 0
    ACTION_WALK   = 1
    ACTION_RUN    = 2
    ACTION_JUMP   = 3
    ACTION_CROUCH = 4


class PWPlayer(PWConstants, PWPlayerAction):
    def __init__(self, position):
        self.bbox_size = 0.25

        self.pos = glm.vec2(position.x, position.y) - self.bbox_size / 2.0
        self.old_pos = glm.vec2(position.x, position.y) - self.bbox_size / 2.0

        self.bbox = PWBBox(glm.vec2(self.bbox_size), glm.vec2(self.pos.x, self.pos.y))
        self.bbox_advance = PWBBox(glm.vec2(self.bbox_size), glm.vec2(self.pos.x, self.pos.y)) 

        self.pos_ud_v = 0.0     # Velocity
        self.pos_ud = 0.0       # Up/Down position (tricks)
        self.action = self.ACTION_NONE


    def getCurrentAction(self):
        return self.action


    def getPosition(self):
        position = self.pos + self.bbox_size / 2.0
        return glm.vec3(position.x, self.pos_ud, position.y)


    def __checkCollisionX(self, move_direction, vector, wall):
        if move_direction.x == 0:
            return

        self.bbox_advance.updatePos(self.old_pos.x, self.old_pos.y)
        self.bbox_advance.pos.x += vector

        if self.bbox_advance.colliderect(wall):
            if move_direction.x > 0:
                self.pos.x = wall.pos.x - self.bbox.wh.x
            else:
                self.pos.x = wall.pos.x + wall.bbox.wh.x    


    def __checkCollisionY(self, move_direction, vector, wall):
        if move_direction.z == 0:
            return

        self.bbox_advance.updatePos(self.old_pos.x, self.old_pos.y)
        self.bbox_advance.pos.y += vector

        if self.bbox_advance.colliderect(wall):
            if move_direction.z > 0:
                self.pos.y = wall.pos.y - self.bbox.wh.y
            else:
                self.pos.y = wall.pos.y + wall.bbox.wh.y       


    def checkCollision(self, move_direction, walls):
        for wall in walls:
            if self.bbox.colliderect(wall):
                length = glm.length(self.pos - self.old_pos)
                offset = glm.normalize(self.pos - self.old_pos)

                self.__checkCollisionX(move_direction, offset.x * length, wall) 
                self.__checkCollisionY(move_direction, offset.y * length, wall)


    # TODO: Add crouching
    def handleSpecialActions(self, delta):
        keys = pygame.key.get_pressed()

        if keys[K_SPACE] and self.action == self.ACTION_NONE:
            self.action = self.ACTION_JUMP
            self.pos_ud_v += self.p_jump_vel

        # Player is in air
        if self.action == self.ACTION_JUMP:
            self.pos_ud_v -= self.d_gravity * delta
            self.pos_ud   += self.pos_ud_v * delta

        # Player is touching the ground. Make sure player doesn't fall through the floor.
        if self.pos_ud <= 0.0:
            self.pos_ud = 0.0
            self.pos_ud_v = 0.0
            self.action = self.ACTION_NONE



    def getMovementDirection(self, camera):
        yaw = glm.radians(-camera.yaw)

        cam_cos = glm.cos(yaw)
        cam_sin = glm.sin(yaw)

        keys = pygame.key.get_pressed()
        move_direction = glm.vec3(0.0)

        if keys[K_w]:
            move_direction -= glm.vec3(-cam_cos, 0.0, cam_sin)

        if keys[K_s]:
            move_direction += glm.vec3(-cam_cos, 0.0, cam_sin)

        if keys[K_d]:
            move_direction += glm.vec3(cam_sin, 0.0, cam_cos)

        if keys[K_a]:
            move_direction -= glm.vec3(cam_sin, 0.0, cam_cos)

        # Normalize the direction, so going diagonally wont result in faster movement.
        if glm.length(move_direction) > 0:
            move_direction = glm.normalize(move_direction)

        return move_direction


    # Draws player bounding box
    def debugDraw(self):
        tl = glm.vec3(self.pos.x, 0.0, self.pos.y)
        tr = glm.vec3(self.pos.x + self.bbox.wh.x, 0.0, self.pos.y + self.bbox.wh.y)

        PWDebug.drawLine(tl, tl + glm.vec3(self.bbox.wh.x, 0.0, 0.0))
        PWDebug.drawLine(tl, tl + glm.vec3(0.0, 0.0, self.bbox.wh.y))

        PWDebug.drawLine(tr, tr - glm.vec3(self.bbox.wh.x, 0.0, 0.0))
        PWDebug.drawLine(tr, tr - glm.vec3(0.0, 0.0, self.bbox.wh.y))


    # TODO: Add smoother movement
    def update(self, delta, camera, walls):
        move_direction = self.getMovementDirection(camera)

        self.old_pos.x = self.pos.x
        self.old_pos.y = self.pos.y
        
        self.pos.x += move_direction.x * self.p_speed * delta
        self.pos.y += move_direction.z * self.p_speed * delta

        self.bbox.updatePos(self.pos.x, self.pos.y)
        #self.debugDraw()
        
        self.checkCollision(move_direction, walls)

        # --------

        self.handleSpecialActions(delta)     # These are mostly camera illusion tricks


if __name__ == "__main__":
    pass
