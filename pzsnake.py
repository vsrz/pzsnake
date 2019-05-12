import sys
import os
import time
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

    def same_x(self, other):
        if self.x == other.x:
            return True
        return False

    def same_y(self, other):
        if self.y == other.y:
            return True
        return False

    def bottom_of(self, other):
        if self.y > other.y:
            return True
        return False

    def top_of(self, other):
        if self.y < other.y:
            return True
        return False

    def left_of(self, other):
        if self.x < other.x:
            return True
        return False

    def right_of(self, other):
        if self.x > other.x:
            return True
        return False

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x},{self.y})'

class Config:
    SCALE = (32, 32)
    TILE_SIZE = 32
    FPS = 6
    START_POS = Position(3 * TILE_SIZE, 8 * TILE_SIZE)

class Food:

    sprite_location = pygame.Rect(
        ((0*64, 3*64), (64, 64))
    )

    def __init__(self, screen, spritesheet):
        self.screen_size = screen.map_size
        self.visible = False
        self.load_sprites(spritesheet)
        self.position = Position(50, 50)

    def load_sprites(self, spritesheet):
        self.image = Subimage(spritesheet, self.sprite_location).image

    def refresh(self):
        self.pos = Position(
            randint(1, self.screen_size.x - 2) * Config.TILE_SIZE,
            randint(1, self.screen_size.y - 2) * Config.TILE_SIZE,
        )
        self.visible = True

    def update(self, surface):
        if not self.visible:
            self.refresh()

    def render(self, screen):
        if not self.visible:
            self.refresh()
        screen.blit(self.image, self.pos.get())

class Direction:
    right = 1
    down = 2
    left = 4
    up = 3

class Background:
    def __init__(self, image):
        img = image.image
        self.image = pygame.Surface.convert_alpha(img)
        self.image.set_alpha(210)
        self.pos = Position(0,0)
        self.visible = True

    def render(self, screen):
        if self.visible:
            screen.blit(self.image, self.pos.get())


class Snake:

    SPEED = 1

    def __init__(self, screen, spritesheet):
        self.velocity = Position(self.SPEED, 0)
        self.up_bound = screen.size
        self.low_bound = Position(0, 0)
        self.reset()
        self.food_up = False
        self.load_sprites(spritesheet)

    def reset(self):
        self.direction = Direction.right
        self.tail = [
            Config.START_POS,
            Position(
                Config.START_POS.x - Config.TILE_SIZE,
                Config.START_POS.y
            ),
            Position(Config.START_POS.x - Config.TILE_SIZE * 2,
                 Config.START_POS.y
            ),
            Position(Config.START_POS.x - Config.TILE_SIZE * 3,
                 Config.START_POS.y
            ),
        ]
        self.move(self.direction)

    def load_sprites(self, spritesheet):
        sprite_size = Position(64, 64).get()
        self.image = {}

        ### HEAD
        # Up
        head_up = Subimage(spritesheet, pygame.Rect(
            ((3*64, 0*64), sprite_size))
        )
        self.image['head_up'] = head_up
        # Right
        head_right = Subimage(spritesheet, pygame.Rect(
            ((4*64, 0*64), sprite_size))
        )
        self.image['head_right'] = head_right
        # Left
        head_left = Subimage(spritesheet, pygame.Rect(
            ((3*64, 1*64), sprite_size))
        )
        self.image['head_left'] = head_left
        # Down
        head_down = Subimage(spritesheet, pygame.Rect(
            ((4*64, 1*64), sprite_size))
        )
        self.image['head_down'] = head_down

        ### BODY
        # Down to right
        body_dr = Subimage(spritesheet, pygame.Rect(
            ((0*64, 0*64), sprite_size))
        )
        self.image['body_dr'] = body_dr
        # Right 
        body_r = Subimage(spritesheet, pygame.Rect(
            ((1*64, 0*64), sprite_size))
        )
        self.image['body_rl'] = body_r
        # Left to down
        body_ld = Subimage(spritesheet, pygame.Rect(
            ((2*64, 0*64), sprite_size))
        )
        self.image['body_ld'] = body_ld
        # Up to right
        body_ur = Subimage(spritesheet, pygame.Rect(
            ((0*64, 1*64), sprite_size))
        )
        self.image['body_ur'] = body_ur
        # Down
        body_down = Subimage(spritesheet, pygame.Rect(
            ((2*64, 1*64), sprite_size))
        )
        self.image['body_ud'] = body_down
        # Up to left
        body_ul = Subimage(spritesheet, pygame.Rect(
            ((2*64, 2*64), sprite_size))
        )
        self.image['body_ul'] = body_ul

        ### TAIL
        tail_up = Subimage(spritesheet, pygame.Rect(
            ((3*64, 2*64), sprite_size))
        )
        self.image['tail_up'] = tail_up

        tail_down = Subimage(spritesheet, pygame.Rect(
            ((4*64, 3*64), sprite_size))
        )
        self.image['tail_down'] = tail_down

        tail_right = Subimage(spritesheet, pygame.Rect(
            ((4*64, 2*64), sprite_size))
        )
        self.image['tail_right'] = tail_right

        tail_left = Subimage(spritesheet, pygame.Rect(
            ((3*64, 3*64), sprite_size))
        )
        self.image['tail_left'] = tail_left

        unk = Subimage(spritesheet, pygame.Rect(
            ((1*64, 1*64), sprite_size))
        )
        self.image['unk'] = unk
    def move(self, direction):
        """
            1 = right, 2 = down, 3 = up, 4 = left, 5 = food
        """
        self.velocity.reset()
        if direction == 1:
            self.velocity.x = self.SPEED
            self.direction = Direction.right
        elif direction == 4:
            self.velocity.x = self.SPEED * -1
            self.direction = Direction.left
        elif direction == 3:
            self.velocity.y = self.SPEED * -1
            self.direction = Direction.up
        elif direction == 2:
            self.velocity.y = self.SPEED
            self.direction = Direction.down
        if direction == 5:
            self.food_up = True
            reader.food_up = False

    def get_head_image(self):
        if self.direction == 1:
            return self.image['head_right'].image
        if self.direction == 2:
            return self.image['head_down'].image
        if self.direction == 3:
            return self.image['head_up'].image
        if self.direction == 4:
            return self.image['head_left'].image

    def get_tail_image(self, my_pos, parent_pos):
        if my_pos.x > parent_pos.x:
            # left
            return self.image['tail_left'].image
        if my_pos.x < parent_pos.x:
            # right
            return self.image['tail_right'].image
        if my_pos.y > parent_pos.y:
            # down
            return self.image['tail_up'].image
        if my_pos.y < parent_pos.y:
            # up
            return self.image['tail_down'].image

    def get_body_image(self, pos, child, parent):
        if pos.left_of(parent):
            if pos.bottom_of(child):
                return self.image['body_ur'].image
            if pos.top_of(child):
                return self.image['body_dr'].image
            if pos.right_of(child):
                # left
                return self.image['body_rl'].image
        if pos.right_of(parent):
            if pos.bottom_of(child):
                return self.image['body_ul'].image
            if pos.top_of(child):
                return self.image['body_ld'].image
            else:
                return self.image['body_rl'].image
        if pos.bottom_of(parent):
            if pos.right_of(child):
                return self.image['body_ul'].image
            if pos.left_of(child):
                return self.image['body_ur'].image
            else:
                return self.image['body_ud'].image
        if pos.top_of(parent):
            if pos.right_of(child):
                return self.image['body_ld'].image
            if pos.left_of(child):
                return self.image['body_dr'].image
            else:
                return self.image['body_ud'].image
        return self.image['unk'].image


    def update_movement(self, pos):
        if self.velocity.x > 0:
            if pos.x + self.velocity.x * Config.TILE_SIZE < self.up_bound.x - 1:
                return Position(pos.x + self.velocity.x * Config.TILE_SIZE, pos.y)
        if self.velocity.x < 0:
            if pos.x + self.velocity.x * Config.TILE_SIZE > self.low_bound.x:
                return Position(pos.x + self.velocity.x * Config.TILE_SIZE, pos.y)
        if self.velocity.y > 0:
            if pos.y + self.velocity.y * Config.TILE_SIZE <= self.up_bound.y + 1:
                return Position(pos.x, pos.y + self.velocity.y * Config.TILE_SIZE)
        if self.velocity.y < 0:
            if pos.y + self.velocity.y * Config.TILE_SIZE > self.low_bound.y:
                return Position(pos.x, pos.y + self.velocity.y * Config.TILE_SIZE)
        return pos

    def grow(self, pos):
        self.tail.insert(0, pos)
        self.food_up = False

    def update(self, screen):
        ## Update tails
        next_pos = self.update_movement(self.tail[0])
        if self.food_up or screen.entities['food'].visible and next_pos == screen.entities['food'].pos:
            screen.entities['food'].refresh()
            self.grow(next_pos)
        else:
            for cnt in range(len(self.tail)-1, -1, -1):
                if not cnt:
                    if next_pos in self.tail:
                        screen.game_over = True
                    self.tail[cnt] = next_pos
                else:
                    self.tail[cnt] = self.tail[cnt-1]

        # Check for wall collision

        # Check for tail collision

    def render(self, screen):
        for e in range(len(self.tail)-1, -1, -1):
            if not e:
                screen.blit(
                    self.get_head_image(),
                    self.tail[e].get()
                )
            elif e == len(self.tail)-1:
                screen.blit(
                    self.get_tail_image(self.tail[e], self.tail[e-1]),
                    self.tail[e].get()
                )

            else:
                screen.blit(
                    self.get_body_image(
                        self.tail[e],
                        self.tail[e+1],
                        self.tail[e-1]),
                    self.tail[e].get()
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
        self.image = pygame.transform.scale(self.image, Config.SCALE)
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
                    screen.quit = True
                    screen.game_over = True
            if event.type == pygame.QUIT:
                screen.quit = True

class Screen:
    def __init__(self, size):
        pygame.init()
        self.size = size
        self.map_size = Position(size.x / Config.TILE_SIZE, size.y / Config.TILE_SIZE)
        self.screen = pygame.display.set_mode(size.get())
        self.running = True
        self.entities = {}
        self.quit = False
        self.game_over = False

    def add_entity(self, name, entity):
        self.entities[name] = entity

    def add_handler(self, processor):
        self.processor = processor

    def run(self):
        while not self.quit:
            clock = pygame.time.Clock()
            while not self.game_over:
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
                self.screen.fill((0, 0, 0))
                dt = clock.tick(Config.FPS)
            time.sleep(1)
            self.game_over = False
            self.entities['snake'].reset()

def run_graphical():
    screen = Screen(Position(640,640))
    spritesheet = Image('snake-graphics.png')
    bg = Background(Image('bg.jpg'))
    ip = InputProcessor()

    food = Food(screen, spritesheet)
    food2 = Food(screen, spritesheet)
    food3 = Food(screen, spritesheet)
    food4 = Food(screen, spritesheet)
    snake = Snake(screen, spritesheet)

    screen.add_handler(ip)
    screen.add_entity('bg', bg)
    screen.add_entity('food', food)
    # screen.add_entity('food2', food2)
    # screen.add_entity('food3', food3)
    # screen.add_entity('food4', food4)
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
