
from parser import extract_show_info, extract_show_id, extract_url_id, extract_show, extract_contestants_section, \
    Contestant, extract_round, Jeopardy


def test_extract_show_info(game_2318):
    show_number, date = extract_show_info(game_2318)
    assert show_number == '3359'
    assert date == 'Thursday, March 25, 1999'


def test_extract_show_id(game_2318):
    show_id = extract_show_id(game_2318)
    assert show_id == '2318'


def test_extract_url_id():
    id = extract_url_id("?123")
    assert id == "123"


def test_extract_show(game_2318):
    show = extract_show(game_2318)
    assert show.id == "2318"
    assert show.season == "38"
    assert show.next_id == "2319"
    assert show.previous_id == "2317"
    assert show.air_date == "Thursday, March 25, 1999"
    assert len(show.contestants) == 3
    assert show.number == "3359"


def test_extract_contestants_section(game_2318):
    contestants, prev_game_id, next_game_id = extract_contestants_section(game_2318)
    assert len(contestants) == 3
    assert prev_game_id == "2317"
    assert next_game_id == "2319"
    validate_brian(contestants[0])
    validate_ajuan(contestants[1])
    validate_brad(contestants[2])


def validate_brian(contestant: Contestant):
    assert contestant.id == '4651'
    assert contestant.name == "Brian Keenan"
    assert contestant.nickname == 'Brian'
    assert contestant.origin == 'Fort Bragg, North Carolina'
    assert contestant.profession == 'a paratrooper'
    assert contestant.streak == 0
    assert not contestant.winnings


def validate_ajuan(contestant: Contestant):
    assert contestant.id == '4652'
    assert contestant.name == "Ajuan Mance"
    assert contestant.nickname == 'Ajuan'
    assert contestant.origin == 'Eugene, Oregon'
    assert contestant.profession == 'an English professor'
    assert contestant.streak == 0
    assert not contestant.winnings


def validate_brad(contestant: Contestant):
    assert contestant.id == '4649'
    assert contestant.name == "Brad Nail"
    assert contestant.nickname == 'Brad'
    assert contestant.origin == 'West Palm Beach, Florida'
    assert contestant.profession == 'a liability analyst'
    assert contestant.streak == "1"
    assert contestant.winnings == "1,999"


def test_extract_jeopardy_round(game_2318):
    rnd = extract_round(game_2318, "jeopardy_round", Jeopardy(), {})


def test_extract_show(game_1004):
    show = extract_show(game_1004)


def test_extract_show(game_7224):
    show = extract_show(game_7224)
