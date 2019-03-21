# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 10:33:38 2019

@author: 591168
"""

import random
from urllib.request import urlopen, Request
import urllib.parse
import urllib.request

import re

from bs4 import BeautifulSoup as bs

#grabs the html of a url
def fetch_url(url):
    url = url.encode('ascii', errors="ignore").decode()
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req)
    soup = bs(html, "html.parser")
    return soup

#finds the team names and ranks and returns the matchup
#[{'name' : 'team1', 'rank': #}, {'name' : 'team2', 'rank': #}]
def parse_teams(match):
    num_regex = r'(br/>|dt>)(\d{1,2})'
    name_regex = r'(>)([A-Z]\w+)'
    
    ranks = re.findall(num_regex, str(match))
    names = re.findall(name_regex, str(match))
    
    matchup = [{'name': names[0][1], 'rank': int(ranks[0][1])}, {'name': names[1][1], 'rank': int(ranks[1][1])}]
    
    return matchup

#returns the matchups of each region
def parse_region(region):
    while region.find('dd'):
        region.find('dd').decompose()
    matches = region.findAll("dl", {"class": "match round1"})
    matchups = []
    for i, match in enumerate(matches):
        matchups.append(parse_teams(match))
        
    return matchups
            
        
def get_teams():
    #make assumption that espn updates this link every year otherwise kmn
    url = 'http://www.espn.com/mens-college-basketball/tournament/bracket'
    
    html = fetch_url(url)
    
    east, west, south, midwest = html.findAll("div", {"class": "region"})
    
    teams = []
    
    teams.append({'division': 'east', 'match_ups': parse_region(east)})
    teams.append({'division': 'west', 'match_ups': parse_region(west)})
    teams.append({'division': 'south', 'match_ups': parse_region(south)})
    teams.append({'division': 'midwest', 'match_ups': parse_region(midwest)})
    
    return teams
    
def strip_score(score):
    score_regex = r'([0-9]{1,3})-([0-9]{1,3})'
    match = re.findall(score_regex, str(score))[0]
    return match[0], match[1]

def get_finals_scores():
    url = 'https://www.ncaa.com/history/basketball-men/d1'
    
    html = fetch_url(url)
    
    data_table = html.find('tbody')
    rows = data_table.findAll('tr')
    
    past_scores = []
    
    for row in rows:
        cols = row.findAll('td')
        year = cols[0].text
        score = cols[3]
        winner, loser = strip_score(score)
        past_scores.append({'year': year, 'winning_score': int(winner), 'losing_score': int(loser)})
        
    return past_scores


class MarchMadness:
    
    def __init__(self, evaluation_metric):
        self.upsets = 0
        self.bracket_round = 0 
    
        #grabs the current teams
        self.teams = get_teams()
        
        #contains year, winning_score, losing_score for all championship games going back to 1939
        self.past_finals_scores = get_finals_scores()
        
        self.evaluation_metric = evaluation_metric
            
        self.champs = {}
    
    def run_bracket(self):
        for division in self.teams:
            print("{} :".format(division['division']))
            match_ups = division['match_ups']
            
            self.bracket_round = 0    
            self.pick_round(match_ups)
            self.champs[division['division']] = self.winner

            print("\n\n\n")
        
        self.final_four()
            
        print("upsets", self.upsets)
                    
    def pick_round(self, match_ups):
        self.bracket_round += 1
        print(" \nRound {} \n".format(self.bracket_round))
        next_round = []
        for i in range(len(match_ups)):
            winner = self.evaluation_metric(match_ups[i])
            self.check_upset(match_ups[i][winner], match_ups[i][winner-1])
            print("{} beats {}".format(self.str_team(match_ups[i][winner]), self.str_team(match_ups[i][winner-1])))
            if (i%2 == 0):
                next_match_up = [match_ups[i][winner]]
            else:
                next_match_up.append(match_ups[i][winner])        
                next_round.append(next_match_up)
        if len(next_round) > 1:
            self.pick_round(next_round)
        
        else:
            self.bracket_round += 1
            print(" \nRound {} \n".format(self.bracket_round))
            winner = self.evaluation_metric(next_round[0])
            self.check_upset(next_round[0][winner], next_round[0][winner-1])
            print("{} beats {}".format(self.str_team(next_round[0][winner]), self.str_team(next_round[0][winner-1])))
            self.winner = next_round[0][winner]
    
    # Stringify the team name and include the rank
    def str_team(self, team):
        return "{0} ({1})".format(team['name'], team['rank'])
    
    # Check if winner upset loser
    def check_upset(self, winning_team, losing_team):
        if winning_team['rank'] > losing_team['rank']:
            self.upsets += 1
    
    # Run final four bracket
    def final_four(self):
        championship = []
        match_ups = [[self.champs['east'], self.champs['west']], [self.champs['south'], self.champs['midwest']]]
        self.bracket_round += 1
        print(" \nRound {} \n\n".format(self.bracket_round))
        
        print("Final Four East/West:")
        winner = self.evaluation_metric(match_ups[0])
        self.check_upset(match_ups[0][winner], match_ups[0][winner-1])
        print("{} beats {}".format(self.str_team(match_ups[0][winner]), self.str_team(match_ups[0][winner-1])))
        championship.append(match_ups[0][winner])
        
        print("Final Four South/Midwest:")
        winner = self.evaluation_metric(match_ups[1])
        self.check_upset(match_ups[1][winner], match_ups[1][winner-1])
        print("{} beats {}".format(self.str_team(match_ups[1][winner]), self.str_team(match_ups[1][winner-1])))
        championship.append(match_ups[1][winner])
        
        self.bracket_round += 1
        print(" \nRound {} \n".format(self.bracket_round))
        print("Championship")
        winner = self.evaluation_metric(championship)
        self.check_upset(championship[winner], championship[winner-1])
        print("{} beats {} to take the Championship".format(self.str_team(championship[winner]), self.str_team(championship[winner-1])))
 
    def championship_score_range(self):
        min_lose = 10000
        min_win = 10000
        max_lose = 0
        max_win = 0
        
        for score in self.past_finals_scores:
            if score['winning_score'] > max_win:
                max_win = score['winning_score']
            if score['winning_score'] < min_win:
                min_win = score['winning_score']
            if score['losing_score'] > max_lose:
                max_lose = score['losing_score']
            if score['losing_score'] < min_lose:
                min_lose = score['losing_score']
        
        return min_win, max_win, min_lose, max_lose
    
    
    def random_championship_score(self):
        min_win, max_win, min_lose, max_lose = self.championship_score_range()
        
        winning_score = random.randint(min_win, max_win)
        
        losing_score = 1000000
        while (losing_score > winning_score):
            losing_score = random.randint(min_lose, max_lose)
        
        print("FINAL SCORE: {0} - {1}".format(winning_score, losing_score))
    
    ####### EVALUTION METRICS
    #this is where you should take the match (has rank and name of team) and then decide who wins, returning 0 for the first team and 1 for the second team
    
    #here is a simple coin toss evaluation
    def coin_toss(match):
        return random.randint(0, 1)
    
    #here is a rankings evaluation (coin toss if teams are equal)
    def rankings(match):
        team1 = match[0]
        team2 = match[1]
        
        if team1['rank'] < team2['rank']:
            return 0
        elif team2['rank'] < team1['rank']:
            return 1
        else:
            return random.randint(0, 1)