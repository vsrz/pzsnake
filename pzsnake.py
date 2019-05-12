import sys
import os
import curses
from random import randint
from time import sleep
import pygame
from pygame.locals import *


class Position:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def reset(self):
        self.x = self.y = 0

    def get(self):
        return (self.x,self.y,)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x},{self.y})'

class Food:

    sprite_location = pygame.Rect(
        ((0*64, 3*64), (64, 64))
    )

    def __init__(self, screen, spritesheet):
        self.screen_size = screen.size
        self.visible = False
        self.load_sprites(spritesheet)
        self.position = Position(50, 50)

    def load_sprites(self, spritesheet):
        self.image = Subimage(spritesheet, self.sprite_location).image

    def refresh(self):
        self.pos = Position(
            randint(1, self.screen_size.x - 2),
            randint(1, self.screen_size.y - 2),
        )
        self.visible = True

    def update(self, surface):
        if not self.visible:
            self.refresh()

    def render(self, screen):
        if not self.visible:
            self.refresh()
        screen.blit(self.image, self.position.get())


class Snake:

    SPEED = 8

    def __init__(self, screen, spritesheet):
        self.velocity = Position(self.SPEED, 0)
        self.up_bound = screen.size
        self.low_bound = Position(0, 0)
        self.tail = [Position(2,2)]
        self.food_up = False
        self.load_sprites(spritesheet)

    def load_sprites(self, spritesheet):
        block_size = Position(64, 64).get()
        self.image = {}

        ### HEAD
        # Up
        head_up = Subimage(spritesheet, pygame.Rect(
            ((3*64, 0*64), block_size))
        )
        head_up.set_position(Position(50, 50))
        self.image['head_up'] = head_up
        # Right
        head_right = Subimage(spritesheet, pygame.Rect(
            ((4*64, 0*64), block_size))
        )
        head_right.set_position(Position(50, 50))
        self.image['head_right'] = head_right
        # Left
        head_left = Subimage(spritesheet, pygame.Rect(
            ((3*64, 1*64), block_size))
        )
        head_left.set_position(Position(50, 50))
        self.image['head_left'] = head_left
        # Down
        head_down = Subimage(spritesheet, pygame.Rect(
            ((4*64, 1*64), block_size))
        )
        head_down.set_position(Position(50, 50))
        self.image['head_down'] = head_down

        ### BODY
        # Down to right
        body_dr = Subimage(spritesheet, pygame.Rect(
            ((0*64, 0*64), block_size))
        )
        body_dr.set_position(Position(50, 50))
        self.image['body_dr'] = body_dr
        # Right 
        body_r = Subimage(spritesheet, pygame.Rect(
            ((1*64, 0*64), block_size))
        )
        body_r.set_position(Position(50, 50))
        self.image['body_r'] = body_r
        # Left to down
        body_ld = Subimage(spritesheet, pygame.Rect(
            ((2*64, 0*64), block_size))
        )
        body_ld.set_position(Position(50, 50))
        self.image['body_ld'] = body_ld
        # Up to right
        body_ur = Subimage(spritesheet, pygame.Rect(
            ((0*64, 1*64), block_size))
        )
        body_ur.set_position(Position(50, 50))
        self.image['body_ur'] = body_ur
        # Down
        body_down = Subimage(spritesheet, pygame.Rect(
            ((2*64, 1*64), block_size))
        )
        body_down.set_position(Position(50, 50))
        self.image['body_down'] = body_down
        # Up to left
        body_ul = Subimage(spritesheet, pygame.Rect(
            ((2*64, 2*64), block_size))
        )
        body_ul.set_position(Position(50, 50))
        self.image['body_ul'] = body_ul


    def move(self, direction):
        """
            1 = right, 2 = down, 3 = up, 4 = left, 5 = food
        """
        self.velocity.reset()
        if direction == 1:
            self.velocity.x = self.SPEED
        elif direction == 4:
            self.velocity.x = self.SPEED * -1
        elif direction == 3:
            self.velocity.y = self.SPEED * -1
        elif direction == 2:
            self.velocity.y = self.SPEED
        if direction == 5:
            self.food_up = True
            reader.food_up = False


    def update_movement(self, pos):
        if self.velocity.x > 0:
            if pos.x + self.velocity.x < self.up_bound.x - 1:
                return Position(pos.x + self.velocity.x, pos.y)
        if self.velocity.x < 0:
            if pos.x + self.velocity.x > self.low_bound.x:
                return Position(pos.x + self.velocity.x, pos.y)
        if self.velocity.y > 0:
            if pos.y + self.velocity.y <= self.up_bound.y + 1:
                return Position(pos.x, pos.y + self.velocity.y)
        if self.velocity.y < 0:
            if pos.y + self.velocity.y > self.low_bound.y:
                return Position(pos.x, pos.y + self.velocity.y)
        return pos

    def update(self, screen):
        ## Update tails
        next_pos = self.update_movement(self.tail[0])
        if self.food_up or screen.entities['food'].visible and next_pos == screen.entities['food'].pos:
            screen.entities['food'].refresh()
            self.tail.insert(0, next_pos)
            self.food_up = False
        else:
            for cnt in range(len(self.tail)-1, -1, -1):
                if not cnt:
                    if next_pos in self.tail:
                        screen.quit = True
                    self.tail[cnt] = next_pos
                else:
                    self.tail[cnt] = self.tail[cnt-1]

        # Check for wall collision

        # Check for tail collision

    def render(self, screen):
        for each in self.tail:
            screen.blit(
                self.image['head_right'].image,
                each.get()
            )

class Image:
    def __init__(self, image_file):
        self.image = pygame.image.load(image_file)
        self.position = Position(50,50)

    def set_position(self, pos):
        self.position = pos

    def update(self, screen):
        pass

    def render(self, screen):
        screen.blit(self.image, self.position.get())

class Subimage:
    def __init__(self, image_obj, rect):
        self.image = image_obj.image.subsurface(rect)
        self.position = Position(50, 50)
        self.visible = False

    def set_position(self, pos):
        self.position = pos

    def update(self, screen):
        pass

    def render(self, screen):
        if self.visible:
            screen.blit(self.image, self.position.get())

class InputProcessor:
    def process_input(self, screen):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    screen.entities['snake'].move(3)
                elif event.key == pygame.K_DOWN:
                    screen.entities['snake'].move(2)
                elif event.key == pygame.K_LEFT:
                    screen.entities['snake'].move(4)
                elif event.key == pygame.K_RIGHT:
                    screen.entities['snake'].move(1)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    pass
                elif event.key == pygame.K_ESCAPE:
                    print('Released')
                    screen.quit = True
            if event.type == pygame.QUIT:
                screen.quit = True

class Screen:
    def __init__(self, size):
        pygame.init()
        self.size = size
        self.screen = pygame.display.set_mode(size.get())
        self.running = True
        self.entities = {}
        self.quit = False

    def add_entity(self, name, entity):
        self.entities[name] = entity

    def add_handler(self, processor):
        self.processor = processor

    def run(self):
        while not self.quit:
            # Check input
            self.processor.process_input(self)
            for k in self.entities.keys():
                # Update
                if hasattr(self.entities[k], 'update'):
                    self.entities[k].update(self)
                # Render
                if hasattr(self.entities[k], 'render'):
                    self.entities[k].render(self.screen)
                pygame.display.flip()


def run_graphical():
    screen = Screen(Position(640,640))
    spritesheet = Image('snake-graphics.png')
    ip = InputProcessor()

    food = Food(screen, spritesheet)
    snake = Snake(screen, spritesheet)

    screen.add_handler(ip)
    screen.add_entity('food', food)
    screen.add_entity('snake', snake)
    screen.run()

def main():
    while True:
        try:
            run_graphical()
            sys.exit(0)
        except Exception as e:
            print(e)

        r = input('Continue? (yes/no)')
        if r[0:1].lower() != 'y':
            sys.exit(0)

if __name__ == '__main__':
    curses.wrapper(main())
