import sys
import getopt
import requests
import re
from bs4 import BeautifulSoup
import pdb


class Show(object):
    def __init__(self, show_number, show_date, id, previous_id, next_id):
        self.number = show_number
        self.air_date = show_date
        self.id = id
        self.previous_id = previous_id
        self.next_id = next_id
        self.comments = None
        self.season = None
        self.contestants = []
        self.jeopardy = None
        self.double_jeopardy = None
        self.final_jeopardy = None
        self.results = None
        self.contestant_lookup = {}

    def add_contestant(self, contestant):
        self.contestants.append(contestant)
        self.contestant_lookup[contestant.id] = contestant
        self.contestant_lookup[contestant.nickname] = contestant
        self.contestant_lookup[contestant.name] = contestant


class Contestant(object):
    def __init__(self, id, name, profession, origin):
        self.id = id 
        self.name = name
        self.profession = profession
        self.origin = origin
        self.streak = 0
        self.winnings = 0
        self.nickname = None


class Category(object):
    def __init__(self, category, comment=None):
        self.category = category
        self.comment = comment


class Jeopardy(object):
    def __init(self):
        self.categories=[]
        self.clues=[]
    
    def add_clue(clue):
        self.clues.append(clue)

    def add_category(category):
        self.categories.append(category)


class DoubleJeopardy(Jeopardy):
    pass


class FinalJeopardy(Jeopardy):
    pass


def extract_show_info(soup):
    text = soup.find_all("div", id="game_title")[0].h1.text
    show = re.search(r"#\d*", text).group()[1:]
    date = re.search(r"- .*", text).group()[2:]
    return show, date


def extract_show_id(soup):
    img = soup.find_all("img", class_="game_dynamics")[0]
    show_id = extract_url_id(img.attrs['src'])
    return show_id


def extract_season(soup):
    text = soup.find_all("a", attrs={"href":re.compile("showseason")})[0]
    url = text.attrs['href']
    season = re.search(r"[\d]*$", url, flags=0)
    return season.group()


def extract_contestants_section(soup):
    table = soup.find_all("table", id="contestants_table")[0]
    for idx, child in enumerate(table.contents[0].children):
        if child == '\n':
            continue
        if idx == 1:
            prev_game = extract_url_id(child.contents[1].attrs['href'])
        elif idx == 3:
            contestants = extract_contestants(child)
        elif idx == 5:
            next_game = extract_url_id(child.contents[1].attrs['href'])

    return contestants, prev_game, next_game


def extract_contestants(soup):
    contestants = []
    for child in soup.children:
        if child == '\n':
            continue
        else:
            contestants.append(extract_contestant(child))
    return contestants


def extract_contestant(soup):
    player_id = extract_url_id(soup.contents[0].attrs['href'])
    name = soup.contents[0].text
    profession, origin = soup.text.replace(f"{name}, ", "").split(" from ")
    contestant = Contestant(player_id, name, profession, origin)
    contestant.nickname = name.split(" ")[0]
    if re.search("\(whose", origin):
        origin, streak, winnings = extract_winnings(origin)
        contestant.origin = origin
        contestant.streak = streak
        contestant.winnings = winnings
    return contestant


def extract_winnings(str):
    origin, commentary = str.split(' (whose ')
    streak =  re.sub("-day.*", "", commentary)
    winnings = re.search("[\d,]*\)$", commentary).group().replace(")", "")
    return origin, streak, winnings


def extract_url_id(url):
    id = re.search(r"[\d]*$", url, flags=0)
    return id.group()


def extract_show(soup):
    pdb.set_trace()
    show_number, date = extract_show_info(soup)
    show_id = extract_show_id(soup)
    season= extract_season(soup)
    contestants, prev, next = extract_contestants_section(soup)
    show = Show(show_number, date, show_id, prev, next)
    for contestant in contestants:
        show.add_contestant(contestant)
    return show
 

def main(argv):
    file_in = ''
    try:
        opts, args = getopt.getopt(argv, "i:", ["infile="])
    except getopt.GetoptError:
        print('parser.py -i <inputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt=='-i':
            file_in = arg

    parse(file_in)


def parse(file):
    with open (file, "r") as f:
        data=f.read()
    soup = BeautifulSoup(data, 'html.parser')
    show = extract_show(soup)

#  game_comments
#  jeopardy
#    categories
#      category|comments
#    clues
#      category|location|value|double_jeopardy?|game_order|clue|correct_answer|winner|[bad_answer|respondant]
#  scores at commercial
#    contestant|score|remarks?
#  scores after jeopardy
#    contestant|score|remarks?
#  double_jeopardy
#    categories
#      category|comments
#    clues
#      category|location|value|double_jeopardy?|game_order|clue|correct_answer|winner|[bad_answer|respondant]
#  scores after double_jeopardy
#    contestant|score|remarks
#  final_jeopardy
#    category|comments
#    category|clue|answer
#    contestant|wager|guess
#  results
#    contestant|place|prize|correct|incorrect|dd_correct|dd_missed
#  combined_coryat
#  game_tape_date


if __name__ == "__main__":
    main(sys.argv[1:])
