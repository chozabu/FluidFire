"""Foobar.py: Description of what foobar does."""

__author__ = "Alex 'Chozabu' P-B"
__copyright__ = "Chozabu"

import sys
import pygame
from pygame.locals import *
from math import *
import random
import time

sw = 800
sh = 800

import random

letters = "abergbargbai3gbkvb"


def randword():
    wrd = ""
    for x in range(5):
        wrd += random.choice(letters)
    return wrd


class Rock:
    def __init__(self, name=None, world=None, parent=None, pos=None):
        self.world = world
        if pos:
            self.x = pos[0]
            self.y = pos[1]
        else:
            self.x = random.random() * world.width
            self.y = random.random() * world.height
        self.z = random.random()
        self.parent = parent
        world.rocks.append(self)
        if name:
            self.name = name
        else:
            self.name = randword()

    def step(self):
        self.y *=0.999
        self.y-=0.3
        if self.y> self.world.height: self.y-=self.world.height
        if self.y< 0: self.y+=self.world.height
        nrad = 20
        nrad2 = nrad * nrad
        for na in self.world.players:
            nb = self
            xd = na.x - nb.x
            yd = na.y - nb.y
            zd = na.z - nb.z
            td2 = xd * xd + yd * yd
            if td2 < nrad2 * 1.0:
                if na.parent:
                    na.parent.uppower += 0.05
                td = sqrt(td2) + 0.001
                diffd = nrad - td
                diffd *= .5
                xd /= td
                yd /= td
                zd /= td
                na.x += xd * diffd
                na.y += yd * diffd


class Player:
    def __init__(self, name=None, world=None, parent=None, pos=None):
        self.world = world
        self.hp = 1.0
        if pos:
            self.x = pos[0]
            self.y = pos[1]
        else:
            self.x = random.random() * world.width
            self.y = random.random() * world.height
        self.ox = self.x
        self.oy = self.y
        self.vx = 0
        self.vy = 0
        self.v2 = 0
        self.z = random.random()
        self.parent = parent
        world.players.append(self)
        if name:
            self.name = name
        else:
            self.name = randword()

    def set_parent(self, new):
        self.parent.minions.remove(self)
        self.parent = new
        self.parent.minions.append(self)

    def step(self):
        if self.hp < 1:
            self.hp += 0.01

        self.oy -= 0.05

        xd = self.x - self.ox
        yd = self.y - self.oy

        self.vx = xd
        self.vy = yd

        self.v2 = xd ** 2 + yd ** 2
        if self.v2 > 100:
            xd *= .9
            yd *= .9

        self.ox = self.x
        self.x += xd * .998
        self.oy = self.y

        self.y += yd * .998

        wrap = True
        if not wrap:
            self.x = max(min(self.x, self.world.width), 0)
            self.y = max(min(self.y, self.world.height), 0)
        else:
            if self.x < 0:
                self.x += self.world.width
                self.ox += self.world.width
            if self.x > self.world.width:
                self.x -= self.world.width
                self.ox -= self.world.width

            if self.y < 0:
                self.y += self.world.height
                self.oy += self.world.height
            if self.y > self.world.height:
                self.y -= self.world.height
                self.oy -= self.world.height

    def __repr__(self):
        return self.name


class SuPlayer:
    def __init__(self, name=None, world=None, pos=None):
        self.world = world
        self.hp = 1.0
        if pos:
            self.x = pos[0]
            self.y = pos[1]
        else:
            self.x = random.random() * world.width
            self.y = random.random() * world.height
        self.ox = self.x
        self.oy = self.y
        self.vx = 0
        self.vy = 0
        self.v2 = 0
        self.joystick = None
        self.z = random.random()
        if name:
            self.name = name
        else:
            self.name = randword()
        # super().__init__(world=world,name=name)
        self.minions = []
        self.colour = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        self.xforce = 0
        self.yforce = 0
        self.jumping = False
        self.input_x = 0.0
        self.input_y = 0.0
        self.uppower = 0.2
        world.suplayers.append(self)

        for p in range(60):
            pos = (random.randrange(int(self.x - 20), int(self.x + 20)), random.randrange(int(self.y - 20), int(self.y + 20)))
            minion = Player(world=self.world, parent=self, pos=pos)
            self.minions.append(minion)

    def step(self):
        self.oy = self.y
        self.ox = self.x
        if not self.minions:
            return
        # super().step()
        # self.x=0
        # self.y=0
        newx = 0
        newy = 0
        mnum = 0
        for p in self.minions:
            xd = p.x - self.x
            yd = p.y - self.y
            if abs(xd) < 300 and abs(yd) < 300:
                newx += p.x
                newy += p.y
                mnum += 1
        if mnum > len(self.minions)/3:
            self.x = newx / mnum
            self.y = newy / mnum
        else:
            self.x = 0
            self.y = 0
            mnum = 0
            for p in self.minions:
                self.x += p.x
                self.y += p.y
                mnum += 1
            if mnum:
                self.x = self.x / mnum
                self.y = self.y / mnum

        forcemul = 10.0
        if self.joystick:
            self.input_x = self.joystick.get_axis(0)
            self.input_y = self.joystick.get_axis(1)
        else:
            pass
            nrsu = None
            nrsd = 1000000
            for sp in self.world.suplayers:
                if sp == self: continue
                if not sp.minions: continue
                xd = self.x-sp.x
                yd = self.y-sp.y
                td2 = xd**2+yd**2
                if td2 < nrsd:
                    nrsd = td2
                    nrsu = sp
            if nrsu:
                xd = self.x-nrsu.x
                yd = self.y-nrsu.y
                if yd > 0:
                    if xd > 0:
                        self.input_x = 1.0
                    else:
                        self.input_x = -1.0
                else:
                    if xd > 0:
                        self.input_x = -1.0
                    else:
                        self.input_x = 1.0
                if abs(xd) < 40:
                    self.input_y = 1.0
                elif abs(xd) > 200:
                    self.input_y = -1.0

        self.xforce = self.input_x
        self.yforce = self.input_y
        if self.yforce > 0:
            self.yforce *= 1.0
        else:
            self.yforce *= self.uppower
        self.x += self.xforce * forcemul
        self.y += self.yforce * forcemul
        if self.jumping:
            self.jumping = False
            self.y -= 100
        for p in self.minions:
            xd = p.x - self.x
            yd = p.y - self.y
            if abs(xd) < 300 and abs(yd) < 300:
                p.x -= xd * .01
                p.y -= yd * .01
        self.uppower = 0.2
    def wxd(self, other):
        xd = self.x - other
        if other > self.x:
            axd = (other-self.world.width)

class World:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.players = []
        self.suplayers = []
        self.rocks = []
        self.gridsize = 50
        self.xc = int(width/self.gridsize)
        self.yc = int(height/self.gridsize)
        self.grid = []
        for x in range(self.yc):
            row = [[] for y in range(self.xc)]
            self.grid.append(row)

    def add_suplayer(self, name=None, output=False, input=False, pos=None):
        player = SuPlayer(name=name, world=self, pos=pos)

        return player

    def add_player(self, name=None, output=False, input=False, pos=None, parent=None):
        player = Player(name=name, world=self, parent=parent)
        # self.players.append(player)
        return player

    def mainstep(self):
        for x in self.grid:
            for y in x:
                y.clear()
        #print(self.grid[0])
        for n in self.players:
            n.step()
        for n in self.suplayers:
            n.step()
        for n in self.rocks:
            n.step()
        for n in self.players:
            nx = int(n.x/self.gridsize)
            ny = int(n.y/self.gridsize)
            if nx < self.xc and nx > 0 and ny > 0 and ny < self.yc:
                self.grid[nx][ny].append(n)
        self.layout_net()


    def layout_net(self):
        #for i in range(1):
        for x in self.grid:
            for g in x:
                my_players = g
                astr = -.01
                nnum = len(my_players)
                nrad = 20
                nrad2 = nrad * nrad
                '''for s in nn.synapses:
                    xd = s.start.x - s.target.x
                    yd = s.start.y - s.target.y
                    s.start.x += xd * astr
                    s.start.y += yd * astr
                    s.target.x -= xd * astr
                    s.target.y -= yd * astr'''

                for nai in range(nnum - 1):
                    for nbi in range(nai + 1, nnum):
                        na = my_players[nai]
                        nb = my_players[nbi]
                        xd = na.x - nb.x
                        yd = na.y - nb.y
                        zd = na.z - nb.z
                        td2 = xd * xd + yd * yd + zd * zd
                        if td2 < nrad2 * 1.2:
                            if na.parent != nb.parent and na.parent and nb.parent:
                                victim = na if na.y > nb.y else nb
                                attacker = na if na.y <= nb.y else nb
                                if victim.hp > 0.1:
                                    victim.hp -= 0.1
                                else:
                                    victim.set_parent(attacker.parent)
                            td = sqrt(td2) + 0.001
                            diffd = nrad - td
                            diffd *= .1
                            xd /= td
                            yd /= td
                            zd /= td
                            na.x += xd * diffd
                            na.y += yd * diffd
                            na.z += zd * diffd
                            nb.x -= xd * diffd
                            nb.y -= yd * diffd
                            na.z -= zd * diffd

def init_world():
    joystick_count = pygame.joystick.get_count()

    world = World(width=sw, height=sh)

    world.add_suplayer(pos=(sw * .1, sh * .7))
    world.add_suplayer(pos=(sw - sw * .1, sh * .7))

    for i in range(50):
        pos = (random.random() * sw, random.random() * sh)
        Rock(world=world, pos=pos)
        pos = (sw - pos[0], pos[1])
        Rock(world=world, pos=pos)


    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        if i < len(world.suplayers):
            world.suplayers[i].joystick = joystick
    return world

def run_pygame():
    length = 10

    pygame.init()
    screen = pygame.display.set_mode((sw, sh), 0, 32)
    blanker = pygame.surface.Surface((sw, sh), pygame.SRCALPHA, 32)
    blanker.fill((0, 0, 0, 10))


    whiter = pygame.surface.Surface((400, 400), pygame.SRCALPHA, 32)
    whiter.fill((255, 255, 255, 10))

    # Initialize the joysticks
    pygame.joystick.init()



    world = init_world()

    ingame = 1
    nearest = None
    steps = 0
    spawning = False
    mousedown = False
    mousedown2 = False

    controldict = {
        K_w: {"player": world.suplayers[0], 'attr': 'input_y', 'val': [-1.0, 0]},
        K_s: {"player": world.suplayers[0], 'attr': 'input_y', 'val': [1.0, 0]},
        K_d: {"player": world.suplayers[0], 'attr': 'input_x', 'val': [1.0, 0]},
        K_a: {"player": world.suplayers[0], 'attr': 'input_x', 'val': [-1.0, 0]},
        K_q: {"player": world.suplayers[0], 'attr': 'jumping', 'val': [True, False]},

        K_i: {"player": world.suplayers[1], 'attr': 'input_y', 'val': [-1.0, 0]},
        K_k: {"player": world.suplayers[1], 'attr': 'input_y', 'val': [1.0, 0]},
        K_l: {"player": world.suplayers[1], 'attr': 'input_x', 'val': [1.0, 0]},
        K_j: {"player": world.suplayers[1], 'attr': 'input_x', 'val': [-1.0, 0]},
    }


    while ingame:
        steps += 1
        #layout_net(world)

        pos = pygame.mouse.get_pos()

        if spawning:
            for i in range(20):
                world.add_player()  # pos = pos)
        if mousedown:
            for p in world.players:
                xd = p.x - pos[0]
                yd = p.y - pos[1]
                p.x += xd * .002
                p.y += yd * .002

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                cd = controldict.get(event.key)
                if cd:
                    player = cd['player']
                    setattr(player,cd['attr'], cd['val'][0])
                if event.key == K_ESCAPE:
                    ingame = False
                elif event.key == K_t:
                    spawning = True
                elif event.key == K_p:
                    world.add_suplayer()
                elif event.key == K_o:
                    for i in range(5):
                        pos = (random.random() * sw, random.random() * sh)
                        Rock(world=world, pos=pos)
                        pos = (sw - pos[0], pos[1])
                        Rock(world=world, pos=pos)
                elif event.key == K_r:
                    world = init_world()
                # player1
            elif event.type == pygame.KEYUP:
                if event.key == K_t:
                    spawning = False
                cd = controldict.get(event.key)
                if cd:
                    player = cd['player']
                    setattr(player,cd['attr'], cd['val'][1])
            if event.type == pygame.MOUSEBUTTONUP:
                mousedown = False
                nearest = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousedown = True

                steps = 0
                # for inny in nn.inputs:
                #     inny.val = 0

                neardist = 100000
                for n in world.players:
                    xd = n.x - pos[0]
                    yd = n.y - pos[1]
                    td = xd * xd + yd * yd
                    if td < neardist:
                        neardist = td
                        nearest = n
        if nearest:
            nearest.x = pos[0]
            nearest.y = pos[1]

        world.mainstep()
        pygame.time.wait(10)
        # screen.fill((10, 10, 25, 0))

        if 1:#steps % 10 == 0:
            col = (abs(int(sin(steps * 0.06783) * 254)), max(min(abs((steps % 400) - 200) + 55, 255), 0.01), abs(int(sin(steps * 0.0673) * 254)))
            x = random.randint(-200,world.width+200)
            y = random.randint(-200,world.height+200)
            rad = random.randint(20,100)
            #pygame.draw.circle(screen, col, (int(x), int(y)), int(rad))
            screen.blit(whiter, (x,y))

        screen.blit(blanker, (0, 0))
        '''for s in nn.synapses:
            x = s.start.x
            y = s.start.y
            nx = s.target.x
            ny = s.target.y
            # print(x,y,nx,ny)

            n = s.start

            col = (1, max(min((n.val * 20)*s.weight, 255), 0.01), 1)
            if n.fired > 0:
                col = (1, max(min(n.val * 20, 255), 0.01), 255)

            col = [int(x) for x in col]

            #print(col)
            pygame.draw.line(screen, col, (int(x), int(y)), (int(nx), int(ny)), int(length / 10))
            nx = x+(nx-x)*.1
            ny = y+(ny-y)*.1
            pygame.draw.line(screen, col, (int(x), int(y)), (int(nx), int(ny)), int(length/2))'''
        for n in world.players:
            x = n.x
            y = n.y
            z = n.z
            # rad = (z*10+10)*.5+1.0
            rad = 3
            col = (1, max(min(50 + n.v2, 255), 0.01), 1)
            col = [int(x) for x in col]
            if hasattr(n, 'parent') and n.parent:
                col = n.parent.colour
                hp = n.hp
                col = [int(c * n.hp + (255 - 255 * hp)) for c in col]
            # print(col)
            pygame.draw.circle(screen, col, (int(x), int(y)), int(rad))
            pygame.draw.line(screen, col, (int(x), int(y)), (int(n.ox), int(n.oy)), int(length / 10))
        for n in world.suplayers:
            if not n.minions:
                continue
            x = n.x
            y = n.y
            rad = 5
            col = n.colour

            # print(col)
            # pygame.draw.circle(screen, col, (int(x), int(y)), int(rad))
            pygame.draw.line(screen, col, (int(x), int(y)), (int(n.ox), int(n.oy)), int(length / 10))
            pygame.draw.line(screen, col, (int(x + 15), int(y)), (int(n.x - 15), int(n.y)), int(length / 10))
            pygame.draw.line(screen, col, (int(x), int(y + 15)), (int(n.x), int(n.y - 15)), int(length / 10))
        for n in world.rocks:
            x = n.x
            y = n.y
            rad = 10+cos(steps/10+n.y/100+n.x)*3
            col = (abs(int(sin(steps*.01)*254)), max(min(abs((steps%400)-200)+55, 255), 0.01), abs(int(sin(steps*.0123456)*254)))
            col = [int(x) for x in col]
            # print(col)
            pygame.draw.circle(screen, col, (int(x), int(y)), int(rad))
        pygame.display.flip()
