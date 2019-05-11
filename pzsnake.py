import sys
import os
import curses
from random import randint
from time import sleep


class Position:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def reset(self):
        self.x = self.y = 0

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x},{self.y})'


class Food:

    sprite = '*'

    def __init__(self, board):
        self.board_size = board.size
        self.pos = Position(-1, -1)
        self.visible = False

    def refresh(self):
        self.pos = Position(
            randint(1, self.board_size.x - 2),
            randint(1, self.board_size.y - 2),
        )
        self.visible = True

    def draw(self, surface):
        if self.visible:
            surface.win.addstr(self.pos.y, self.pos.x, f'{self.sprite}')

    def update(self, surface):
        if not self.visible:
            self.refresh()

class Snake:
    head_sprite = '@'
    tail_sprite = '='

    def __init__(self, board):
        self.velocity = Position(1, 0)
        self.up_bound = board.size
        self.low_bound = Position(0, 0)
        self.tail = [Position(2,2)]
        self.food_up = False

    def move(self, reader):
        self.velocity.reset()
        if reader.dir['right']:
            self.velocity.x = 1
        elif reader.dir['left']:
            self.velocity.x = -1
        elif reader.dir['up']:
            self.velocity.y = -1
        elif reader.dir['down']:
            self.velocity.y = 1
        if reader.food_up:
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

    def update(self, surface):
        ## Update tails
        next_pos = self.update_movement(self.tail[0])
        if self.food_up or surface.items['food'].visible and next_pos == surface.items['food'].pos:
            surface.items['food'].refresh()
            self.tail.insert(0, next_pos)
            self.food_up = False
        else:
            for cnt in range(len(self.tail)-1, -1, -1):
                if not cnt:
                    if next_pos in self.tail:
                        surface.items['inreader'].quit = True
                    self.tail[cnt] = next_pos
                else:
                    self.tail[cnt] = self.tail[cnt-1]

        # Check for wall collision

        # Check for tail collision
        # Cheater mode:
        surface.items['inreader'].quit = False


    def draw(self, surface):
        for each in self.tail:
            if self.tail[0] == each:
                sp = self.head_sprite
            else:
                sp = self.tail_sprite
            surface.win.addstr(each.y, each.x, f'{sp}')
            # surface.win.addstr(i, 0, f'Tail: {each}')


class Board:
    def __init__(self):
        self.size = Position(72, 20)

    def update(self, win):
        pass

    def draw(self, surface):
        surface.win.addstr(0, 0, f'+{"-" * 70}+')
        for i in range(1,22):
            surface.win.addstr(i, 0, f'|{" " * 70}|')
        surface.win.addstr(22,0,f'+{"-" * 70}+')

class Inreader:
    def __init__(self):
        self.quit = False
        self.set_movement()
        self.food_up = False
        self.slp = 0.05

    def set_movement(self, key = False):
        self.dir = {
            'right' : False,
            'down' : False,
            'left' : False,
            'up' : False,
        }
        if key:
            self.dir[key] = True

    def update(self, surface):
        key = surface.win.getch()
        if key == curses.ERR:
            return
        if key == curses.KEY_LEFT or key == ord('a'):
            self.set_movement('left')
        elif key == curses.KEY_RIGHT or key == ord('d'):
            self.set_movement('right')
        elif key == curses.KEY_DOWN or key == ord('s'):
            self.set_movement('down')
        elif key == curses.KEY_UP or key == ord('w'):
            self.set_movement('up')
        elif key == ord('='):
            if not self.slp <= 0.01:
                self.slp -= 0.01
        elif key == ord('-'):
            self.slp += 0.01
        elif key == ord('m'):
            self.food_up = True
        elif key == ord('p'):
            self.quit = True

    def auto_move(self):
        for e in self.dir.keys():
            self.dir[e] = False
        rl = randint(0,2)
        if rl == 0:
            self.dir['left'] = True
        elif rl == 2:
            self.dir['right'] = True

        du = randint(0,2)
        if du == 0:
            self.dir['down'] = True
        elif du == 2:
            self.dir['up'] = True

    def draw(self, surface):
        surface.win.addstr(23,0,f'Speed: {self.slp*1}')

class Surface:

    win_size = Position(80, 30)
    win_start = Position(0,0)
    def __init__(self):
        self.curses = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.curses.keypad(True)
        self.items = {}
        self.win = curses.newwin(self.win_size.y, self.win_size.x, self.win_start.y, self.win_start.x)
        self.win.nodelay(True)

    def add_item(self, name, item):
        self.items[name] = item

    def clear(self):
        pass

    def update(self):
        for keys in self.items.keys():
            self.items[keys].update(self)
            self.items[keys].draw(self)
        self.win.addstr(23, 0, ' ')
        self.win.refresh()

    def __del__(self):
        self.win.addstr(23, 0, 'OUCH! You lose!')
        self.win.nodelay(False)
        self.win.refresh()
        self.win.getkey()
        curses.nocbreak()
        self.curses.keypad(False)
        curses.echo()
        curses.endwin()



def run():
    surface = Surface()
    board = Board()
    snake = Snake(board)
    ir = Inreader()
    food = Food(board)
    ir.set_movement('right')
    surface.add_item('board', board)
    surface.add_item('snake', snake)
    surface.add_item('inreader', ir)
    surface.add_item('food', food)
    cnt = 0
    while not ir.quit:
        sleep(ir.slp)
        snake.move(ir)
        surface.update()

def main():
    while True:
        try:
            run()
        except Exception as e:
            print(e)

        r = input('Continue? (yes/no)')
        if r[0:1].lower() != 'y':
            sys.exit(0)

if __name__ == '__main__':
    curses.wrapper(main())
