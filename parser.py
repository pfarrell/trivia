import sys
import getopt
import re
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup
import pdb


class Contestant(object):
    def __init__(self, contestant_id, name, profession, origin):
        self.id = contestant_id
        self.name = name
        self.profession = profession
        self.origin = origin
        self.streak = 0
        self.winnings = None
        self.nickname = None


class Show(object):
    def __init__(self, season, show_number, show_date, show_id, previous_id, next_id):
        self.number = show_number
        self.air_date = show_date
        self.id = show_id
        self.previous_id = previous_id
        self.next_id = next_id
        self.season = season
        self.comments = None
        self.contestants: List[Contestant] = []
        self.jeopardy: Optional[Jeopardy] = None
        self.double_jeopardy: Optional[DoubleJeopardy] = None
        self.final_jeopardy: Optional[FinalJeopardy] = None
        self.results = None
        self.contestant_lookup: Dict[Any: Contestant] = {}

    def add_contestant(self, contestant: Contestant):
        self.contestants.append(contestant)
        self.contestant_lookup[contestant.id] = contestant
        self.contestant_lookup[contestant.nickname] = contestant
        self.contestant_lookup[contestant.name] = contestant


class Category(object):
    def __init__(self, category, comment=None):
        self.category = category
        self.comment = comment


class Clue(object):
    def __init__(self, value, category, location, text, correct_response):
        self.text = text
        self.value = value
        self.correct_response = correct_response
        self.category = category
        self.location = location
        self.id = None
        self.order = None
        self.daily_double = None
        self.responder = None


class Jeopardy(object):
    def __init(self):
        self.categories: List[Category] = []
        self.clues: List[Clue] = []

    def add_clue(self, clue: Clue):
        self.clues.append(clue)

    def add_category(self, category: Category):
        self.categories.append(category)


class DoubleJeopardy(Jeopardy):
    def __init(self):
        Jeopardy.__init__(self)


class FinalJeopardy(Jeopardy):
    def __init(self):
        Jeopardy.__init__(self)


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


def extract_nicknames(soup):
    nicknames = []
    name_list = soup.find_all("div", id="double_jeopardy_round")[0].find_all("td", class_="score_player_nickname")
    for name in name_list:
        nicknames.append(name.text)
    return nicknames

def extract_contestants_section(soup):
    table = soup.find_all("table", id="contestants_table")[0]
    contestants, prev_game, next_game = (None, None, None)
    nicknames = extract_nicknames(soup)
    contestants = extract_contestants(table.find_all("p", class_="contestants"), nicknames)
    prev_id, next_id = extract_game_links(table)
    return contestants, prev_id, next_id


def extract_game_link(soup):
    pass

def extract_game_links(soup):
    prev_id, next_id = None, None
    links = soup.find_all("td")
    if len(links) == 3:
        prev_id = extract_game_link(links[0])
        next_id = extract_game_link(links[2])
    return prev_id, next_id


def extract_contestants(contestants_list, nicknames):
    contestants = []
    for child in contestants_list:
        if child == '\n':
            continue
        else:
            contestants.append(extract_contestant(child, nicknames[len(contestants)]))
    return contestants


def extract_contestant(soup, nickname):
    player_id = extract_url_id(soup.contents[0].attrs['href'])
    assert player_id
    name = soup.contents[0].text
    assert name
    split = soup.text.replace(f"{name}, ", "").rsplit(" originally from ", 1)
    if len(split) == 2:
        profession, origin = split
    else:
        profession, origin = soup.text.replace(f"{name}, ", "").rsplit(" from ", 1)
    print(f"{name} ; {origin} ; {profession}")
    assert origin
    contestant = Contestant(player_id, name, profession, origin)
    # TODO this does not work (on game 52, where Christina is nicknamed "Chris").  Need to check final results by order
    # to extract nicknames
    contestant.nickname = nickname
    if re.search(r"\(whose", origin):
        origin, streak, winnings = extract_winnings(origin)
        contestant.origin = origin
        contestant.streak = streak
        contestant.winnings = winnings
    return contestant


def extract_winnings(str_val):
    origin, commentary = str_val.split(' (whose ')
    assert origin
    assert commentary
    streak = re.sub("-day.*", "", commentary)
    winnings = re.search(r"[\d,]*\)$", commentary).group().replace(")", "")
    return origin, streak, winnings


def extract_url_id(url):
    url_id = re.search(r"[\d]*$", url, flags=0)
    return url_id.group()


def extract_round(soup, identifier, rnd, contestant_lookup):
    data = soup.find("div", id=identifier)
    # extract categories
    rnd.categories = extract_round_categories(data.find_all("td", class_="category"))
    # extract clues
    if type(rnd) is not FinalJeopardy:
        rnd.clues = extract_clues(data, rnd.categories, contestant_lookup)
    else:
        rnd.clues = extract_final_clue(data, rnd.categories, contestant_lookup)
    return rnd


def extract_round_categories(cats):
    categories = []
    for idx, cat in enumerate(cats):
        category = extract_category(cat)
        comment = extract_comment(cat)
        categories.append(Category(category, comment))
    return categories


def extract_category(cat):
    return cat.find_all("td", class_="category_name")[0].text


def extract_comment(cat):
    comment = cat.find_all("td", class_="category_comments")
    if len(comment) > 0:
        return comment[0].text
    return None


def extract_clues(rnd, categories, contestant_lookup):
    clues = []
    clues_data = rnd.find_all("td", class_="clue")
    for clue_data in clues_data:
        if clue_data.text != '\n':
            clues.append(extract_clue(clue_data, categories, contestant_lookup))
    return clues


def extract_final_clue(rnd, categories, contestant_lookup):
    clues = []
    clue = extract_clue(rnd, categories, contestant_lookup)
    clues.append(clue)
    return clues


def extract_clue_value(clue_data):
    normal_clue = clue_data.find_all("td", class_="clue_value")
    if normal_clue:
        return normal_clue[0].text, False, False
    else:
        daily_double = clue_data.find_all("td", class_="clue_value_daily_double")
        if daily_double:
            return daily_double[0].text, True, False
        else:
            return None, False, True


def extract_clue_order(clue_data):
    order = clue_data.find_all("td", class_="clue_order_number")
    if order:
        return order[0].text
    else:
        return None


def extract_clue_id(clue_data):
    order = clue_data.find_all("td", class_="clue_order_number")
    if not order:
        return
    return order[0].contents[0].attrs['href']


def extract_correct_response(clue_data):
    response = None
    mo = clue_data.find_all("div")[0].attrs["onmouseover"]
    split_attempt = mo.split('<em class="correct_response">')
    if len(split_attempt) == 2:
        response = split_attempt[1]
        response = re.sub(r"<em>.*", "", response)
    else:
        split_attempt = mo.split('<em class=\\"correct_response\\">')
        if len(split_attempt) == 2:
            response = split_attempt[1]
            response = re.sub(r"</em>.*", "", response)
    return response


def calculate_category(clue_data, categories):
    # final jeopardy
    if len(categories) == 1:
        return categories[0]
    else:
        cat_num = extract_location(clue_data).split("_")[2]
        return categories[int(cat_num) - 1]


def extract_clue_text(clue_data):
    return clue_data.find_all("td", class_="clue_text")[0].text


def extract_location(clue_data):
    id = clue_data.find_all("td", class_="clue_text")[0].attrs['id']
    return id


def extract_responder(clue_data, contestant_lookup):
    responder = None
    mo = clue_data.find_all("div")[0].attrs["onmouseover"]
    split_attempt = mo.split('<td class="right">')
    if len(split_attempt) == 2:
        response = split_attempt[1]
        response = re.sub(r"</td>.*", "", response)
        responder = contestant_lookup[response]
    else:
        split_attempt = mo.split('<em class=\\"correct_response\\">')
        if len(split_attempt) == 2:
            response = split_attempt[1]
            response = re.sub(r"</em>.*", "", response)
    return responder


def extract_clue(clue_data, categories, contestant_lookup):
    value, daily_double, final_jeopardy = extract_clue_value(clue_data)
    text = extract_clue_text(clue_data)
    location = extract_location(clue_data)
    correct_response = extract_correct_response(clue_data)
    category = calculate_category(clue_data, categories)
    clue = Clue(value, category, location, text, correct_response)
    clue.daily_double = daily_double
    if not final_jeopardy:
        clue.id = extract_clue_id(clue_data)
        clue.order = extract_clue_order(clue_data)
        clue.responder = extract_responder(clue_data, contestant_lookup)
    return clue


def extract_show(soup):
    show_number, date = extract_show_info(soup)
    show_id = extract_show_id(soup)
    season = extract_season(soup)
    contestants, prev_id, next_id = extract_contestants_section(soup)
    show = Show(season, show_number, date, show_id, prev_id, next_id)
    for contestant in contestants:
        show.add_contestant(contestant)
    show.jeopardy = extract_round(soup, 'jeopardy_round', Jeopardy(), show.contestant_lookup)
    show.double_jeopardy = extract_round(soup, 'double_jeopardy_round', DoubleJeopardy(), show.contestant_lookup)
    show.final_jeopardy = extract_round(soup, 'final_jeopardy_round', FinalJeopardy(), show.contestant_lookup)
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

    return parse(file_in)


def parse(file):
    with open (file, "r") as f:
        data=f.read()
    soup = BeautifulSoup(data, 'html.parser')
    show = extract_show(soup)
    return show

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
    show = main(sys.argv[1:])
    print(show.air_date)
