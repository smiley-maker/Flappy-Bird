import pygame
import neat
import time
import os
import random
pygame.font.init()


WIN_WIDTH = 500
WIN_HEIGHT = 700

#Load images
#pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird1.jpg")))
BIRD_IMGS = [pygame.image.load(os.path.join("assets", "flappy bird 1.png")), pygame.image.load(os.path.join("assets", "flappy bird 2.png")), pygame.image.load(os.path.join("assets", "flappy bird 3.png")), pygame.image.load(os.path.join("assets", "flappy bird 4.png"))]
PIPE = pygame.image.load(os.path.join("assets", "pipe.png"))
BACKGROUND = pygame.image.load(os.path.join("assets", "background.png"))
CLOUDS = pygame.image.load(os.path.join("assets", "clouds.png"))

STAT_FONT = pygame.font.SysFont("swiss721black", 50)


class Bird:
    #Class variables
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
    

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
    

    def move(self):
        self.tick_count += 1

        displacement = self.vel * self.tick_count + 1.5*self.tick_count**2

        if displacement >= 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2
        
        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1] #Level wings for nose dive
            self.img_count = self.ANIMATION_TIME * 2
        
        #Rotate around center based on current tilt
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)        
        win.blit(rotated_img, new_rect.topleft)
    

    def get_mask(self):
        return pygame.mask.from_surface(self.img)



class Pipe:
    GAP = 200
    PIPE_VEL = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
 
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE, False, True)
        self.PIPE_BOTTOM = PIPE
 
        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(40, 350)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    

    def move(self):
        self.x -= self.PIPE_VEL
    
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    

    def isColliding(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #Returns None if no collision
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Clouds:
    BASE_VEL = 5
    WIDTH = CLOUDS.get_width()
    IMG = CLOUDS

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    

    def move(self):
        self.x1 -= self.BASE_VEL
        self.x2 -= self.BASE_VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
        
    
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, clouds, score):
    win.blit(BACKGROUND, (0,0)) #Draws background
    
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH-10-text.get_width(), 10))
    
    clouds.draw(win)
    bird.draw(win)
    pygame.display.update()


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    bird = Bird(230, 350)
    base = Clouds(650)
    pipes = [Pipe(600)]

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
#        bird.move()
        rem = []
        add_pipe = False

        for pipe in pipes:
            if pipe.isColliding(bird):
                pass
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(500))
        
        for r in rem:
            pipes.remove(r)
        
        if bird.y + bird.img.get_height() > 730:
            pass

        base.move()
        draw_window(win, bird, pipes, base, score)
        
    pygame.quit()            


main()
#print(pygame.font.get_fonts())