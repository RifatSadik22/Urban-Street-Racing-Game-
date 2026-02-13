"""3D Urban Street Racing"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
W, H = 1000, 800
fovY = 90
GRID_LENGTH = 600
rand_var = 423
# State
game_over = False
cheat_mode = False
is_night = True
# Event message system
event_messages = []  # List of (text, color, timer)
game_paused = False  # Track pause state
day_ratio = 0.0  # 0.0 = Night, 1.0 = Day (for smooth transition)
show_welcome_overlay = True

score_distance = 0.0
world_scroll = 0.0
last_time = 0
# Player
player_lane = 1
LANE_X = [-320, -160, 0, 160, 320]
current_player_x = 0.0
player_speed = 0.0
target_speed = 20.0
car_health = 100
boost_speed = 0.0
slow_speed = 0.0

# Camera
camera_mode = 0  # 0: Third, 1: First, 2: Cinematic
# camera_pos = (0, -200, 100)
camera_target = (0, 400, 0)
camera_fov = 90.0
camera_dist = 180.0
camera_fp_dist = 100.0

#Camera transition animation
camera_transition_active = False
camera_transition_start_time = 0.0
camera_transition_duration = 0.3
camera_transition_from_mode = 0
camera_transition_to_mode = 0
#Timers
boost_timer = 0.0
slow_timer = 0.0  # New: for temporary slow effect
invincible_timer = 0.0
camera_shake_timer = 0.0
camera_shake_intensity = 0.0

# Track if speed event messages have been shown
boost_message_shown = False
slow_message_shown = False
is_jumping = False #jumping tiles er jonno 
player_jump_timer = 0.0
player_jump_duration = 0.55
player_jump_peak = 75.0
player_jump_z = 0.0
jump_cooldown = 0.0
drift_active = False #drift mode
drift_offset_x = 0.0
drift_dir = 0
rear_view_active = False #rear view
#Entities Lists
obstacles = []
powerups = []
ai_cars = []
zones = []
scenery = []
stars = []
clouds = []
#Logic
def init_game():
    global game_over, score_distance, world_scroll, car_health, last_time
    global player_lane, current_player_x, player_speed, target_speed
    global boost_timer, invincible_timer, obstacles, powerups, ai_cars, zones, scenery
    global cheat_mode, stars, clouds, day_ratio, is_night, camera_shake_timer, camera_shake_intensity, event_messages
    global is_jumping, player_jump_timer, player_jump_z, jump_cooldown, drift_active, drift_offset_x, rear_view_active

    game_over = False
    cheat_mode = False
    is_night = True
    day_ratio = 0.0

    event_messages = []  #Clear event messages on restart
    
    score_distance = 0.0
    world_scroll = 0.0
    car_health = 100
    last_time = time.time()
    
    player_lane = 2  #middle lane e start
    current_player_x = LANE_X[player_lane]
    player_speed = 0.0
    target_speed = 20.0
    
    boost_timer = 0.0
    global slow_timer
    slow_timer = 0.0
    invincible_timer = 0.0
    camera_shake_timer = 0.0
    camera_shake_intensity = 0.0
    is_jumping = False #jumping 
    player_jump_timer = 0.0
    player_jump_z = 0.0
    jump_cooldown = 0.0

    drift_active = False #drift
    drift_offset_x = 0.0
    
    #Rear View Camera
    rear_view_active = False
    
    #clear Lists
    obstacles.clear()
    powerups.clear()
    ai_cars.clear()
    zones.clear()
    scenery.clear()
    stars.clear()
    clouds.clear()
    
    #Stars (Wider area)
    for _ in range(500):
        stars.append((
            random.randint(-6000, 6000), 
            random.randint(1000, 4500),   
            random.randint(500, 3000)     
        ))

    #Clouds (Wide coverage)
    for _ in range(25):
        clouds.append({
            "x": random.randint(-5000, 5000),
            "y": random.randint(3000, 4500),
            "z": random.randint(500, 1500),
            "size": random.randint(250, 500)
        })
    
    #Scenery
    for i in range(100):
        side = 1 if i % 2 == 0 else -1
        kind = random.choice(["BUILDING", "TREE"])
        #static random color prottek building er jonno 
        if kind == "BUILDING":
            color = (
                random.uniform(0.2, 1.0),
                random.uniform(0.2, 1.0),
                random.uniform(0.2, 1.0)
            )
        else:
            color = (
                random.uniform(0.1, 0.2),
                random.uniform(0.1, 0.2),
                random.uniform(0.3, 0.5)
            )
        scenery.append({
            "x": random.randint(600, 1800) * side,
            "y": random.randint(-500, 3000),
            "kind": kind,
            "h": random.randint(200, 600) if random.random() > 0.5 else random.randint(100, 250),
            "w": random.randint(100, 200) if random.random() > 0.5 else random.randint(60, 100),
            "c": color
        })
    
    for _ in range(6): 
        obstacles.append({"lane": random.randint(0, 4), "y": random.randint(1000, 3000), "type": random.choice(["BLOCK", "CONE"])})
    
    for _ in range(3): 
        powerups.append({"lane": random.randint(0, 4), "y": random.randint(1500, 4000), "type": random.choice(["BOOST", "HEAL"])})
        
    #AI Overtake
    for _ in range(4): 
        lane = random.randint(0, 4)
        is_overtaker = random.random() < 0.4  #40% chance
        if is_overtaker:
            ai_cars.append({
                "lane": lane,
                "lane_x": LANE_X[lane],
                "y": random.randint(-900, -400),  #Spawn behind
                "speed_offset": random.uniform(0.8, 1.2),
                "color": (random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0)),
                "role": "OVERTAKE",
                "overtake_speed": target_speed * random.uniform(1.10, 1.25)
            })
        else:
            ai_cars.append({
                "lane": lane,
                "lane_x": LANE_X[lane],
                "y": random.randint(800, 3000),
                "speed_offset": random.uniform(0.8, 1.2),
                "color": (random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0)),
                "role": "NORMAL"
            })

    #zones with Jump type
    for i in range(10): 
        if i % 3 == 0:
            zone_type = "JUMP"
        elif i % 2 == 0:
            zone_type = "BOOST"
        else:
            zone_type = "SLOW"
        zones.append({"y": i * 1500 + 800, "lane": random.randint(0, 4), "type": zone_type})

init_game()
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1,1,1)):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



#welcome/instructions overlay on top of the game
def draw_welcome_overlay():
    glColor3f(1, 0.8, 0.2)
    draw_text(220, 600, "3D URBAN STREET RACING GAME", GLUT_BITMAP_HELVETICA_18)
    glColor3f(1, 1, 1)
    draw_text(250, 540, "A 3D endless racing game with day/night cycle, powerups, and AI cars.")
    draw_text(250, 510, "Controls:")
    draw_text(270, 480, "A/D: Change Lane    W/S: Accelerate/Brake    V: Change Camera    N: Day/Night")
    draw_text(270, 450, "SPACE: Toggle Drift    B: Toggle Rear View    C: Toggle Cheat    R: Restart")
    draw_text(270, 420, "Avoid obstacles, collect powerups, jump over hazards, and survive!")
    draw_text(270, 390, "Press Enter to Start", GLUT_BITMAP_HELVETICA_18)

def check_collision(px, py, pw, ph, ex, ey, ew, eh):
    return (abs(px - ex) * 2 < (pw + ew)) and (abs(py - ey) * 2 < (ph + eh))

def draw_shapes():
    #massive colored quad behind everything to simulate sky color
    r = 0.05 + (0.48 * day_ratio)
    g = 0.05 + (0.76 * day_ratio)
    b = 0.15 + (0.83 * day_ratio)
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex3f(-10000, -10000, -100)
    glVertex3f(10000, -10000, -100)
    glVertex3f(10000, 10000, -100)
    glVertex3f(-10000, 10000, -100)
    glEnd()
    
    #change AI car lanes
    for a in ai_cars:
        if random.random() < 0.002:  # 0.2% chance per frame to start lane change
            possible_lanes = [l for l in range(len(LANE_X)) if l != a["lane"]]
            a["target_lane"] = random.choice(possible_lanes)
            a["target_x"] = LANE_X[a["target_lane"]]
        # If target_lane is set, move lane_x gradually
        if "target_lane" in a:
            lane_change_speed = 1.0  #units per frame, much slower
            if abs(a["lane_x"] - a["target_x"]) > lane_change_speed:
                if a["lane_x"] < a["target_x"]:
                    a["lane_x"] += lane_change_speed
                else:
                    a["lane_x"] -= lane_change_speed
            else:
                a["lane_x"] = a["target_x"]
                a["lane"] = a["target_lane"]
                del a["target_lane"]
                del a["target_x"]
    
    # --- SKY RENDERING ---
    # Sun and Moon Rotation based on day_ratio
    # day_ratio 0.0 (Night) -> Moon High, Sun Low
    # day_ratio 1.0 (Day)   -> Sun High, Moon Low

    #Clouds (Always visible, white/grey based on time)
    cloud_color = 0.2 + (0.8 * day_ratio) #ratre darker clouds
    glColor3f(cloud_color, cloud_color, cloud_color)
    for c in clouds:
        glPushMatrix()
        glTranslatef(c["x"], c["y"], c["z"])
        glScalef(2.0, 0.8, 1.0) # Flatten
        glutSolidSphere(c["size"], 10, 10)
        glPopMatrix()
    
    # Stars (Fade out as day_ratio increases)
    if day_ratio < 0.8:
        star_brightness = 1.0 - day_ratio
        glColor3f(star_brightness, star_brightness, star_brightness)
        glPointSize(2)
        glBegin(GL_POINTS)
        for sx, sy, sz in stars:
            glVertex3f(sx, sy, sz)
        glEnd()

    #Sun (Moves up/down based on day_ratio)
    glPushMatrix()
    sun_y = 3500
    sun_z = -1000 + (day_ratio * 2500) # Rises as day_ratio goes to 1
    glTranslatef(0, sun_y, sun_z)
    
    
    #Sun Core
    glColor3f(1.0, 1.0, 0.0)
    glutSolidSphere(280, 40, 40)
    glPopMatrix()

    #Moon (Moves down as day_ratio goes to 1)
    glPushMatrix()
    moon_y = 3500
    moon_z = 1500 - (day_ratio * 2500) # Sets when day comes
    glTranslatef(500, moon_y, moon_z)
    glColor3f(0.9, 0.9, 0.9)
    glutSolidSphere(200, 30, 30)
    glPopMatrix()
    # --- ENVIRONMENT ---
    #Ground (Darker at night)
    g_col = 0.1 + (0.4 * day_ratio)
    glColor3f(0.05, g_col, 0.05)
    
    glBegin(GL_QUADS)
    glVertex3f(-8000, -GRID_LENGTH, -10); glVertex3f(-500, -GRID_LENGTH, -10)
    glVertex3f(-500, 4500, -10); glVertex3f(-8000, 4500, -10)
    glVertex3f(500, -GRID_LENGTH, -10); glVertex3f(8000, -GRID_LENGTH, -10)
    glVertex3f(8000, 4500, -10); glVertex3f(500, 4500, -10)
    glEnd()
    #Road Borders (Sidelines) - Yellow
    glColor3f(1.0, 1.0, 0.2) # Yellow
    glBegin(GL_QUADS)
    #Left Curb
    glVertex3f(-520, -GRID_LENGTH, -4); glVertex3f(-500, -GRID_LENGTH, -4)
    glVertex3f(-500, 4500, -4); glVertex3f(-520, 4500, -4)
    #Right Curb
    glVertex3f(500, -GRID_LENGTH, -4); glVertex3f(520, -GRID_LENGTH, -4)
    glVertex3f(520, 4500, -4); glVertex3f(500, 4500, -4)
    glEnd()
    #Road Surface
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-500, -GRID_LENGTH, -5); glVertex3f(500, -GRID_LENGTH, -5)
    glVertex3f(500, 4500, -5); glVertex3f(-500, 4500, -5)
    glEnd()
    #Lane Lines
    offset = (world_scroll % 200)
    glColor3f(1, 1, 1)
    # Draw four lane lines for five lanes
    lane_line_x = [-240, -80, 80, 240]
    for i in range(-2, 22):
        y = i * 200 - offset
        if y > -500:
            for x in lane_line_x:
                glPushMatrix(); glTranslatef(x, y+500, 1); glScalef(10, 80, 0); glutSolidCube(1); glPopMatrix()
    #Zones
    for z in zones:
        if z["y"] > -500 and z["y"] < 3000:
            glPushMatrix()
            glTranslatef(LANE_X[z["lane"]], z["y"], 1)
            #JUMP zones purple
            if z["type"] == "JUMP":
                glColor3f(0.6, 0.2, 1.0)
            elif z["type"] == "BOOST":
                glColor3f(0, 1, 0)
            else:
                glColor3f(0.8, 0.2, 0)
            glScalef(140, 100, 2)
            glutSolidCube(1)
            glPopMatrix()

    #Scenery
    for s in scenery:
        if s["y"] > -800 and s["y"] < 3500:
            glPushMatrix()
            glTranslatef(s["x"], s["y"], 0)
            if s["kind"] == "BUILDING":
                # Use the static color assigned at creation, modulated by day/night
                r = s["c"][0] * (0.5 + 0.5 * day_ratio)
                g = s["c"][1] * (0.5 + 0.5 * day_ratio)
                b = s["c"][2] * (0.5 + 0.5 * day_ratio)
                glColor3f(r, g, b)
                glPushMatrix(); glTranslatef(0, 0, s["h"]/2); glScalef(s["w"], s["w"], s["h"]); glutSolidCube(1); glPopMatrix()
                # Windows light up at night
                win_c = 0.9 - (0.8 * day_ratio)
                glColor3f(win_c, win_c, 0.6 * win_c)
                glPointSize(3)
                glBegin(GL_POINTS)
                for wx in range(-1, 2):
                    for wz in range(1, 6):
                         glVertex3f(wx*(s["w"]*0.3), -(s["w"]*0.51), wz*(s["h"]*0.12))
                glEnd()
            else: #Tree
                glColor3f(0.4 * (0.5+0.5*day_ratio), 0.3 * (0.5+0.5*day_ratio), 0.1) 
                glPushMatrix(); glTranslatef(0,0,30); glScalef(1,1,3); gluCylinder(gluNewQuadric(), 10, 10, 20, 8, 1); glPopMatrix()
                
                g_tree = s["c"][1] * (0.5 + 0.5 * day_ratio)
                glColor3f(0, g_tree, 0)
                glPushMatrix(); glTranslatef(0,0,60); gluCylinder(gluNewQuadric(), s["w"], 0, s["h"], 8, 1); glPopMatrix()
            glPopMatrix()
    #Obstacles
    for o in obstacles:
        if o["y"] > -500 and o["y"] < 3000:
            glPushMatrix()
            glTranslatef(LANE_X[o["lane"]], o["y"], 20)
            if o["type"] == "BLOCK":
                glColor3f(0.6, 0.4, 0.2)
                glScalef(80, 80, 80); glutSolidCube(1)
            else:
                glColor3f(1, 0.5, 0)
                gluCylinder(gluNewQuadric(), 25, 0, 60, 10, 5) 
            glPopMatrix()
    #Powerups
    for p in powerups:
        if p["y"] > -500 and p["y"] < 3000:
            glPushMatrix()
            glTranslatef(LANE_X[p["lane"]], p["y"], 30)
            glRotatef((time.time() * 200) % 360, 0, 0, 1)
            if p["type"] == "BOOST":
                glColor3f(0, 1, 0); gluSphere(gluNewQuadric(), 20, 10, 10)
            else:
                glColor3f(1, 0, 0); gluSphere(gluNewQuadric(), 20, 10, 10)
            glPopMatrix()

    #AI Cars
    for a in ai_cars:
        if a["y"] > -500 and a["y"] < 3000:
            glPushMatrix()
            glTranslatef(a["lane_x"], a["y"], 0)
            #Main body
            glColor3f(*a["color"])
            glPushMatrix(); glTranslatef(0, 0, 20); glScalef(70, 110, 18); glutSolidCube(1); glPopMatrix()
            #Cabin (lighter/darker glass)
            glColor3f(0.15, 0.15, 0.18)
            glPushMatrix(); glTranslatef(0, 15, 35); glScalef(50, 60, 16); glutSolidCube(1); glPopMatrix()
            # Spoiler
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix(); glTranslatef(0, -55, 32); glScalef(60, 12, 4); glutSolidCube(1); glPopMatrix()
            #Wheels (black cylinders)
            glColor3f(0,0,0)
            wheels = [(-35, 35), (25, 35), (-35, -35), (25, -35)]
            for wx, wy in wheels:
                glPushMatrix()
                glTranslatef(wx, wy, 10); glRotatef(90, 0, 1, 0)
                gluCylinder(gluNewQuadric(), 12, 12, 10, 10, 1)
                glPopMatrix()
            #Headlights (white)
            glColor3f(1, 1, 0.8)
            glPushMatrix(); glTranslatef(-20, 55, 18); glScalef(8, 4, 6); glutSolidCube(1); glPopMatrix()
            glPushMatrix(); glTranslatef(20, 55, 18); glScalef(8, 4, 6); glutSolidCube(1); glPopMatrix()
            #Taillights (red)
            glColor3f(1, 0, 0)
            glPushMatrix(); glTranslatef(-20, -55, 18); glScalef(8, 4, 6); glutSolidCube(1); glPopMatrix()
            glPushMatrix(); glTranslatef(20, -55, 18); glScalef(8, 4, 6); glutSolidCube(1); glPopMatrix()
            
            #Visual marker for overtakers
            if a["role"] == "OVERTAKE":
                glColor3f(0, 1, 1)  # Cyan roof light
                glPushMatrix(); glTranslatef(0, 0, 45); glScalef(15, 15, 8); glutSolidCube(1); glPopMatrix()
            
            glPopMatrix()


    #improved car with tilt

    if camera_mode != 1:
        glPushMatrix()
        #Drift Mode (Apply drift offset)
        glTranslatef(current_player_x + drift_offset_x, 0, player_jump_z)
        # Crash effect: rotate car if health is 0
        if car_health <= 0 or game_over:
            # Rotate to look crashed (sideways and nose down)
            glRotatef(-70, 1, 0, 0)
            glRotatef(40, 0, 0, 1)
        else:
            # Calculate tilt angle based on lane change direction and speed
            tx = LANE_X[player_lane]
            lane_diff = tx - current_player_x
            # Clamp tilt to max 18 degrees, smooth with a factor
            tilt_angle = max(-18, min(18, lane_diff * 0.25))
            glRotatef(-tilt_angle, 0, 0, 1)  # Negative for natural car lean
            
            #Add extra tilt when drifting
            if drift_active:
                drift_tilt = 8 if drift_offset_x > 0 else -8
                glRotatef(drift_tilt, 0, 1, 0)

        # Flashing effects
        if cheat_mode and int(time.time()*5)%2==0: glColor3f(0, 1, 1)
        elif invincible_timer > 0 and int(time.time()*10)%2==0: glColor3f(1, 1, 0)
        else: glColor3f(0.1, 0.3, 0.9) # Sport Blue

        # Main Chassis
        glPushMatrix(); glTranslatef(0, 0, 20); glScalef(70, 130, 18); glutSolidCube(1); glPopMatrix()

        # Cabin (Black Glass)
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix(); glTranslatef(0, 10, 35); glScalef(60, 70, 18); glutSolidCube(1); glPopMatrix()

        # Spoiler (Black)
        glPushMatrix(); glTranslatef(0, -60, 35); glScalef(70, 15, 5); glutSolidCube(1); glPopMatrix()
        # Spoiler legs
        glPushMatrix(); glTranslatef(-20, -60, 25); glScalef(5, 10, 15); glutSolidCube(1); glPopMatrix()
        glPushMatrix(); glTranslatef(20, -60, 25); glScalef(5, 10, 15); glutSolidCube(1); glPopMatrix()

        # Headlights (Yellow)
        glColor3f(1, 1, 0.5)
        glPushMatrix(); glTranslatef(-25, 65, 20); glScalef(10, 5, 8); glutSolidCube(1); glPopMatrix()
        glPushMatrix(); glTranslatef(25, 65, 20); glScalef(10, 5, 8); glutSolidCube(1); glPopMatrix()

        # Taillights (Red)
        glColor3f(1, 0, 0)
        glPushMatrix(); glTranslatef(-25, -65, 20); glScalef(10, 5, 8); glutSolidCube(1); glPopMatrix()
        glPushMatrix(); glTranslatef(25, -65, 20); glScalef(10, 5, 8); glutSolidCube(1); glPopMatrix()

        # Wheels (Cylinders)
        glColor3f(0,0,0)
        wheels = [(-40, 40), (30, 40), (-40, -40), (30, -40)] # (x, y) positions of wheels. 
        for wx, wy in wheels:
            glPushMatrix()
            glTranslatef(wx, wy, 15); glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 15, 15, 12, 10, 1)
            glPopMatrix()

        glPopMatrix()


def keyboardListener(key, x, y):
    global player_lane, game_over, camera_mode, target_speed, player_speed, cheat_mode, is_night, show_welcome_overlay, game_paused
    global drift_active, rear_view_active

    # If overlay is showing, only respond to Enter
    if show_welcome_overlay:
        if key == b'\r' or key == b'\n':  # Enter key
            show_welcome_overlay = False
        return

    # Pause/unpause with P
    if key == b'p' or key == b'P':
        game_paused = not game_paused
        return

    # Quit with ESC
    if key == b'\x1b':
        from OpenGL.GLUT import glutLeaveMainLoop
        glutLeaveMainLoop()

    if key == b'r':
        init_game()
        return

    if not game_over:
        if key == b'a': player_lane = max(0, player_lane - 1)
        if key == b'd': player_lane = min(4, player_lane + 1)
        if key == b'w':
            global target_speed
            # Cap manual speed to 50.0 (250km/h)
            target_speed = min(target_speed + 5.0, 50.0)
            
        if key == b's':
            # Always allow reducing speed, even if player_speed > 50.0
            target_speed = max(target_speed - 5.0, 0.0)
        if key == b'c': cheat_mode = not cheat_mode
        if key == b'v':
            global camera_transition_active, camera_transition_start_time, camera_transition_from_mode, camera_transition_to_mode
            camera_transition_active = True
            camera_transition_start_time = time.time()
            camera_transition_from_mode = camera_mode
            camera_transition_to_mode = (camera_mode + 1) % 3
            camera_mode = camera_transition_to_mode
        if key == b'n': is_night = not is_night

        # SPACE key toggles drift (press to turn on, press again to turn off)
        if key == b' ':
            drift_active = not drift_active

        #'b' key toggles rear view (press to turn on, press again to turn off)
        if key == b'b':
            rear_view_active = not rear_view_active


def mouseListener(button, state, x, y):
    global camera_mode, camera_transition_active, camera_transition_start_time, camera_transition_from_mode, camera_transition_to_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_transition_active = True
        camera_transition_start_time = time.time()
        camera_transition_from_mode = camera_mode
        camera_transition_to_mode = (camera_mode + 1) % 3
        camera_mode = camera_transition_to_mode

def setupCamera():
    # As speed increases, zoom out (increase distance, decrease FOV), as speed decreases, zoom in (decrease distance, increase FOV)
    global camera_fov, camera_dist, camera_fp_dist
    min_fov = 70
    max_fov = 110
    min_dist = 180
    max_dist = 350
    min_fp_dist = 60
    max_fp_dist = 100
    # Normalize speed (0 to 60+)
    speed_norm = min(max(player_speed, 0), 60) / 60.0
    # Target FOV and camera distance
    target_fov = max_fov - (max_fov - min_fov) * speed_norm
    target_dist = min_dist + (max_dist - min_dist) * speed_norm
    target_fp_dist = min_fp_dist + (max_fp_dist - min_fp_dist) * (1 - speed_norm)

    # Smoothly interpolate camera_fov and camera_dist
    lerp_speed = 0.08  # Lower is slower, higher is snappier
    camera_fov += (target_fov - camera_fov) * lerp_speed
    camera_dist += (target_dist - camera_dist) * lerp_speed
    camera_fp_dist += (target_fp_dist - camera_fp_dist) * lerp_speed

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(camera_fov, 1.25, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    global camera_pos, camera_target, camera_shake_timer, camera_shake_intensity
    # Improved camera shake: smooth, decaying oscillation
    shake_x = 0
    shake_y = 0
    shake_z = 0
    if camera_shake_timer > 0:
        #using a sine wave for smooth shake, decaying over time
        t = time.time() * 20
        decay = camera_shake_timer / 0.5  # 0.5 is max shake duration
        amplitude = camera_shake_intensity * decay
        # Increased shake multipliers for more intense effect
        shake_x = math.sin(t) * amplitude * 2.0
        shake_y = math.cos(t * 0.7) * amplitude * 1.2
        shake_z = math.sin(t * 1.3) * amplitude * 0.8
        camera_shake_timer -= 0.03
        if camera_shake_timer < 0:
            camera_shake_timer = 0
            camera_shake_intensity = 0
    elif player_speed > 30:
        shake_x = math.sin(time.time() * 10) * 1.2
        shake_y = math.cos(time.time() * 7) * 0.7


    global camera_transition_active, camera_transition_start_time, camera_transition_duration, camera_transition_from_mode, camera_transition_to_mode
    def get_camera_pos_for_mode(mode):
        if mode == 0:
            return (current_player_x * 0.3 + shake_x, -camera_dist + shake_y, camera_dist + shake_z), (0, 600, 0)
        elif mode == 1:
            return (current_player_x + shake_x, 20 + shake_y, camera_fp_dist + shake_z), (current_player_x, 1000, camera_fp_dist)
        elif mode == 2:
            t = time.time()
            radius = 400 + 100 * math.sin(t * 0.5)
            angle = t * 0.4
            cam_x = current_player_x + math.cos(angle) * radius
            cam_y = math.sin(angle) * radius * 0.7
            cam_z = 120 + 60 * math.sin(angle * 0.7)
            return (cam_x, cam_y, cam_z), (current_player_x, 0, 0)
        return (0,0,0), (0,0,0)

    if camera_transition_active:
        t_now = time.time()
        t_elapsed = t_now - camera_transition_start_time
        t_ratio = min(t_elapsed / camera_transition_duration, 1.0)
        from_pos, from_target = get_camera_pos_for_mode(camera_transition_from_mode)
        to_pos, to_target = get_camera_pos_for_mode(camera_transition_to_mode)
        interp = lambda a, b: a + (b - a) * t_ratio
        cam_pos = tuple(interp(a, b) for a, b in zip(from_pos, to_pos))
        cam_target = tuple(interp(a, b) for a, b in zip(from_target, to_target))
        #rear view er jonno 
        if rear_view_active:
            cam_target = (current_player_x, -900, 0)
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  cam_target[0], cam_target[1], cam_target[2],
                  0, 0, 1)
        if t_ratio >= 1.0:
            camera_transition_active = False
    else:
        cam_pos, cam_target = get_camera_pos_for_mode(camera_mode)
        #rear view camera
        if rear_view_active:
            cam_target = (current_player_x, -900, 0)
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
                  cam_target[0], cam_target[1], cam_target[2],
                  0, 0, 1)


def idle():
    global last_time, current_player_x, player_speed, target_speed, world_scroll, score_distance, slow_timer, event_messages
    global car_health, game_over, boost_timer, invincible_timer, rand_var, cheat_mode, day_ratio, camera_shake_timer, camera_shake_intensity, show_welcome_overlay
    global is_jumping, player_jump_timer, player_jump_z, jump_cooldown, drift_active, drift_offset_x

    # Pause all updates if welcome overlay is showing
    if show_welcome_overlay:
        glutPostRedisplay()
        return

    curr_time = time.time()
    dt = curr_time - last_time
    last_time = curr_time
    if dt > 0.1: dt = 0.1

    # SMOOTH DAY/NIGHT TRANSITION Logic
    if is_night:
        if day_ratio > 0.0:
            day_ratio -= dt * 0.5 # Fade to Night
            if day_ratio < 0: day_ratio = 0.0
    else:
        if day_ratio < 1.0:
            day_ratio += dt * 0.5 # Fade to Day
            if day_ratio > 1.0: day_ratio = 1.0

    if game_paused or game_over:
        return
    if not game_over:
        #updating jump state
        if is_jumping:
            player_jump_timer -= dt
            progress = 1.0 - (player_jump_timer / player_jump_duration)
            player_jump_z = math.sin(progress * math.pi) * player_jump_peak
            if player_jump_timer <= 0:
                is_jumping = False
                player_jump_z = 0.0
        else:
            player_jump_z = 0.0
        
        if jump_cooldown > 0:
            jump_cooldown -= dt
        
        tx = LANE_X[player_lane]
        diff = tx - current_player_x
        
        #Applying drift behavior
        if drift_active:
            # Slower lane change during drift
            if abs(diff) > 1.0:
                current_player_x += diff * 6.0 * dt
            else:
                current_player_x = tx
            # Drift sideways
            drift_dir = 1 if diff > 0 else -1
            drift_offset_x += drift_dir * 80.0 * dt
            drift_offset_x = max(-55, min(55, drift_offset_x))
        else:
            # Normal lane change
            if abs(diff) > 1.0:
                current_player_x += diff * 10.0 * dt
            else:
                current_player_x = tx
            # Decay drift offset
            drift_offset_x *= 0.85


        # Only apply tile effects if active, otherwise keep user-set target_speed
        global boost_speed, slow_speed
        global boost_message_shown, slow_message_shown
        if boost_timer > 0:
            boost_timer -= dt
            temp_speed = boost_speed  # No cap for boost
        elif slow_timer > 0:
            slow_timer -= dt
            temp_speed = slow_speed  # Slow to the calculated speed
        else:
            temp_speed = target_speed
            boost_message_shown = False
            slow_message_shown = False

        if player_speed < temp_speed:
            player_speed += 15.0 * dt
        elif player_speed > temp_speed:
            player_speed -= 30.0 * dt
        if player_speed < 0:
            player_speed = 0



        if invincible_timer > 0:
            invincible_timer -= dt

        move = player_speed * 30 * dt
        world_scroll += move
        score_distance += move / 10.0
        rand_var = int(score_distance)

        for s in scenery:
            s["y"] -= move
            if s["y"] < -800:
                s["y"] = random.randint(2500, 3500)

        for o in obstacles:
            o["y"] -= move * 0.8
            if o["y"] < -500:
                o["y"] = random.randint(2000, 3000)
                o["lane"] = random.randint(0, 2)
            #Skip obstacle collision if jumping high
            if player_jump_z <= 35:
                if not cheat_mode and invincible_timer <= 0:
                    if check_collision(current_player_x, 0, 60, 100, LANE_X[o["lane"]], o["y"], 60, 60):
                        car_health -= 10
                        event_messages.append(("Clashed with obstacle!", (1,0.3,0.3), 2.0))
                        if car_health < 0:
                            car_health = 0
                        o["y"] = -1000
                        camera_shake_timer = 0.5
                        camera_shake_intensity = 10.0
                        if car_health <= 0:
                            game_over = True

        for p in powerups:
            p["y"] -= move
            if p["y"] < -500:
                p["y"] = random.randint(2000, 4000)
                p["lane"] = random.randint(0, 2)
            if check_collision(current_player_x, 0, 60, 100, LANE_X[p["lane"]], p["y"], 40, 40):
                if p["type"] == "BOOST":
                    invincible_timer = 10.0  # 10 seconds invincibility
                    event_messages.append(("Invincibility!", (0,1,0.5), 2.0))
                else:
                    car_health = min(100, car_health + 10)
                    event_messages.append(("HP Increased!", (0.2,1,0.2), 2.0))
                p["y"] = -1000

        #Updating AI cars with different movement for NORMAL vs OVERTAKE
        for a in ai_cars:
            if a["role"] == "NORMAL":
                a["y"] -= (player_speed - (20 * a["speed_offset"])) * dt * 20
                if a["y"] < -500:
                    lane = random.randint(0, 4)
                    a["y"] = random.randint(2000, 3500)
                    a["lane"] = lane
                    a["lane_x"] = LANE_X[lane]
            else:  # OVERTAKE
                a["y"] += (a["overtake_speed"] - player_speed) * 18.0 * dt
                if a["y"] > 2600:
                    lane = random.randint(0, 4)
                    a["y"] = random.randint(-900, -400)
                    a["lane"] = lane
                    a["lane_x"] = LANE_X[lane]
                    a["overtake_speed"] = target_speed * random.uniform(1.10, 1.25)
            
            if not cheat_mode and invincible_timer <= 0:
                if check_collision(current_player_x, 0, 60, 110, a["lane_x"], a["y"], 60, 110):
                    car_health -= 10
                    event_messages.append(("Clashed with car!", (1,0.5,0.2), 2.0))
                    if car_health < 0:
                        car_health = 0
                    a["y"] += 400
                    camera_shake_timer = 0.5
                    camera_shake_intensity = 10.0
                    if car_health <= 0:
                        game_over = True

        for z in zones:
            z["y"] -= move
            if z["y"] < -600:
                z["y"] += 15000
            if abs(z["y"]) < 50 and z["lane"] == player_lane:
                if z["type"] == "BOOST":
                    boost_timer = 2.0  #2 seconds boost
                    boost_speed = player_speed * 1.5  # 50% boost, no cap
                    if not boost_message_shown:
                        event_messages.append(("Speed Increased!", (0.2,0.8,1), 2.0))
                        boost_message_shown = True
                elif z["type"] == "SLOW":
                    slow_timer = 2.0  # 2 seconds slow
                    # Always use current player_speed for slow effect
                    if player_speed > 0:
                        slow_speed = max(player_speed * 0.5, 5.0)
                    else:
                        slow_speed = 5.0
                    if not slow_message_shown:
                        event_messages.append(("Speed Decreased!", (1,0.6,0.2), 2.0))
                        slow_message_shown = True
                #Trigger jump
                elif z["type"] == "JUMP":
                    if not is_jumping and jump_cooldown <= 0:
                        is_jumping = True
                        player_jump_timer = player_jump_duration
                        jump_cooldown = 0.8
                        event_messages.append(("JUMP!", (0.8,0.4,1), 1.2))
                        z["y"] = -1000

        # Updating event message timers
        for i in range(len(event_messages)-1, -1, -1):
            text, color, timer = event_messages[i]
            timer -= dt
            if timer <= 0:
                event_messages.pop(i)
            else:
                event_messages[i] = (text, color, timer)

    glutPostRedisplay()


def showScreen():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    glEnable(GL_DEPTH_TEST)
    draw_shapes()

    # HUD
    glDisable(GL_DEPTH_TEST)
    if game_paused:
        draw_text(420, 440, "PAUSED", color=(1,1,0.2))
    # Show event messages only if not game over
    if not game_over:
        for idx, (text, color, timer) in enumerate(event_messages):
            draw_text(420, 400-idx*30, text, color=color)
    if game_over:
        draw_text(400, 400, "GAME OVER", color=(1,0.2,0.2))
        draw_text(380, 370, f"Distance: {int(score_distance)} KM", color=(1,0.8,0.2))
        draw_text(380, 340, "Press R to Restart", color=(1,1,1))
    else:

        # --- Health and Speed Bars (Bottom Left) ---
        bar_x = 30
        speed_bar_y = 50
        health_bar_y = speed_bar_y + 45
        bar_height = 20
        bar_max_width = 200  # Max width for both bars
        speed_ratio = min(player_speed / 40.0, 1.0)  # Assume 40 is max speed
        speed_bar_width = int(bar_max_width * speed_ratio)
        health_ratio = max(min(car_health / 100.0, 1.0), 0.0)
        health_bar_width = int(bar_max_width * health_ratio)
        # Health color: green > 60, yellow > 30, red <= 30
        if car_health > 60:
            health_color = (0.2, 1, 0.2)
        elif car_health > 30:
            health_color = (1, 1, 0.2)
        else:
            health_color = (1, 0.2, 0.2)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        # Draw health bar
        glColor3f(*health_color)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, health_bar_y)
        glVertex2f(bar_x + health_bar_width, health_bar_y)
        glVertex2f(bar_x + health_bar_width, health_bar_y + bar_height)
        glVertex2f(bar_x, health_bar_y + bar_height)
        glEnd()
        # Draw health text above the bar
        draw_text(bar_x, health_bar_y + bar_height + 8, f"Car Health: {car_health} HP", color=health_color)
        # Draw speed bar
        glColor3f(0.2, 0.6, 1)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, speed_bar_y)
        glVertex2f(bar_x + speed_bar_width, speed_bar_y)
        glVertex2f(bar_x + speed_bar_width, speed_bar_y + bar_height)
        glVertex2f(bar_x, speed_bar_y + bar_height)
        glEnd()
        # Draw speed text above the bar
        speed_display = int(round(player_speed * 5))
        draw_text(bar_x, speed_bar_y + bar_height + 8, f"Speed: {speed_display} km/h", color=(0.2,0.6,1))
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Score color: gold (bottom right)
        draw_text(800, 70, f"Score: {int(score_distance)}", color=(1,0.8,0.2))


        # Camera mode color: cyan (bottom right)
        cam_str = ["Third", "First", "Cinematic"][camera_mode]
        draw_text(800, 40, f"Cam: {cam_str} (V)", color=(0.2,1,1))

        # Day/Night mode color (bottom right)
        if is_night:
            mode_color = (0.6, 0.7, 1)
        else:
            mode_color = (1, 1, 0.5)
        mode_str = "Night" if is_night else "Day"
        draw_text(800, 10, f"Mode: {mode_str} (N)", color=mode_color)

        # Distance (bottom right, above score)
        draw_text(800, 100, f"Distance: {int(score_distance/100)} KM", color=(1,0.8,0.2))

        # Cheat mode
        if cheat_mode:
            draw_text(420, 770, "CHEAT MODE ON", color=(0,1,1))
        # Invincible
        if invincible_timer > 0:
            draw_text(800, 740, "INVINCIBLE!", color=(0,1,0))
        # Braking
        if target_speed == 0:
            draw_text(800, 710, "BRAKING", color=(1,0,0))
        
        # [NEW FEATURE: Drift Mode]
        if drift_active:
            draw_text(420, 740, "DRIFTING!", color=(1,0.5,0))
        
        # [NEW FEATURE: Rear View Camera]
        if rear_view_active:
            draw_text(420, 710, "REAR VIEW", color=(0,1,1))

    # Overlay welcome/instructions if needed
    if show_welcome_overlay:
        draw_welcome_overlay()

    glutSwapBuffers()

def specialKeyListener(key, x, y):
    pass  



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Urban Street Racing Group11")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
