import pygame, sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

class Game:
    def __init__(self):
        # player setup
        playerSprite = Player((screenWidth/2,screenHeight),screenWidth,5)
        self.player = pygame.sprite.GroupSingle(playerSprite)

        # health and score setup
        self.lives = 3
        self.livesSurface = pygame.image.load('graphics/player.png').convert_alpha()
        self.livesXStartPos = screenWidth - (self.livesSurface.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)

        # obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacleAmount = 4
        self.obstacle_x_position = [num * (screenWidth/self.obstacleAmount) for num in range(self.obstacleAmount)]
        self.createMultipleObstacles(*self.obstacle_x_position, xStart = screenWidth/15, yStart= 480)
        self.aliensDirection = 1

        # alien setup
        self.aliens = pygame.sprite.Group()
        self.alienSetup(rows = 6, cols = 8)
        self.alienLasers = pygame.sprite.Group()

        # extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extraSpawnTime = randint(40, 80)

        # Audio 
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.2)
        music.play(loops=-1)
        self.laserSound = pygame.mixer.Sound('audio/laser.wav')
        self.laserSound.set_volume(0.5)
        self.explosionSound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosionSound.set_volume(0.3)

    def createObstacle(self, xStart, yStart, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = xStart + col_index * self.block_size + offset_x
                    y = yStart + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (241,79,80), x, y)
                    self.blocks.add(block)

    def createMultipleObstacles(self,*offset,xStart,yStart):
        for offset_x in offset:
            self.createObstacle(xStart, yStart,offset_x)

    def alienSetup(self,rows,cols, xDistance = 60, yDistance = 48, xOffset = 70, yOffset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * xDistance + xOffset
                y = row_index * yDistance + yOffset

                if row_index == 0: alienSprite =  Alien('yellow', x, y)
                elif 1 <= row_index <= 2: alienSprite = Alien('green', x, y)
                else: alienSprite = Alien('red', x, y)
                self.aliens.add(alienSprite)

    def alienPositionChecker(self):
        allAliens = self.aliens.sprites()
        for alien in allAliens:
            if alien.rect.right >= screenWidth:
                self.aliensDirection = -1
                self.alienMoveDown(2)
            elif alien.rect.left <= 0:
                self.aliensDirection = 1
                self.alienMoveDown(2)

    def alienMoveDown(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alienShoot(self):
        if self.aliens.sprites():
            randomAlien = choice(self.aliens.sprites())
            laserSprite = Laser(randomAlien.rect.center, 6, screenHeight)
            self.alienLasers.add(laserSprite)
            self.laserSound.play()

    def extraAlienTimer(self):
        self.extraSpawnTime -= 1
        if self.extraSpawnTime <= 0:
            self.extra.add(Extra(choice(['right', 'left']), screenWidth))
            self.extraSpawnTime = randint(400, 800)

    def collisionChecks(self):

        # player lasers 
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collision
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collision
                aliensHit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliensHit:
                    for alien in aliensHit:
                        self.score += alien.value
                    laser.kill()
                    self.explosionSound.play()

                # extra collision
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    laser.kill()
                    self.score += 500
                    self.explosionSound.play

        # alien laser
        if self.alienLasers:
            for laser in self.alienLasers:
                # obstacle collision
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                # player collision
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                    
                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def displayLives(self):
        for live in range (self.lives - 1):
            x = self.livesXStartPos + (live * (self.livesSurface.get_size()[0] + 10))
            screen.blit(self.livesSurface, (x,8))

    def displayScore(self):
        scoreSurface = self.font.render(f'score: {self.score}',False,'white')
        scoreRect = scoreSurface.get_rect(topleft = (10,-10))
        screen.blit(scoreSurface, scoreRect)

    def victoryMessage(self):
        if not self.aliens.sprites():
            victorySurface = self.font.render("You Fucked Alien Pussy", False, 'white')
            victoryRect = victorySurface.get_rect(center = (screenWidth/2, screenHeight/2))
            screen.blit(victorySurface, victoryRect)

    def run(self):
        self.player.update()
        self.aliens.update(self.aliensDirection)
        self.alienPositionChecker()
        self.alienLasers.update()
        self.extraAlienTimer()
        self.extra.update()
        self.collisionChecks()

        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)

        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alienLasers.draw(screen)
        self.extra.draw(screen)
        self.displayLives()
        self.displayScore()
        self.victoryMessage()
        # update all sprite groups
        #draw all sprite groups

class CRT:
    def __init__(self):
        self.tv = pygame.image.load('graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screenWidth,screenHeight))
    
    def createCRTLines(self):
        lineHeight = 3
        lineAmount = int(screenHeight/lineHeight)
        for line in range(lineAmount):
            yPos = line * lineHeight
            pygame.draw.line(self.tv, 'black', (0, yPos), (screenWidth, yPos), 1)

    def draw(self):
        self.tv.set_alpha(randint(0, 100))
        self.createCRTLines()
        screen.blit(self.tv, (0,0))

if __name__ == '__main__':
    pygame.init()
    screenHeight=600
    screenWidth=600
    screen=pygame.display.set_mode((screenWidth,screenHeight))
    clock=pygame.time.Clock()
    game = Game()

    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alienShoot()

        screen.fill((30,30,30))
        game.run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)
