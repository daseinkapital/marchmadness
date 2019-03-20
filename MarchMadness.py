# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 10:33:38 2019

@author: 591168
"""

import random


class MarchMadness:
    
    def __init__(self):
        self.upsets = 0
        self.bracket_round = 0 
    
        self.teams = [
            {'division': 'east',
             'match_ups': [
                     ['Duke (1)', 'NDS/NCC (16)'],
                     ['VCU (8)', 'UCF (9)'],
                     ['Mississippi St (5)', 'Liberty (12)'],
                     ['Virginia Tech (4)', 'Saint Louis (13)'],
                     ['Maryland (6)', 'Belmont (11)'],
                     ['LSU (3)', 'Yale (14)'],
                     ['Louisville (7)', 'Minnesota (10)'],
                     ['Michigan St (2)', 'Bradley (15)']
                 ]
            },
            {'division': 'south',
             'match_ups': [ 
                     ['Virginia (1)', 'Gardner-Webb (16)'],
                     ['Ole Miss (8)', 'Oklahoma (9)'],
                     ['Wisconsin (5)', 'Oregon (12)'],
                     ['Kansas State (4)', 'UC Irvine (13)'],
                     ['Villanova (6)', 'Saint Mary\'s (11)'],
                     ['Purdue (3)', 'Old Dominion (14)'],
                     ['Cincinnati (7)', 'Iowa (10)'],
                     ['Tennessee (2)', 'Colgate (15)']
                 ]
            },
            {'division': 'west',
             'match_ups': [
                     ['Gonzaga (1)', 'F. Dickinson (16)'],
                     ['Syracuse (8)', 'Baylor (9)'],
                     ['Marquette (5)', 'Murray State (12)'],
                     ['Florida St (4)', 'Vermont (13)'],
                     ['Buffalo (6)', 'ASU/SJU (11)'],
                     ['Texas Tech (3)', 'N Kentucky (14)'],
                     ['Nevada (7)', 'Florida (10)'],
                     ['Michigan (2)', 'Montana (15)']
                 ]
            },
            {'division': 'midwest',
             'match_ups': [ 
                     ['North Carolina (1)', 'Iona (16)'],
                     ['Utah State (8)', 'Washington (9)'],
                     ['Auburn (5)', 'New Mexico St (12)'],
                     ['Kansas (4)', 'Northeastern (13)'],
                     ['Iowa State (6)', 'Ohio State (11)'],
                     ['Houston (3)', 'Georgia State (14)'],
                     ['Wofford (7)', 'Seton Hall (10)'],
                     ['Kentucky (2)', 'Abil Christian (15)']
                 ]
            },
        ]
            
        self.champs = {}
    
    def coin_toss(self):
        for division in self.teams:
            print("{} :".format(division['division']))
            match_ups = division['match_ups']
            
            self.bracket_round = 0    
            self.pick_round_coin_toss(match_ups)
            self.champs[division['division']] = self.winner

            print("\n\n\n")
        
        self.final_four()
            
        print("upsets", self.upsets)
                    
    def pick_round_coin_toss(self, match_ups):
        self.bracket_round += 1
        print(" \nRound {} \n".format(self.bracket_round))
        next_round = []
        for i in range(len(match_ups)):
            coin_toss = random.randint(0, 1)
            if self.team_ranking(match_ups[i][coin_toss]) > self.team_ranking(match_ups[i][coin_toss-1]):
                self.upsets += 1
            print("{} beats {}".format(match_ups[i][coin_toss], match_ups[i][coin_toss-1]))
            if (i%2 == 0):
                next_match_up = [match_ups[i][coin_toss]]
            else:
                next_match_up.append(match_ups[i][coin_toss])        
                next_round.append(next_match_up)
        if len(next_round) > 1:
            self.pick_round_coin_toss(next_round)
        
        else:
            self.bracket_round += 1
            print(" \nRound {} \n".format(self.bracket_round))
            coin_toss = random.randint(0, 1)
            if self.team_ranking(next_round[0][coin_toss]) > self.team_ranking(next_round[0][coin_toss-1]):
                self.upsets += 1
            print("{} beats {}".format(next_round[0][coin_toss], next_round[0][coin_toss-1]))
            self.winner = next_round[0][coin_toss]
        
    def team_ranking(self, team):
        start = team.find("(") + 1
        end = team.find(")")
        return int(team[start:end])
    
    def final_four(self):
        championship = []
        match_ups = [[self.champs['east'], self.champs['west']], [self.champs['south'], self.champs['midwest']]]
        self.bracket_round += 1
        print(" \nRound {} \n".format(self.bracket_round))
        
        print("Final Four East/West:")
        coin_toss = random.randint(0, 1)
        if self.team_ranking(match_ups[0][coin_toss]) > self.team_ranking(match_ups[0][coin_toss-1]):
            self.upsets += 1
        print("{} beats {}".format(match_ups[0][coin_toss], match_ups[0][coin_toss-1]))
        championship.append(match_ups[0][coin_toss])
        
        print("Final Four South/Midwest:")
        coin_toss = random.randint(0, 1)
        if self.team_ranking(match_ups[1][coin_toss]) > self.team_ranking(match_ups[1][coin_toss-1]):
            self.upsets += 1
        print("{} beats {}".format(match_ups[1][coin_toss], match_ups[1][coin_toss-1]))
        championship.append(match_ups[1][coin_toss])
        
        self.bracket_round += 1
        print(" \nRound {} \n".format(self.bracket_round))
        print("Championship")
        coin_toss = random.randint(0, 1)
        if self.team_ranking(championship[coin_toss]) > self.team_ranking(championship[coin_toss-1]):
            self.upsets += 1
        print("{} beats {} to take the Championship".format(championship[coin_toss], championship[coin_toss-1]))
    