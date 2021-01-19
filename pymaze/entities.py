import glm

from debug import *

class PWBBox(object):
    def __init__(self, wh, pos):
        self.wh = wh
        self.pos = pos

    def updatePos(self, x, y):
        self.pos.x = x
        self.pos.y = y

    def colliderect(self, rect):
        s = 64.0    # Increase the resolution for the collision checking

        p_pos1 = self.pos * s
        r_pos1 = (rect.pos + rect.bbox.wh) * s

        p_pos2 = (self.pos + self.wh) * s
        r_pos2 = rect.pos * s

        if (p_pos1.x < r_pos1.x and p_pos2.x > r_pos2.x) and \
           (p_pos1.y < r_pos1.y and p_pos2.y > r_pos2.y):
            return True
        else:
            return False


class PWWall(object):
    def __init__(self, position, wh):
        self.pos = glm.vec2(position)
        self.bbox = PWBBox(wh, glm.vec2(self.pos.x, self.pos.y))

    def debugDraw(self):
        tl = glm.vec3(self.pos.x, 0.0, self.pos.y)
        tr = glm.vec3(self.pos.x + self.bbox.wh.x, 0.0, self.pos.y + self.bbox.wh.y)

        PWDebug.drawLine(tl, tl + glm.vec3(self.bbox.wh.x, 0.0, 0.0))
        PWDebug.drawLine(tl, tl + glm.vec3(0.0, 0.0, self.bbox.wh.y))

        PWDebug.drawLine(tr, tr - glm.vec3(self.bbox.wh.x, 0.0, 0.0))
        PWDebug.drawLine(tr, tr - glm.vec3(0.0, 0.0, self.bbox.wh.y))