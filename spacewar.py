#!/usr/bin/python
# [SublimeLinter flake8-max-line-length:1000]
# This comment is just so Sublime Text quits complaining about overly long
# lines. I may remove it later, when I refactor the code.
from __future__ import print_function, division

import pygame
import pygame.gfxdraw

import sys
import os
import math
import random
import yaml
import glob

# This somewhat-hackish import changes YAML's behavior just by being imported;
# to stop flake8 from complaining about the unused import, I've added the
# "noqa" tag.
import yaml_modifier    # noqa

if sys.version_info[0] < 3:
    import ConfigParser as configparser
else:
    import configparser

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

pygame.mixer.pre_init(44100, buffer=1024)

SCREEN_SIZE = 160, 160
FULLSCREEN = False
PIXEL_PERFECT = False
BITBOX = pygame.mask.Mask((9, 9))
BITBOX.fill()

FOREGROUND = (0,   0,   0)
BACKGROUND = (255, 255, 255)

SENTRY_INVALID = ((1, 11), (2, 10), (3, 10), (3, 9), (4, 8), (5, 8), (6, 7), (7, 7), (7, 6), (8, 6), (8, 5), (9, 5), (10, 4), (11, 4), (12, 3), (12, 2), (13, 2), (14, 1))

RANKS = (
    "cadet",
    "ensign",
    "lieutenant jg",
    "lieutenant",
    "commander",
    "captain",
    "commodore",
    "rear admiral",
    "vice admiral",
    "admiral",
    "fleet admiral",
)

XP_VALUES = [1500, 5000, 12000, 25000]
# Pad the XP_VALUES until we have enough for every rank (except the final one).
while len(XP_VALUES) < len(RANKS) - 1:
    i = len(XP_VALUES) - 3
    XP_VALUES.append(25000*i**2 - 25000*i + 50000)
# Alternatively, if our list of ranks is very short for some reason...
while len(XP_VALUES) >= len(RANKS):
    XP_VALUES.pop()

RANK_XP = OrderedDict(zip(RANKS, XP_VALUES))

RANK_PROMOTE = OrderedDict()

for i, rank in enumerate(RANKS[:-1]):
    RANK_PROMOTE[rank] = RANKS[i+1]

STATS = {
    "shields": {
        "min": 100,
        "max": 360,
        "step": 10,
    },
    "phasers": {
        "min": 20,
        "max": 100,
        "step": 5,
    },
    "torpedo": {
        "min": 30,
        "max": 120,
        "step": 5,
    },
    "engine": {
        "min": 5,
        "max": 10,
        "step": 1,
    },
}

THEME = None
races = ()

SOUND_LIST = {}


def playsound(sound):
    if not SOUND_ENABLED:
        return
    elif not sound in SOUND_LIST:
        paths = (os.path.join(SOUND_FOLDER, sound+'.wav'), os.path.join('data', sound+'.wav'), sound+'.wav')
        for path in paths:
            if os.path.exists(path):
                break
        else:
            print('Unable to find {0!r}, {1!r}, or {2!r}.'.format(*paths))
            path = None
        if path:
            SOUND_LIST[sound] = pygame.mixer.Sound(path)
    if sound in SOUND_LIST:
        SOUND_LIST[sound].set_volume(SOUND_VOLUME / 100)
        SOUND_LIST[sound].play()

pygame.init()

WINDOW_SIZE = pygame.display.Info()
WINDOW_SIZE = WINDOW_SIZE.current_w, WINDOW_SIZE.current_h
if WINDOW_SIZE == (800, 480):
    FULLSCREEN = True
WINDOW_MULTIPLIER = min((WINDOW_SIZE[0] - (0 if FULLSCREEN else 20)) // 160, (WINDOW_SIZE[1] - (0 if FULLSCREEN else 20)) // 160)

INI_DEFAULTS = OrderedDict((
    ('Window', OrderedDict((
        ('Caption', 'SpaceWar'),
        ('Icon', os.path.join('data', 'icon.png')),
    ))),
    ('Data Files', OrderedDict((
        ('Sound folder', os.path.join('data', 'sound')),
        ('Theme folder', os.path.join('data', 'themes')),
        ('Character folder', os.path.join('data', 'saves')),
        ('Localization file', os.path.join('data', 'English.txt')),
        ('Settings file', 'settings.cfg'),
    ))),
))

SETTINGS_DEFAULTS = OrderedDict((
    ('Window', OrderedDict((
        ('Scaling multiplier', repr(WINDOW_MULTIPLIER)),
        ('Fullscreen', repr(FULLSCREEN)),
        ('Font size', '16' if WINDOW_MULTIPLIER > 4 else '12'),
    ))),
    ('Audio', OrderedDict((
        ('Sound enabled', 'True'),
        ('Sound volume', '100'),
    ))),
    ('Gameplay', OrderedDict((
        ('Classic collisions', 'True'),
        ('White-on-black', 'False'),
    ))),
))

INI_FILE = 'spacewar.ini'

CONFIG = configparser.SafeConfigParser(dict_type=OrderedDict)
CONFIG.read_dict(INI_DEFAULTS)

if os.path.exists(INI_FILE):
    CONFIG.read(INI_FILE)
else:
    with open(INI_FILE, "w") as f:
        CONFIG.write(f)

WINDOW_CAPTION = CONFIG.get('Window', 'Caption')
ICON_FILE = CONFIG.get('Window', 'Icon')
SOUND_FOLDER = CONFIG.get('Data Files', 'Sound folder')
THEME_FOLDER = CONFIG.get('Data Files', 'Theme folder')
SAVE_FOLDER = CONFIG.get('Data Files', 'Character folder')
TEXT_FILE = CONFIG.get('Data Files', 'Localization file')
SETTINGS_FILE = CONFIG.get('Data Files', 'Settings file')

SETTINGS = configparser.SafeConfigParser(dict_type=OrderedDict)
SETTINGS.read_dict(SETTINGS_DEFAULTS)

if os.path.exists(SETTINGS_FILE):
    SETTINGS.read(SETTINGS_FILE)
else:
    with open(SETTINGS_FILE, "w") as f:
        SETTINGS.write(f)

WINDOW_MULTIPLIER = SETTINGS.getint('Window', 'Scaling multiplier')
FULLSCREEN = SETTINGS.getboolean('Window', 'Fullscreen')
FONT_SIZE = SETTINGS.getint('Window', 'Font size')
SOUND_ENABLED = SETTINGS.getboolean('Audio', 'Sound enabled')
SOUND_VOLUME = SETTINGS.getint('Audio', 'Sound volume')
PIXEL_PERFECT = SETTINGS.getboolean('Gameplay', 'Classic collisions')
if SETTINGS.getboolean('Gameplay', 'White-on-black'):
    FOREGROUND = (255, 255, 255)
    BACKGROUND = (0,   0,   0)

WINDOW_SIZE = SCREEN_SIZE[0] * WINDOW_MULTIPLIER, SCREEN_SIZE[1] * WINDOW_MULTIPLIER

IMAGE_LIST = {}


def load_image(name, colorkey=None):
    if isinstance(name, pygame.Surface):
        return name
    elif isinstance(name, tuple):
        name, colorkey = name
    if name not in IMAGE_LIST:
        if not os.path.exists(name):
            raise Exception("Image file {0!r} not found.".format(name))
        image = pygame.image.load(name)
        if colorkey or not image.get_flags() & pygame.SRCALPHA:
            image = image.convert()
            if colorkey:
                image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        IMAGE_LIST[name] = image
    return IMAGE_LIST[name]

TEXT_LIST = {}


class TextFileError(Exception):
    pass


def load_text(tag):
    alternate = None
    if THEME:
        alternate = os.path.join(THEME_FOLDER, THEME, os.path.basename(TEXT_FILE))
        if alternate in TEXT_LIST and tag in TEXT_LIST[alternate]:
            return load_text_from(tag, alternate)
    for file in TEXT_LIST:
        if tag in TEXT_LIST[file]:
            return load_text_from(tag, file)
    try:
        return load_text_from(tag)
    except TextFileError as orig:
        if THEME:
            if os.path.exists(alternate):
                try:
                    return load_text_from(tag, alternate)
                except TextFileError:
                    pass
        for name in glob.glob(os.path.join(THEME_FOLDER, "*", os.path.basename(TEXT_FILE))):
            if name == alternate:
                pass
            elif os.path.exists(name):
                try:
                    return load_text_from(tag, name)
                except TextFileError:
                    pass
        raise orig


def load_text_from(tag, file=TEXT_FILE):
    tag = tag.lower()
    if file in TEXT_LIST and tag in TEXT_LIST[file]:
        text = TEXT_LIST[file][tag]
    else:
        if not file in TEXT_LIST:
            TEXT_LIST[file] = {}
        kw = {}
        if sys.version_info[0] >= 3:
            kw['encoding'] = "utf8"
        with open(file, "r", **kw) as f:
            result = ""
            found = None
            for i, line in enumerate(f):
                line = line.strip("\r\n")
                if sys.version_info[0] < 3:
                    line = line.decode("utf8")
                if line.startswith("<"):
                    temp = line[1:line.index(">")]
                    if found:
                        TEXT_LIST[file][found] = result[1:]
                    found = temp.lower()
                    result = ""
                elif found:
                    result += "\n" + line
            else:
                TEXT_LIST[file][found] = result[1:]
        if not tag in TEXT_LIST[file]:
            raise TextFileError("Text tag {0!r} not found in text file {1!r}.".format(tag, file))
        text = TEXT_LIST[file][tag]
    final = ""
    checks = text.split(">")
    final += checks[0]
    for segment in checks[1:]:
        if not "<" in segment:
            final += ">"
        else:
            tag, segment = segment.split("<", 1)
            final += load_text(tag)
        final += segment
    return final

themes = OrderedDict()

for name in glob.glob(os.path.join(THEME_FOLDER, "*", "theme")):
    data = {}
    with open(name, "r") as f:
        data = yaml.safe_load(f)
    for race in data["Races"]:
        file = os.path.join(os.path.split(name)[0], data["Races"][race])
        racedat = {}
        with open(file, "r") as f:
            racedat = yaml.safe_load(f)
        if not "phasers" in racedat:
            racedat["phasers"] = data["phasers"]
        if not "torpedo" in racedat:
            racedat["torpedo"] = data["torpedo"]
        racedat["folder"] = os.path.split(file)[0]
        data["Races"][race] = racedat
    sentry = data["Special"].get("sentry", None)
    if sentry:
        file = os.path.join(os.path.split(name)[0], sentry)
        sentry = {}
        with open(file, "r") as f:
            sentry = yaml.safe_load(f)
        if not "phasers" in sentry:
            sentry["phasers"] = data["phasers"]
        if not "torpedo" in sentry:
            sentry["torpedo"] = data["torpedo"]
        sentry["folder"] = os.path.split(file)[0]
        data["Special"]["sentry"] = sentry
    themes[os.path.basename(os.path.split(name)[0])] = data

ships = {}


def load_ship_graphics():
    for race in races:
        data = themes[THEME]["Races"][race]
        image, folder, colorkey = data["image"], data["folder"], data["colorkey"]
        ships[race] = load_image(os.path.join(folder, image), colorkey)
        if "cloaked" in data:
            ships["cloaked-"+race] = load_image(os.path.join(folder, data["cloaked"]), colorkey)
    data = themes[THEME]["Special"]["sentry"]
    image, folder, colorkey = data["image"], data["folder"], data["colorkey"]
    ships["sentry"] = load_image(os.path.join(folder, image), colorkey)

if FULLSCREEN:
    display = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
else:
    display = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_icon(load_image(ICON_FILE))
pygame.display.set_caption(WINDOW_CAPTION)
clock = pygame.time.Clock()
pygame.key.set_repeat(300, 30)

screen = pygame.Surface((160, 160))

hex = pygame.Surface((15, 15))
hex.fill(BACKGROUND)
hex.set_colorkey(BACKGROUND)
for pt in ((7, 0), (6, 1), (5, 1), (4, 2), (3, 2), (2, 3), (1, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, 11), (2, 11), (3, 12), (4, 12), (5, 13), (6, 13), (7, 14), (8, 13), (9, 13), (10, 12), (11, 12), (12, 11), (13, 11), (14, 10), (14, 9), (14, 8), (14, 7), (14, 6), (14, 5), (14, 4), (13, 3), (12, 3), (11, 2), (10, 2), (9, 1), (8, 1)):
    hex.set_at(pt, FOREGROUND)

select = pygame.Surface((11, 11))
select.fill(BACKGROUND)
select.set_colorkey(BACKGROUND)
invalid = pygame.Surface((11, 11))
invalid.fill(BACKGROUND)
invalid.set_colorkey(BACKGROUND)
for pt in ((5, 0), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (5, 10)):
    select.set_at(pt, (99, 255, 156))
    invalid.set_at(pt, (206, 207, 156))

screen.fill(BACKGROUND)
for row in range(14):
    for column in range(10 if row % 2 else 11):
        screen.blit(hex, (2 + 14*column + (row % 2)*7, 15+10*row))

#for row in range(14):
#    for column in range(10 if row % 2 else 11):
#        pygame.draw.rect(screen, (0, 0, 255), (2 + 14*column + (row%2)*7, 17+10*row, 14, 10), 1)

background = screen.copy()


def hex_to_coords(row, column):
    return (14*column + ((row-1) % 2)*7 - 9, 8+10*row)


def coords_to_hex(pos):
    if pos[0] < 2 or pos[1] < 17 or pos[0] > 155 or pos[1] > 156:
        return None
    elif pos[0] < 9 and (pos[1] - 17) % 20 >= 10:
        return None
    elif (pos[1] - 17) % 20 < 10:
        return (pos[1] - 17) // 10 + 1, (pos[0] - 2) // 14 + 1
    else:
        return (pos[1] - 17) // 10 + 1, (pos[0] - 9) // 14 + 1


def hex_distance(hex1, hex2):
    hex1 = hex1[0], hex1[1] - (hex1[0] + 1) // 2
    hex1 += 0 - hex1[0] - hex1[1],
    hex2 = hex2[0], hex2[1] - (hex2[0] + 1) // 2
    hex2 += 0 - hex2[0] - hex2[1],
    return max(abs(hex1[0] - hex2[0]), abs(hex1[1] - hex2[1]), abs(hex1[2] - hex2[2]))


class Ship(object):
    def __init__(self, type, pos, angle, rank, captain, name, shields, phasers, torpedoes, engine, human=False):
        self.type = type
        self.image = pygame.transform.rotate(ships[type], angle)
        if type == "sentry":
            self.specials = themes[THEME]["Special"][type]["specials"]
        else:
            self.specials = themes[THEME]["Races"][type]["specials"]
        self.pos = pos
        self.angle = angle
        self.rank = rank
        self.captain = captain
        self.name = name
        self.shields = shields
        self.max_shields = shields
        self.phasers = phasers
        self.torpedoes = torpedoes
        self.engine = engine
        self.human = human
        self.speed = 2
        self.cloaked = False
        self.action = None
        self.target = None
        self.movement = None
        self.shot_recently = 0
        self.explode = 0
        self.regen = 0
        self.move_target = None
        self.teleport_target = None

    def render(self, screen):
        if self.explode:
            pygame.gfxdraw.filled_circle(screen, self.pos[0]+4, self.pos[1]+4, -self.explode, (255, 127, 0))
        else:
            screen.blit(self.image, self.pos)

    def move(self, pos, time):
        self.pos = (pos[0] - self.pos[0]) / time + self.pos[0], (pos[1] - self.pos[1]) / time + self.pos[1]
        if time == 1:
            self.pos = int(self.pos[0]), int(self.pos[1])

    def cloak(self, enabled=True):
        self.cloaked = enabled
        self.rotate(self.angle)

    def shot(self, amount):
        if self.cloaked:
            amount *= 2
        if "ablative" in self.specials and not self.action:
            amount = amount // 2
        self.shields -= amount
        self.shot_recently = 5

    def rotate(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(ships["cloaked-"+self.type if self.cloaked else self.type], angle)

    def get_valid_destination(self, row, column, attacking):
        hex = coords_to_hex(self.pos)
        dist = hex_distance(hex, (row, column))
        if dist >= self.speed - (4 if ("acceleration" in self.specials and not attacking) else 2) and dist <= self.speed + (4 if ("acceleration" in self.specials and not attacking) else 2) and dist <= self.engine:
            return True
        else:
            return False

    @property
    def mask(self):
        return (pygame.mask.from_surface(self.image) if PIXEL_PERFECT else BITBOX)


class Infobox(object):
    def __init__(self, target, font):
        self.target = target
        self.font = font
        if self.target.type == "sentry":
            self.surfaces = [self.font.render(self.target.name, True, FOREGROUND), self.font.render(load_text("shield-prefix")+repr(self.target.shields), True, FOREGROUND)]
        else:
            self.surfaces = [self.font.render(load_text("rank-"+self.target.rank), True, FOREGROUND), self.font.render(self.target.captain, True, FOREGROUND), self.font.render(self.target.name, True, FOREGROUND), self.font.render(load_text("shield-prefix")+repr(self.target.shields), True, FOREGROUND), self.font.render(load_text("speed-prefix")+repr(self.target.speed), True, FOREGROUND)]
        width = 0
        height = 0
        for surface in self.surfaces:
            if surface.get_width() > width:
                width = surface.get_width()
            height += surface.get_height()
        width += 4
        height += 4
        self.image = pygame.Surface((width, height))
        self.image.fill(BACKGROUND)
        pygame.draw.rect(self.image, FOREGROUND, self.image.get_rect(), 1)
        self.rect = pygame.Rect(self.target.pos[0] + 10, self.target.pos[1], width, height)

    def update(self):
        if self.target.type == "sentry":
            self.surfaces = [self.font.render(self.target.name, True, FOREGROUND), self.font.render(load_text("shield-prefix")+repr(self.target.shields), True, FOREGROUND)]
        else:
            self.surfaces = [self.font.render(load_text("rank-"+self.target.rank), True, FOREGROUND), self.font.render(self.target.captain, True, FOREGROUND), self.font.render(self.target.name, True, FOREGROUND), self.font.render(load_text("shield-prefix")+repr(self.target.shields), True, FOREGROUND), self.font.render(load_text("speed-prefix")+repr(self.target.speed), True, FOREGROUND)]
        self.rect.topleft = self.target.pos
        self.rect.left += 10

    def render(self, screen):
        screen.blit(self.image, self.rect)
        height = 2
        for surface in self.surfaces:
            screen.blit(surface, (self.rect.left + 2, self.rect.top + height))
            height += surface.get_height()


def wordwrap_render(text, font, width):
    surfaces = []
    text = text.split("\n")
    line = 0
    final_width = 0
    final_height = 0
    while line < len(text):
        center = False
        temp = text[line]
        if temp.startswith("$"):
            center = True
            temp = temp[1:]
        elif temp.startswith("\$"):
            temp = temp[1:]
        temp_words = temp.split(" ")
        result = 1
        cur = " ".join(temp_words[:result])
        while "\t" in cur:
            idx = cur.index("\t")
            spaces = " " * (8 - idx % 8)
            cur = spaces.join(cur.partition("\t")[::2])
        temp_surf = font.render(cur, True, FOREGROUND)
        while temp_surf.get_width() < width and result < len(temp_words):
            result += 1
            cur = " ".join(temp_words[:result])
            while "\t" in cur:
                idx = cur.index("\t")
                spaces = " " * (8 - idx % 8)
                cur = spaces.join(cur.partition("\t")[::2])
            temp_surf = font.render(cur, True, FOREGROUND)
        if temp_surf.get_width() >= width:
            result -= 1
            cur = " ".join(temp_words[:result])
            while "\t" in cur:
                idx = cur.index("\t")
                spaces = " " * (8 - idx % 8)
                cur = spaces.join(cur.partition("\t")[::2])
            temp_surf = font.render(cur, True, FOREGROUND)
            text.insert(line+1, ("$" if center else "") + " ".join(temp_words[result:]))
        surfaces.append((temp_surf, center))
        if temp_surf.get_width() > final_width:
            final_width = temp_surf.get_width()
        final_height += temp_surf.get_height()
        line += 1
    final_surf = pygame.Surface((final_width, final_height))
    final_surf.fill(BACKGROUND)
    final_surf.set_colorkey(BACKGROUND)
    y = 0
    for surf, center in surfaces:
        if center:
            rect = surf.get_rect()
            rect.top = y
            rect.centerx = final_width // 2
            final_surf.blit(surf, rect)
        else:
            final_surf.blit(surf, (0, y))
        y += surf.get_height()
    return final_surf


class Messagebox(object):
    def __init__(self, text, font):
        self.font = font
        self.text = wordwrap_render(text, self.font, display.get_width() - 4)
        self.image = pygame.Surface((self.text.get_width() + 4, self.text.get_height() + 4))
        self.image.fill(BACKGROUND)
        pygame.draw.rect(self.image, FOREGROUND, (0, 0, self.image.get_width(), self.image.get_height()), 1)

    def render(self, screen):
        rect = self.image.get_rect()
        rect.centery = screen.get_height() // 2
        rect.centerx = screen.get_width() // 2
        screen.blit(self.image, rect)
        screen.blit(self.text, (rect.left + 2, rect.top + 2))


class Torpedo(object):
    def __init__(self, pos, target, firer, power, color):
        self.rect = pygame.Rect(0, 0, 3, 3)
        self.rect.center = pos
        self.pos = pos
        delta = target[0] - pos[0], target[1] - pos[1]
        if abs(delta[0]) <= 0.01 and abs(delta[1]) <= 0.01:
            self.dx, self.dy = 3.0, 0.0
        else:
            dist = math.hypot(*delta)
            self.dx, self.dy = (delta[0] / dist) * 3, (delta[1] / dist) * 3
        self.firer = firer
        self.power = power
        self.color = color
        self.mask = pygame.mask.Mask((3, 3))
        self.mask.fill()
        self.active = True

    def update(self):
        if self.active:
            self.pos = self.pos[0] + self.dx, self.pos[1] + self.dy
            self.rect.center = self.pos
            for target in ship_list:
                if target == self.firer:
                    continue
                tmask = target.mask
                offset = (int(self.rect.left - target.pos[0]), int(self.rect.top - target.pos[1]))
                if tmask.overlap(self.mask, offset):
                    playsound("hit")
                    if self.firer == player:
                        match_stats[player]["torpedoes hit"] += 1
                    before = target.shields
                    target.shot(self.power)
                    if self.firer == player and target.shields < 0 and before >= 0:
                        match_stats[player]["kills-"+target.type] += 1
                    damage = before - target.shields
                    if team_game and self.firer.type == target.type:
                        match_stats[self.firer]["teamdamage"] -= damage
                    else:
                        match_stats[self.firer]["damage"] += damage
                    self.blam()
                    break
            else:
                for torpedo in torpedo_list:
                    if torpedo == self:
                        continue
                    if self.rect.colliderect(torpedo.rect):
                        playsound("hit")
                        torpedo.blam()
                        self.blam()
                        break
                else:
                    if self.rect.bottom < 17 or self.rect.top > 159 or self.rect.right < 2 or self.rect.left > 157:
                        self.blam()

    def render(self, screen):
        screen.fill(self.color, self.rect)

    def blam(self):
        if self in torpedo_list:
            torpedo_list.remove(self)
        self.active = False


def render_button(text, font):
    text = font.render(text, True, FOREGROUND)
    frame = pygame.Surface((text.get_width() + 4, text.get_height() + 4))
    rect = frame.get_rect()
    frame.fill(BACKGROUND)
    pygame.draw.rect(frame, FOREGROUND, rect, 1)
    frame.blit(text, (2, 2))
    return frame, rect


class SelectionButton(object):
    def __init__(self, text, callback):
        self.image, self.rect = render_button(text, infofont)
        self.callback = callback

    def render(self, screen):
        screen.blit(self.image, self.rect)


class SelectionList(object):
    def __init__(self, title, *buttons):
        self.title = wordwrap_render(title, infofont, display.get_width() - 4)
        self.title_rect = self.title.get_rect()
        self.buttons = [SelectionButton(text, callback) for text, callback in buttons]
        height = self.title_rect.height
        width = self.title_rect.width
        for button in self:
            height += button.rect.height + 2
            if button.rect.width > width:
                width = button.rect.width
        self.frame = pygame.Surface((width+4, height+4))
        self.frame.fill(BACKGROUND)
        self.rect = self.frame.get_rect()
        pygame.draw.rect(self.frame, FOREGROUND, self.rect, 1)

    def __iter__(self):
        return iter(self.buttons)

    def render(self, screen):
        self.rect.center = screen.get_width() // 2, screen.get_height() // 2
        self.title_rect.top = self.rect.top + 2
        self.title_rect.centerx = self.rect.centerx
        screen.blit(self.frame, self.rect)
        screen.blit(self.title, self.title_rect)
        y = self.title_rect.bottom + 2
        for button in self:
            button.rect.top = y
            button.rect.centerx = self.rect.centerx
            button.render(screen)
            y += button.rect.height + 2


class TextEntry(object):
    def __init__(self, prompt, start, callback):
        self.prompt = infofont.render(prompt, True, FOREGROUND)
        self.text = start
        self.start = start
        self.callback = callback

    def update(self):
        self.image = infofont.render(self.text + "_", True, FOREGROUND)
        self.frame = pygame.Surface((max(self.prompt.get_width(), self.image.get_width()) + 4, self.prompt.get_height() + self.image.get_height() + 8))
        self.rect = self.frame.get_rect()
        self.frame.fill(BACKGROUND)
        pygame.draw.rect(self.frame, FOREGROUND, self.rect, 1)
        self.rect.center = display.get_width() // 2, display.get_height() // 2

    def render(self):
        display.blit(self.frame, self.rect)
        rect = self.prompt.get_rect()
        rect.top = self.rect.top + 2
        rect.centerx = self.rect.centerx
        display.blit(self.prompt, rect)
        rect = self.image.get_rect()
        rect.bottom = self.rect.bottom - 2
        rect.centerx = self.rect.centerx
        display.blit(self.image, rect)


class CommandBox(object):
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.movement_info = self.font.render(load_text("move to") + "(XX, XX)", True, FOREGROUND)
        longest = 0, None
        for tag in ("do nothing", "fire-phaser", "fire-torpedo", "self-destruct"):
            if len(load_text(tag)) > longest[0]:
                longest = len(load_text(tag)), tag
        self.action_info = self.font.render(load_text("action-prefix") + load_text(longest[1]) + "(XX, XX)", True, FOREGROUND)
        self.action_info_rect = self.action_info.get_rect()
        self.okay_button, self.okay_button_rect = render_button(load_text("button-okay"), self.font)
        self.cancel_button, self.cancel_button_rect = render_button(load_text("button-cancel"), self.font)
        self.move_button, self.move_button_rect = render_button(load_text("button-destination"), self.font)
        self.act_button, self.act_button_rect = render_button(load_text("button-target"), self.font)
        self.frame = pygame.Surface((max(self.movement_info.get_width() + self.move_button.get_width() + 4, self.action_info.get_width() + self.act_button.get_width() + 4, self.screen.get_width() // 2), self.movement_info.get_height() + self.action_info.get_height() + max(self.okay_button_rect.height, self.cancel_button_rect.height) + 16))
        self.frame.fill(BACKGROUND)
        self.rect = pygame.Rect(0, 0, self.frame.get_width(), self.frame.get_height())
        pygame.draw.rect(self.frame, FOREGROUND, self.rect, 1)
        self.rect.bottom = (self.screen.get_height() * 3) // 4
        self.rect.centerx = self.screen.get_width() // 2
        self.okay_button_rect.bottom = self.rect.bottom - 2
        self.cancel_button_rect.right = self.rect.right - 3
        self.cancel_button_rect.bottom = self.okay_button_rect.bottom
        self.okay_button_rect.right = self.cancel_button_rect.left - 3
        self.action_info_rect.topleft = (self.rect.left + 2, self.rect.top + 10 + self.movement_info.get_height())
        self.move_button_rect.centery = self.rect.top + 4 + self.movement_info.get_height() // 2
        self.move_button_rect.right = self.rect.right - 3
        self.act_button_rect.centery = self.action_info_rect.centery
        self.act_button_rect.right = self.rect.right - 3

    def update(self):
        self.movement_info = self.font.render(load_text("move to")+(repr(player.movement) if player.movement else "..."), True, FOREGROUND)
        text = load_text("action-prefix")
        if not player.action:
            text += load_text("do nothing")
        elif player.action in ("phaser", "torpedo"):
            text += load_text("fire-"+player.action)+(repr(player.target) if player.target else "...")
        elif player.action == "self-destruct":
            text += load_text("self-destruct")
        self.action_info = self.font.render(text, True, FOREGROUND)
        self.action_info_rect = self.action_info.get_rect()
        self.action_info_rect.topleft = (self.rect.left + 2, self.rect.top + 10 + self.movement_info.get_height())

    def render(self):
        self.screen.blit(self.frame, self.rect)
        self.screen.blit(self.movement_info, (self.rect.left + 2, self.rect.top + 2))
        self.screen.blit(self.move_button, self.move_button_rect)
        self.screen.blit(self.action_info, self.action_info_rect)
        if player.action in ("phaser", "torpedo"):
            self.screen.blit(self.act_button, self.act_button_rect)
        self.screen.blit(self.okay_button, self.okay_button_rect)
        self.screen.blit(self.cancel_button, self.cancel_button_rect)

font = pygame.font.SysFont("Courier New,Liberation Mono", 12)
infofont = pygame.font.SysFont("Courier New,Liberation Mono", FONT_SIZE, bold=True)


def screenshot(screen):
    scrnames = glob.glob(os.path.join("screenshots", "screenshot*.png"))
    names = []
    max = 0
    for name in scrnames:
        names.append(os.path.splitext(os.path.basename(name))[0][10:])
    for name in names:
        if not set(name).difference(set("0123456789")) and int(name) > max:
            max = int(name)
    if not "screenshots" in os.listdir("."):
        os.mkdir("screenshots")
    pygame.image.save(screen, os.path.join("screenshots", "screenshot%04d.png" % (max + 1)))

player_character = None
home_player = None
player = None
ship_list = []
dead_list = []
collisions = []
match_stats = {}
team_game = False
move_time = 0
selected = None
moving = False
attacking = False
info_target = None
command_entry = False
take_screenshot = False
box = None
message_box = None
selection_list = None
instant_action = False
text_entry = None
torpedo_list = []
rapid_end = False
game_over = False
quit = False
command_box = None
battle_settings = [False, (RANKS[0], "random"), None, None]
num_enemies = 1


def ia_choose_theme(theme):
    def callback(theme=theme):
        global races, THEME
        THEME = theme
        races = tuple(themes[THEME]["Races"])
        load_ship_graphics()
        return SelectionList(load_text("instant-action-race select"), *[(load_text(race), ia_make_player(race)) for race in races]+[(load_text("special-option-"+special_random), ia_make_player(random.choice(special_selection))) for special_random, special_selection in themes[THEME]["Special"].items() if isinstance(special_selection, tuple)])
    return callback


def ia_make_player(race):
    def callback(race=race):
        global player, command_box, home_player
        player = Ship(race, hex_to_coords(1, 1), 180, RANKS[0], load_text("default-captain"), load_text("default-ship"), 100, 20, 30, 5, human=True)
        home_player = player
        ship_list.append(player)
        match_stats[player] = {"damage": 0, "teamdamage": 0, "victory": 0, "rank": 0, "phasers shot": 0, "phasers hit": 0, "torpedoes shot": 0, "torpedoes hit": 0, "kills-sentry": 0}
        if not "sentry" in themes[THEME]["Special"]:
            del match_stats[player]["kills-sentry"]
        for race in races:
            match_stats[player]["kills-"+race] = 0
        command_box = CommandBox(display, infofont)
        return SelectionList(load_text("instant-action-team game"), (load_text("menu-yes"), ia_choose_team_game(True)), (load_text("menu-no"), ia_choose_team_game(False)))
    return callback


def ia_choose_team_game(choice):
    def callback(choice=choice):
        global team_game
        team_game = choice
        return SelectionList(load_text("instant-action-num opponents"), (load_text("menu-one"), ia_choose_opponents(1)), (load_text("menu-two"), ia_choose_opponents(2)), (load_text("menu-three"), ia_choose_opponents(3)))
    return callback


def ia_choose_opponents(num):
    def callback(num=num):
        global num_enemies
        num_enemies = num
        return SelectionList(load_text("instant-action-ai race").format(len(ship_list)), *[(load_text(race), ia_make_enemy(race)) for race in races]+[(load_text("special-option-"+special_random), ia_make_enemy(random.choice(special_selection))) for special_random, special_selection in themes[THEME]["Special"].items() if isinstance(special_selection, tuple)])
    return callback


def ia_make_enemy(race):
    def callback(race=race):
        global team_game
        if race == "sentry":
            e_captain = ""
            e_name = load_text("sentry")
        else:
            captain_names = load_text("captain-names-"+race).split("\n")
            ship_names = load_text("ship-names-"+race).split("\n")
            valid_captain_names = captain_names[:]
            valid_ship_names = ship_names[:]
            for ship in ship_list:
                if ship.captain in valid_captain_names:
                    valid_captain_names.remove(ship.captain)
                if ship.name in valid_ship_names:
                    valid_ship_names.remove(ship.name)
            if not valid_captain_names:
                valid_captain_names = captain_names
            if not valid_ship_names:
                valid_ship_names = ship_names
            e_captain = random.choice(valid_captain_names)
            e_name = random.choice(valid_ship_names)
        enemy = Ship(race, hex_to_coords(*((14, 10), (1, 11), (14, 1))[len(ship_list)-1]), (180 if len(ship_list) == 2 and not race == "sentry" else 0), RANKS[0], e_captain, e_name, (200 if race == "sentry" else 100), 20, 30, (0 if race == "sentry" else 5))
        ship_list.append(enemy)
        match_stats[enemy] = {"damage": 0, "teamdamage": 0, "victory": 0, "rank": 0}
        if len(ship_list) <= num_enemies:
            return SelectionList(load_text("instant-action-ai race").format(len(ship_list)), *[(load_text(new_race), ia_make_enemy(new_race)) for new_race in races]+([(load_text("special-option-sentry"), ia_make_enemy("sentry"))] if True else [])+[(load_text("special-option-"+special_random), ia_make_enemy(random.choice(special_selection))) for special_random, special_selection in themes[THEME]["Special"].items() if isinstance(special_selection, tuple)])
        elif team_game and not any([True for ship in ship_list if not ship.type == ship_list[0].type]):
            global message_box
            team_game = False
            message_box = Messagebox(load_text("cancel-team-game"), infofont)
    return callback


def create_new_character(theme):
    char = OrderedDict((
        ("name", load_text("default-captain")),
        ("ship", load_text("default-ship")),
        ("theme", theme),
        ("race", "random"),
        ("rank", RANKS[0]),
        ("xp", 0),
        ("bonus", 0),
        ("shields", 100),
        ("phasers", 20),
        ("torpedo", 30),
        ("engine", 5),
        ("games played", 0),
        ("phasers shot", 0),
        ("phasers hit", 0),
        ("torpedoes shot", 0),
        ("torpedoes hit", 0),
        ("average points", 0),
        ("average shields", 0),
    ))
    for race in races:
        char["kills-"+race] = 0
    if "sentry" in themes[THEME]["Special"]:
        char["kills-sentry"] = 0
    global player_character
    player_character = char
    return campaign_menu()


class InvalidCharacterError(Exception):
    pass


def load_existing_character(name):
    char = OrderedDict()
    with open(name, "r") as f:
        char = yaml.safe_load(f)
        char["bonus"] = 0
        char["rank"] = RANKS[0]
        while char["rank"] in RANK_XP and char["xp"] > RANK_XP[char["rank"]]:
            char["rank"] = RANK_PROMOTE[char["rank"]]
            char["bonus"] += 5
        for stat, data in STATS.items():
            if char[stat] < data["min"] or char[stat] > data["max"] or (char[stat] - data["min"]) % data["step"]:
                raise InvalidCharacterError("invalid {0} value: {1!r}".format(stat, char[stat]))
            elif char[stat] > data["min"]:
                char["bonus"] -= (char[stat] - data["min"]) // data["step"]
        if char["bonus"] < 0:
            raise InvalidCharacterError("can't have {0!r} bonus points".format(char["bonus"]))
        global battle_settings
        battle_settings = list(char["battle-settings"])
    global player_character, THEME, races
    THEME = char["theme"]
    races = tuple(themes[THEME]["Races"])
    for stat in list(char):
        if not stat.startswith("kills-") or stat == "kills-sentry":
            continue
        race = stat[6:]
        if race not in races:
            del char[stat]
    for race in races:
        if not "kills-"+race in char:
            char["kills-"+race] = 0
    if "sentry" in themes[THEME]["Special"] and not "kills-sentry" in char:
        char["kills-sentry"] = 0
    char["savefile"] = os.path.splitext(os.path.basename(name))[0]
    player_character = char
    load_ship_graphics()


def start_battle():
    global message_box, home_player
    if not any([True for ai in battle_settings[1:] if ai and not ai == "sentry"]):
        message_box = Messagebox(load_text("no-players"), infofont)
        return selection_list
    global player, command_box, team_game
    race = player_character["race"]
    if race in themes[THEME]["Special"]:
        race = random.choice(themes[THEME]["Special"][race])
    player = Ship(race, hex_to_coords(1, 1), 180, player_character["rank"], player_character["name"], player_character["ship"], player_character["shields"], player_character["phasers"], player_character["torpedo"], player_character["engine"], human=True)
    home_player = player
    ship_list.append(player)
    match_stats[player] = {"damage": 0, "teamdamage": 0, "victory": 0, "rank": 0, "phasers shot": 0, "phasers hit": 0, "torpedoes shot": 0, "torpedoes hit": 0, "kills-sentry": 0}
    if not "sentry" in themes[THEME]["Special"]:
        del match_stats[player]["kills-sentry"]
    for race in races:
        match_stats[player]["kills-"+race] = 0
    command_box = CommandBox(display, infofont)
    for i, slot in enumerate(battle_settings[1:]):
        if slot and not slot == "sentry":
            rank, race = slot
            if race in themes[THEME]["Special"]:
                race = random.choice(themes[THEME]["Special"][race])
            points = RANKS.index(rank) * 5
            stats = {}
            for stat, data in STATS.items():
                stats[stat] = data["min"]
            while points:
                available = []
                for stat, data in STATS.items():
                    if stats[stat] < data["max"]:
                        available.append(stat)
                upgrade = random.choice(available)
                stats[upgrade] += STATS[upgrade]["step"]
                points -= 1
            captain_names = load_text("captain-names-"+race).split("\n")
            ship_names = load_text("ship-names-"+race).split("\n")
            valid_captain_names = captain_names[:]
            valid_ship_names = ship_names[:]
            for ship in ship_list:
                if ship.captain in valid_captain_names:
                    valid_captain_names.remove(ship.captain)
                if ship.name in valid_ship_names:
                    valid_ship_names.remove(ship.name)
            if not valid_captain_names:
                valid_captain_names = captain_names
            if not valid_ship_names:
                valid_ship_names = ship_names
            e_captain = random.choice(valid_captain_names)
            e_name = random.choice(valid_ship_names)
            enemy = Ship(race, hex_to_coords(*((14, 10), (1, 11), (14, 1))[i]), (180 if i == 1 else 0), rank, e_captain, e_name, stats["shields"], stats["phasers"], stats["torpedo"], stats["engine"])
            ship_list.append(enemy)
            match_stats[enemy] = {"damage": 0, "teamdamage": 0, "victory": 0, "rank": 0}
        elif slot == "sentry":
            enemy = Ship("sentry", hex_to_coords(*((14, 10), (1, 11), (14, 1))[i]), 0, RANKS[0], "", load_text("sentry"), 200, 20, 30, 0)
            ship_list.append(enemy)
            match_stats[enemy] = {"damage": 0, "teamdamage": 0, "victory": 0, "rank": 0}
    team_game = battle_settings[0]
    if team_game and not any([True for ship in ship_list if not ship.type == "sentry" and not ship.type == ship_list[0].type]):
        team_game = False
        message_box = Messagebox(load_text("cancel-team-game"), infofont)


def add_ai_slot(num):
    def callback(num=num):
        battle_settings[num] = (RANKS[0], "random")
        return change_ai_setting(num)()
    return callback


def add_sentry_gun(num):
    def callback(num=num):
        battle_settings[num] = "sentry"
        return change_ai_setting(num)()
    return callback


def remove_ai_slot(num):
    def callback(num=num):
        battle_settings[num] = None
        return change_ai_setting(num)()
    return callback


def change_ai_rank(num):
    def callback(num=num):
        def make_callback(rank):
            def set_rank(rank=rank):
                battle_settings[num] = (rank, battle_settings[num][1])
                return change_ai_setting(num)()
            return set_rank
        return SelectionList(load_text("menu-choose rank"), *[(load_text("rank-"+rank), make_callback(rank)) for rank in RANKS])
    return callback


def change_ai_race(num):
    def callback(num=num):
        def make_callback(race):
            def set_race(race=race):
                battle_settings[num] = (battle_settings[num][0], race)
                return change_ai_setting(num)()
            return set_race
        return SelectionList(load_text("menu-choose race"), *[(load_text(race), make_callback(race)) for race in races] + [(load_text("special-option-"+option), make_callback(option)) for option in themes[THEME]["Special"] if not option == "sentry"])
    return callback


def change_ai_setting(num):
    def callback(num=num):
        if battle_settings[num]:
            if battle_settings[num] == "sentry":
                return SelectionList(load_text("menu-slot").format(num)+load_text("special-option-sentry"), (load_text("menu-remove-sentry"), remove_ai_slot(num)), (load_text("menu-back"), battle_setup))
            else:
                return SelectionList(load_text("menu-slot-ai").format(num) + "{0} - {1}".format(load_text("rank-"+battle_settings[num][0]), load_text(battle_settings[num][1] if battle_settings[num][1] in races else "special-option-"+battle_settings[num][1])), (load_text("menu-change-rank"), change_ai_rank(num)), (load_text("menu-change-race"), change_ai_race(num)), (load_text("menu-remove-ai"), remove_ai_slot(num)), (load_text("menu-back"), battle_setup))
        else:
            return SelectionList(load_text("menu-slot").format(num)+load_text("menu-empty-slot"), (load_text("menu-fill-slot"), add_ai_slot(num)), *([(load_text("menu-add-sentry"), add_sentry_gun(num))] if num > 1 else []) + [(load_text("menu-back"), battle_setup)])
    return callback


def change_team_setting():
    battle_settings[0] = not battle_settings[0]
    return battle_setup()


def battle_setup():
    slots = []
    for slot in range(1, 4):
        data = battle_settings[slot]
        if data == "sentry":
            text = load_text("special-option-sentry")
        elif data:
            text = "{0} - {1}".format(load_text("rank-"+data[0]), load_text(data[1] if data[1] in races else "special-option-"+data[1]))
        else:
            text = load_text("menu-empty-slot")
        slots.append((text, change_ai_setting(slot)))
    return SelectionList(load_text("battle-setup-title"), (load_text("battle-setup-team battle-on" if battle_settings[0] else "battle-setup-team battle-off"), change_team_setting), slots[0], slots[1], slots[2], (load_text("menu-fight"), start_battle), (load_text("menu-back"), campaign_menu))


def change_captain_name():
    global text_entry

    def callback(text=None):
        if text:
            player_character["name"] = text
        player_setup()

    text_entry = TextEntry(load_text("player-setup-change name"), player_character["name"], callback)


def change_ship_name():
    global text_entry

    def callback(text=None):
        if text:
            player_character["ship"] = text
        player_setup()

    text_entry = TextEntry(load_text("player-setup-change ship"), player_character["ship"], callback)


def change_race():
    def make_callback(race):
        def callback(race=race):
            player_character["race"] = race
            return player_setup()
        return callback
    return SelectionList(load_text("player-setup-choose race"), *[(load_text(race), make_callback(race)) for race in races] + [(load_text("special-option-"+option), make_callback(option)) for option in themes[THEME]["Special"] if not option == "sentry"])


def player_setup():
    global selection_list

    def spend_points(stat):
        def callback(stat=stat):
            menu = []
            data = STATS[stat]

            def increase_stat():
                player_character["bonus"] -= 1
                player_character[stat] += data["step"]
                return callback()

            def decrease_stat():
                player_character["bonus"] += 1
                player_character[stat] -= data["step"]
                return callback()

            if player_character["bonus"] and player_character[stat] < data["max"]:
                menu.append((load_text("stat-increase").format(data["step"], player_character[stat] + data["step"]), increase_stat))
            if player_character[stat] > data["min"]:
                menu.append((load_text("stat-decrease").format(data["step"], player_character[stat] - data["step"]), decrease_stat))
            menu.append((load_text("menu-return-player setup"), player_setup))
            return SelectionList("{0}: {1!r}".format(load_text("stat-"+stat), player_character[stat]), *menu)
        return callback

    selection_list = SelectionList(load_text("player-setup-title").format(formatted_rank=load_text("rank-"+player_character["rank"]), **player_character), (load_text("player-setup-name").format(player_character["name"]), change_captain_name), (load_text("player-setup-ship").format(player_character["ship"]), change_ship_name), (load_text("player-setup-race").format(load_text(player_character["race"] if player_character["race"] in races else "special-option-"+player_character["race"])), change_race), (load_text("player-setup-shields").format(player_character["shields"]), spend_points("shields")), (load_text("player-setup-phasers").format(player_character["phasers"]), spend_points("phasers")), (load_text("player-setup-torpedo").format(player_character["torpedo"]), spend_points("torpedo")), (load_text("player-setup-engine").format(player_character["engine"]), spend_points("engine")), (load_text("menu-back"), campaign_menu))
    return selection_list


def view_statistics():
    text = load_text("player-statistics")
    next = (repr(RANK_XP[player_character["rank"]] - player_character["xp"]) if player_character["rank"] in RANK_XP else load_text("n/a"))
    phaser_percent = ("0%" if player_character["phasers shot"] == 0 else "{0:.2%}".format(player_character["phasers hit"] / player_character["phasers shot"]))
    torpedo_percent = ("0%" if player_character["torpedoes shot"] == 0 else "{0:.2%}".format(player_character["torpedoes hit"] / player_character["torpedoes shot"]))
    text = text.format(next=next, phaser_percent=phaser_percent, torpedo_percent=torpedo_percent, **player_character)
    text += "\n" + load_text("kill-count-prefix")
    killstats = [(load_text(stat[6:])+": ", value) for stat, value in player_character.items() if stat.startswith("kills-")]
    col1, col2 = killstats[:len(killstats)//2], killstats[len(killstats)//2:]
    if len(killstats) % 2:
        col1.insert(0, None)
        col2.insert(0, killstats[-1])
    else:
        text += "\n"
    widths = [len(load_text("kill-count-prefix"))-7 if col1[0] is None else 0, 0]
    for name in col1:
        if name is None:
            continue
        if len(name[0]) > widths[0]:
            widths[0] = len(name[0])
    for name in col2:
        if len(name[0]) > widths[1]:
            widths[1] = len(name[0])
    widths[0] += 7 - (widths[0]) % 8
    for left, right in zip(col1, col2):
        if left is not None:
            left, value = left
            text += left.rjust(widths[0]) + repr(value)
        right, value = right
        text += "\t" + right.rjust(widths[1]) + repr(value) + "\n"
    text = text[:-1]

    def reset_confirm():
        def reset_callback():
            for stat in ("games played", "phasers shot", "phasers hit", "torpedoes shot", "torpedoes hit", "average points", "average shields"):
                player_character[stat] = 0
            for stat in [key for key in player_character if key.startswith("kills-")]:
                player_character[stat] = 0
            return campaign_menu()
        return SelectionList(load_text("menu-stats-reset-confirm"), (load_text("menu-yes"), reset_callback), (load_text("menu-no"), view_statistics))

    return SelectionList(text, (load_text("menu-stats-reset"), reset_confirm), (load_text("menu-back"), campaign_menu))


def save_character():
    global text_entry

    def callback(text=None):
        if not text:
            message_box = Messagebox(load_text("character-not-saved"), infofont)
            campaign_menu()
            return
        char = dict(**player_character)
        char["battle-settings"] = battle_settings
        del char["rank"]
        del char["bonus"]
        if "savefile" in char:
            del char["savefile"]
        file = os.path.join(SAVE_FOLDER, text+".chr")
        if not os.path.exists(SAVE_FOLDER):
            os.mkdir(SAVE_FOLDER)
        with open(file, "w") as f:
            yaml.safe_dump(char, f, indent=4)
        player_character["savefile"] = text
        global message_box
        message_box = Messagebox(load_text("character-saved"), infofont)
        campaign_menu()

    text_entry = TextEntry(load_text("save-character-prompt"), (player_character["name"] if not "savefile" in player_character else player_character["savefile"]), callback)


def campaign_menu():
    global selection_list
    selection_list = SelectionList(load_text("menu-campaign-title").format(**player_character), (load_text("menu-battle-setup"), battle_setup), (load_text("menu-player-setup"), player_setup), (load_text("menu-view-statistics"), view_statistics), (load_text("menu-save-character"), save_character), (load_text("menu-return-main menu"), main_menu_confirm))
    return selection_list


def main_menu_confirm():
    return SelectionList(load_text("warning-save"), (load_text("menu-yes-sure"), main_menu), (load_text("menu-no-sure"), campaign_menu))


def main_menu():
    global selection_list, instant_action, player_character, THEME, races
    instant_action, player_character, THEME, races = False, None, None, ()

    def new_choose_theme(theme):
        def callback(theme=theme):
            global races, THEME
            THEME = theme
            races = tuple(themes[THEME]["Races"])
            load_ship_graphics()
            return create_new_character(theme)
        return callback

    def new_callback():
        return SelectionList(load_text("new-character-theme"), *[(load_text("theme-"+theme), new_choose_theme(theme)) for theme in themes] + [(load_text("menu-cancel"), main_menu)])

    def load_character(name):
        def callback(name=name):
            try:
                load_existing_character(name)
            except Exception as err:
                global message_box
                message_box = Messagebox(load_text("load-error")+"\n{0}: {1}".format(err.__class__.__name__, err), infofont)
                return selection_list
            return campaign_menu()
        return callback

    def load_callback():
        import glob
        names = glob.glob(os.path.join(SAVE_FOLDER, "*.chr"))
        if names:
            return SelectionList(load_text("load-character-title"), *[(os.path.splitext(os.path.basename(name))[0], load_character(name)) for name in names] + [(load_text("menu-cancel"), main_menu)])
        else:
            global message_box
            message_box = Messagebox(load_text("no-characters"), infofont)
            return selection_list

    def instant_action_callback():
        global instant_action
        instant_action = True
        return SelectionList(load_text("instant-action-choose theme"), *[(load_text("theme-"+theme), ia_choose_theme(theme)) for theme in themes])

    def quit_callback():
        global quit
        quit = True

    selection_list = SelectionList(load_text("main-menu-title"), (load_text("menu-new character"), new_callback), (load_text("menu-load character"), load_callback), (load_text("menu-instant action"), instant_action_callback), (load_text("menu-quit"), quit_callback))
    return selection_list

main_menu()


def fire_phaser(who, where, step):
    playsound("phaser")
    color = themes[THEME]["Races"][who.type]["phasers"] if who.type in races else themes[THEME]["Special"]["sentry"]["phasers"]
    if isinstance(color[0], tuple):
        color = color[step]
    where = hex_to_coords(*where)
    where = where[0]+4, where[1]+4
    origin = who.pos[0]+4, who.pos[1]+4
    dx, dy = where[0] - origin[0], where[1] - origin[1]
    if abs(dx) <= 0.01 and abs(dy) <= 0.01:
        dx = 100
    while where[0] > 0 and where[0] < 160 and where[1] > 0 and where[1] < 160:
        where = where[0] + dx, where[1] + dy
    temp = pygame.surface.Surface((160, 160))
    pygame.draw.line(temp, (255, 255, 255), origin, where, 2)
    temp.set_colorkey((0, 0, 0))
    mask = pygame.mask.from_surface(temp)
    cpoint = None
    for target in ship_list:
        if target == who:
            continue
        tmask = target.mask
        if mask.overlap(tmask, tuple(map(int, target.pos))):
            omask = mask.overlap_mask(tmask, tuple(map(int, target.pos)))
            points = list(set(omask.outline()))
            for p in points:
                dist = math.hypot(origin[0] - p[0], origin[1] - p[1])
                if cpoint is None or dist < cpoint[0]:
                    cpoint = dist, p, target
    for torp in torpedo_list:
        omask = mask.overlap_mask(torp.mask, torp.rect.topleft)
        points = list(set(omask.outline()))
        for p in points:
            dist = math.hypot(origin[0] - p[0], origin[1] - p[1])
            if cpoint is None or dist < cpoint[0]:
                cpoint = dist, p, torp
    if cpoint is not None:
        cpoint, what = cpoint[1], cpoint[2]
        if isinstance(what, Ship):
            before = what.shields
            what.shot(who.phasers // 5)
            if who == player and what.shields < 0 and before >= 0:
                match_stats[player]["kills-"+what.type] += 1
            damage = before - what.shields
            if team_game and who.type == what.type:
                match_stats[who]["teamdamage"] -= damage
            else:
                match_stats[who]["damage"] += damage
            global already_hit
            if who == player and not already_hit:
                match_stats[player]["phasers hit"] += 1
                already_hit = True
        else:
            what.blam()
        return color, origin, cpoint, 2
    else:
        return color, origin, where, 2


def fire_torpedo(who, where):
    playsound("torpedo")
    color = themes[THEME]["Races"][who.type]["torpedo"] if who.type in races else themes[THEME]["Special"]["sentry"]["torpedo"]
    where = hex_to_coords(*where)
    where = where[0]+4, where[1]+4
    if who == player:
        match_stats[player]["torpedoes shot"] += 1
    torpedo_list.append(Torpedo((who.pos[0]+4, who.pos[1]+4), where, who, who.torpedoes, color))


def start_turn():
    for enemy in ship_list:
        if enemy == player:
            continue
        ehex = coords_to_hex(enemy.pos)
        if enemy.type == "sentry":
            enemy.action = "torpedo"
        else:
            enemy.action = random.choice((None, "phaser", "torpedo"))
        valid_targets = []
        valid_movements = []
        for row in range(1, 15):
            for col in range(1, 12 if row % 2 else 11):
                if enemy.get_valid_destination(row, col, bool(enemy.action)) and (enemy.type == "sentry" or not (row, col) == ehex):
                    valid_movements.append((row, col))
                if enemy.type == "sentry":
                    # Really, these become valid again if there's only one sentry... ah, screw it.
                    if not (row, col) in SENTRY_INVALID:
                        valid_targets.append((row, col))
                else:
                    for target in ship_list:
                        if target == enemy or target.cloaked or (team_game and target.type == enemy.type):
                            continue
                        thex = coords_to_hex(target.pos)
                        if hex_distance(thex, (row, col)) <= min(target.speed + 2, target.engine) // 2:
                            valid_targets.append((row, col))
                            break
        if enemy.action and not valid_targets:
            row = random.randint(1, 14)
            enemy.target = row, random.randint(1, 11 if row % 2 else 10)
        elif enemy.action:
            enemy.target = random.choice(valid_targets)
        enemy.movement = random.choice(valid_movements)
        if "teleportation" in enemy.specials and not enemy.action and random.random() > 0.5:
            row = random.randint(1, 14)
            enemy.movement = row, random.randint(1, 11 if row % 2 else 10)
    global move_time
    move_time = 90
    for ship in ship_list:
        if "teleportation" in ship.specials and not ship.action and not ship.get_valid_destination(ship.movement[0], ship.movement[1], bool(ship.action)):
            ship.teleport_target = hex_to_coords(*ship.movement)
            ship.speed = 0
            if "cloaking" in ship.specials:
                ship.cloak(False)
        else:
            ship.move_target = hex_to_coords(*ship.movement)
            ship.speed = hex_distance(coords_to_hex(ship.pos), ship.movement)
            dx, dy = ship.pos[0] - ship.move_target[0], ship.pos[1] - ship.move_target[1]
            if dx or dy:
                if dx < 0 and dx < -abs(dy):
                    ship.rotate(270)
                elif dx > 0 and dx > abs(dy):
                    ship.rotate(90)
                elif dy > 0:
                    ship.rotate(0)
                else:
                    ship.rotate(180)
            if not ship.action and "regeneration" in ship.specials:
                ship.regen = 5
            if not ship.action and "cloaking" in ship.specials:
                ship.cloak()
            elif ship.action and "cloaking" in ship.specials:
                ship.cloak(False)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F4 and event.mod & pygame.KMOD_ALT:
                break
            elif event.key == pygame.K_F12:
                take_screenshot = True
            if text_entry:
                if event.key == pygame.K_BACKSPACE:
                    text_entry.text = text_entry.text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    text_entry = text_entry.callback()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    text_entry = text_entry.callback(text_entry.text)
                elif event.unicode:
                    result = event.unicode
                    if sys.version_info[0] < 3:
                        result = result.encode("latin-1", "replace")
                    text_entry.text += result
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                break
        elif event.type == pygame.MOUSEBUTTONUP and not move_time:
            if message_box:
                message_box = None
            elif text_entry:
                pass
            elif selection_list:
                for button in selection_list:
                    if button.rect.collidepoint(event.pos):
                        selection_list = button.callback()
                        break
            elif command_entry:
                if command_box.cancel_button_rect.collidepoint(event.pos):
                    selected, moving, command_entry = None, False, False
                elif command_box.okay_button_rect.collidepoint(event.pos):
                    if not player.movement:
                        message_box = Messagebox(load_text("no-destination"), infofont)
                    elif not player.get_valid_destination(player.movement[0], player.movement[1], bool(player.action)) and not ("teleportation" in player.specials and not player.action):
                        message_box = Messagebox(load_text("invalid-destination"), infofont)
                    elif player.action and not player.action == "self-destruct" and not player.target:
                        message_box = Messagebox(load_text("no-target"), infofont)
                    else:
                        start_turn()
                        selected, moving, command_entry = None, False, False
                elif command_box.move_button_rect.collidepoint(event.pos):
                    moving, command_entry = True, False
                elif command_box.act_button_rect.collidepoint(event.pos) and player.action in ("phaser", "torpedo"):
                    attacking, command_entry = True, False
                elif command_box.action_info_rect.collidepoint(event.pos):
                    def action_callback(action):
                        def callback():
                            player.action = action
                        return callback
                    selection_list = SelectionList(load_text("choose-action"), (load_text("do nothing"), action_callback(None)), (load_text("fire-phaser"), action_callback("phaser")), (load_text("fire-torpedo"), action_callback("torpedo")), (load_text("self-destruct"), action_callback("self-destruct")))
            elif info_target:
                info_target, box, selected = None, None, None
            else:
                pos = event.pos[0] // WINDOW_MULTIPLIER, event.pos[1] // WINDOW_MULTIPLIER
                thex = coords_to_hex(pos)
                if thex:
                    if moving:
                        player.movement = thex
                        moving, command_entry = False, True
                    elif attacking:
                        player.target = thex
                        attacking, command_entry = False, True
                    elif player and thex == coords_to_hex(player.pos):
                        if event.button == 1 and not game_over:
                            selected = player
                            command_entry = True
                        else:
                            selected = player
                            info_target = player
                    else:
                        for ship in ship_list:
                            if ship == player:
                                continue
                            if thex == coords_to_hex(ship.pos) and (not ship.cloaked or not player or (team_game and ship.type == player.type)):
                                if selected == ship:
                                    selected = None
                                    info_target = None
                                else:
                                    selected = ship
                                    info_target = ship
                                break
                        else:
                            if game_over:
                                game_over, rapid_end, player, ship_list, dead_list, collisions, match_stats, message_box = False, False, None, [], [], [], {}, None
                                if instant_action:
                                    main_menu()
                                else:
                                    campaign_menu()
                            elif not player:
                                def rapid_end_callback():
                                    global rapid_end
                                    rapid_end = True
                                selection_list = SelectionList(load_text("after-death-menu"), (load_text("process-turn"), start_turn), (load_text("fast-forward"), rapid_end_callback), (load_text("return-to-board"), lambda: None))
    else:
        if not quit:
            draw_phasers = []
            if not move_time and not player and not message_box and not selection_list and not text_entry and not game_over and rapid_end:
                start_turn()
            if move_time:
                for i, ship in enumerate(ship_list):
                    if ship.move_target:
                        ship.move(ship.move_target, move_time)
                    if move_time > 0:
                        for other in ship_list[i+1:]:
                            if abs(ship.pos[0] - other.pos[0]) < 9 and abs(ship.pos[1] - other.pos[1]) < 9:
                                if not (ship, other) in collisions and not (other, ship) in collisions:
                                    collisions.append((ship, other))
                                    playsound("hit")
                                    before = ship.shields, other.shields
                                    ship.shot(10)
                                    other.shot(10)
                                    if ship == player and other.shields < 0 and before[1] >= 0:
                                        match_stats[player]["kills-"+other.type] += 1
                                    elif other == player and ship.shields < 0 and before[0] >= 0:
                                        match_stats[player]["kills-"+ship.type] += 1
                                    damage = before[0] - ship.shields, before[1] - other.shields
                                    if team_game and ship.type == other.type:
                                        match_stats[ship]["teamdamage"] -= damage[0]
                                        match_stats[other]["teamdamage"] -= damage[1]
                                    else:
                                        match_stats[ship]["damage"] += damage[0]
                                        match_stats[other]["damage"] += damage[1]
                            elif (ship, other) in collisions or (other, ship) in collisions:
                                if (ship, other) in collisions:
                                    collisions.remove((ship, other))
                                elif (other, ship) in collisions:
                                    collisions.remove((other, ship))
                if move_time == 90 and any([ship.teleport_target for ship in ship_list]):
                    playsound("teleport")
                if move_time == 80:
                    for ship in ship_list:
                        if ship.teleport_target:
                            ship.pos = ship.teleport_target
                if move_time == 70:
                    for ship in ship_list:
                        if ship.teleport_target:
                            ship.teleport_target = None
                elif move_time == 85:
                    for ship in ship_list:
                        if ship.action == "torpedo":
                            fire_torpedo(ship, ship.target)
                elif move_time <= 50 and move_time > 45:
                    if move_time == 50:
                        already_hit = False
                        if player and player.action == "phaser":
                            match_stats[player]["phasers shot"] += 1
                    for ship in ship_list:
                        if ship.action == "phaser":
                            draw_phasers.append(fire_phaser(ship, ship.target, 50 - move_time))
                elif move_time == 1:
                    for ship in ship_list:
                        if ship.action == "self-destruct":
                            ship.shields = -1
                for torp in torpedo_list[:]:
                    torp.update()
                move_time -= 1
                if move_time == 0:
                    dying = []
                    collisions = []
                    recheck = True
                    while recheck:
                        recheck = False
                        for ship in ship_list:
                            if ship in dying:
                                continue
                            ship.move_target = None
                            if ship.regen:
                                ship.shields = min(ship.shields + ship.regen, ship.max_shields)
                                ship.regen = 0
                            if ship.shields < 0:
                                dying.append(ship)
                                for other in ship_list:
                                    if other == ship:
                                        continue
                                    if hex_distance(coords_to_hex(ship.pos), coords_to_hex(other.pos)) <= 1:
                                        if other.shields >= 0:
                                            before = other.shields
                                            other.shot(30)
                                            damage = before - other.shields
                                            if team_game and ship.type == other.type:
                                                match_stats[ship]["teamdamage"] -= damage
                                            else:
                                                match_stats[ship]["damage"] += damage
                                            recheck = True
                    if dying:
                        move_time = -1
                        playsound("explode")
                    else:
                        for ship in ship_list:
                            if ship.shot_recently:
                                ship.shot_recently = 0
                if move_time < 0 and move_time > -11:
                    for ship in dying:
                        ship.explode = move_time
                elif move_time == -11:
                    for ship in dying:
                        ship_list.remove(ship)
                        dead_list.append(ship)
                        if ship == player:
                            player = None
                    move_time = 0
                    non_sentries = [ship for ship in ship_list if not ship.type == "sentry"]
                    if len(non_sentries) <= 1 or (team_game and not any([True for ship in ship_list if not ship.type == "sentry" and not ship.type == ship_list[0].type])):
                        winner = None
                        if player:
                            winner, text = player, "after-battle-report-player"
                        elif non_sentries:
                            winner, text = non_sentries[0], "after-battle-report-other"
                        if winner:
                            winning_faction = load_text("faction-name-"+winner.type)
                            quote = load_text("victory-quote-"+winner.type)
                        else:
                            winning_faction = load_text("no-faction")
                            quote = load_text("draw-quote-"+THEME)
                            text = "after-battle-report-draw"
                        text = load_text(text).format(winning_faction=winning_faction, quote=quote)
                        winning_team = []
                        if team_game and non_sentries:
                            for ship in ship_list+dead_list:
                                if ship.type == non_sentries[0].type:
                                    winning_team.append(ship)
                        elif non_sentries:
                            winning_team = non_sentries[:]
                        for ship in ship_list+(dead_list[::-1]):
                            stats = match_stats[ship]
                            vic = 0
                            rank = 0
                            if ship in winning_team:
                                vic = 500 // len(winning_team)
                                s_rank = RANKS.index(ship.rank)
                                for other in match_stats:
                                    if other in winning_team:
                                        continue
                                    o_rank = RANKS.index(other.rank)
                                    if o_rank > s_rank:
                                        rank += 100 * (o_rank - s_rank)
                            dam, teamdam = stats["damage"] * 2, stats["teamdamage"] * 2
                            extras = (load_text("extras-you") if ship == home_player else (load_text("extras-human") if ship.human else "")) + (load_text("extras-dead") if not ship in ship_list else "")
                            match_stats[ship]["total"] = total = dam + teamdam + vic + rank
                            rank_bonus = rank
                            rank = load_text("rank-"+ship.rank) if ship.rank else ""
                            text += "\n" + load_text("statistics-"+("sentry" if ship.type == "sentry" else "ship")).format(name=ship.name, rank=rank, captain=ship.captain, extras=extras, dam=dam, teamdam=teamdam, vic=vic, rank_bonus=rank_bonus, total=total)
                        if not instant_action:
                            stats = match_stats[home_player]
                            for stat in stats:
                                if stat in ("damage", "teamdamage", "victory", "rank", "total"):
                                    continue
                                player_character[stat] += stats[stat]
                            player_character["average points"] = (player_character["average points"] * player_character["games played"] + stats["total"]) / (player_character["games played"] + 1)
                            player_character["average shields"] = (player_character["average shields"] * player_character["games played"] + ship.shields) / (player_character["games played"] + 1)
                            player_character["games played"] += 1
                            player_character["xp"] += stats["total"]
                            bonus = 0
                            while player_character["rank"] in RANK_XP and player_character["xp"] > RANK_XP[player_character["rank"]]:
                                bonus += 5
                                player_character["rank"] = RANK_PROMOTE[player_character["rank"]]
                            if bonus:
                                text += "\n\n" + load_text("promotion").format(rank=load_text("rank-"+player_character["rank"]), bonus=bonus)
                                player_character["bonus"] += bonus
                        message_box = Messagebox(text, infofont)
                        home_player = None
                        game_over = True
                for ship in ship_list:
                    if ship.shot_recently:
                        ship.shot_recently -= 1
                screen.fill(BACKGROUND)
            else:
                screen.blit(background, (0, 0))
            if selected == player:
                if moving:
                    for row in range(1, 15):
                        for column in range(1, 12 if row % 2 else 11):
                            if not player.get_valid_destination(row, column, bool(player.action)):
                                x, y = hex_to_coords(row, column)
                                screen.blit(invalid, (x-1, y-1))
            if selected:
                screen.blit(select, (selected.pos[0]-1, selected.pos[1]-1))
            for torp in torpedo_list:
                torp.render(screen)
            for phaser in draw_phasers:
                pygame.draw.line(screen, *phaser)
            for ship in ship_list:
                if ship == player:
                    continue
                if not ship.cloaked or ship.shot_recently or ship.explode or not player or (team_game and ship.type == player.type):
                    ship.render(screen)
            if player:
                player.render(screen)
            for ship in ship_list:
                if ship.teleport_target:
                    if move_time > 80:
                        pygame.gfxdraw.filled_circle(screen, ship.pos[0]+4, ship.pos[1]+4, move_time - 80, (0, 255, 0))
                    else:
                        pygame.gfxdraw.filled_circle(screen, ship.pos[0]+4, ship.pos[1]+4, 80 - move_time, (0, 255, 0))
            screen.blit(font.render(load_text("titlebar").format(shields=player.shields, speed=player.speed) if player else load_text("titlebar-no-player"), True, FOREGROUND, BACKGROUND), (0, 0))
            pygame.transform.scale(screen, WINDOW_SIZE, display)
            if info_target:
                if box and box.target == info_target:
                    box.update()
                else:
                    box = Infobox(info_target, infofont)
                box.rect.left *= WINDOW_MULTIPLIER
                box.rect.top *= WINDOW_MULTIPLIER
                if box.rect.right > WINDOW_SIZE[0]:
                    box.rect.right = (int(info_target.pos[0]) - 1) * WINDOW_MULTIPLIER
                if box.rect.bottom > WINDOW_SIZE[1]:
                    box.rect.bottom = WINDOW_SIZE[1]
                box.render(display)
            if command_entry:
                command_box.update()
                command_box.render()
            if selection_list:
                selection_list.render(display)
            if text_entry:
                text_entry.update()
                text_entry.render()
            if message_box:
                message_box.render(display)
            pygame.display.flip()
            if take_screenshot:
                screenshot(display)
                take_screenshot = False
            clock.tick(30)
            continue
        else:
            break
    break

pygame.quit()
