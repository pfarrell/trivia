import pytest
from bs4 import BeautifulSoup


def get_game_data(game_id):
    file = f"../test/fixtures/game_{game_id}"
    with open(file, "r") as f:
        return f.read()


@pytest.fixture
def game_2318():
    data = get_game_data('2318')
    return BeautifulSoup(data, 'html.parser')


@pytest.fixture
def game_1004():
    data = get_game_data('1004')
    return BeautifulSoup(data, 'html.parser')


@pytest.fixture
def game_7224():
    data = get_game_data('7224')
    return BeautifulSoup(data, 'html.parser')
