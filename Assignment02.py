import sys
import random
import time
from math import fabs
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import * 
WINDOW_WIDTH=800 #resolution ar fps for smoothness
WINDOW_HEIGHT=600
FPS_TARGET=60

WHITE=(1.0,1.0,1.0)
RED=(1.0, 0.2,0.2)
TEAL=(0.0,0.8,0.7)
AMBER=(1.0,0.6,0.0)
BLACK=(0.0,0.0,0.0)
score=0
playing=True #game chole 
game_over=False
cheat_mode=False
last_time=None
diamond_x=0
diamond_y=0 #decrease namar time 
diamond_size=18 
diamond_color=(1, 1, 1)
diamond_speed=120.0 
diamond_accel=20.0  #speed increase 

catcher_width=140 #catcher trapzoid shape 
catcher_height=24
catcher_y=40
catcher_x=WINDOW_WIDTH//2
catcher_speed=350.0 
catcher_color=WHITE
 
button_top=WINDOW_HEIGHT-60
button_height=44
button_width=64
button_spacing=20
left_button_x=20 #restart
middle_button_x=left_button_x+button_width+button_spacing #play
right_button_x=middle_button_x+button_width+button_spacing #cross

def current_time():
    return time.time()

def midpoint_line(x0, y0, x1, y1):
    x0 = int(round(x0))
    y0 = int(round(y0))
    x1 = int(round(x1))
    y1 = int(round(y1))
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    if x0 < x1:
        sx=1  
    else: 
        sx=-1
    if y0 < y1:    
        sy=1  
    else:
        sy=-1
    if dy <= dx:
        err=dx//2
        y=y0
        x=x0
        for r in range(dx+1):
            glVertex2i(x,y)
            x+=sx
            err-=dy
            if err < 0:
                y+=sy
                err+=dx
    else:
        err=dy//2
        x=x0
        y=y0
        for i in range(dy+1):
            glVertex2i(x,y)
            y+=sy
            err-=dx
            if err < 0:
                x+=sx
                err+=dy

def draw_line(x0, y0, x1, y1):
    glBegin(GL_POINTS)
    midpoint_line(x0, y0, x1, y1)
    glEnd()

def draw_diamond(cx, cy, size, color): #4 line diye diamond 
    r,g,b=color
    glColor3f(r, g, b)
    top=(cx,cy+size)
    right=(cx+size,cy)
    bottom=(cx,cy-size)
    left=(cx-size,cy)
    glBegin(GL_POINTS)
    midpoint_line(top[0],top[1],right[0],right[1])
    midpoint_line(right[0],right[1],bottom[0],bottom[1])
    midpoint_line(bottom[0],bottom[1],left[0],left[1])
    midpoint_line(left[0],left[1],top[0],top[1])
    glEnd()

def draw_catcher(cx,cy,width,height,color): #niche width komano bowl dekhate
    r,g,b=color
    glColor3f(r,g,b)
    half_top=width//2
    half_bottom=int(width*0.6)//2 
    top_y=cy+height
    bottom_y=cy
    left_top=(cx-half_top,top_y)
    right_top=(cx+half_top,top_y)
    right_bottom=(cx+half_bottom,bottom_y)
    left_bottom=(cx-half_bottom,bottom_y)
    glBegin(GL_POINTS)
    midpoint_line(left_top[0],left_top[1],right_top[0],right_top[1]) #top edge
    midpoint_line(right_top[0],right_top[1],right_bottom[0],right_bottom[1]) #right side
    midpoint_line(right_bottom[0],right_bottom[1],left_bottom[0],left_bottom[1])  #bottom edge
    midpoint_line(left_bottom[0],left_bottom[1],left_top[0],left_top[1])  #left side
    glEnd()

def draw_buttons():
    draw_button_box(left_button_x,button_top, button_width,button_height,TEAL) #restart
    draw_l_arrow_icon(left_button_x+button_width//2,button_top+button_height//2) 
    draw_button_box(middle_button_x,button_top,button_width,button_height,AMBER) #play/pause
    play_pause(middle_button_x+button_width//2,button_top+button_height//2)
    draw_button_box(right_button_x,button_top,button_width,button_height,RED) #cross
    forcross(right_button_x+button_width//2,button_top+button_height//2)

def draw_button_box(x,y,w,h,color):
    r,g,b=color
    glColor3f(r,g,b)
    left=x
    right=x+w
    top=y+h
    bottom=y
    glBegin(GL_POINTS)
    midpoint_line(left,bottom,right,bottom)
    midpoint_line(right,bottom,right,top)
    midpoint_line(right,top,left,top)
    midpoint_line(left,top,left,bottom)
    glEnd()

def draw_l_arrow_icon(cx,cy):
    glColor3f(*WHITE)
    size=12
    p1=(cx-size,cy)
    p2=(cx+size//2,cy+size)
    p3=(cx+size//2,cy-size)
    glBegin(GL_POINTS)
    midpoint_line(p1[0],p1[1],p2[0],p2[1])
    midpoint_line(p2[0],p2[1],p3[0],p3[1])
    midpoint_line(p3[0],p3[1],p1[0],p1[1])
    glEnd()

def play_pause (cx,cy):
    glColor3f(*WHITE)
    size=12
    if playing and not game_over:
        left_bar_x=cx-6
        right_bar_x=cx+2
        top=cy+size
        bottom=cy-size
        glBegin(GL_POINTS)
        midpoint_line(left_bar_x,bottom,left_bar_x,top)
        midpoint_line(right_bar_x,bottom,right_bar_x,top)
        glEnd()
    else:
        p1=(cx-6,cy-size)
        p2=(cx-6,cy+size)
        p3=(cx+10,cy)
        glBegin(GL_POINTS)
        midpoint_line(p1[0],p1[1],p2[0],p2[1])
        midpoint_line(p2[0],p2[1],p3[0],p3[1])
        midpoint_line(p3[0],p3[1],p1[0],p1[1])
        glEnd()

def forcross (cx,cy):
    glColor3f(*WHITE)
    size=10
    glBegin(GL_POINTS)
    midpoint_line(cx-size,cy-size,cx+size,cy+size)
    midpoint_line(cx-size,cy+size,cx+size,cy-size)
    glEnd()

def inside_bounds(mx,my,x,y,w,h):
    return (mx>=x and mx<=x+w and my>=y and my<=y+h)
def aabb_collision(ax,ay,aw,ah,bx,by,bw,bh):
    return (ax<bx+bw and ax+aw>bx and ay<by+bh and ay+ah>by)
def fordiamond ():
    global diamond_x, diamond_y, diamond_color
    margin=diamond_size+4 #edge limit
    diamond_x=random.randint(margin,WINDOW_WIDTH-margin)
    diamond_y=WINDOW_HEIGHT-(diamond_size+10) 
    def bright_component():
        return random.uniform(0.4,1.0)
    diamond_color=(bright_component(),bright_component(),bright_component())

left_pressed = False
right_pressed = False
def keyboard(key, x, y): 
    global cheat_mode
    if key==b'\x1b':  #ESC
        print(f"Goodbye {score}")
        glutLeaveMainLoop()
    elif key==b'c' or key==b'C': #cheat key
        cheat_mode=not cheat_mode
        print("Cheat mode:","ON" if cheat_mode else "OFF")

def special_input(key,x,y):
    global left_pressed,right_pressed
    if key==GLUT_KEY_LEFT:
        left_pressed=True
    elif key==GLUT_KEY_RIGHT:
        right_pressed=True

def special_up(key,x,y):
    global left_pressed,right_pressed
    if key==GLUT_KEY_LEFT:
        left_pressed=False
    elif key==GLUT_KEY_RIGHT:
        right_pressed=False

def mouse_click(button,state,x,y):
    if state!=GLUT_DOWN:
        return
    mx,my=x,WINDOW_HEIGHT-y
    if inside_bounds(mx,my,left_button_x,button_top,button_width,button_height):
        restart_pressed()
    elif inside_bounds(mx,my,middle_button_x,button_top,button_width,button_height):
        play_pause_pressed()
    elif inside_bounds(mx,my,right_button_x,button_top,button_width,button_height):
        quit_pressed()

def restart_pressed():
    global score,diamond_speed,catcher_color,game_over,playing
    score=0
    diamond_speed=120.0
    catcher_color=WHITE
    game_over=False
    playing=True
    fordiamond()
    print("Starting Over")

def play_pause_pressed():
    global playing
    if game_over:
        return
    playing=not playing
    if not playing:
        print("Paused")
    else : 
        print("Resumed")

def quit_pressed():
    print(f"Goodbye {score}")
    glutLeaveMainLoop()
def update(dt):
    global diamond_y,diamond_speed,score,game_over,catcher_x, catcher_color
    if not playing or game_over:
        return
    diamond_y-=diamond_speed*dt  #diamond er control
    if cheat_mode:
        target_x=diamond_x
        if abs(target_x-catcher_x)>2:
            if target_x>catcher_x:
                dir_sign=1 
            else :
                dir_sign=-1
            move_amount=catcher_speed*dt
            catcher_x+=dir_sign*min(move_amount,abs(target_x-catcher_x))
    else:
        if left_pressed:
            catcher_x-=catcher_speed*dt
        if right_pressed:
            catcher_x+=catcher_speed*dt
    half = catcher_width//2 #catcher boundary te thaka
    if catcher_x-half<0: #min beyond right edge
        catcher_x=half
    if catcher_x+half>WINDOW_WIDTH:  #max beyond left endge
        catcher_x=WINDOW_WIDTH-half

    d_w=diamond_size*2  # width
    d_h=diamond_size*2  # height
    d_x=diamond_x-diamond_size
    d_y=diamond_y-diamond_size
    c_w=catcher_width
    c_h=catcher_height
    c_x=catcher_x-c_w//2
    c_y=catcher_y

    if aabb_collision(d_x,d_y,d_w,d_h,c_x,c_y,c_w,c_h): #diamond & catcher collison avoid 
        score+=1
        print("Score:",score)
        diamond_speed+=diamond_accel
        fordiamond()
    if diamond_y+(-diamond_size)<=0: #diamond missed 
        game_over=True
        catcher_color=RED
        print("Game Over",score)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_buttons()
    if not game_over:
        draw_diamond(diamond_x,diamond_y,diamond_size,diamond_color)
    draw_catcher(catcher_x,catcher_y,catcher_width,catcher_height,catcher_color)
    glutSwapBuffers()
def idle():
    global last_time
    now=current_time()
    if last_time is None:
        last_time=now
    dt=now-last_time #koto time gese ager frame theke,sob update kore 
    if dt>0.25:
        dt=0.25
    last_time=now
    update(dt)
    glutPostRedisplay()
    time.sleep(max(0.0,(1.0/FPS_TARGET)-(current_time()-now)))
def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,WINDOW_WIDTH,0,WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
def main():
    global last_time
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    window = glutCreateWindow(b"Catch the Diamonds!")
    init_opengl()
    fordiamond()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_input)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse_click)
    last_time=current_time()
    glutMainLoop()
if __name__ == "__main__":
    main()
