import sys

from mechanize import Browser
from bs4 import BeautifulSoup
import twitter

from secrets import *


def tweet_dunk(twitter_api, tweet):
    """
    Posts a Twitter Status for the given tweet text
    """
    status = twitter_api.PostUpdate(tweet)
    print status.text


def get_score(play):
    """
    Gets the score of the game at the time of the given play
    """
    score = play.parent.parent.parent.find_all("td")[2].string
    return "(%s)" % score


def format_dunk_tweet(play, team_string):
    dunk_index = play.find(" makes")
    player_name = play[0:dunk_index]

    tweet = "%s %s: %s #DUNK" % (team_string, get_score(play), player_name)
    return tweet


def get_team_string(soup):
    """
    Returns TEAM1 vs. TEAM2
    Based on the box score at the top of the page
    """
    linescore = soup.find("table", class_="linescore")
    teams = linescore.find_all("td", class_="team")
    cities = []
    for team in teams[1:]:
        team_city = team.find("a").string
        cities.append(team_city)
    team_string = " vs. ".join(cities)
    return team_string


def find_dunks_for_game(gameID, twitter_api):
    """
    Finds and tweets the dunks for the given gameID
    """
    url = "http://espn.go.com/nba/playbyplay?gameId=%s&period=0" % gameID

    br = Browser()
    br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6; en-us) AppleWebKit/531.9 (KHTML, like Gecko) Version/4.0.3 Safari/531.9')]
    br.set_handle_robots(False)

    response = br.open(url)
    soup = BeautifulSoup(response.read())

    team_string = get_team_string(soup)
    scoring_plays = soup.find_all('b')
    for scoring_play in scoring_plays:
        play = scoring_play.string
        if play.find("dunk") != -1:
            tweet = format_dunk_tweet(play, team_string)
            tweet_dunk(twitter_api, tweet)


def twitter_login():
    """
    Log in to Twitter using the keys from the secrets file
    """
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)
    return api


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "--------------------------------------------------"
        print "Not Enough Arguments. You must specify a gameID"
        print "Usage: python tweet_dunks.py gameID1 gameID2 ..."
        print "--------------------------------------------------"
    else:
        twitter_api = twitter_login()
        for gameID in sys.argv[1:len(sys.argv)]:
            find_dunks_for_game(gameID, twitter_api)
