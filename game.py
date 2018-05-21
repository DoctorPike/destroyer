########################################################################################################################
# Destroyer - a small boat shooter game.                                                                               #
# Copyright (C) 2018 by Hendrik Braun                                                                                  #
#                                                                                                                      #
# This program is free software: you can redistribute it and/or modify it under the terms of the                       #
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                                                                  #
#                                                                                                                      #
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied   #
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more        #
# details.                                                                                                             #
#                                                                                                                      #
# You should have received a copy of the GNU General Public License along with this program.                           #
# If not, see <http://www.gnu.org/licenses/>.                                                                          #
########################################################################################################################

#blaaa

import pygame
import sys
from units import *
from gfx import *
from menus import *
from logic import *
from unit_handling import *
from time import sleep
import datetime

class Timer(object):
    def __init__(self):
        self.__old_time = None
        self.__new_time = None
        self.__delta = None

    def start(self):
        self.__old_time = datetime.datetime.now()
        self.__delta = 0

    def time(self):
        new_time = datetime.datetime.now()
        self.__delta = (new_time-self.__old_time).total_seconds()
        self.__old_time = new_time

    def get_delta(self):
        return self.__delta

    def reset(self):
        self.__old_time = datetime.datetime.now()
        self.__delta = 0

class Game_level(object):
    def __init__(self, init_level=0):
        self.__game_level = init_level

    def increase(self):
        self.__game_level += 1

    def get_level(self):
        return self.__game_level

class Destroyer_game(object):
    """
    The following dictionaries give the game level dependend variable values for game level brakes, maximum enemies
    and enemy wait ranges. Game level breaks define how many enemies the player has to sink before going to the next
    level. Max enemies defines the maximum number of enemies per game level. Enemy wait time ranges define the wait
    time interval in seconds that is used when spawning the next enemy.
    """
    __game_level_breaks = {
        0:20,
        1:20,
        2:20,
        3:20,
        4:20,
        5:20,
        6:20,
        7:20,
        8:20,
        9:20
    }

    __max_enemies = {
        0:5,
        1:5,
        2:6,
        3:6,
        4:7,
        5:7,
        6:8,
        7:8,
        8:10,
        9:10
    }

    __enemy_wait_time_ranges = {
        0:(1,3),
        1:(1,3),
        2:(1,3),
        3:(1,5),
        4:(1,5),
        5:(1,5),
        6:(1,5),
        7:(1,5),
        8:(1,5),
        9:(1,5),
    }

    def __init__(self, window_size=(1024,800), init_game_level=0, font_size=16):
        """
        Main class for the game creating and managing all game object class instances.

        :param window_size      : window size as x,y
        :param init_game_level  : the initial game level
        :param enemy_wait_range : range of spawn waiting times between enemies in seconds
        :param font_size        : font size for HUD
        :type window_size       : set
        :type init_game_level   : set
        :type font_size         : int

        :returns:
        """
        self.__window_size = window_size
        self.__enemies = []
        self.__bullets = []
        self.__enemy_strenght = None
        self.__font_size = font_size
        self.__total_enemies = 0
        self.__max_level = max(self.__game_level_breaks.keys())
        self.__next_level_in = self.__game_level_breaks[init_game_level]
        self.__max_enemies_ff = self.__max_enemies[init_game_level]
        self.__wait_time_range = self.__enemy_wait_time_ranges[init_game_level]
        self.__screen = pygame.display.set_mode(window_size)

        #Initializing all game objects
        timer = Timer()
        pygame.init()
        pygame.font.init()
        game_level = Game_level(init_game_level)
        points = Points()
        texts = Texts(timer)
        explosions = Explosions(timer)
        destroyer = Destroyer(0,500, 500, self.__window_size)
        bullets = Bullets(timer, (self.__window_size[0]/2, self.__window_size[1]/2), self.__window_size)
        torpedos = Torpedos(timer)
        crates = Crates(timer, self.__window_size, self.__font_size + 20, destroyer, game_level)
        enemies = Enemies(timer, self.__wait_time_range, self.__max_enemies_ff, torpedos, crates, game_level,
                          self.__window_size, font_size)
        crates.set_enemies(enemies)
        fades = Fades(timer)
        timer.start()
        enemies.add_enemy()

        #Initializing game logic
        logic = Destroyer_logic(destroyer, enemies, bullets, torpedos, explosions, fades, texts, points, crates,
                                self.__window_size)

        #Initializing game graphics
        graphics = Destroyer_gfx(self.__screen, destroyer, enemies, bullets, torpedos, explosions, fades, texts, points,
                                 crates, game_level, font_size, "./media/background.png")

        #Initializing game menus
        kwargs = {"add_text":[0,"Hello","Hallo"]}
        ingame_menu = Ingame_menu(self.__screen, window_size, "Titel", "Background", **kwargs)

        graphics.draw()
        exit_game = False
        counter = 0
        oldtime = datetime.datetime.now()

        while not exit_game:

            #Level handling
            if enemies.get_sunk_count() == self.__next_level_in:
                if game_level.get_level() < self.__max_level:
                    game_level.increase()
                    enemies.reset_sunk_count()
                    enemies.set_max_enemies(self.__max_enemies[game_level.get_level()])
                    enemies.set_wait_time_range(self.__enemy_wait_time_ranges[game_level.get_level()])
                    self.__next_level_in = self.__game_level_breaks[game_level.get_level()]
                    texts.add_text((window_size[0]/2, window_size[1]/2), "LEVEL UP!", font_size=20, positive=True)

            destroyer.regenerate_power()
            enemies.add_enemy()
            enemies.move()
            enemies.shoot()
            torpedos.move()
            bullets.move()
            explosions.change_frames()
            fades.fade()
            texts.move()
            crates.make_crate(timer)
            crates.check()

            self.__total_enemies = enemies.get_total_enemies()

            if logic.check():
                sys.exit()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                destroyer.turn_tower(1,2)

            if keys[pygame.K_LEFT]:
                destroyer.turn_tower(3,2)

            if keys[pygame.K_SPACE]:
                if destroyer.shoot():
                    bullets.add_bullet(timer, 0,100, destroyer.get_direction(), 800)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

                if event.type is pygame.KEYDOWN:
                    key = pygame.key.name(event.key)

                    if key == "escape":
                        if ingame_menu.show() == 2:
                            exit_game = True
                        else:
                            timer.reset()


            graphics.draw()
            timer.time()
            new_time = datetime.datetime.now()
            if (new_time-oldtime).total_seconds() >= 1:
                print(counter)
                counter=0
                oldtime = new_time
            else:
                counter += 1

    def __del__(self):
        pass
