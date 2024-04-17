import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation, get_font
from scripts.tilemap import Tilemap
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.button import Button
import os


class Game:
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption('Dungeon Ninja')
        self.screen = pygame.display.set_mode((1080, 720))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        
        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]

        self.assets = {
            'decor': load_images('/tiles/decor'),
            'floor': load_images('/tiles/floor'),
            'stone': load_images('/tiles/stone'),
            'large_decor': load_images('/tiles/large_decor'),
            'main_menu': load_image('/main_menu/wallpaper.png'),                        
            #'player': load_image('/entities/player.png'),
            'particle/flame': Animation(load_images('/particles/grndtorchflame3'), img_dur=8),
            'background': load_image('/Background/Layer 4.png'),
            'stalathings': load_images('/stalathings'),
            'enemy/idle': Animation(load_images('/entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('/entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('/entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('/entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('/entities/player/jump')),
            'player/slide': Animation(load_images('/entities/player/slide')),
            'player/wall_slide': Animation(load_images('/entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('/particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('/particles/particle'), img_dur=6, loop=False),
            'spawners': load_images('/tiles/spawners'),
            'gun': load_image('/gun.png'),
            'projectile': load_image('/projectile.png'),
            'wall': load_images('/tiles/wall'),
            'grass': load_images('/tiles/grass'),
        }
        
        self.sfx = {
            'jump': pygame.mixer.Sound('Dungeon_Ninja/assets/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('Dungeon_Ninja/assets/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('Dungeon_Ninja/assets/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('Dungeon_Ninja/assets/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('Dungeon_Ninja/assets/sfx/ambience.wav'),
        }
        
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        
                
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.level = 0
        self.load_level(self.level)
        
        self.screenshake = 0
        
        #print(self.tilemap.extract([('large_decor', 2)], keep=True))
        

        
    def load_level(self, map_id):
        self.tilemap.load('Dungeon_Ninja/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        self.torch_spawners = []
        for torch in self.tilemap.extract([('large_decor', 3)], keep=True):
            self.torch_spawners.append(pygame.Rect(torch['pos'][0], torch['pos'][1], 16, 16))
        
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
                
        self.projectiles = []
        self.particles = []
        self.sparks = []
                
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
        
    def main_menu(self):
        while True:
            pygame.mixer.music.load('Dungeon_Ninja/assets/Anna-Murphy_-_harley-quinn_(mp3zvon.com).mp3')
            pygame.mixer.music.set_volume(0.05)
            pygame.mixer.music.play(-1)
            mainText = get_font(42).render("Dungeon Ninja", True, "white")
            mainRect = mainText.get_rect(center=(540,150))            
            menu_pos = pygame.mouse.get_pos()
            self.screen.blit(self.assets['main_menu'], (0, 0))
            
            new_game_button = Button(image=None, pos=(540,300), textInput= "Start", font= get_font(35), baseColor= "#d7fcd4", hoveringColor= "White")
            
            self.screen.blit(mainText,mainRect)
            
            for button in [new_game_button]:
                button.changeColor(menu_pos)
                button.update(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.checkForInput(menu_pos):
                    self.run()  

            pygame.display.update()
    
    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))
            for j in range(3):  # parallax
                speed = 1
                for i in self.assets['stalathings']:
                    self.display_2.blit(i, (-320 + (j * i.get_width() - self.scroll[0]) * speed, j * i.get_height()))
                    speed += 0.2
                    
            self.screenshake = max(0, self.screenshake - 1)
            
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('Dungeon_Ninja/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1
            
            if self.dead:
                self.dead += 1
                if self.dead == 10:
                    self.transition = min(self.transition + 1, 30)
                if self.dead > 40:
                    self.load_level(self.level)

            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 4999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            for rect in self.torch_spawners:
                if random.random() * 4999 < rect.width * rect.height:
                    pos = (rect.x + 9, rect.y - 6.5)
                    self.particles.append(Particle(self, 'flame', pos, velocity=[0, 0], frame=random.randint(0, 6)))
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            if not self.dead:
                self.player.update(self.tilemap, ((self.movement[1]-self.movement[0]), 0))
                self.player.render(self.display, offset=render_scroll)
            
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1]
                    projectile[2] += 1
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                    if self.tilemap.solid_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                    elif projectile[2] > 360:
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            self.sfx['hit'].play()
                            self.screenshake  = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                            
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
                    
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)      
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False     
                        
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0)) 
                        
            self.display_2.blit(self.display, (0, 0))
            
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)          
            
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)        
            pygame.display.update()
            self.clock.tick(60)
            
Game().main_menu()
