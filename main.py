import pyglet
from game_core import *
import math

# Sprites: around 30x30 pixels, Screen is 900x600

w2 = 900//2
h2 = 600//2

# Loading images
player_image = image('weird_guy.png')
jumper_image = image('jump_guy.png')
badmouse = image('badmouse.png')
brick_image = image('brick.png')
spikes_image = image('spikes.png')
untargetable_image = image('untargetable.png')

# Defining the movement of normal player
def player(p):
    v = 0.02

    if key( pyglet.window.key.A ):
        p.dx -= v
    
    if key( pyglet.window.key.W ):
        p.dy += v
    
    if key( pyglet.window.key.D ):
        p.dx += v
    
    if key(pyglet.window.key.S):
        p.dy -= v

    #Check for collision
    x_grid = max(1, min(math.floor((p.x+1)*15),28))
    y_grid = max(1, min(math.floor((p.y+1)*10),18))

    if abs(p.dy) > 0:
        sign = round(p.dy/abs(p.dy))
        for j in range(-1,2):
            potential_wall = walls[x_grid+j][y_grid+sign]
            if potential_wall:
                if abs(p.y+p.dy - potential_wall.y) < 1.5*p.sy + 15/300 and abs(p.x - potential_wall.x) < 0.8*p.sx + 15/450:
                    p.y = potential_wall.y - sign*(1.5*p.sy + 15/300)
                    p.dy = 0

    if abs(p.dx) > 0:
        sign = round(p.dx/abs(p.dx))
        for j in range(-1,2):
            potential_wall = walls[x_grid+sign][y_grid+j]
            if potential_wall:
                if abs(p.x+p.dx - potential_wall.x) < p.sx + 15/450 and abs(p.y - potential_wall.y) < p.sy + 15/300:
                    p.x = potential_wall.x - sign*(p.sx + 15/450)
                    p.dx = 0
    
    if math.sqrt(p.dx**2+p.dy**2) > v:
        p.dx = p.dx/1.42
        p.dy = p.dy/1.42
    
    p.x += p.dx
    p.y += p.dy

    p.dx, p.dy = 0, 0
    p.time += time_min

    if p.untargetable:
        p.time_hit += time_min
        if p.time_hit > 1:
            p.untargetable = False
            p.image = player_image


# defining the movement of a character affected by gravity
def jumper(l):
    # gravitational constant
    g = 0.0012
    l.time += time_min
    
    if l.y > -1 + 2*l.sy:
        l.dy -= g

    if key(pyglet.window.key.SPACE) and l.time > 0.1 and l.ground_below:
        l.dy = 0.04
        l.time = 0
    
    if key(pyglet.window.key.P):
        l.dx += 0.02
    
    if key(pyglet.window.key.O):
        l.dx -= 0.02

    # rotate sprite according to velocity in x-direction
    if l.dx > 0:
        l.r = 1-0.125
    elif l.dx <0:
        l.r = 0.125
    else:
        l.r = 0

    #Check for collision
    x_grid = max(1, min(math.floor((l.x+1)*15),28))
    y_grid = max(1, min(math.floor((l.y+1)*10),18))

    solid_ground = False
    if abs(l.dy) > 0:
        sign = round(l.dy/abs(l.dy))
        for j in range(-1,2):
            potential_wall = walls[x_grid+j][y_grid+sign]
            if potential_wall:
                if abs(l.y+l.dy - potential_wall.y) < 1.5*l.sy + 15/300 and abs(l.x - potential_wall.x) < 0.8*l.sx + 15/450:
                    if l.dy < 0:
                        solid_ground = True
                    l.y = potential_wall.y - sign*(1.5*l.sy + 15/300)
                    l.dy = 0

    if abs(l.dx) > 0:
        sign = round(l.dx/abs(l.dx))
        for j in range(-1,2):
            potential_wall = walls[x_grid+sign][y_grid+j]
            if potential_wall:
                if abs(l.x+l.dx - potential_wall.x) < l.sx + 15/450 and abs(l.y - potential_wall.y) < l.sy + 15/300:
                    l.x = potential_wall.x - sign*(l.sx + 15/450)
                    l.dx = 0
    l.y += l.dy
    l.x += l.dx
    l.ground_below = solid_ground
    l.dx = 0
    if l.untargetable:
        l.time_hit += time_min
        if l.time_hit > 1:
            l.untargetable = False
            l.image = jumper_image

def spikes(sp):
    for o in group(player, jumper):
        if not o.untargetable:
            if o.y > sp.y:
                if abs(o.x-sp.x) < 15/450 + o.sx and abs(o.y-sp.y) < 7/300 + o.sy:
                    o.life -= 1
                    o.image = untargetable_image
                    o.untargetable = True
                    o.time_hit = 0
    sp.time += time_min

def createBorders():
    for i in range(30):
        createStaticObject(brick_image, 30/600, i, 0)
        createStaticObject(brick_image, 30/600, i, 19)
    for j in range(20):
        createStaticObject(brick_image, 30/600, 0, j)
        createStaticObject(brick_image, 30/600, 29, j)

def level(ind):
    if 1:
        for i in range(4,10):
            createStaticObject(brick_image, 30/600, i, 4)
        for i in range(3,8):
            createStaticObject(brick_image, 30/600, i, 15)
        for i in range(16,23):
            createStaticObject(brick_image, 30/600, i, 8)
        for i in range(23,26):
            createStaticObject(brick_image, 30/600, i, 13)
        for i in range(9,11):
            createStaticObject(brick_image, 30/600, i, 12)
        for i in range(17,19):
            createStaticObject(brick_image, 30/600, i, 14)
        for i in range(14,17):
            createStaticObject(brick_image, 30/600, 23, i)
        for i in range(26,29):
            createSpikes(-1 + (i+0.5)*(30/450), -1 + (0.1+12/300) )

def createPlayer(size=0.1, x=0, y=0):
    createMovingObject(player, player_image, size=size, x=x , y=y, life=2, untargetable=False)

def createJumper(size=0.1, x=0, y=0):
    createMovingObject(jumper, jumper_image, size = size, x=x, y=y, ground_below=False, life=2, untargetable=False)

def createSpikes(x=0, y=0):
    createMovingObject(spikes, spikes_image, 27/900, x=x, y=y)

def start_now():
    print("Starting game")
    createBorders()
    level(1)
    createPlayer(30/900, -0.2 , 0)
    createJumper(30/900, 0.2, 0)


run(start_now, w=2*w2, h=2*h2, bg=(0.5, 0.5, 1), tc=(1,1,1))

