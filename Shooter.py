#Dhruv's shooter game
import pygame
import random
from os import path

img_dir=path.join(path.dirname(__file__), 'img')
snd_dir=path.join(path.dirname(__file__), 'snd')

WIDTH=480
HEIGHT=600
FPS=60
POWERUP_TIME=5000

#colours
WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
YELLOW=(255,255,0)

#initializing shit
pygame.init()
pygame.mixer.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Shooter")
clock=pygame.time.Clock()

font_name=pygame.font.match_font('calibri')
def draw_text(surf,text,size,x,y):  #rendering score
    font=pygame.font.Font(font_name,size)
    text_surface=font.render(text,True,RED) #true is for AA
    text_rect=text_surface.get_rect()
    text_rect.midtop=(x,y)
    surf.blit(text_surface,text_rect)

def newmob():
        m=Mob()       #adds more enemies as they get deleted
        all_sprites.add(m)
        mobs.add(m)

def draw_shield_bar(surf,x,y,pct):
    if pct<0:
        pct=0
    BAR_LENGTH=100
    BAR_HEIGHT=10
    fill=(pct/100)*BAR_LENGTH
    outline_rect=pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect=pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

def draw_lives(surf,x,y,lives,img):
    for i in range(lives):
        img_rect=img.get_rect()
        img_rect.x=x+30*i
        img_rect.y=y
        surf.blit(img,img_rect)

class Player(pygame.sprite.Sprite): #PLAYER sprite
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.transform.scale(player_img,(50,38)) #scale payer image
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.radius=20
        #pygame.draw.circle(self.image, RED, self.rect.center,self.radius) #circle for collisions check
        self.rect.centerx=WIDTH/2
        self.rect.bottom=HEIGHT-10
        self.speedx=0
        self.shield=100
        self.shoot_delay=250
        self.last_shot=pygame.time.get_ticks()   #check when last shot
        self.lives=3
        self.hidden=False
        self.hide_timer=pygame.time.get_ticks()
        self.power=1
        self.power_time=pygame.time.get_ticks()

    def update(self):
        #timeout fo rpower up
        if self.power>=2 and pygame.time.get_ticks()-self.power_time>POWERUP_TIME:
            self.power=1
            self.power_time=pygame.time.get_ticks()
        #check unhide
        if self.hidden and pygame.time.get_ticks()-self.hide_timer>1500:
            self.hidden=False
            self.rect.centerx=(WIDTH/2)
            self.rect.bottom=HEIGHT-10
        self.speedx=0
        keystate=pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx= -8
        if keystate[pygame.K_RIGHT]:
            self.speedx= 8
        if keystate[pygame.K_SPACE]:    #as long as space is pressed
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right>WIDTH:
            self.rect.right=WIDTH
        if self.rect.left<0:
            self.rect.left=0

    def powerup(self):
        self.power+=1
        self.power_time=pygame.time.get_ticks()

    def shoot(self):
        now=pygame.time.get_ticks() #get time
        if now- self.last_shot>self.shoot_delay:    #now minus last shot>delay
            self.last_shot=now
            if self.power==1:
                bullet=Bullet(self.rect.centerx,self.rect.top) #bottom of bullet to top of PLAYER
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power>=2:
                bullet1=Bullet(self.rect.left,self.rect.centery) #bottom of bullet to top of PLAYER
                bullet2=Bullet(self.rect.right,self.rect.centery) #bottom of bullet to top of PLAYER
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        #hide player temporarily
        self.hidden=True #flag
        self.hide_timer=pygame.time.get_ticks()
        self.rect.center=(WIDTH/2,HEIGHT+200) #hiding player off screen

class Mob(pygame.sprite.Sprite):    #ENEMY sprite

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig=random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image=self.image_orig.copy()
        self.rect=self.image.get_rect()
        self.radius=int(self.rect.width*0.85/2)
        #pygame.draw.circle(self.image, RED,self.rect.center,self.radius)
        self.rect.x=random.randrange(WIDTH-self.rect.width) #randomize position
        self.rect.y=random.randrange(-150,-100)
        self.speedy=random.randrange(1,7)
        self.speedx=random.randrange(-3,3)
        self.rot=0      #rotation
        self.rot_speed=random.randrange(-8,8)
        self.last_update=pygame.time.get_ticks()
         #updates clcock ticks
    def rotate(self):   #rotation function cehck
        now=pygame.time.get_ticks()
        if now-self.last_update>50:
            self.last_update=now
            self.rot=(self.rot+self.rot_speed)%360 #rotation less than 360
            #new_image=pygame.transform.rotate(self.image_orig,self.rot)
            old_center=self.rect.center     #checking rect with rotation
            self.image=pygame.transform.rotate(self.image_orig,self.rot)
            self.rect=self.image.get_rect()
            self.rect.center=old_center

    def update(self):
        self.rotate()
        self.rect.x+=self.speedx
        self.rect.y+=self.speedy
        if self.rect.top>HEIGHT+10 or self.rect.left<-25 or self.rect.right>WIDTH+20:  #re-randomize position at respawn | add random diagonal movmt and cap at sides
            self.rect.x=random.randrange(WIDTH-self.rect.width)
            self.rect.y=random.randrange(-100,-40)
            self.speedy=random.randrange(1,8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=bullet_img                  #bullet image
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.rect.bottom=y
        self.rect.centerx=x
        self.speedy=-10

    def update(self):
        self.rect.y+=self.speedy
        #kill if it moves off screen
        if self.rect.bottom<0:
            self.kill()
class Pow(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type=random.choice(['shield','gun'])
        self.image=powerup_images[self.type]                #bullet image
        self.image.set_colorkey(BLACK)
        self.rect=self.image.get_rect()
        self.rect.center=center
        self.speedy=2

    def update(self):
        self.rect.y+=self.speedy
        #kill if it moves off screen
        if self.rect.top>HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size=size
        self.image=explosion_anim[self.size][0]
        self.rect=self.image.get_rect()
        self.rect.center=center
        self.frame=0
        self.last_update=pygame.time.get_ticks()
        self.frame_rate=24  #frames to show animation in
    def update(self):
        now=pygame.time.get_ticks()
        if now-self.last_update>self.frame_rate:
            self.last_update=now
            self.frame+=1
            if self.frame==len(explosion_anim[self.size]):
                self.kill()
            else:
                center=self.rect.center
                self.image=explosion_anim[self.size][self.frame]
                self.rect.center=center

def show_go_screen():
    screen.blit(background,background_rect)
    draw_text(screen,"Space Shooter",64,WIDTH/2,HEIGHT/4)
    draw_text(screen,"Arrow keys to move and space to fire.",22,WIDTH/2,HEIGHT/2)
    draw_text(screen,"Shield powerup grants energy, Lightning gives dual wield lasers",22,WIDTH/2,HEIGHT/2+100)
    draw_text(screen,"Press a key to begin, Made by Dhruv97",18,WIDTH/2,HEIGHT*3/4)
    pygame.display.flip()
    waiting=True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
            if event.type==pygame.KEYUP:
                waiting=False

#load graphics
background=pygame.image.load(path.join(img_dir, "back.png")).convert()
background_rect=background.get_rect()
player_img=pygame.image.load(path.join(img_dir, "player.png")).convert()
player_mini_img=pygame.transform.scale(player_img,(25,19))
player_mini_img.set_colorkey(BLACK)
#meteor_img=pygame.image.load(path.join(img_dir, "meteor.png")).convert()
bullet_img=pygame.image.load(path.join(img_dir, "bullet.png")).convert()
meteor_images=[]
meteor_list=['meteorBrown_big1.png','meteorBrown_med1.png','meteorBrown_med3.png','meteorBrown_small1.png','meteorBrown_small2.png','meteorBrown_tiny2.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir,img)).convert())
#Animation
explosion_anim={}
explosion_anim['lg']=[]
explosion_anim['sm']=[]
explosion_anim['player']=[]
for i in range(9):
    filename='explosion0{}.png'.format(i)   #loop for running through explosion files
    img=pygame.image.load(path.join(img_dir,filename)).convert()
    img.set_colorkey(BLACK)
    img_lg=pygame.transform.scale(img,(60,60))
    explosion_anim['lg'].append(img_lg)
    img_sm=pygame.transform.scale(img,(32,32))
    explosion_anim['sm'].append(img_sm)
    filename='blackSmoke0{}.png'.format(i)   #loop for running through explosion files
    img=pygame.image.load(path.join(img_dir,filename)).convert()
    img.set_colorkey(BLACK)
    img_player=pygame.transform.scale(img,(150,150))
    explosion_anim['player'].append(img_player)
powerup_images={}
powerup_images['shield']=pygame.image.load(path.join(img_dir,'shield_gold.png')).convert()
powerup_images['gun']=pygame.image.load(path.join(img_dir,'bolt_gold.png')).convert()

#loading game sounds
hit_sound=pygame.mixer.Sound(path.join(snd_dir, 'hit'))
shoot_sound=pygame.mixer.Sound(path.join(snd_dir, 'lasershoot'))
shield_sound=pygame.mixer.Sound(path.join(snd_dir, 'pow4.wav'))
power_sound=pygame.mixer.Sound(path.join(snd_dir, 'pow5.wav'))
explosion_sounds=[]
for snd in ['explosion','explosion2']:
    explosion_sounds.append(pygame.mixer.Sound(path.join(snd_dir,snd)))
    player_die_sound=pygame.mixer.Sound(path.join(snd_dir,'rumble1.ogg'))
pygame.mixer.music.load(path.join(snd_dir,'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)


pygame.mixer.music.play(loops=-1)   #BG music

#GAYme loop
game_over=True
running=True
while running:
    if game_over:
        show_go_screen()
        game_over=False
        all_sprites=pygame.sprite.Group()   #setting sprite groups
        mobs=pygame.sprite.Group()
        bullets=pygame.sprite.Group()
        powerups=pygame.sprite.Group()
        player=Player()             #spawning
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score=0 #score 0
    #loop running at speed
    clock.tick(FPS)
    #process input
    for event in pygame.event.get():
        #check window close
        if event.type==pygame.QUIT:
            running=False
        #changed coz auto shoot
        #elif event.type==pygame.KEYDOWN:
        #    if event.key ==pygame.K_SPACE:
        #        player.shoot()
    #update
    all_sprites.update()

    #check bullet hits mobs
    hits=pygame.sprite.groupcollide(mobs, bullets, True, True) #both enemy and bullet gets deleted
    for hit in hits:
        score+=50-hit.radius #score acc to radius
        random.choice(explosion_sounds).play()
        expl=Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        if random.random()>0.9:
            pow=Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    #check for mob-player collision
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:

        player_die_sound.play()
        player.shield-=hit.radius*2
        expl=Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield<=0:
            hit_sound.play()
            death=Explosion(player.rect.center,'player')
            all_sprites.add(death)
            player.hide()
            player.lives-=1
            player.shield=100
    #check powerups shield increases health between 10 and 30
    hits=pygame.sprite.spritecollide(player,powerups,True)
    for hit in hits:
        if hit.type=='shield':
            player.shield+=random.randrange(10,30)
            shield_sound.play()
            if player.shield>=100:
                player.shield=100
        if hit.type=='gun':
            player.powerup()
            power_sound.play()


    #if lives is 0 and animatio is over then end game

    if player.lives==0 and not death.alive():   #does it exist??
        game_over=True


    #render
    screen.fill(BLACK) #background
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen,str(score),21,WIDTH/2,10)  #rendering text
    draw_shield_bar(screen,5,5,player.shield)
    draw_lives(screen,WIDTH-100,5,player.lives,player_mini_img)
    #after drawing, flip
    pygame.display.flip()

pygame.quit()


#Made by @dhruv97
#Credits for art and sound as requested:.
#Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
#GFX Art by kenney.nl
