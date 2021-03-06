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

from math import sin, cos, radians, sqrt, atan, degrees
import pygame
import datetime
from math import floor
from random import randrange


def project_point(original_x, original_y, bearing, distance):

    """
    Function for projecting an x,y position with a specified bearing and a specified distance. Returns the new
    position.

    :param original_x   : x origin
    :param original_y   : y origin
    :param bearing      : bearing in degrees with 0/360 degrees as north
    :param distance     : the distance in pixels the point is to be projektet
    :type original_x    : int
    :type original_y    : int
    :type bearing       : int
    :type distance      :int

    :returns: list of integer
    """

    if bearing >= 360:
        bearing = bearing -360

    if bearing == 0:
        return [original_x, original_y - distance]
    if bearing == 90:
        return [original_x + distance, original_y]
    if bearing == 180:
        return [original_x, original_y + distance]
    if bearing == 270:
        return [original_x - distance, original_y]

    if 0 <= bearing < 90:
        angle = bearing
        move_x = sin(radians(angle))*distance
        move_y = cos(radians(angle))*distance
        return [original_x + move_x, original_y - move_y]

    if 90 <= bearing < 180:
        angle = bearing - 90
        move_x = cos(radians(angle))*distance
        move_y = sin(radians(angle))*distance
        return [original_x + move_x, original_y + move_y]

    if 180 <= bearing < 270:
        angle = bearing - 180
        move_x = sin(radians(angle))*distance
        move_y = cos(radians(angle))*distance
        return [original_x - move_x, original_y + move_y]

    if 270 <= bearing < 360:
        angle = bearing - 270
        move_x = cos(radians(angle))*distance
        move_y = sin(radians(angle))*distance
        return [original_x - move_x, original_y - move_y]


def get_bearing(point_1, point_2):
    """
    Function for calculating the bearing and distance (azimuth) between two points

    :param point_1: coordinates of first point as set(x,y)
    :param point_2: coorindate of second point as set(x,y)
    :return: bearing as int, distance as int
    """
    delta_x = point_2[0] - point_1[0]
    delta_y = point_2[1] - point_1[1]

    print(delta_x, delta_y)

    distance = sqrt(pow(delta_x, 2)+pow(delta_y, 2))

    if delta_x == 0 and delta_y == 0:
        return 0,0
    if delta_x == 0 and delta_y < 0:
        return 0
    if delta_x == 0 and delta_y > 0:
        return 180
    if delta_x < 0 and delta_y == 0:
        return 270
    if delta_x > 0 and delta_y == 0:
        return 90

    if delta_y < 0 < delta_x:
        return degrees(atan((point_2[0] - point_1[0])/-(point_2[1] - point_1[1]))), distance

    elif delta_x > 0 and delta_y > 0:
        return 180 + degrees(atan((point_2[0] - point_1[0])/-(point_2[1] - point_1[1]))), distance

    elif delta_x < 0 < delta_y:
        return 180 + degrees(atan((point_2[0] - point_1[0])/-(point_2[1] - point_1[1]))), distance

    elif delta_x < 0 and delta_y < 0:
        return 360 + degrees(atan((point_2[0] - point_1[0])/-(point_2[1] - point_1[1]))), distance

class Destroyer(object):

    def __init__(self, type, reload_time, hp, window_size):

        """
        Class for the players ship.
        :param type         : Destroyer type. So far only 0 is implemented
        :param reload_time  : reload time between shots in ms
        :param hp           : HP for destroyer
        :param window_size  : window size as x,y
        :type type          : int
        :type reload_time   : int
        :type hp            : int
        :type window_size   : list

        :returns:
        """

        self.__tower_direction = 0
        self.__image = None
        self.__reload_time = None
        self.__hp = hp
        self.__max_hp = hp
        self.__last_shot = None
        self.__window_size = window_size
        self.__shooting_power = 100
        self.__last_shooting_power_check = datetime.datetime.now()

        if type == 0:
            self.__pipe_length = 30

            self.__image = pygame.image.load("./media/warship.png")
            rect = self.__image.get_rect()
            self.__image_size = rect[2], rect[3]

            self.__rect = pygame.Rect(self.__window_size[0]/2 - self.__image_size[0]/2,
                                      self.__window_size[1]/2 - self.__image_size[1]/2,
                                      self.__image_size[0], self.__image_size[1])

            self.__tower_image = pygame.image.load("./media/tower1.png")
            rect = self.__tower_image.get_rect()
            self.__tower_size = rect[2], rect[3]

            self.__tower_rect = pygame.Rect(self.__window_size[0]/2 - self.__tower_size[0]/2,
                                            self.__window_size[1]/2 - self.__tower_size[1]/2,
                                            self.__tower_size[0], self.__tower_size[1])
            self.__pipe = (self.__window_size[0]/2, self.__window_size[1]/2 - 10)

        self.__reload_time = reload_time

    def turn_tower(self, direction, steps):
        if direction == 1:
            if self.__tower_direction >=360:
                self.__tower_direction = self.__tower_direction - 360
            self.__tower_direction += steps

        if direction == 3:
            if self.__tower_direction <= 0:
                self.__tower_direction = self.__tower_direction + 360
            self.__tower_direction -= steps

        self.__pipe = project_point(self.__window_size[0]/2, self.__window_size[1]/2,
                                    self.__tower_direction, self.__pipe_length)

    def set_reload_time(self, time):
        self.__reload_time = time

    def get_reload_time(self):
        return self.__reload_time

    def get_image(self):
        return self.__image, self.__rect

    def get_tower(self):
        return self.__tower_image, self.__tower_rect

    def get_pipe(self):
        return self.__pipe

    def shoot(self, held_in=True):
        if self.__shooting_power < 20:
            return False
        else:
            if self.__last_shot is None:
                self.__last_shot = datetime.datetime.now()
                return True
            else:
                delta = datetime.datetime.now() - self.__last_shot
                if delta.total_seconds()*1000 > self.__reload_time:
                    self.__last_shot = datetime.datetime.now()
                    if self.__shooting_power < 80:
                        self.__shooting_power -= 40
                    else:
                        self.__shooting_power -= 30
                    if self.__shooting_power < 0:
                        self.__shooting_power = 0
                    return True
                else:
                    return False

    def regenerate_power(self):
        """
        Method to regenerate shooting power if drained. Slower regeneration below 20 to give a distadvanatage when
        using permanent fire. Fast regeneration above 50 to not drain too much when using single shots.
        :return:
        """
        new_time = datetime.datetime.now()
        delta = (new_time - self.__last_shooting_power_check).total_seconds()
        if self.__shooting_power > 20:
            self.__shooting_power += 50 * delta
        else:
            self.__shooting_power += 20 * delta
        if self.__shooting_power > 100:
            self.__shooting_power = 100
        self.__last_shooting_power_check = new_time

    def get_shooting_power(self):
        return self.__shooting_power

    def get_direction(self):
        return self.__tower_direction

    def reduce_hp(self, hp):

        """
        Reduced hp by a specified number and returns True if no hp left
        :param hp   : reduce destroyer HP by hp points
        :type hp    : int

        :returns: boolean
        """

        self.__hp -= hp
        if self.__hp <= 0:
            return True
        else:
            return False

    def increase_hp(self, hp):
        if self.__hp + hp > self.__max_hp:
            self.__hp = self.__max_hp
        else:
            self.__hp += hp

    def get_hp(self):
        return self.__hp

    def get_max_hp(self):
        return self.__max_hp

class Enemy(object):

    _param_dict = {
        "hp":None,
        "min_speed":None,
        "max_speed": None,
        "game_speed_multiplier":None,
        "min_dist":None,
        "has_torpedo":None,
        "torpedo_type":None,
        "torpedo_speed":None,
        "torpedo_chance":None,
        "points":None,
        "damage":None,
        "spawn_method":None,
        "fixed_spawn":[(),None]
    }

    def __init__(self, hp, px_per_second, origin, direction):

        """
        Base class for enemy objects. That can be ships as well as for example torpedos.
        :param timer            : timer game instance
        :param hp               : HP of the enemy vessel
        :param px_per_second    : unit movement speed in pixels per second
        :param origin           : origin as x,y
        :param direction        : direction of the vessel, 0=north, 1=east, 2=south, 3=west
        :type hp                : int
        :type px_per_second     : int
        :type origin            : set
        :type direction         : int

        The enemies are initialized by the game instance of the Enemies class by randomizing the type of enemy to be
        spawned, pull the parameter dictionary (param_dict) from that class, randomizing the starting position of
        the boat, the speed and if it has a torpedo. The randomized parameters are then used to initiate the
        instance of the enemy class.

        The parameters in the param_dict dictionary are to be defined as followed:
        "strength" (int)                  : enemy strength points
        "min_speed" (int)                 : minimum unit speed in px/sec
        "max_speed" (int)                 : maximum unit speed int px/sec
        "game_speed_multiplier" (float)   : speed vector multiplication value. 0.1 means 10% faster per game level
        "min_dist" (int)                  : minumum distance from the unit to the destroyer's horizontal center line
        "has_torpedo" (bool)              : defines if the unit shoots torpedos
        "torpedo_type(int)                : torpedo type
        "torpedo_speed(int)               :torpedo speed in px/sec
        "torpedo_chance(float)            : chance of shooting torpedo, between 0.0 and 1.0
        "points (int)                     : points awarded to player when enemy is shot
        "spawn_type" (int)                : sets wether the start point of the ship is randomized (value 0) or defined
                                            by the origin parameter
        "fixed_spawn" (list)              : origin as x,y and direction (0-3). Either the x or y of the origin can be
                                            defined as -1, so the enemy is spawned at the edge of the game window.
                                            Example: [(-1, 50), 3] will give a ship that is spawned on the right outer
                                            limit of the game window at 50 pixels down and go towards west.

        :returns:
        """

        self._hp = hp
        self._position = origin
        self._real_position = origin
        self._direction = direction
        self._px_per_second = px_per_second
        self._direction = direction
        self._image = None
        self._image_size = None
        self._rect = None
        self._has_torpedo = None
        self._torpedo_shot = False

    def get_rect(self):
        rect = pygame.Rect(self._position[0], self._position[1], self._position[0] + self._rect[2], self._position[1] + \
               self._rect[3])
        return rect

    def get_direction(self):
        return self._direction

    def get_position(self):
        return self._position

    def get_center_point(self):
        return self._position[0] + self._image_size[0]/2, self._position[1] + self._image_size[1]/2

    def move(self, time_delta, level=0):

        """
        Method to move the enemy vessel. The movement per cycle is calculated based on the time elapsed since the
        last cycle and the movement speed as pixels per seconds set in the parameter dictionary. The distance is
        also adjusted for the specified game speed multiplier based on the level parameter

        :param level    : game level
        :type level     : int

        """

        vector_delta = time_delta * (self._px_per_second + (self._px_per_second *
                                                     self._param_dict["game_speed_multiplier"] *
                                                     level))

        if self._direction == 0:
            self._real_position = self._real_position[0], self._real_position[1] - vector_delta
            self._rect = pygame.Rect(self._real_position[0] - self._image_size[0]/2, self._real_position[1],
                                     self._image_size[0], self._image_size[1])

        if self._direction == 1:
            self._real_position = self._real_position[0] + vector_delta, self._real_position[1]
            self._rect = pygame.Rect(self._real_position[0], self._real_position[1] - self._image_size[1]/2,
                                     self._image_size[0], self._image_size[1])

        if self._direction == 2:
            self._real_position = self._real_position[0], self._real_position[1] + vector_delta
            self._rect = pygame.Rect(self._real_position[0] - self._image_size[0]/2, self._real_position[1],
                                     self._image_size[0], self._image_size[1])

        if self._direction == 3:
            self._real_position = self._real_position[0] - vector_delta, self._real_position[1]
            self._rect = pygame.Rect(self._real_position[0], self._real_position[1] - self._image_size[1]/2,
                                     self._image_size[0], self._image_size[1])

        self._position = int(round(self._real_position[0],0)), int(round(self._real_position[1],0))

    def get_image(self):
        return self._image, self._rect

    def has_torpedo(self):

        """
        Method to check if the instance of the enemy vessel has a torpedo. When run for the first time, a torpedo
        might be attached based on the chance of the enemy boat being equipped with a torpedo specified in the
        parameter dictionary. When called afterwards, it returns if a torpedo is attached or not.

        :returns: boolean
        """

        if self._param_dict["has_torpedo"]:
            if self._has_torpedo is None:
                chance = self._param_dict["torpedo_chance"]*10
                rand = randrange(1,10,1)
                if rand <= chance:
                    self._has_torpedo = True
                    return True
                else:
                    self._has_torpedo = False
                    return False
            else:
                if self._has_torpedo:
                    return True
                else:
                    return False

        else:
            return False

    def set_torpedo_shot(self):
        self._torpedo_shot = True

    def get_torpedo_shot(self):
        return self._torpedo_shot

    def reduce_hp(self, hp):

        """
        Reduced hp by a specified number and returns True if no hp left
        :param hp   : hp
        :type hp    : int

        :returns: integer
        """

        self._hp -= hp
        if self._hp <= 0:
            return True
        else:
            return False

    def get_hp(self):
        return self._hp

    def set_ship_param(self, param, value):
        try:
            self._param_dict[param] = value
        except:
            return 1


class Submarine(Enemy):

    param_dict = {
        "hp":200,
        "min_speed":60,
        "max_speed":80,
        "game_speed_multiplier":0.1,
        "min_dist":100,
        "has_torpedo":True,
        "torpedo_type":1,
        "torpedo_speed":30,
        "torpedo_chance":0.6,
        "points":100,
        "damage":None,
        "spawn_method":0,
        "fixed_spawn":[(),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over parameter dict to parent
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/submarine.png")
        if self._direction == 1:
            self._image = pygame.transform.rotate(self._image, 180)

        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict


class Torpedoboat(Enemy):

    param_dict = {
        "hp":100,
        "min_speed":120,
        "max_speed":150,
        "game_speed_multiplier":0.1,
        "min_dist":100,
        "has_torpedo":True,
        "torpedo_type":0,
        "torpedo_speed":0,
        "torpedo_chance":0.4,
        "points":100,
        "damage":None,
        "spawn_method":0,
        "fixed_spawn":[(),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over parameter dict to parent
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/torpedoboat.png")
        if self._direction == 1:
            self._image = pygame.transform.rotate(self._image, 180)
        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict


class Torpedoboat2(Enemy):

    param_dict = {
        "hp":100,
        "min_speed":140,
        "max_speed":160,
        "game_speed_multiplier":0.1,
        "min_dist":100,
        "has_torpedo":True,
        "torpedo_type":2,
        "torpedo_speed":0,
        "torpedo_chance":0.4,
        "points":100,
        "damage":None,
        "spawn_method":0,
        "fixed_spawn":[(),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over parameter dict to parent
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/torpedoboat2.png")
        if self._direction == 1:
            self._image = pygame.transform.rotate(self._image, 180)
        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict

class Torpedo_0(Enemy):

    param_dict = {
        "hp":100,
        "min_speed":80,
        "max_speed":80,
        "game_speed_multiplier":0.1,
        "min_dist":100,
        "has_torpedo":False,
        "torpedo_type":0,
        "torpedo_speed":0,
        "torpedo_chance":0,
        "points":300,
        "damage":50,
        "spawn_method":0,
        "fixed_spawn":[(),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over the parameter dict to the parent class
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/torpedo1.png")
        if self._direction == 0:
            self._image = pygame.transform.rotate(self._image, 180)
        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict

    def get_damage(self):
        return self._param_dict["damage"]


class Torpedo_2(Enemy):

    param_dict = {
        "hp":100,
        "min_speed":60,
        "max_speed":60,
        "game_speed_multiplier":0,
        "min_dist":100,
        "has_torpedo":False,
        "torpedo_type":0,
        "torpedo_speed":0,
        "torpedo_chance":0,
        "points":300,
        "damage":100,
        "spawn_method":None,
        "fixed_spawn":[(),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over the parameter dict to the parent class
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/torpedo2.png")
        if self._direction == 0:
            self._image = pygame.transform.rotate(self._image, 180)
        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict

    def get_damage(self):
        return self._param_dict["damage"]


class Torpedo_1(Enemy):

    param_dict = {
        "hp":100,
        "min_speed":60,
        "max_speed":60,
        "game_speed_multiplier":0,
        "min_dist":100,
        "has_torpedo":False,
        "torpedo_type":0,
        "torpedo_speed":0,
        "torpedo_chance":0,
        "points":300,
        "damage":100,
        "spawn_method":None,
        "fixed_spawn":[(),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over the parameter dict to the parent class
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/torpedo1.png")
        if self._direction == 0:
            self._image = pygame.transform.rotate(self._image, 180)
        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict

    def get_damage(self):
        return self._param_dict["damage"]

class Rowing_boat(Enemy):

    param_dict = {
        "hp":100,
        "min_speed":30,
        "max_speed":50,
        "game_speed_multiplier":0.1,
        "min_dist":100,
        "has_torpedo":False,
        "torpedo_type":0,
        "torpedo_speed":0,
        "torpedo_chance":0,
        "points":300,
        "damage":50,
        "spawn_method":1,
        "fixed_spawn":[(-1,0),None]
    }

    def __init__(self, px_per_second, origin, direction):

        Enemy.__init__(self, self.param_dict["hp"], px_per_second, origin, direction)

        #Handing over the parameter dict to the parent class
        self._param_dict = self.param_dict

        #Setting image related parameters
        self._image = pygame.image.load("./media/torpedo1.png")
        rect = self._image.get_rect()
        self._image_size = rect[2], rect[3]
        self._rect = pygame.Rect(self._position[0], self._position[1]-self._image_size[1]/2,
                                 self._image_size[0], self._image_size[1])

    @classmethod
    def get_params(cls):
        return cls.param_dict

    def get_damage(self):
        return self._param_dict["damage"]


class Bullet(object):

    def __init__(self, timer, type, power, origin, direction, px_per_second):

        """
        Base class for bullets.
        :param timer        : game timer instance
        :param type         : bullet type
        :param power        : damage done to the enemy on bullet impact
        :param origin       : bullet origin as x,y. Usually the center of the game window
        :param direction    : direction of the bullet as bearing, between 0 and 360 (north)
        :param px_per_second: bullet speed as pixels per second
        :type type          : int
        :type power         : int
        :type origin        : set
        :type direction     : int
        :type px_per_second : int

        :returns:
        """
        self.__timer = timer
        self.__type = type
        self.__power = power
        self.__position = list(origin)
        self.__direction = direction
        self.__old_time = datetime.datetime.now()
        self.__px_per_second = px_per_second
        self.__original_time = datetime.datetime.now()
        self.__image = None

        if type == 0:
            self.__image = pygame.image.load("./media/bullet1.png")

        self.__image = pygame.transform.rotate(self.__image, - self.__direction)
        rect = self.__image.get_rect()
        self.__image_size = rect[2], rect[3]

        self.__rect = pygame.Rect(self.__position[0]-self.__image_size[0]/2, self.__position[1] - self.__image_size[1]/2,
                                  self.__image_size[0], self.__image_size[1])

    def move(self):

        """
        Method for bullet movement. The movement distance is calculated by the elapsed time since the last call
        and the speed as defined at instance creation.

        :returns:
        """

        time_delta = self.__timer.get_delta()
        vector_delta = floor(time_delta * self.__px_per_second)

        self.__position = project_point(self.__position[0], self.__position[1], self.__direction, vector_delta)

        self.__rect = pygame.Rect(self.__position[0]-self.__image_size[0]/2, self.__position[1] - self.__image_size[1]/2,
                                  self.__image_size[0], self.__image_size[1])

    def get_position(self):
        return [int(floor(self.__position[0])), int(floor(self.__position[1]))]

    def __del__(self):
        pass

    def get_image(self):
        return self.__image, self.__rect

    def get_power(self):
        return self.__power

class Crate(object):
    def __init__(self, origin, return_points, crate_type, effect_points=100):

        """
        Crate class. The instance is initialted from the Crates class game instance. The parameters are randomized
        and the position checked for collisions with other objects.

        :param origin           : origin as x,y
        :param return_points    : points awarded to the player if the crate is destroyed
        :param crate_type       : the type of crate. Different types can potentially have different images etc. What
                                  happens when a crate of a type is shot is specified in the Destroyer_logic class
        :param effect_points    : points for the effect that the destruction of the crate has. The effect is defined
                                  in the Destroyer_logic class and can for example be health points.
        :type origin            : set
        :type return_points     : int
        :type crate_type        : int
        :type effect_points     : int

        :returns:
        """

        self._origin = origin
        self._return_points = return_points
        self._image = pygame.image.load("./media/crate.png")
        self._rect = pygame.Rect(origin[0], origin[1], self._image.get_rect()[2], self._image.get_rect()[3])
        self._type = crate_type
        self._create_time = datetime.datetime.now()
        self._effect_points = effect_points

    def get_image(self):
        return self._image, self._rect

    def get_type(self):
        return self._type

    def get_age(self):

        """
        Returns the age of the crate in seconds. Used to check wether the instance of a crate has exceeded the
        best before date and is ready for the trash bin...

        :returns: integer
        """

        return (datetime.datetime.now() -  self._create_time).total_seconds()

    def get_rect(self):
        return self._rect

    def get_points(self):
        return self._return_points

    def get_effect_points(self):
        return self._effect_points

    @classmethod
    def get_size(self):
        image = pygame.image.load("./media/crate.png")
        rect = image.get_rect()
        return rect[2], rect[3]

