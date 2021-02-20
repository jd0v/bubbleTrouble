
import sys
import os
import pygame
import random
import math
import itertools

# Additional ball regeneration numbers at ball.range: [12 , 17 , 24 , 34 , 48 , 68 , 98 , 139 , 199 , 284]

resolution = (1280,720)
#resolution = (1920,1080)
fps = 60
player_number = 1

# Image load
logo = pygame.image.load(os.path.join('images','logo1.png'))
image_desktop = pygame.image.load(os.path.join("images", 'desktop1.png'))
image_desktop = pygame.transform.scale(image_desktop,resolution)
image_desktop.set_alpha(None)
image_game_background1 = pygame.image.load(os.path.join("images", 'game background1.png'))
#image_game_background1 = pygame.transform.scale(image_game_background1,resolution)

image_player1 = pygame.image.load(os.path.join("images", 'band3.png'))
image_player2 = pygame.image.load(os.path.join("images", "player2.png"))
image_bubble_stand = pygame.image.load(os.path.join("images", 'bubble3.png'))
image_arrow_stand = pygame.image.load(os.path.join("images", 'arrow2.png'))
image_ground_soil = pygame.image.load(os.path.join("images", 'ground soil.png'))
image_ground_ice = pygame.image.load(os.path.join("images", 'ground ice.png'))
# upgrades
image_upgr_add_arr = pygame.image.load(os.path.join("images", 'two arrows.png'))
image_upgr_shield = pygame.image.load(os.path.join("images", 'upgr shield.png'))
image_shield = pygame.image.load(os.path.join("images", 'shield.png'))
image_shield_dying = []
image_shield_dying.append( pygame.image.load(os.path.join("images", 'shield dying 1.png')) )
image_shield_dying.append( pygame.image.load(os.path.join("images", 'shield dying 2.png')) )
image_speed_2x = pygame.image.load(os.path.join("images", 'upgr speed 2x.png'))
image_speed_3x = pygame.image.load(os.path.join("images", 'upgr speed 3x.png'))
image_upgr_arr_rope = pygame.image.load(os.path.join("images", 'upgr arrow rope.png'))
image_arr_rope = pygame.image.load(os.path.join("images", 'arrow rope.png'))
# level buttons
image_level_buttons = []
for i in range(10):
    image_level_buttons.append( pygame.image.load(os.path.join("images", 'level button '+str(i+1)+'.png')) )
image_level_singleplayer = pygame.image.load(os.path.join("images", 'Singleplayer button.png'))
image_level_multiplayer = pygame.image.load(os.path.join("images", 'Multiplayer button.png'))
# end game buttons
image_end_game_levels = pygame.image.load(os.path.join("images", 'end game button levels.png'))
image_end_game_repeat = pygame.image.load(os.path.join("images", 'end game button repeat.png'))
image_end_game_won = pygame.image.load(os.path.join("images", 'end game won.png'))
image_end_game_lost = pygame.image.load(os.path.join("images", 'end game lost.png'))

# [size_x, size_y, pos_x, pos_y, max_speed, image, ice]
#stand_player = [30,50,resolution[0]//2-40, resolution[1] - 50, 4, image_player1, False]
stand_player = {'size_x':30 , 'size_y':50 , 'pos_x':resolution[0]//2-40 , 'pos_y':resolution[1] , 
                'max_speed':4 , 'image':image_player1, 'acceleration_x_ratio':0.01}

# [diameter, pos_x, pos_y, speed_x, boost, infimum_radius, gravity, image]
#stand_bubble = [128, 500, 228, -2, 0, 9, 0.2, image_bubble_stand]
stand_bubble = {'diameter':128 , 'pos_x':500 , 'pos_y':228 , 'speed_x':-1.5 , 'speed_y':0 , 'infimum_diameter':9 , 
                'gravity':0.2 , 'image':image_bubble_stand}

# stand_setting: background/ground[image,position,size]
ground_height = 30
stand_setting = {'background':[image_game_background1,(0,0),resolution] , 
                 'ground':[image_ground_soil,(0,resolution[1]-ground_height),(resolution[0],30)]}

class Player(pygame.sprite.Sprite):
    
    def __init__(self, attributes):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.size = (attributes['size_x'],attributes['size_y'])
        self.pos = [ attributes['pos_x'],resolution[1] - attributes['size_y'] - ground_height ]
        self.image = pygame.transform.scale(attributes['image'], self.size)
        self.rect = pygame.Rect(self.pos,self.size)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 0
        self.max_speed_init = attributes['max_speed']
        self.max_speed = self.max_speed_init
        self.acceleration = round(self.max_speed/(attributes['acceleration_x_ratio']*fps) , 2)

        self.arrows_tot = 0
        self.arrows_max = 1
        self.shield = False # upgrade
        self.arrow_rope = False # upgrade
        #self.name = 0
        
    def movement(self,direction):
        # sign of speed
        if self.speed >= 0:
            speed_sgn = 1
        else:
            speed_sgn = -1
        # acceleration
        if abs(self.speed) < self.max_speed:
            self.speed += self.acceleration*direction
        elif abs(self.speed) > self.max_speed:
            self.speed = speed_sgn * self.max_speed
        elif abs(self.speed) == self.max_speed and direction != speed_sgn:
            self.speed -= speed_sgn * self.acceleration
        if not direction: # or 
            if abs(self.speed) > self.acceleration:
                self.speed -= speed_sgn * self.acceleration
            else:
                self.speed = 0
        self.speed = round(self.speed,2)
        # movement
        self.pos[0] += self.speed
        if self.pos[0] < 0:
            self.pos[0] = 0
        elif self.pos[0] + self.size[0] > resolution[0]:
            self.pos[0] = resolution[0] - self.size[0]
        self.rect = pygame.Rect(self.pos, self.size)
                
    def controls(self,left='K_LEFT', right = 'K_RIGHT', shoot = 'K_UP'):
        self.left = left
        self.right = right
        self.shoot = shoot

class Arrow(pygame.sprite.Sprite):
    
    def __init__(self, player, image = image_arrow_stand):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.player = player
        self.speed = 15
        if player.arrow_rope:
            self.image = pygame.transform.scale(image_arr_rope , (16,720) )
        else:
            self.image = pygame.transform.scale(image , (16,120) )
        self.rect = self.image.get_rect()
        self.player_pos = ([player.pos[0]+player.size[0]/2 , player.pos[1]])
        self.pos = [self.player_pos[0]-self.rect[2]/2 , self.player_pos[1]]
        self.rect = self.image.get_rect(topleft = self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        global players
        self.rect.move_ip(0,-self.speed)
        #if self.rect[1] + self.rect[3] < 0:
        if self.rect[1] + 120 < 0:
            self.death()
    
    def death(self):
        if self in player1_arrows:
            player1.arrows_tot -= 1
        else:
            player2.arrows_tot -= 1
        self.kill()

class Bubble(pygame.sprite.Sprite):
    
    #def __init__(self,diameter=stand_bubble[0],pos_x=stand_bubble[1],pos_y=stand_bubble[2],speed_x=stand_bubble[3],
    #             speed_y=stand_bubble[4], infimum_diameter=stand_bubble[5], gravity=stand_bubble[6], image=stand_bubble[7]):
    def __init__(self,attributes,inheritance_attributes = stand_bubble):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.attributes = attributes # for death/regeneration
        self.inheritance_attributes = inheritance_attributes # for death/regeneration
        self.diameter = attributes['diameter']
        self.pos = [ round(attributes['pos_x']) , round(attributes['pos_y']) ]
        self.speed = [ attributes['speed_x'] , attributes['speed_y'] ]
        self.infimum_diameter = attributes['infimum_diameter']
        self.gravity = attributes['gravity']
        self.image = pygame.transform.scale(attributes['image'], (round(self.diameter),round(self.diameter)))
        self.rect = pygame.Rect(self.pos,[self.diameter,self.diameter])
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        self.speed[1] += self.gravity
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        if self.pos[0]  < 0 or self.pos[0] + self.diameter > resolution[0]:
            self.speed[0] *= -1
            self.pos[0] += self.speed[0]
        if self.pos[1] + self.diameter > resolution[1] - ground_height or self.pos[1] < 0:
            self.speed[1] *= -1
            self.pos[1] += self.speed[1]
        self.rect = pygame.Rect(self.pos, (self.rect[2], self.rect[3]))
        
    def death(self):
        if self.diameter > self.infimum_diameter:
            self.regeneration(self.pos,self.diameter,-5)
        upgrade_create([self.pos[0]+self.diameter/2,self.pos[1]+self.diameter/2])
        self.kill()
        
    def regeneration(self,pos,old_radius,speed_y=0):
        self.difficulty = 0.7
        if pos[1] > resolution[1]-70 - ground_height:
            speed_y = -6
        new_attributes = stand_bubble.copy()
        for key in self.inheritance_attributes.keys():
            new_attributes[key] = self.inheritance_attributes[key]
        new_attributes['diameter'] = old_radius*self.difficulty
        new_attributes['pos_x'] = pos[0]
        new_attributes['pos_y'] = pos[1]
        new_attributes['speed_y'] = speed_y
        
        Bubble(new_attributes , self.inheritance_attributes)
        
        new_attributes['speed_x'] = -1*new_attributes['speed_x']
        
        Bubble(new_attributes , self.inheritance_attributes)

class Button:
    
    def __init__(self, but_type, scale_ratio, pos_centre_x_top_y , image):
        self.type= but_type
        self.size = image.get_size()
        self.scale_ratio = scale_ratio
        self.size = [round(self.size[0]*self.scale_ratio) , round(self.size[1]*self.scale_ratio)]
        self.pos = [round(pos_centre_x_top_y[0]-self.size[0]/2) , pos_centre_x_top_y[1]]
        self.image = pygame.transform.scale(image , self.size)
        desktop.blit(self.image, self.pos)
        
    def click(self, click_pos):
        if self.type == 'circle':
            if (self.size[0]/2)**2 > (self.pos[0] + self.size[0]/2 - click_pos[0])**2 + (self.pos[1] + self.size[1]/2 - click_pos[1])**2:
                return True
        elif self.type == 'rect':
            if self.pos[0] < click_pos[0] < self.pos[0]+self.size[0]:
                if self.pos[1] < click_pos[1] < self.pos[1]+self.size[1]:
                    return True

class Page:
    
    def __init__(self):
        self
    
    def levels(self):
        
        global from_game_to_levels, which_level, player_number, lb_singleplayer, lb_multiplayer, lb_current_player
        from_game_to_levels = False
        
        #create_levels(min(len(levels) , len(image_level_buttons)))
        create_levels(11)
        pygame.display.flip()
        
        while True:
            ev = pygame.event.wait()
            # EXIT
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # LEVEL
            if ev.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                    # SWICH PLAYER NUMBER
                if lb_current_player.click(pos):
                    if lb_current_player == lb_singleplayer:
                        lb_current_player = lb_multiplayer
                        player_number = 2
                    else:
                        lb_current_player = lb_singleplayer
                        player_number = 1
                    desktop.blit(lb_current_player.image, lb_current_player.pos)
                    pygame.display.flip()
                    # PLAY A GAME
                for butt in button:
                    if butt.click(pos):
                        while not from_game_to_levels:
                            which_level = button.index(butt)+1
                            game_loop(levels[button.index(butt)+1]) 
            if ev.type == pygame.KEYDOWN:
                # EXIT
                if ev.dict["key"] == 27:
                    pygame.quit()
                    sys.exit()
            if from_game_to_levels:
                break

    def game(self, level_NR):
        game_loop(level_NR)

class Text:
    
    def __init__(self,size):
        self.color = (0,0,0)
        self.size = size
    
    def write(self,text, position):
        self.position = position
        #my_font = pygame.font.SysFont("Courier", self.size)
        my_font = pygame.font.SysFont("Courier", self.size)
        the_text = my_font.render(str(text), True, self.color)
        desktop.blit(the_text,self.position)

def upgrade_create(pos_centre):
    rand = random.random()
    # prob. coef.
    coef = [['return',94] , ['UpgradeAdditionalArrow(pos_centre)',2.5] , ['UpgradeShield(pos_centre)',1.5] , 
            ['UpgradeSpeed(pos_centre,1.3)',2] , ['UpgradeSpeed(pos_centre,1.6)',1] , 
            ['UpgradeArrowRope(pos_centre)',1.5]] # Choose any values
    unit = 0
    for i in coef:
        unit  += i[1]
    unit = 1/unit
    if rand < coef[0][1] * unit:
        return
    else:
        n = coef[0][1] * unit
        del coef[0]
        for i in coef:
            n += i[1] * unit
            if rand < n:
                exec(i[0])
                return
# upgrades have similarities (for example, update()), so it might be a good idea to give them inheritance
class UpgradeAdditionalArrow(pygame.sprite.Sprite):
    
    def __init__(self,pos_centre):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.size = [25,25]
        self.pos = [pos_centre[0]-self.size[0] , pos_centre[1]-self.size[1]]
        self.image = pygame.transform.scale(image_upgr_add_arr , self.size).convert()
        self.rect = pygame.Rect(self.pos , self.size)
        self.lifetime = 6 # seconds
        self.fall_speed = 2
        self.drawn_speed = self.size[1]/(fps * self.lifetime)
        self.alpha = 255

    def update(self):
        if self.pos[1]+self.size[1] + ground_height < resolution[1]:
            self.pos[1] += self.fall_speed
        elif self.pos[1] + ground_height > resolution[1] - self.size[1]:
            self.pos[1] = resolution[1] - self.size[1] - ground_height
        elif self.image.get_alpha() > 0:
            self.alpha -= 255 / (fps * self.lifetime)
            self.image.set_alpha(round(self.alpha))
        else:
            self.death()
        self.rect = pygame.Rect(self.pos , self.size)
        
    def death(self, player=0):
        if player != 0:
            player.arrows_max += 1
        self.kill()

class UpgradeArrowRope(pygame.sprite.Sprite):
    
    def __init__(self,pos_centre):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.size = [25,25]
        self.pos = [pos_centre[0]-self.size[0] , pos_centre[1]-self.size[1]]
        self.image = pygame.transform.scale(image_upgr_arr_rope , self.size).convert()
        self.rect = pygame.Rect(self.pos , self.size)
        self.lifetime = 6 # seconds
        self.fall_speed = 2
        self.drawn_speed = self.size[1]/(fps * self.lifetime)
        self.alpha = 255

    def update(self):
        if self.pos[1]+self.size[1] + ground_height < resolution[1]:
            self.pos[1] += self.fall_speed
        elif self.pos[1] + ground_height > resolution[1] - self.size[1]:
            self.pos[1] = resolution[1] - self.size[1] - ground_height
        elif self.image.get_alpha() > 0:
            self.alpha -= 255 / (fps * self.lifetime)
            self.image.set_alpha(round(self.alpha))
        else:
            self.death()
        self.rect = pygame.Rect(self.pos , self.size)
        
    def death(self, player=0):
        if player != 0:
            player.arrow_rope = True
        self.kill()

class UpgradeShield(pygame.sprite.Sprite):
    
    def __init__(self,pos_centre):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.size = [25,25]
        self.pos = [pos_centre[0]-self.size[0] , pos_centre[1]-self.size[1]]
        self.image = pygame.transform.scale(image_upgr_shield , self.size).convert()
        self.rect = pygame.Rect(self.pos , self.size)
        self.lifetime = 6 # seconds
        self.fall_speed = 2
        self.drawn_speed = self.size[1]/(fps * self.lifetime)
        self.alpha = 255
        
    def update(self):
        if self.pos[1]+self.size[1] + ground_height < resolution[1]:
            self.pos[1] += self.fall_speed
        elif self.pos[1] + ground_height > resolution[1] - self.size[1]:
            self.pos[1] = resolution[1] - self.size[1] - ground_height
        elif self.image.get_alpha() > 0:
            self.alpha -= 255 / (fps * self.lifetime)
            self.image.set_alpha(round(self.alpha))
        else:
            self.death()
        self.rect = pygame.Rect(self.pos , self.size)
        
    def death(self, player=0):
        if player != 0:
            if not player.shield:
                Shield(player)
        self.kill()

class Shield(pygame.sprite.Sprite):
    
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self, self.containers)
        #self.add(shields)
        self.player = player
        player.shield = True
        self.size = image_shield.get_size()
        self.scale_ratio = 0.25
        self.size = [round(self.size[0]*self.scale_ratio) , round(self.size[1]*self.scale_ratio)]
        self.pos_correction = player.size[0]/2-self.size[0]/2
        self.pos = [player.pos[0]+self.pos_correction , resolution[1]-self.size[1] - ground_height]
        self.rect = pygame.Rect(self.pos , self.size)
        self.image = pygame.transform.scale(image_shield , self.size)
        self.image_shield_dying = []
        self.image_shield_dying.append( pygame.transform.scale(image_shield_dying[0] , self.size) )
        self.image_shield_dying.append( pygame.transform.scale(image_shield_dying[1] , self.size) )
        self.image_shield_dying = itertools.cycle(self.image_shield_dying)
        self.mask = pygame.mask.from_surface(self.image)
        self.dying_time = 1500 # miliseconds
        self.dying_image_change_time = 100 # miliseconds
    
    def update(self):
        self.pos[0] = self.player.pos[0]+self.pos_correction
        self.rect = pygame.Rect(self.pos , self.size)
        # shield dying
        try:
            if pygame.time.get_ticks() - self.first_collision_time >= self.dying_time:
                self.player.shield = False
                self.kill()
            if pygame.time.get_ticks() - self.last_image_time > self.dying_image_change_time: 
                self.last_image_time = pygame.time.get_ticks()
                self.image = next(self.image_shield_dying)
        except:
            pass    

    def death(self):
        try:
            if pygame.time.get_ticks() - self.first_collision_time >= self.dying_time:
                self.player.shield = False
                self.kill()
        except:
            self.first_collision_time = pygame.time.get_ticks()
            self.last_image_time = pygame.time.get_ticks()
            self.image = next(self.image_shield_dying)

class UpgradeSpeed(pygame.sprite.Sprite):
    
    def __init__(self, pos_centre, boost):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.boost = boost
        self.size = [25,25]
        self.pos = [pos_centre[0]-self.size[0] , pos_centre[1]-self.size[1]]
        if self.boost == 1.3:
            self.image = pygame.transform.scale(image_speed_2x, self.size).convert()
        elif self.boost == 1.6:
            self.image = pygame.transform.scale(image_speed_3x, self.size).convert()
        self.rect = pygame.Rect(self.pos , self.size)
        self.lifetime = 6 # seconds
        self.fall_speed = 2
        self.drawn_speed = self.size[1]/(fps * self.lifetime)
        self.alpha = 255

    def update(self):
        if self.pos[1]+self.size[1] + ground_height < resolution[1]:
            self.pos[1] += self.fall_speed
        elif self.pos[1] + ground_height > resolution[1] - self.size[1]:
            self.pos[1] = resolution[1] - self.size[1] - ground_height
        elif self.image.get_alpha() > 0:
            self.alpha -= 255 / (fps * self.lifetime)
            self.image.set_alpha(round(self.alpha))
        else:
            self.death()
        self.rect = pygame.Rect(self.pos , self.size)
        
    def death(self, player=0):
        if player != 0:
            player.max_speed = player.max_speed_init * self.boost
        self.kill()

def make_setting(new_setting):
    
    current_setting = stand_setting.copy()
    for key in new_setting.keys():
        current_setting[key] = new_setting[key]
    setting = desktop.blit(current_setting['background'][0],current_setting['background'][1],current_setting['background'][2])
    setting.blit(current_setting['ground'][0],current_setting['ground'][1],current_setting['ground'][2])
    return setting
    

class CollisionDetection:
    
    def __init__(self):
        self.arrows_bubbles()
        self.bubbles_players()
        self.player_upgrades()
        self.bubbles_shields()
    
    @staticmethod
    def arrows_bubbles():
        for arr in arrows:
            for bubb in pygame.sprite.spritecollide(arr, bubbles,0): # RECT COLLISION
                if bubb:
                    if pygame.sprite.collide_mask(arr,bubb): # MASK COLLISION
                        bubb.death()
                        arr.death()
                        break
    
    @staticmethod
    def bubbles_players():
        for pl in players:
            if pl.shield:
                continue
            for bubb in pygame.sprite.spritecollide(pl,bubbles,0): # RECT COLLISION
                if bubb:
                    if pygame.sprite.collide_mask(pl,bubb): # MASK COLLISION
                        pl.kill()
                        pl.add(dead_player)
                        bubb.add(bubble_of_death) # SO THAT THE BUBBLES WOULD BE IN THE FIRST FRAME
                        return
    
    @staticmethod
    def player_upgrades():
        for pl in players:
            for upg in pygame.sprite.spritecollide(pl,upgrades,0):
                if upg:
                    #if pygame.sprite.collide_mask(pl,upg): # no necessity at the moment, because players' RECTs are good
                    upg.death(pl)
    
    @staticmethod
    def bubbles_shields():
        for bubb in bubbles:
            for sh in pygame.sprite.spritecollide(bubb,shields,0):
                if sh:
                    if pygame.sprite.collide_mask(bubb,sh):
                        sh.death()

def level_make(count, data, mirror=False):
    # creates different levels with two 'for' cycles
    
    def single_bubble_calculation():
        
        #nonlocal parameters, operations, changes, par
        intermediate = {}
        for j in data.keys():
            if data[j][1] == 0:
                intermediate[j] = data_copy[j]
            elif data[j][1] == '+':
                intermediate[j] = data_copy[j] + data[j][2]
            elif data[j][1] == '*':
                intermediate[j] = data_copy[j] * data[j][2]
            data_copy[j] = intermediate[j]
        level.append(intermediate)
    
    data_copy = {}
    for key in data.keys():
        data_copy[key] = data[key][0]
    level = [data_copy.copy()]
    
    if mirror:
        for i in range(math.ceil(count/2)-1):
            single_bubble_calculation()
        level1 = level[:]
        for i in level1:
            j = i.copy()
            try:
                j['pos_x'] = resolution[0] - i['pos_x']
            except:
                pass
            try:
                j['speed_x'] = -1 * i['speed_x']
            except:
                pass
            if j.get('pos_x',True) == i.get('pos_x',True) and j.get('speed_x',True) == i.get('speed_x',True): # bubble in the middle
                continue
            level.append(j)
    else:
        for i in range(count-1):
            single_bubble_calculation()
    return level

def make_level_bubbles(level_bubbles):
    
    for inheritance_family in level_bubbles:
        #try:
        #    inheritance = inheritance_family['inheritance']
        #except:
        #    inheritance = stand_bubble
        inheritance = inheritance_family.get('inheritance', stand_bubble)
        inheritance_complete = stand_bubble.copy()
        for key in inheritance.keys():
            inheritance_complete[key] = inheritance[key]
        for bubbles in inheritance_family['bubbles']:
            try: # mirror = True ?
                bubb = level_make(bubbles[0],bubbles[1],bubbles[2])
            except:
                try: # do we need level_make ?
                    bubb = level_make(bubbles[0],bubbles[1])
                except: # we have to make only one Bubble.
                    bubb = [bubbles]
   
            for single_bubb in bubb: # take each bubble data set
                complete_bubb = stand_bubble.copy() # make sure, that all necessary inputs are present
                for key in single_bubb.keys():
                    complete_bubb[key] = single_bubb[key]
                Bubble(complete_bubb , inheritance)

def make_level_setting(level_setting):
    
    if level_setting != stand_setting:
        level_setting_complete = stand_setting.copy()
        for key in level_setting.keys():
            level_setting_complete[key] = level_setting[key]
    else:
        level_setting_complete = stand_setting.copy()
    setting_image = pygame.transform.scale(level_setting_complete['background'][0] , 
                                           level_setting_complete['background'][2])
    ground_image = pygame.transform.scale(level_setting_complete['ground'][0] , level_setting_complete['ground'][2])
    setting_image.blit(ground_image , level_setting_complete['ground'][1])
    return setting_image

def make_level_players(level_players):
    
    #if level_players == stand_player:
    #   if player_number == 1:
    #        return Player(stand_player) , None
    #    else:
    #        return Player(stand_player) , Player(stand_player)
    
    try:
        pl1_att = level_players['player1']
        
        pl1_att_complete = stand_player.copy()
        for key in pl1_att.keys():
            pl1_att_complete[key] = pl1_att[key]
    except:
        pl1_att_complete = stand_player.copy()
    
    if player_number == 2:
        try:
            pl2_att = level_players['player2']
        except:
            try:
                pl2_att = level_players['player1']
            except:
                pl2_att_complete = stand_player.copy()
                pl2_att_complete['pos_x'] += 50
                pl2_att_complete['image'] = image_player2
                return Player(pl1_att_complete) , Player(pl2_att_complete)
        pl2_att_complete = stand_player.copy()
        for key in pl2_att.keys():
            pl2_att_complete[key] = pl2_att[key]
        pl2_att_complete['pos_x'] += 50
        pl2_att_complete['image'] = image_player2
    else:
        return Player(pl1_att_complete) , None
    return Player(pl1_att_complete) , Player(pl2_att_complete)
    
def create_levels(count):
    # draws page with levels !!!!!!!
    
    global button, lb_current_player, lb_singleplayer, lb_multiplayer
    button = []
    
    desktop.blit(image_desktop,(0,0))
    
    # level_button_array
    lba_distance = 30
    diameter = 150
    lb_size = [diameter,diameter]

    for i in range(count):
        button.append(Button( 'circle' , 0.15 , (resolution[0]/2 + (i%5-2)*(lba_distance+diameter) , 200 + (lba_distance+lb_size[1])*(i//5)) 
                   #, image_level_buttons[i] ))
                   , image_level_buttons[i%10] )) # laikinas. eilute auksciau yra GERAS !!!!
    
    if player_number == 1:
        lb_multiplayer = Button('rect' , 0.15 , (resolution[0]//2 , 20) , image_level_multiplayer)
        lb_singleplayer = Button('rect' , 0.15 , (resolution[0]//2 , 20) , image_level_singleplayer)
        lb_current_player = lb_singleplayer
    elif player_number == 2:
        lb_singleplayer = Button('rect' , 0.15 , (resolution[0]//2 , 20) , image_level_singleplayer)
        lb_multiplayer = Button('rect' , 0.15 , (resolution[0]//2 , 20) , image_level_multiplayer)
        lb_current_player = lb_multiplayer
        
def game_loop(level):
    
    global from_game_to_levels, player_number, player1_arrows, player1, player2
    global players, arrows, bubbles, dead_player, bubble_of_death, upgrades, shields
        
    players = pygame.sprite.Group()
    bubbles = pygame.sprite.Group()
    arrows = pygame.sprite.Group()
    player1_arrows = pygame.sprite.Group()
    player2_arrows = pygame.sprite.Group()
    upgrades = pygame.sprite.Group()
    evryth = pygame.sprite.RenderUpdates()
    shields = pygame.sprite.Group()
    # for draw
    dead_player = pygame.sprite.Group()
    bubble_of_death = pygame.sprite.Group()
        
    Player.containers = evryth, players
    Bubble.containers = evryth, bubbles
    Arrow.containers = evryth, arrows
    [UpgradeAdditionalArrow.containers , UpgradeShield.containers , UpgradeSpeed.containers , 
     UpgradeArrowRope.containers] = 4*[[evryth, upgrades]]
    Shield.containers = evryth, shields
    
    # modern generation of sprites and setting
    make_level_bubbles(level['level_bubbles'])
    
    # generation of objects
    #player1 = Player(stand_player)
    #player1.name = 'player1'
    player1 , player2 = make_level_players(level.get('level_players',stand_player))
    #if player_number == 2:
    #    stand_player2 = stand_player.copy()
    #    stand_player2['pos_x'] += 50
    #    stand_player2['image'] = image_player2
    #    player2 = Player(stand_player2)
        #player2.name = 'player2'
    
    setting_image = make_level_setting( level.get('level_setting', stand_setting) )
    
    desktop.blit(setting_image,(0,0))
    Text(100).write('{0} level'.format(which_level), (resolution[0]//3,100))
    dirty = evryth.draw(desktop)
    pygame.display.update(dirty)
    pygame.display.flip()
    pygame.time.wait(1500)
    
    # create background for game
    desktop.blit(setting_image,(0,0))
    pygame.display.flip()
    
    while True:
        
        desktop.blit(setting_image,(0,0))
        # arba daryti clear kaip alien.py
        
        # input
        ev = pygame.event.poll()
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ev.type == pygame.KEYDOWN:
            if ev.dict["key"] == 27:
                from_game_to_levels = True
                break
            # genneration of a new arrow
            if ev.key == pygame.K_UP and player1.arrows_tot < player1.arrows_max:
                arrow1 = Arrow(player1)
                player1_arrows.add(arrow1)
                player1.arrows_tot += 1
            try:
                if ev.key == pygame.K_w and player2.arrows_tot < player2.arrows_max:
                    arrow2 = Arrow(player2)
                    player2_arrows.add(arrow2)
                    player2.arrows_tot += 1
            except:
                pass
            
        keystate = pygame.key.get_pressed()
        direction1 = keystate[pygame.K_RIGHT] - keystate[pygame.K_LEFT]
        direction2 = keystate[pygame.K_d] - keystate[pygame.K_a]
        
        # UPDATE
        player1.movement(direction1)
        try:
            player2.movement(direction2)
        except:
            pass
        
        evryth.update()       

        # TEST IF COLLIDE AND DRAW
        
        CollisionDetection()
                
        dirty = evryth.draw(desktop)
        pygame.display.update(dirty) # kam reikia dirty?
        #desktop.blit(ground_image,(0,resolution[1] - ground_height))
        #pygame.display.flip() # stringa del update

        # frames per second
        game_clock = pygame.time.Clock()
        game_clock.tick(fps)

        # END OF GAME
        
        if len(players) < player_number or len(bubbles) == 0:
            pygame.display.update(dead_player.draw(desktop)) # SO THAT THE BUBBLES WOULD BE IN THE FIRST FRAME
            pygame.display.update(bubble_of_death.draw(desktop)) # SO THAT THE BUBBLES WOULD BE IN THE FIRST FRAME
            if len(players) < player_number:
                desktop.blit(image_end_game_lost, ( (resolution[0] - image_end_game_lost.get_size()[0])//2 , 10 ))
            else:
                desktop.blit(image_end_game_won, ( (resolution[0] - image_end_game_won.get_size()[0])//2 , 10 ))

            blevels = Button('rect' , 0.4 , [resolution[0]/4,resolution[1]*5/9] , image_end_game_levels)
            brepeat = Button('rect' , 0.4 , [resolution[0]*3/4,resolution[1]*5/9] , image_end_game_repeat)
            pygame.display.flip()
            
            out = False
            while not out:
                # EXIT
                ev = pygame.event.wait()
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.dict["key"] == 27:
                        out = True
                        from_game_to_levels = True
                # CLICK OF A BUTTON
                if ev.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    for butt in [blevels,brepeat]:
                        if butt.click(pos):
                            out = True
                            if butt is blevels:
                                from_game_to_levels = True
                            break
            break

def main():
    
    pygame.init()
    #pygame.display.set_icon(pygame.image.load(os.path.join('images','bubble1.png')))
    global resolution, desktop, stand_player, stand_bubble, levels, data

    desktop = pygame.display.set_mode(resolution)#,pygame.FULLSCREEN)
    pygame.display.set_caption('Bubble Kingdom')
    #pygame.display.set_icon(logo)
    # make data list, where each element represents data of a level in a type of 'dict'
    levels = [{} for i in range(101)]
    # Additional ball regeneration levels at ball.range: [9 , 12 , 17 , 24 , 34 , 48 , 68 , 98 , 139 , 199 , 284]
    #                                   Hits to destroy: [1    2    3    4    5    6    7    8     9    10    11] MINUS ONE WHEN INFUMUM == 9 !
    # levels = [level , level , ... , level]
    # level = { level_bubbles:[{bubbles,inheritance},{bubbles,inheritance}...] , level_players:{}... }
    # bubbles = [bubble,bubble] - all these belong to the same inheritance family
    
    # 1 lvl
    levels[1]['level_bubbles'] = [ {'bubbles':[{'diameter':24 , 'pos_x':60 , 'pos_y':resolution[1]/6*5-ground_height}]} ]
    #levels[1]['level_setting'] = stand_setting
    # 2 lvl
    levels[2]['level_bubbles'] = [ {'bubbles':[[3 , {'diameter':[24,'*',2] , 'pos_x':[resolution[0]/6,'+',resolution[0]/3] , 
                                                     'pos_y':[428-ground_height,'+',100] , 'speed_x':[-2,'*',0]} , True]]} ]
    # 3 lvl
    levels[3]['level_bubbles'] = [ {'bubbles':[[9 , {'diameter':[17,0,0] , 'pos_x':[resolution[0]/2-400,'+',100] , 'pos_y':[150,0,0] , 
                                               'speed_x':[-2,'+',0.5]} , True]]} ]
    # 4 lvl
    levels[4]['level_bubbles'] = [ {'bubbles':[{'diameter':139 , 'pos_x':650 , 'pos_y':228  }]} ]
    # 5 lvl
    levels[5]['level_bubbles'] = [ {'bubbles':[[10 , {'diameter':[12,0,0] , 'pos_x':[50,0,0] , 'pos_y':[510-ground_height,'+',-100] , 
                                                     'speed_x':[-5.5,'+',1]} , True]]} ]
    # 6 lvl
    levels[6]['level_bubbles'] = [ {'bubbles':[[21 , {'diameter':[9,0,0] , 'pos_x':[resolution[0]/2,0,0] , 
                                                     'pos_y':[100,0,0] , 'speed_x':[-5,'+',0.5]} , True]]} ]
    # 7 lvl
    levels[7]['level_bubbles'] = [ {'bubbles':[[18 , {'diameter':[9,0,0] , 'pos_x':[resolution[0]/20,'+',resolution[0]/40] , 
                                                     'pos_y':[resolution[1]-90-ground_height,0,0] , 'speed_x':[1,0,0]} , True]]} ]
    # 8 lvl
    levels[8]['level_bubbles'] = [ {'bubbles':[[8 , {'diameter':[12,0,0] , 'pos_x':[resolution[0]/20,'+',resolution[0]/15] , 
                                                    'pos_y':[resolution[1]-13-ground_height,0,0] , 'speed_x':[3,'+',0.1] , 
                                                    'speed_y':[4,0,0] , 'gravity':[0,0,0]} , True]]} ]
    # 9 lvl
    levels[9]['level_bubbles'] = [ {'bubbles':[[6 , {'diameter':[17,0,0] , 'pos_x':[resolution[0]/20,'+',resolution[0]/15] , 
                                                    'pos_y':[resolution[1]-18-ground_height,0,0] , 'speed_x':[3,'+',0.1] , 
                                                    'speed_y':[4,0,0] , 'gravity':[0,0,0]} , True]] , 
                                    'inheritance':{'gravity':0}} ]
    # 10 lvl
    levels[10]['level_bubbles'] = [ {'bubbles':[[6 , {'diameter':[24,0,0] , 'pos_x':[resolution[0]/2,0,0] , 
                                                    'pos_y':[resolution[1]/4-ground_height,'+',resolution[1]/4] , 
                                                    'speed_x':[7,0,0] , 'gravity':[0,0,0]} , True] , 
                                                [5 , {'diameter':[17,0,0] , 'pos_x':[resolution[0]/6,'+',resolution[0]/6] , 
                                                        'pos_y':[resolution[1]-17-ground_height,'+',-(resolution[1]-17*1.8)/5] , 
                                                        'speed_x':[0,0,0] , 'speed_y':[6,0,0] , 'gravity':[0,0,0]}]]} ]
    # 11 lvl
    levels[11]['level_bubbles'] = [ {'bubbles':[[10, {'diameter':[17,0,0] , 'pos_x':[resolution[0]/11,'+',resolution[0]/11] , 
                                                    'pos_y':[250,0,0]}]]} ]
    levels[11]['level_players'] = {'player1': {'acceleration_x_ratio':0.7}}
    levels[11]['level_setting'] = {'ground':[image_ground_ice,(0,resolution[1]-ground_height),(resolution[0],30)]}
    

    while True:
        Page().levels()
    

    
    pygame.quit()

main()
