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
    ranks = match.findAll('span', {'class': 'seed'})
    teams = match.findAll('span', {'class': 'name'})

    rank1 = ranks[0].text
    team1 = teams[0].text
    rank2 = ranks[1].text
    team2 = teams[1].text
    matchup = [{'name': team1, 'rank': int(rank1)}, {'name': team2, 'rank': int(rank2)}]
    return matchup

def parse_region(region):
    round1 = region.findAll('div', {'class': 'round-1'})[0]
    matches = round1.findAll('div', {'class': 'play-pod'})
    
    matchups = []
    for match in matches:
        matchups.append(parse_teams(match))
        
    return matchups

def get_teams():
    
    url = 'https://www.ncaa.com/brackets/basketball-men/d1'
    
    html = fetch_url(url)
    
    east, west, south, midwest = html.findAll("div", {"class": "region"})[1:]
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

def get_team_win_loss_percentages():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/168"
    paginations = ['', '/p2', '/p3', '/p4', '/p5', '/p6', '/p7', '/p8']

    data = []    
    for page in paginations:
        html = fetch_url(url + page)
        
        data_table = html.find('tbody')
        rows = data_table.findAll('tr')
        
        for row in rows:
            cols = row.findAll('td')
            name = row.find('a')
            team_name = name.text
            wins = int(cols[2].text)
            loses = int(cols[3].text)
            pct = float(cols[4].text)
            data.append({'team_name': team_name, 'wins': wins, 'loses': loses, 'pct': pct})
        
    print(data)
            
        # finish this algorithm via webscraping
        # http://www.mathaware.org/mam/2010/essays/ChartierBracketology.pdf

class MarchMadness:
    
    def __init__(self, evaluation_metric):
        self.upsets = 0
        self.bracket_round = 0 
        self.pretty_print = True
    
        #grabs the current teams
        self.teams = get_teams()
        
        self.round1 = self.teams.copy()
        self.round2 = []
        self.round3 = []
        self.round4 = []
        self.round5 = []
        self.round6 = []
        
        #contains year, winning_score, losing_score for all championship games going back to 1939
        self.past_finals_scores = get_finals_scores()
        
        self.evaluation_metric = evaluation_metric
            
        self.champs = {}
        self.champion = '';
    
    def run_bracket_statistic(self, pretty_print=True):
        self.pretty_print = pretty_print
        for division in self.teams:
            if not self.pretty_print:
                print("{} :".format(division['division']))
            match_ups = division['match_ups']
            
            self.bracket_round = 0    
            self.pick_round(division['division'], match_ups)
            self.champs[division['division']] = self.winner

            if not self.pretty_print:
                print("\n\n\n")
        
        self.final_four()
        
        if self.pretty_print:
            self.pretty_print_bracket()
            self.pretty_print_final_four()
            
        print("\n\nupsets", self.upsets)
                    
    def pick_round(self, division, match_ups):
        self.bracket_round += 1
        if self.bracket_round == 2:
            self.round2.append({'division': division, 'match_ups': match_ups})
        elif self.bracket_round == 3:
            self.round3.append({'division': division, 'match_ups': match_ups})
        if not self.pretty_print:
            print(" \nRound {} \n".format(self.bracket_round))
        next_round = []
        for i in range(len(match_ups)):
            winner = self.evaluation_metric(match_ups[i])
            self.check_upset(match_ups[i][winner], match_ups[i][winner-1])
            if not self.pretty_print:
                print("{} beats {}".format(self.str_team(match_ups[i][winner]), self.str_team(match_ups[i][winner-1])))
            if (i%2 == 0):
                next_match_up = [match_ups[i][winner]]
            else:
                next_match_up.append(match_ups[i][winner])        
                next_round.append(next_match_up)
        if len(next_round) > 1:
            self.pick_round(division, next_round)
        
        else:
            self.bracket_round += 1
            self.round4.append({'division': division, 'match_ups': match_ups})
            if not self.pretty_print:
                print(" \nRound {} \n".format(self.bracket_round))
            winner = self.evaluation_metric(next_round[0])
            self.check_upset(next_round[0][winner], next_round[0][winner-1])
            if not self.pretty_print:
                print("{} beats {}".format(self.str_team(next_round[0][winner]), self.str_team(next_round[0][winner-1])))
            self.winner = next_round[0][winner]
    
    # Stringify the team name and include the rank
    def str_team(self, team):
        return "{0} ({1})".format(team['name'], team['rank'])
    
    #for printing purposes of final pracket
    def preprocess_team_print(self, team):
        #get the team's length
        team_len = len(self.str_team(team))
        length = self.get_length_of_longest_team_name()
        diff = length - team_len
        print_str = self.str_team(team)
        print_str += " " * diff
        return print_str
    
    # Get the names of all the teams playing
    def get_all_team_names(self):
        team_names = []
        for division in self.teams:
            matchups = division['match_ups']
            for game in matchups:
                team_names.append(game[0])
                team_names.append(game[1])
        
        return team_names
    
    #return the length of the longest team name
    def get_length_of_longest_team_name(self):
        longest_name = 0
        team_names = self.get_all_team_names()
        for name in team_names:
            if len(self.str_team(name)) > longest_name:
                longest_name = len(self.str_team(name))
        
        return longest_name
    
    def pretty_print_bracket(self):
        divisions = ['East', 'West', 'South', 'Midwest']
        tab = self.get_length_of_longest_team_name()
        
        spaces = " " * tab
        overscores = "‾" * tab
        team_return = "{}\n"
        team_cont = "{}|"
        end = "|"
        
        #division name plus a new line
        bracket_str = "{}\n\n"
        
        bracket_str += team_return
        bracket_str += overscores + end + team_return        
        bracket_str += team_cont + overscores + end + '\n'
        bracket_str += overscores + " " + spaces + end + team_return
        bracket_str += team_cont[:-1] + " " + spaces + end + overscores + end + '\n'
        bracket_str += overscores + end + team_cont + spaces + end + '\n'
        bracket_str += team_cont + overscores + " " + spaces + end + '\n'
        bracket_str += overscores + " " + spaces + " " + spaces + end + team_return
        bracket_str += team_cont[:-1] + " " + spaces + " " + spaces + end + overscores + end + '\n'
        bracket_str += overscores + end + team_cont[:-1] + " " + spaces + end + spaces + end + '\n'
        bracket_str += team_cont + overscores + end + spaces + end + spaces + end + '\n'
        bracket_str += overscores + ' ' + spaces + end + team_cont + spaces + end + '\n'
        bracket_str += team_cont[:-1] + ' ' + spaces + end + overscores + ' ' + spaces + end + '\n'
        bracket_str += overscores + end + team_cont +  spaces + ' ' + spaces + end + '\n'
        bracket_str += team_cont + overscores + ' ' + spaces + ' ' + spaces + end + '\n'
        bracket_str += overscores + ' ' + spaces + ' ' + spaces + ' ' + spaces + end + team_return
        bracket_str += team_cont[:-1] + ' ' + spaces + ' ' + spaces + ' ' + spaces + end + overscores + '\n'
        bracket_str += overscores + end + team_cont[:-1] + ' ' + spaces + ' ' + spaces + end + '\n'    
        bracket_str += team_cont + overscores + end + spaces + ' ' + spaces + end + '\n'
        bracket_str += overscores + " " + spaces + end + team_cont[:-1] + ' ' + spaces + end + '\n'
        bracket_str += team_cont[:-1] + " " + spaces + end + overscores + end + spaces + end + '\n'
        bracket_str += overscores + end + team_cont + spaces + end + spaces + end + '\n'
        bracket_str += team_cont + overscores + " " + spaces + end + spaces + end + '\n'
        bracket_str += overscores + " " + spaces + " " + spaces + end + team_cont + '\n'
        bracket_str += team_cont[:-1] + " " + spaces + " " + spaces + end + overscores + '\n'
        bracket_str += overscores + end + team_cont[:-1] + " " + spaces + end + '\n'
        bracket_str += team_cont + overscores + end + spaces + end + '\n'
        bracket_str += overscores + ' ' + spaces + end + team_cont + '\n'
        bracket_str += team_cont[:-1] + ' ' + spaces + end + overscores + '\n'
        bracket_str += overscores + end + team_cont + '\n'
        bracket_str += team_cont + overscores + '\n'
        bracket_str += overscores + '\n'
        
        division_str = []
        
        i = 0
        
        for division in divisions:
            division_str.append({'div' : division, 'bracket': bracket_str})
            for corner in self.round1:
                if corner['division'] == division.lower():
                    round1 = corner['match_ups']
            for corner in self.round2:
                if corner['division'] == division.lower():
                    round2 = corner['match_ups']
            for corner in self.round3:
                if corner['division'] == division.lower():
                    round3 = corner['match_ups']
            for corner in self.round4:
                if corner['division'] == division.lower():
                    round4 = corner['match_ups']
            champ = self.champs[division.lower()]
            
            division_str[i]['bracket'] = division_str[i]['bracket'].format(
                    division,
                    self.preprocess_team_print(round1[0][0]),
                    self.preprocess_team_print(round2[0][0]),
                    self.preprocess_team_print(round1[0][1]),
                    self.preprocess_team_print(round3[0][0]),
                    self.preprocess_team_print(round1[1][0]),
                    self.preprocess_team_print(round2[0][1]),
                    self.preprocess_team_print(round1[1][1]),
                    self.preprocess_team_print(round4[0][0]),
                    self.preprocess_team_print(round1[2][0]),
                    self.preprocess_team_print(round2[1][0]),
                    self.preprocess_team_print(round1[2][1]),
                    self.preprocess_team_print(round3[0][1]),
                    self.preprocess_team_print(round1[3][0]),
                    self.preprocess_team_print(round2[1][1]),
                    self.preprocess_team_print(round1[3][1]),
                    self.preprocess_team_print(champ),
                    self.preprocess_team_print(round1[4][0]),
                    self.preprocess_team_print(round2[2][0]),
                    self.preprocess_team_print(round1[4][1]),
                    self.preprocess_team_print(round3[1][0]),
                    self.preprocess_team_print(round1[5][0]),
                    self.preprocess_team_print(round2[2][1]),
                    self.preprocess_team_print(round1[5][1]),
                    self.preprocess_team_print(round4[0][1]),
                    self.preprocess_team_print(round1[6][0]),
                    self.preprocess_team_print(round2[3][0]),
                    self.preprocess_team_print(round1[6][1]),
                    self.preprocess_team_print(round3[1][1]),
                    self.preprocess_team_print(round1[7][0]),
                    self.preprocess_team_print(round2[3][1]),
                    self.preprocess_team_print(round1[7][1])
                    )
        
            print(division_str[i]['bracket'])
            i += 1

    def pretty_print_final_four(self):
        tab = self.get_length_of_longest_team_name()
        
        spaces = " " * tab
        overscores = "‾" * tab
        team_return = "{}\n"
        team_cont = "{}|"
        end = "|"
        
        bracket_str = "Final Four and Championship \n\n"
        bracket_str += team_return
        bracket_str += overscores + end + team_return        
        bracket_str += team_cont + overscores + end + '\n'
        bracket_str += overscores + " " + spaces + end + team_return
        bracket_str += team_cont[:-1] + " " + spaces + end + overscores + '\n'
        bracket_str += overscores + end + team_cont + '\n'
        bracket_str += team_cont + overscores + '\n'
        bracket_str += overscores
        
        bracket_str = bracket_str.format(
                self.preprocess_team_print(self.round5[0][0]),
                self.preprocess_team_print(self.round6[0]),
                self.preprocess_team_print(self.round5[0][1]),
                self.preprocess_team_print(self.champion),
                self.preprocess_team_print(self.round5[1][0]),
                self.preprocess_team_print(self.round6[1]),
                self.preprocess_team_print(self.round5[1][1])
                )
        
        print(bracket_str)
        
            
    # Check if winner upset loser
    def check_upset(self, winning_team, losing_team):
        if winning_team['rank'] > losing_team['rank']:
            self.upsets += 1
    
    # Run final four bracket
    def final_four(self):
        championship = []
        match_ups = [[self.champs['east'], self.champs['west']], [self.champs['south'], self.champs['midwest']]]
        self.round5 = match_ups
        self.bracket_round += 1
        winner = self.evaluation_metric(match_ups[0])
        self.check_upset(match_ups[0][winner], match_ups[0][winner-1])
        
        if not self.pretty_print:
            print(" \nRound {} \n\n".format(self.bracket_round))
            print("Final Four East/West:")
            print("{} beats {}".format(self.str_team(match_ups[0][winner]), self.str_team(match_ups[0][winner-1])))
        championship.append(match_ups[0][winner])
        
        winner = self.evaluation_metric(match_ups[1])
        self.check_upset(match_ups[1][winner], match_ups[1][winner-1])
        if not self.pretty_print:
            print("Final Four South/Midwest:")
            print("{} beats {}".format(self.str_team(match_ups[1][winner]), self.str_team(match_ups[1][winner-1])))
        championship.append(match_ups[1][winner])
        
        self.bracket_round += 1
        self.round6 = championship
        winner = self.evaluation_metric(championship)
        self.check_upset(championship[winner], championship[winner-1])
        self.champion = championship[winner]
        if not self.pretty_print:
            print(" \nRound {} \n".format(self.bracket_round))
            print("Championship")
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
    
    #tries to reduce upsets, while leaving a possibility for them
    def weighted_rankings(match):
        team1 = match[0]
        team2 = match[1]
        
        rank_delta = team1['rank'] - team2['rank']
        
        #if the teams are evenly matched, pick one at random
        if rank_delta == 0:
            return random.randint(0, 1)
        elif rank_delta < 0:
            rank_delta = rank_delta * -1
        
        # gives a 4.5% chance (compounding) of ranking diff
        game_split = (1.045 ** rank_delta)
        
        better_ranked_team_win_percentage = 0.5 * game_split
        

        if random.random() < better_ranked_team_win_percentage:            
            if team1['rank'] < team2['rank']:
                return 0
            elif team2['rank'] < team1['rank']:
                return 1
        else:
            if team1['rank'] > team2['rank']:
                return 0
            elif team2['rank'] > team1['rank']:
                return 1
            
madness = MarchMadness(MarchMadness.weighted_rankings)
madness.run_bracket_statistic()