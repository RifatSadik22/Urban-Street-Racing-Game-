from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random
W,H=1000,800
GRID_LENGTH=600
TILE=60
fovY=110
camera_pos=(0,500,500)
cam_angle=45
cam_radius=650
cam_height=420
first_person=False
camera_height_fp=60
px,py=0.0,0.0
angle=0.0
life=5
player_down=False
score=0
missed=0
game_over=False
cheat_mode=False
auto_follow=False  #only visible in first-person
bullets=[]
enemies=[]
enemy_scale=1.0
scale_dir=1
ENEMY_SPEED=0.6
BULLET_SPEED=18
CHEAT_ROT_SPEED=3
CHEAT_FIRE_COOLDOWN=8
cheat_fire_timer=0
PLAYER_MARGIN=40 #player size-ish
ENEMY_MARGIN=35  #enemy size-ish
for r in range(5): #5 ta enemy spawn
    enemies.append([
        random.randint(-GRID_LENGTH + ENEMY_MARGIN, GRID_LENGTH - ENEMY_MARGIN),
        random.randint(-GRID_LENGTH + ENEMY_MARGIN, GRID_LENGTH - ENEMY_MARGIN)])
def draw_text(x, y,text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,W,0,H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x,y)
    for cha in text:
        glutBitmapCharacter(font,ord(cha))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def draw_shapes():
    global enemy_scale,first_person,player_down
    if not first_person: #3rd pov
        glPushMatrix()
        glTranslatef(px,py,0)
        glRotatef(angle,0,0,1)
        if player_down:
            glRotatef(90,1,0,0)
        LEG_H=45
        LEG_Y=17
        LEG_THIN_GROUND_R=4   
        LEG_THICK_BODY_R=8    
        TORSO_Z=LEG_H+15
        TORSO_SX,TORSO_SY,TORSO_SZ=0.45,0.9,1.3
        ARM_Z=TORSO_Z+10
        ARM_SIDE_Y=20       
        ARM_X_OFFSET=12       
        ARM_LEN=18
        ARM_SHOULDER_R=6
        ARM_HAND_R=3
        GUN_Z=ARM_Z-2
        GUN_X=22            
        GUN_LEN=32            
        GUN_BASE_R=6
        GUN_TIP_R=1
        glColor3f(0,0,1)
        glPushMatrix() #left paa
        glTranslatef(0, LEG_Y, 0)
        gluCylinder(gluNewQuadric(),LEG_THIN_GROUND_R,LEG_THICK_BODY_R,LEG_H,14,14)
        glPopMatrix()
        glPushMatrix() #right paa
        glTranslatef(0,-LEG_Y,0)
        gluCylinder(gluNewQuadric(),LEG_THIN_GROUND_R,LEG_THICK_BODY_R,LEG_H,14,14)
        glPopMatrix()
        glPushMatrix() #body
        glTranslatef(0,0,TORSO_Z)
        glColor3f(0.30,0.45,0.10)
        glScalef(TORSO_SX,TORSO_SY,TORSO_SZ)
        glutSolidCube(40)
        glPopMatrix()
        glColor3f(0.9,0.8,0.7) #haat
        glPushMatrix() #left haat
        glTranslatef(ARM_X_OFFSET,ARM_SIDE_Y,ARM_Z)
        glRotatef(-90,0,1,0)
        gluCylinder(gluNewQuadric(),ARM_HAND_R,ARM_SHOULDER_R,ARM_LEN,14,14)
        glPopMatrix()
        glPushMatrix() #dan haat
        glTranslatef(ARM_X_OFFSET,-ARM_SIDE_Y,ARM_Z)
        glRotatef(-90,0,1,0)
        gluCylinder(gluNewQuadric(),ARM_HAND_R,ARM_SHOULDER_R,ARM_LEN,14,14)
        glPopMatrix()
        glPushMatrix() #gun
        glTranslatef(GUN_X,0,GUN_Z) #center e ante
        glRotatef(-90,0,1,0)       
        glColor3f(0.6,0.6,0.6)
        gluCylinder(gluNewQuadric(),GUN_TIP_R,GUN_BASE_R,GUN_LEN,16,16)
        glPopMatrix()
        glPushMatrix() #head
        glTranslatef(0,0,TORSO_Z+40)
        glColor3f(0,0,0)
        gluSphere(gluNewQuadric(),16,20,20)
        glPopMatrix()
        glPopMatrix()
    else: #1st person
        FP_BACK=60
        FP_UP=90
        eye_x=px-FP_BACK*math.cos(math.radians(angle))
        eye_y=py-FP_BACK*math.sin(math.radians(angle))
        eye_z=FP_UP
        fwd_x=math.cos(math.radians(angle))
        fwd_y=math.sin(math.radians(angle))
        right_x=math.cos(math.radians(angle-90))
        right_y=math.sin(math.radians(angle-90))
        gun_x=eye_x+right_x*25+fwd_x*35
        gun_y=eye_y+right_y*25+fwd_y*35
        gun_z=eye_z-20
        glPushMatrix()
        glTranslatef(gun_x,gun_y,gun_z)
        glRotatef(angle,0,0,1)

        glPushMatrix()
        glColor3f(0.9,0.8,0.7)
        glScalef(0.8,0.35,0.35)
        glutSolidCube(30)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(25,0,0)
        glColor3f(0.6,0.6,0.6)
        glScalef(1.6,0.25,0.25)
        glutSolidCube(30)
        glPopMatrix()
        glPopMatrix()
    for b in bullets: #bullets
        glPushMatrix()
        glTranslatef(b[0],b[1],20)
        glColor3f(1, 1, 0)
        glutSolidCube(10)
        glPopMatrix()
    for r in enemies: #enemies
        glPushMatrix()
        glTranslatef(r[0],r[1],30)
        glScalef(enemy_scale,enemy_scale,enemy_scale)
        glColor3f(1,0,0)
        gluSphere(gluNewQuadric(),22,20,20)
        glTranslatef(0,0,26)
        glColor3f(0,0,0)
        gluSphere(gluNewQuadric(),13,20,20)
        glPopMatrix()
def keyboardListener(key, x, y):
    global px,py,angle,cheat_mode,auto_follow
    global life,score,missed,game_over,player_down
    global cheat_fire_timer
    if game_over and (key==b'r' or key==b'R'): #restart hobe
        px,py,angle=0.0,0.0,0.0
        life,score,missed=5,0,0
        game_over=False
        player_down=False
        bullets.clear()
        enemies.clear()
        for i in range(5):
            enemies.append([
                random.randint(-GRID_LENGTH + ENEMY_MARGIN, GRID_LENGTH - ENEMY_MARGIN),
                random.randint(-GRID_LENGTH + ENEMY_MARGIN, GRID_LENGTH - ENEMY_MARGIN)])
        cheat_fire_timer=0
        return
    if game_over:
        return
    if key==b'w' or key==b'W': #player movement
        px+=12*math.cos(math.radians(angle))
        py+=12*math.sin(math.radians(angle))
    if key==b's' or key==b'S':
        px-=12*math.cos(math.radians(angle))
        py-=12*math.sin(math.radians(angle))
    px = max(-GRID_LENGTH + PLAYER_MARGIN, min(px, GRID_LENGTH - PLAYER_MARGIN)) #player boundary te thakbe 
    py = max(-GRID_LENGTH + PLAYER_MARGIN, min(py, GRID_LENGTH - PLAYER_MARGIN))
    if key==b'a' or key==b'A': #rotate korte
        angle+=5
    if key==b'd' or key==b'D':
        angle-=5
    if key==b'c' or key==b'C': #cheat
        cheat_mode=not cheat_mode
        if not cheat_mode:
            auto_follow=False
    if key==b'v' or key==b'V': #auto toggle
        if cheat_mode:
            auto_follow=not auto_follow
def specialKeyListener(key,x,y):
    global cam_angle, cam_height
    if key==GLUT_KEY_LEFT:
        cam_angle+=5
    elif key==GLUT_KEY_RIGHT:
        cam_angle-=5
    elif key==GLUT_KEY_UP:
        cam_height+=20
    elif key==GLUT_KEY_DOWN:
        cam_height-=20
    cam_height=max(120,min(cam_height,1400))
def mouseListener(button,state,x,y):
    global first_person
    if button==GLUT_LEFT_BUTTON and state==GLUT_DOWN and not game_over:
        bullets.append([px, py, angle])
    if button==GLUT_RIGHT_BUTTON and state==GLUT_DOWN:
        first_person=not first_person
def setupCamera():
    global camera_pos
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY,W/H,0.1,3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person:
        FP_BACK=100 #increase to see more body
        FP_UP=150 
        eye_x=px-FP_BACK*math.cos(math.radians(angle))
        eye_y=py-FP_BACK*math.sin(math.radians(angle))
        eye_z=FP_UP
        look_x=px+120*math.cos(math.radians(angle))
        look_y=py+120*math.sin(math.radians(angle))
        look_z=FP_UP
        if cheat_mode and auto_follow and len(enemies)>0: #auto follow 
            nearest=None
            best=10**18
            for e in enemies:
                dx=e[0]-px
                dy=e[1]-py
                d2=dx*dx+dy*dy
                if d2<best:
                    best=d2
                    nearest=e
            if nearest is not None:
                look_x,look_y=nearest[0],nearest[1]
        gluLookAt(eye_x,eye_y,eye_z,look_x,look_y,look_z,0,0,1)
    else:
        cx=cam_radius*math.cos(math.radians(cam_angle))
        cy=cam_radius*math.sin(math.radians(cam_angle))
        camera_pos=(cx,cy,cam_height)
        x, y,z=camera_pos
        gluLookAt(x,y,z,0,0,0,0,0,1)
def idle():
    global enemy_scale,scale_dir,angle
    global missed, life,game_over,score,player_down
    global cheat_fire_timer
    while len(enemies)<5: #5 ta enemy er jonno 
        enemies.append([
            random.randint(-GRID_LENGTH + ENEMY_MARGIN, GRID_LENGTH - ENEMY_MARGIN),
            random.randint(-GRID_LENGTH + ENEMY_MARGIN, GRID_LENGTH - ENEMY_MARGIN)])
    while len(enemies)>5:
        enemies.pop()
    enemy_scale+= 0.01*scale_dir #pulsing
    if enemy_scale>1.2 or enemy_scale<0.8:
        scale_dir*=-1
    if cheat_mode and not game_over: #cheat mode
        angle=(angle+CHEAT_ROT_SPEED)%360
        if cheat_fire_timer > 0:
            cheat_fire_timer -= 1
        if cheat_fire_timer<=0 and len(enemies)>0 and len(bullets)<2: #rare miss
            nearest=None
            best=10**18
            for e in enemies:
                dx=e[0]-px
                dy=e[1]-py
                d2=dx*dx+dy*dy
                if d2<best:
                    best=d2
                    nearest=e
            if nearest is not None:
                dx=nearest[0]-px
                dy=nearest[1]-py
                aim_ang=math.degrees(math.atan2(dy,dx))
                bullets.append([px,py,aim_ang])
                cheat_fire_timer=CHEAT_FIRE_COOLDOWN
    if not game_over:
        if cheat_mode:
            speed=BULLET_SPEED*1.8  #speed barai for rare miss 
        else:
            speed=BULLET_SPEED*1.0
        for b in bullets[:]:
            b[0]+=speed*math.cos(math.radians(b[2]))
            b[1]+=speed*math.sin(math.radians(b[2]))
            if abs(b[0])>GRID_LENGTH or abs(b[1])>GRID_LENGTH:
                bullets.remove(b)
                missed+=1
                if missed>=10:
                    game_over=True
                    player_down=True
        for e in enemies: #enemeies move 
            dx=px-e[0]
            dy=py-e[1]
            d=math.sqrt(dx*dx + dy*dy)
            if d!=0:
                e[0]+=(dx/d)*ENEMY_SPEED
                e[1]+=(dy/d)*ENEMY_SPEED
            e[0]=max(-GRID_LENGTH+ENEMY_MARGIN,min(e[0],GRID_LENGTH-ENEMY_MARGIN)) #boundary 
            e[1]=max(-GRID_LENGTH+ENEMY_MARGIN,min(e[1],GRID_LENGTH-ENEMY_MARGIN))
            if d<40:
                life-=1
                e[0]=random.randint(-GRID_LENGTH+ENEMY_MARGIN,GRID_LENGTH-ENEMY_MARGIN)
                e[1]=random.randint(-GRID_LENGTH+ENEMY_MARGIN,GRID_LENGTH-ENEMY_MARGIN)
                if life<=0:
                    game_over=True
                    player_down=True
        if cheat_mode: #larger hit radius er jonno 
            hit_r=55  
        else :
            hit_r=30
        for b in bullets[:]:
            hit_any=False
            for e in enemies:
                if abs(b[0]-e[0])<hit_r and abs(b[1]-e[1])<hit_r:
                    score+=1
                    e[0]=random.randint(-GRID_LENGTH+ENEMY_MARGIN,GRID_LENGTH-ENEMY_MARGIN)
                    e[1]=random.randint(-GRID_LENGTH+ENEMY_MARGIN,GRID_LENGTH-ENEMY_MARGIN)
                    hit_any=True
                    break
            if hit_any and b in bullets:
                bullets.remove(b)
    glutPostRedisplay()
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glViewport(0,0,W,H)
    setupCamera()
    for x in range(-GRID_LENGTH, GRID_LENGTH, TILE): #floor
        for y in range(-GRID_LENGTH,GRID_LENGTH,TILE):
            if ((x+y)//TILE)%2==0:
                glColor3f(0.70,0.50,0.95)
            else:
                glColor3f(1,1,1)
            glBegin(GL_QUADS)
            glVertex3f(x,y,0)
            glVertex3f(x+TILE,y,0)
            glVertex3f(x+TILE,y+TILE,0)
            glVertex3f(x,y+TILE,0)
            glEnd()
    wall_h=140
    wall_t=25
    glPushMatrix()
    glTranslatef(-GRID_LENGTH-wall_t/2.0,0,wall_h/2.0)
    glColor3f(0.0,0.0,1.0)
    glScalef(wall_t,GRID_LENGTH*2,wall_h)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0,GRID_LENGTH+wall_t/2.0,wall_h/2.0)
    glColor3f(0.0,1.0,1.0)
    glScalef(GRID_LENGTH*2,wall_t,wall_h)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(GRID_LENGTH+wall_t/2.0,0,wall_h/2.0)
    glColor3f(0.0,1.0,0.0)
    glScalef(wall_t,GRID_LENGTH*2,wall_h)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0,-GRID_LENGTH-wall_t/2.0,wall_h/2.0)
    glColor3f(1.0,1.0,1.0)
    glScalef(GRID_LENGTH*2,wall_t,wall_h)
    glutSolidCube(1.0)
    glPopMatrix()
    draw_shapes()
    draw_text(10,770,f"Player Life Remaining:{life}")
    draw_text(10,740,f"Game Score:{score}")
    draw_text(10, 710,f"Player Bullet Missed:{missed}")
    if game_over:
        draw_text(420,400,"GAME OVER - Press R")
    glutSwapBuffers()
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(W,H)
    glutInitWindowPosition(0,0)
    glutCreateWindow(b"3D Bullet Frenzy")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()
if __name__=="__main__":
    main()
