import pytest
from src.utils import verify_link

valid_links = [
    "https://www.espncricinfo.com/team/afghanistan-40",
    "https://www.espncricinfo.com/cricketers/team/afghanistan-40",
    "https://www.espncricinfo.com/team/australia-2",
    "https://www.espncricinfo.com/cricketers/team/australia-2"
]
invalid_links = [
    "https://www.espncricinfo.com/team/",
    "https://www.espncricinfo.com/cricketers/team/",
    "https://www.espncricinfo.com/team/afghanistan-40/squad",
    "https://www.espncricinfo.com/cricketers/team/afghanistan-40/squad",
    "https://www.espncricinfo.com/teams/afghanistan-40",
    "https://www.espncricinfo.com/cricketers/afghanistan-40",
    "https://www.espncricinfo.com/"

    '''
    not sure how long the last digits of a team can be e.g. team-40 or team-123
    "https://www.espncricinfo.com/team/afghanistan",
    "https://www.espncricinfo.com/cricketers/team/afghanistan",
    '''
]

@pytest.mark.parametrize("url", valid_links)
def test_verify_link_valid(url):
    assert verify_link(url, "team") is True

@pytest.mark.parametrize("url", invalid_links)
def test_verify_link_invalid(url):
    assert verify_link(url, "team") is False