import json
import configparser
import requests
from datetime import datetime
from math import floor
from bs4 import BeautifulSoup

from blessed import Terminal

__version__ = "0.0.0.1"


FRAGARIA_URL = 'https://fragaria.cz'
TALK_IS_CHEAP_URL = 'https://fragaria.cz/'
SHOW_ME_THE_CODE_URL = 'https://github.com/fragaria/karmen/blob/feat/backend2/src/components/printers/webcam-stream.js#L1'
BLOGS_URL = f'{FRAGARIA_URL}/blog/archive/'
MEMBERS_URL = f'{FRAGARIA_URL}/work-with-us/'
LOG_TIME_URL = 'https://www.google.com/search?q=logtime'
LI_CHAR = '🍓'
THEME_LIGHT = 'l'
THEME_DARK = 'd'
THEMES = {
    THEME_LIGHT: ('black', 'white'),
    THEME_DARK: ('green', 'black'),
}


def parse_isoformat(dt_iso_str):
    return datetime.fromisoformat(dt_iso_str.replace('Z', '+00:00'))


def format_date(d):
    return d.strftime('%d.%m.%Y')


def roundxy(x, y):
    return int(floor(x)), int(floor(y))


def get_link_href(el):
    if el:
        return el.attrs['href']
    return None


def get_theme_value(theme):
    return '_on_'.join(THEMES[theme])


def set_theme(term, theme, init=False):
    theme_value = get_theme_value(theme)
    if init:
        print(f'{term.home}{getattr(term, theme_value)}{term.clear}')
    else:
        print(f"{getattr(term, theme_value)}")


class Strawberry:

    @classmethod
    def get_strawberry_lines(cls, theme):
        black = 'black' if theme == THEME_LIGHT else 'gray5'
        return (
            (black,),
            (black, 'peachpuff4', black),
            (black, black, 'peachpuff4', 'khaki4', 'darkolivegreen1',black, black),
            (black, 'peachpuff4', 'peachpuff4', 'darkolivegreen1',black, 'darkolivegreen1', 'darkolivegreen1', 'khaki4', black),
            (black, black, black, 'khaki4','darkolivegreen1', 'darkolivegreen1', black, black, black),
            (black, 'brown', 'brown', 'red', black, 'khaki4', black, 'red', 'brown', 'brown', black),
            (black, 'brown', 'red', 'red', 'red', 'red', black, 'red', 'red', 'red', 'brown', 'red', black),
            (black, 'brown', 'red', 'white', 'red', 'red', 'red', 'red', 'red', 'white', 'red', 'red', black),
            (black, 'brown', 'red', 'red', 'red', 'red', 'white', 'red', 'red', 'red', 'red', 'red', black),
            (black, 'brown', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'brown', black),
            (black, 'brown', 'red', 'white', 'red', 'red', 'red', 'white', 'red', 'brown', black),
            (black, 'brown', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'brown', black),
            (black, 'brown', 'red', 'red', 'white', 'red', 'red', 'red', black),
            (black, 'brown', 'brown', 'red', 'red', 'red', 'red', 'brown', black),
            (black, 'brown', 'brown', 'red', 'red', 'brown', black),
            (black, 'brown', 'brown', 'brown', black),
            (black, black, black),
        )

    @classmethod
    def draw(cls, term, config, theme):
        y, ys = 2, 1
        move = term.move_xy(*roundxy(24, y))
        print(f"{move}{term.link(FRAGARIA_URL, 'FRAGARIA.CZ')}")
        y += ys
        y += ys

        strawberry_lines = cls.get_strawberry_lines(theme)
        max_len = max(map(lambda i: len(i), strawberry_lines))
        multiplier = 3
        for line in strawberry_lines:
            x = 10 + ((multiplier * max_len - multiplier * len(line)) // 2)
            xs = 1
            for column in line:
                for i in range(0, multiplier):
                    move = term.move_xy(*roundxy(x, y))
                    color = f'white_on_{column}'
                    txt = f'{move}{getattr(term, color)} '
                    print(txt)
                    x += xs
            y += ys
        move = term.move_xy(*roundxy(23, y + 1))
        set_theme(term, theme)
        print(f"{move}{term.link(TALK_IS_CHEAP_URL, 'TALK IS CHEAP')}")
        move = term.move_xy(*roundxy(21, y + 2))
        print(f"{move}{term.link(SHOW_ME_THE_CODE_URL, 'SHOW ME THE CODE')}")


class Members:
    @classmethod
    def get_best_profile(cls, profiles):
        profile = profiles.get('github', None)
        if not profile:
            profile = profiles.get('linkedin', None)
        if not profile:
            profile = profiles.get('twitter', None)
        return profile

    @classmethod
    def get_profiles_for_member(cls, el):
        return {
            'twitter': get_link_href(el.find(attrs={'team-member__profile--twitter'})),
            'linkedin': get_link_href(el.find(attrs={'team-member__profile--linkedin'})),
            'github': get_link_href(el.find(attrs={'team-member__profile--github'})),
        }

    @classmethod
    def fetch_members(cls):
        content = BeautifulSoup(requests.get(MEMBERS_URL).content, 'html.parser')
        return [
            {
                'name': el.find(attrs={'team-member__name'}).text,
                'alt': el.find(attrs={'team-member__alt'}).text,
                'profiles': cls.get_profiles_for_member(el)
            }
            for el in content.findAll(attrs={'team-member__body'})
        ]

    @staticmethod
    def get_ico_for_member(member):
        name = member["name"]
        name_parts = [p.strip() for p in name.split(' ')]
        first_name = name_parts[0]
        last_name = name_parts[1]
        if last_name == 'Bílek' and first_name == 'Martin':
            return '🐴'
        if last_name == 'Burián':
            return '🥜'
        return '👨‍💻' if not first_name.endswith('a') else '👩‍💻'

    @classmethod
    def draw(cls, term, config, theme):
        y, ys = 2, 1
        x = 60
        move = term.move_xy(*roundxy(x, y))
        title = term.link(MEMBERS_URL, 'MEMBERS:')
        print(f"{move}{title}")
        y += 2 * ys
        move = term.move_xy(*roundxy(x, y))
        for member in cls.fetch_members():
            name = f'{member["name"]} ({member["alt"]})'
            profile = cls.get_best_profile(member['profiles'])
            line = name
            if profile:
                line = f'{term.link(profile, name)}'
            ico = cls.get_ico_for_member(member)
            print(f"{move}{ico} {line}")
            y += ys
            move = term.move_xy(*roundxy(x, y))


class Blogs:
    @classmethod
    def fetch_blogs(cls):
        content = BeautifulSoup(requests.get(BLOGS_URL).content, 'html.parser')
        return [
            {
                'name': el.find(attrs={'blog-posting__headline'}).text,
                'date': el.find(attrs={'blog-posting__pubdate'}).text,
                'link': '/'.join((FRAGARIA_URL, get_link_href(el.find(attrs={'blog-posting__body'}))))
            }
            for el in content.findAll(attrs={'blog-listing__post'})
        ]

    @classmethod
    def draw(cls, term, config, theme):
        y, ys = 2, 1
        x = 60
        move = term.move_xy(*roundxy(x, y))
        title = term.link(BLOGS_URL, 'BLOGS:')
        print(f"{move}{title}")
        y += 2 * ys
        move = term.move_xy(*roundxy(x, y))
        for blog in cls.fetch_blogs():
            name = f'{blog["name"]} ({blog["date"]})'
            line = f'{term.link(blog["link"], name)}'
            ico = '📝'
            print(f"{move}{ico} {line}")
            y += ys
            move = term.move_xy(*roundxy(x, y))


class Videos:
    channel_id = 'UCz1zwJ9_6-IVdX6oCvq6T_g'
    api_videos_url_pattern = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&order=date&maxResults=15&part=snippet'
    videos_url_pattern = 'https://www.youtube.com/channel/{}/videos'
    video_url_pattern = 'http://www.youtube.com/watch?v={}'

    @classmethod
    def fetch_videos(cls):
        api_key = cls.config['youtube']['key']
        videos_url = cls.api_videos_url_pattern.format(api_key, cls.channel_id)
        content = json.loads(requests.get(videos_url).content)
        return [
            {
                'name': el['snippet']['title'],
                'link': cls.video_url_pattern.format(el['id']['videoId']),
                'date': format_date(parse_isoformat(el['snippet']['publishedAt']))
            }
            for el in content['items']
        ]

    @classmethod
    def draw(cls, term, config, theme):
        cls.config = config
        y, ys = 2, 1
        x = 60
        move = term.move_xy(*roundxy(x, y))
        title = term.link(cls.videos_url_pattern.format(cls.channel_id), 'VIDEOS:')
        print(f"{move}{title}")
        y += 2 * ys
        move = term.move_xy(*roundxy(x, y))
        for video in cls.fetch_videos():
            name = f'{video["name"]} ({video["date"]})'
            line = f'{term.link(video["link"], name)}'
            ico = '📺'
            print(f"{move}{ico} {line}")
            y += ys
            move = term.move_xy(*roundxy(x, y))


class LogTime:
    @classmethod
    def draw(cls, term, config, theme):
        y = 2
        x = term.width - 15
        move = term.move_xy(*roundxy(x, y))
        title = term.link(LOG_TIME_URL, '🕰  Log time')
        print(f"{move}{title}")


MENU_ITEMS = {
    'e': ('👨‍💻', 'Members', Members),
    'b': ('📝', 'Blogs', Blogs),
    'v': ('📺', 'Videos', Videos),
}


class Menu:
    @classmethod
    def draw(cls, term, config, theme):
        y, ys = 2, 1
        x = 60
        move = term.move_xy(*roundxy(x, y))
        print(f"{move}MENU:")
        y += 2 * ys
        move = term.move_xy(*roundxy(x, y))
        for key, item in MENU_ITEMS.items():
            ico = item[0]
            title = item[1]
            print(f"{move}{ico} {title} ({key})")
            y += ys
            move = term.move_xy(*roundxy(x, y))

ALL_CHOICES = {
    **MENU_ITEMS,
    'm': ('', 'Menu', Menu),
}


def get_theme_by_key(key, prev_theme):
    theme = prev_theme

    if key == 'l':
        theme = THEME_LIGHT
    elif key == 'd':
        theme = THEME_DARK

    theme_changed = theme != prev_theme
    return theme, theme_changed


class SafeTerm:
    def __init__(self, term):
        self.term = term

    def __enter__(self):
        return self.term

    def __exit__(self, type, value, traceback):
        # cleanup
        print(f'{self.term.home}{self.term.normal}{self.term.clear}')


def main():
    term = Terminal()
    with SafeTerm(term) as term:
        config = configparser.ConfigParser()
        config.read('.fraga-term.ini')
        with term.cbreak(), term.hidden_cursor():
            inp = None
            # clear the screen
            theme = THEME_DARK
            set_theme(term, theme, True)
            drawn = False
            choice = 'm'
            prev_choice = choice
            while inp not in ('q', 'Q'):
                inp = term.inkey(timeout=0.02)
                if inp in ALL_CHOICES:
                    choice = inp
                theme, theme_changed = get_theme_by_key(inp, theme)
                if (
                    not drawn or
                    theme_changed or
                    choice != prev_choice
                ):
                    set_theme(term, theme, True)
                    Strawberry.draw(term, config, theme)
                    draw_cls = ALL_CHOICES[choice][2]
                    draw_cls.draw(term, config, theme)
                    LogTime.draw(term, config, theme)
                    prev_choice = choice
                drawn = True

if __name__ == "__main__":
    main()
