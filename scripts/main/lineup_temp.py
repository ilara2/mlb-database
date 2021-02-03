# coding: utf-8
pitcher = card.find('div', class_='starting-lineups__pitchers')
pitcher
[away_pit, home_pit] = pitcher.div('div', recursive=False)[::2]
away_pit
away_pit.text
away_pit
away_pit.prettify()
home_pit.text
away_pit.find('a', href=re.compile('https://www.mlb.com/player/[a-zA-Z\-]+[0-9]+'))
import re
away_pit.find('a', href=re.compile('https://www.mlb.com/player/[a-zA-Z\-]+[0-9]+'))
a = away_pit.find('a', href=re.compile('https://www.mlb.com/player/[a-zA-Z\-]+[0-9]+'))
a
a = away_pit.find('a', href=re.compile('https://www.mlb.com/player/.*[0-9]+'))
a
a = away_pit.find('a', href=re.compile(r'https://www.mlb.com/player/.*[0-9]+'))
a
a
away_pit
a = away_pit.find('a', href=re.compile(r'/player/.*[0-9]+'))
a
a = away_pit.find('a', href=re.compile(r'/player/.*[0-9]+'))['href']
a
away_pitcher = re.findall(r'[0-9]+', away_pit.find('a', href=re.compile(r'/player/.*[0-9]+'))['href'])
away_pitcher
away_pitcher = re.findall(r'[0-9]+', away_pit.find('a', href=re.compile(r'/player/.*[0-9]+'))['href'])[0]
away_pitcher
home_pitcher = re.findall(r'[0-9]+', home_pit.find('a', href=re.compile(r'/player/.*[0-9]+'))['href'])[0]
home_pitcher
