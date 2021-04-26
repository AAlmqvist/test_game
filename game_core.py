import pyglet
from pyglet.window.key import *
import os

#Create the window
window = pyglet.window.Window()

# creating path to load image/sound from right directories
work_dir = os.path.dirname(os.path.relpath(__file__))
pyglet.resource.path = [os.path.join(work_dir, './images'), os.path.join(work_dir, './sounds')]
pyglet.resource.reindex()

# create batches for moving and static objects
batch = pyglet.graphics.Batch()
static_batch = pyglet.graphics.Batch()

# label to display text on how to get help 
test_label = pyglet.text.Label(anchor_x='left', anchor_y='top')

# label with actual help text
help_label = pyglet.text.Label(anchor_x='center', anchor_y='center')
help_draw = False

# Function for when window draws the new state
@window.event
def on_draw():
    pyglet.gl.glClearColor(*background, 1)
    window.clear()
    static_batch.draw()
    batch.draw()

    test_label.text = 'Help: H'
    test_label.font_size = window.height//40
    test_label.draw()

    if help_draw:
        help_label.text = 'Red blob: WASD\nGreen blob: SPACE to jump and O-P to move sideways\nBACKSPACE: reset game'
        help_label.font_size = window.height//30
        help_label.width = window.width//1.5
        help_label.height = window.height//1.5
        help_label.multiline = True
        help_label.draw()

# sets to save state of key-presses
key_state = key_state_old = set()

# when key is pressed
@window.event
def on_key_press(symbol, modifiers):
    key_state.add(symbol)

# when key is released
@window.event
def on_key_release(symbol, modifiers):
    key_state.discard(symbol)

# boolean funtction to see if key is pressed
def key(k):
    return k in key_state

# boolean function to see if key was pressed last cycle
def key_old(k):
    return k in key_state_old

# list to bunch all the moving stuff together 
movers = []

# dummy class for all moving objects
class Mover:
    pass

# creating a moving object
def createMovingObject(move_func, image=None, size=0.1, x=0, y=0, dx=0, dy=0, **kargs):
    m = Mover()
    # This is the move-function that specifies each moving objects abilities
    m.move = move_func
    m.image = image

    if image:
        m.sprite = pyglet.sprite.Sprite(image, batch=batch)
        m.sprite.scale_x = m.sprite.scale_y = 0
    else:
        m.sprite = None
    
    m.sx = m.sy = size
    m.x, m.y = x, y
    m.dx, m.dy = dx, dy
    m.r = m.state = m.time = 0
    m.life = 1

    for k, v in kargs.items():
        setattr(m, k, v)

    movers.append(m)

    return m

# Gridded list that keeps track of where on the map there are walls
walls = [[None for loop_y in range(20)] for loop_x in range(30)]

# dummy class for static objects
class StaticObject:
    pass

# Function to create a static object, a.k.a. a wall
def createStaticObject(image=None, size=0.1, x=0, y=0, **kargs):
    st = StaticObject()
    st.image = image

    if image:
        st.sprite = pyglet.sprite.Sprite(image, batch=static_batch)
        st.scale_x = st.scale_y = 0
        # 900x600 window, 30x20 grid cells, each grid cell is 30x30 pixels
        st.sprite.x = 15 + x*30 # +15 to center the sprite
        st.sprite.y = 15 + y*30 # +15 to center the sprite
    else:
        st.sprite = None

    st.x = (st.sprite.x - 450) / 450
    st.y = (st.sprite.y - 300) / 300

    for k, v in kargs.items():
        setattr(st, k, v)
    walls[x][y] = st

# Function that loads the image files
def image(file):
    img = pyglet.resource.image(file)
    img.anchor_x = img.width//2
    img.anchor_y = img.height//2
    return img

# Function to get itterator from group of objects with specified move-function (could list many move funcs)
def group(*move):
    for m in movers:
        if m.move in move:
            yield m

# time constants used for when to move stuff
time_sum = 0
time_min = (1/60)*0.9

# Cyclic function called by the window to update the state of the game
def move_objects(dt):
    global help_draw, key_state_old, time_sum, time_min, movers

    time_sum += dt

    if time_sum > time_min:
        time_sum = 0

        for m in movers:
            m.move(m)

    w, w2, h2 = window.width, window.width//2, window.height//2

    for m in movers:
        if m.sprite:
            m.sprite.image = m.image
            m.sprite.scale_x = m.sx * w / m.image.width
            m.sprite.scale_y = m.sy *w / m.image.height
            m.sprite.x = m.x * w2 + w2
            m.sprite.y = m.y * h2 + h2
            m.sprite.rotation = -m.r * 360

    old_movers = movers
    movers = [m for m in old_movers if m.life > 0]

    if key(ESCAPE):
        pyglet.app.exit()

    if key(H) and not key_old(H):
        help_draw = not help_draw

    if key(BACKSPACE) and not key_old(BACKSPACE):
        movers.clear()
        start()

    key_state_old = key_state.copy()

# Function that starts and runs the app
def run(start_func, w=window.width, h=window.height, bg=(1,1,1), fs=False, tc=(0.5, 0.5, 0.5), tfn='Arial'):
    global start, background

    
    window.set_size(w,h)
    window.set_fullscreen(fs)



    start = start_func

    background = bg
    

    test_label.color = int(255*tc[0]), int(255*tc[1]), int(255*tc[2]), 255
    test_label.font_name = tfn
    test_label.x = 32
    test_label.y = h-32

    help_label.x = w//2
    help_label.y = h//2


    start()

    pyglet.clock.schedule(move_objects)
    
    pyglet.app.run()