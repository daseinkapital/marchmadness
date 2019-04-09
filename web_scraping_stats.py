# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:59:03 2019

@author: 591168
"""

from urllib.request import urlopen, Request
import urllib.parse
import urllib.request

import re
import copy

from bs4 import BeautifulSoup as bs

#grabs the html of a url
def fetch_url(url):
    url = url.encode('ascii', errors="ignore").decode()
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req)
    soup = bs(html, "html.parser")
    return soup


#def parse_teams(match):
#    num_regex = r'(br/>|dt>)(\d{1,2})'
#    name_regex = r'(>)([A-Z]\w+)'
#    
#    ranks = re.findall(num_regex, str(match))
#    names = re.findall(name_regex, str(match))
#    
#    matchup = [{'name': names[0][1], 'rank': int(ranks[0][1])}, {'name': names[1][1], 'rank': int(ranks[1][1])}]
#    
#    return matchup
#
##returns the matchups of each region
#def parse_region(region):
#    while region.find('dd'):
#        region.find('dd').decompose()
#    matches = region.findAll("dl", {"class": "match round1"})
#    matchups = []
#    for i, match in enumerate(matches):
#        matchups.append(parse_teams(match))
#        
#    return matchups
#            
#        
#def get_teams():
#    #make assumption that espn updates this link every year otherwise kmn
#    url = 'http://www.espn.com/mens-college-basketball/tournament/bracket'
#    
#    #refactor for this url
#    #https://www.ncaa.com/brackets/basketball-men/d1
#    
#    html = fetch_url(url)
#    
#    east, west, south, midwest = html.findAll("div", {"class": "region"})
#    
#    
#    teams = []
#    
#    teams.append({'division': 'east', 'match_ups': parse_region(east)})
#    teams.append({'division': 'west', 'match_ups': parse_region(west)})
#    teams.append({'division': 'south', 'match_ups': parse_region(south)})
#    teams.append({'division': 'midwest', 'match_ups': parse_region(midwest)})
#    
#    return teams


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

get_teams()

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

def get_three_point_attempts():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/625"
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
            
            #number of games three point data is based on
            tpa_gm = int(cols[2].text)
            
            #total field goals made
            tfg = int(cols[3].text)
            
            #total field goals attempted
            tfga = int(cols[4].text)
            
            
            data.append({'team_name': team_name, 'tpa_gm': tpa_gm, '3fg': tfg, '3fga': tfga})
        
    return data

def get_assist_turnover_ratio():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/474"
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
            
            #number of games assist/turnover ratio is based on
            atr_gm = int(cols[2].text)
            
            #number of assists
            ast = int(cols[3].text)
            
            #number of turnovers
            to = int(cols[4].text)
            
            #ratio of assists to turnovers
            ratio = float(cols[5].text)
            
            data.append({'team_name': team_name, 'atr_gm': atr_gm, 'ast': ast, 'to': to, 'ratio': ratio})
        
    return data

def get_assist_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/214"
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
            
            #number of games the assists per game is based on
            apg_gm = int(cols[2].text)
            
            #number of assists
            ast = int(cols[3].text)
            
            #number of assists per game
            apg = float(cols[4].text)
            data.append({'team_name': team_name, 'apg_gm': apg_gm, 'ast': ast, 'apg': apg})
        
    return data

def get_blocked_shots_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/216"
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
            
            #number of games blocked shots per game data is calculated on
            bspg_gm = int(cols[2].text)
            
            #number of blocks
            blks = int(cols[3].text)
            
            #blocks per game
            bkpg = float(cols[4].text)
            
            data.append({'team_name': team_name, 'bspg_gm': bspg_gm, 'blks': blks, 'bkpg': bkpg})
        
    return data

def get_defensive_rebounds_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/859"
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
            
            #number of games defensive rebounds is based on
            def_reb_gm = int(cols[2].text)
            
            #number of defensive rebounds
            drebs = int(cols[3].text)
            
            #number of defensive rebounds per game
            rpg = float(cols[4].text)
            
            data.append({'team_name': team_name, 'def_reb_gm': def_reb_gm, 'drebs': drebs, 'rpg': rpg})
        
    return data

def get_fewest_fouls():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/642"
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
            
            #number of games fewest fouls is based on
            foul_gm = int(cols[2].text)
            
            #foul numbers
            fouls = int(cols[3].text)
            
            
            data.append({'team_name': team_name, 'foul_gm': foul_gm, 'fouls': fouls})
        
    return data

def get_fewest_turnovers():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/640"
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
            
            #number of games fewest turnovers is based on
            fto_gm = int(cols[2].text)
            
            #fewest turnovers data
            fto = int(cols[3].text)
            
            data.append({'team_name': team_name, 'fto_gm': fto_gm, 'fto': fto})
        
    return data

def get_field_goal_percentage():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/148"
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
            
            #number of games the field goal data is based on
            fg_gm = int(cols[2].text)
            
            #field goals made
            fgm = int(cols[3].text)
            
            #field goals attempted
            fga = int(cols[4].text)
            
            #field goal percentage
            fgp = float(cols[5].text)
            
            data.append({'team_name': team_name, 'fg_gm': fg_gm, 'fgm': fgm, 'fga': fga, 'fgp': fgp})
        
    return data

def get_field_goal_percentage_defense():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/149"
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
            
            #number of games the field goal defense data is based on
            fgd_gm = int(cols[2].text)
            
            #field goals made
            opp_fgm = int(cols[3].text)
            
            #field goals attempted
            opp_fga = int(cols[4].text)
            
            #field goal percentage
            opp_fgp = float(cols[5].text)
            
            data.append({'team_name': team_name, 'fgd_gm': fgd_gm, 'opp_fgm': opp_fgm, 'opp_fga': opp_fga, 'opp_fgp': opp_fgp})
        
    return data

def get_free_throw_attempts():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/638"
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
            
            
            #number of games free throw attempts are based on
            fta_gm = int(cols[2].text)
            
            #free throws made from attempts
            ftam = int(cols[3].text)
            
            #free throw attemped
            ftaa = float(cols[4].text)
            
            data.append({'team_name': team_name, 'fta_gm': fta_gm, 'ftam': ftam, 'ftaa': ftaa})
        
    return data

def get_free_throw_made():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/633"
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
            
            #number of games for ftm
            ftm_gm = int(cols[2].text)
            
            #free throws made
            ftm = int(cols[3].text)
            
            #free throws attempted
            fta = int(cols[4].text)
                        
            data.append({'team_name': team_name, 'ftm_gm': ftm_gm, 'ftm': ftm, 'fta': fta})
        
    return data

def get_free_throw_percentage():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/150"
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
            
            #number of games for ftp
            ftp_gm = int(cols[2].text)
            
            #free throws made
            ftpm = int(cols[3].text)
            
            #free throws attempted
            ftpa = int(cols[4].text)
            
            #free throw percentage
            ftp = float(cols[5].text)
                        
            data.append({'team_name': team_name, 'ftp_gm': ftp_gm, 'ftpm': ftpm, 'ftpa': ftpa, 'ftp': ftp})
        
    return data

def get_offensive_rebounds_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/857"
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
            
            #number of games for offensive rebounds per game
            orpg_gm = int(cols[2].text)
            
            #offensive rebounds made
            orebs = int(cols[3].text)
            
            #number of offensive rebounds per game
            rpg = float(cols[4].text)
            
            data.append({'team_name': team_name, 'orpg_gm': orpg_gm, 'orebs': orebs, 'rpg': rpg})
        
    return data

def get_personal_fouls_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/286"
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
            
            #number of games for personal fouls per game
            pfpg_gm = int(cols[2].text)
            
            #personal fouls
            pfouls = int(cols[3].text)
            
            #number of personal fouls per game
            pfpg = float(cols[4].text)
            
            #number of foul outs
            dq = int(cols[5].text)
            
            data.append({'team_name': team_name, 'pfpg_gm': pfpg_gm, 'pfouls': pfouls, 'pfpg': pfpg, 'dq': dq})
        
    return data

def get_rebound_margin():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/151"
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
            
            #number of games for rebound margins
            rm_gm = int(cols[2].text)
            
            #rebounds
            rm_reb = int(cols[3].text)
            
            #rebounds per game
            rm_rpg = float(cols[4].text)
            
            #opponent rebounds
            rm_opp_reb = int(cols[5].text)
            
            #opponent rebounds per game
            rm_opp_rpg = float(cols[6].text)
            
            #rebound margin
            rm = float(cols[7].text)
            
            data.append({'team_name': team_name, 'rm_gm': rm_gm, 'rm_reb': rm_reb, 'rm_rpg': rm_rpg, 'rm_opp_reb': rm_opp_reb, 'rm_opp_rpg': rm_opp_rpg, 'rm': rm})
        
    return data

def get_scoring_defense():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/146"
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
            
            #number of games for scoring defense
            sd_gm = int(cols[2].text)
            
            #opponent's points scored
            opp_pts = int(cols[3].text)
            
            #opponent's points per game
            opp_ppg = float(cols[4].text)
                        
            data.append({'team_name': team_name, 'sd_gm': sd_gm, 'opp_pts': opp_pts, 'opp_ppg': opp_ppg})
        
    return data

def get_scoring_margin():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/147"
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
            
            #number of games for scoring defense
            sm_gm = int(cols[2].text)
            
            #points scored
            pts_scr = int(cols[3].text)
            
            #points per game
            ppg_scr = float(cols[4].text)
            
            #opponent's points scored
            sm_opp_pts = int(cols[5].text)
            
            #opponent's points per game
            sm_opp_ppg = float(cols[6].text)
            
            #score margin
            scr_mar = float(cols[7].text)
                        
            data.append({'team_name': team_name, 'sm_gm': sm_gm, 'pts_scr': pts_scr, 'ppg_scr': ppg_scr, 'sm_opp_pts': sm_opp_pts, 'sm_opp_ppg': sm_opp_ppg, 'scr_mar': scr_mar})
        
    return data

def get_scoring_offense():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/145"
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
            
            #number of games for scoring defense
            so_gm = int(cols[2].text)
            
            #points scored
            so_pts = int(cols[3].text)
            
            #points per game
            so_ppg = float(cols[4].text)
                        
            data.append({'team_name': team_name, 'so_gm': so_gm, 'so_pts': so_pts, 'so_ppg': so_ppg})
        
    return data

def get_steals_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/215"
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
            
            #number of games for steals
            spg_gm = int(cols[2].text)
            
            #steals
            steals = int(cols[3].text)
            
            #steals per game
            spg = float(cols[4].text)
                        
            data.append({'team_name': team_name, 'spg_gm': spg_gm, 'steals': steals, 'spg': spg})
        
    return data

def get_three_pt_fg_defense():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/518"
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
            
            #number of games for three point defense
            tpfgd_gm = int(cols[2].text)
            
            #opposition 3 pt field goal attempts
            opp_tpfga = int(cols[3].text)
            
            #steals per game
            opp_tpfg = int(cols[4].text)
            
            #not sure what this
            tpfg_pct = float(cols[5].text)
            
            data.append({'team_name': team_name, 'tpfgd_gm': tpfgd_gm, 'opp_tpfga': opp_tpfga, 'opp_tpfg': opp_tpfg, 'tpfg_pct': tpfg_pct})
        
    return data

def get_three_pt_fg_per_game():
    url = "https://www.ncaa.com/stats/basketball-men/d1/current/team/153"
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
            
            #number of games for three points per game
            tpfgpg_gm = int(cols[2].text)
            
            #three point field goals
            tpfg = int(cols[3].text)
            
            #threes per game
            tpfgpg = float(cols[4].text)
                        
            data.append({'team_name': team_name, 'tpfgpg_gm': tpfgpg_gm, 'tpfg': tpfg, 'tpfgpg': tpfgpg})
        
    return data

def get_win_loss_percentages():
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
        
    return data

def team_statistics_info():
    return """

    

    """

def get_all_team_statistics():
    
    team_stats = {}
    
    all_stat_functions = [
            get_three_point_attempts,
            get_assist_turnover_ratio,
            get_assist_per_game,
            get_blocked_shots_per_game,
            get_defensive_rebounds_per_game,
            get_fewest_fouls,
            get_fewest_turnovers,
            get_field_goal_percentage,
            get_field_goal_percentage_defense,
            get_free_throw_attempts,
            get_free_throw_made,
            get_free_throw_percentage,
            get_offensive_rebounds_per_game,
            get_personal_fouls_per_game,
            get_rebound_margin,
            get_scoring_defense,
            get_scoring_margin,
            get_scoring_offense,
            get_steals_per_game,
            get_three_pt_fg_defense,
            get_three_pt_fg_per_game,
            get_win_loss_percentages
            ]
    
    for stat in all_stat_functions:
        
        stats = stat()

        for team in stats:
            if team['team_name'] not in team_stats:
                team_stats[team['team_name']] = {}
            new_stats = team.copy()
            new_stats.pop('team_name')
            for key in new_stats:
                team_stats[team['team_name']][key] = new_stats[key]
    
    #returns the 
    first_matchup = get_teams()[0]['match_ups'][0]
    print(first_matchup[0]['name'], team_stats[first_matchup[0]['name']])
    print(first_matchup[1]['name'], team_stats[first_matchup[1]['name']]) 

    return team_stats        

get_all_team_statistics()