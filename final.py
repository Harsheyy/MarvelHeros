import requests
from bs4 import BeautifulSoup
import json
import sys
import sqlite3
import csv
import secret
import hashlib
import time

DBNAME = 'marvel.db'
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()

statement = "DROP TABLE IF EXISTS 'Characters';"
cur.execute(statement)

statement = '''
	CREATE TABLE 'Characters' (
		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
		'MarvelId' INT NOT NULL,
		'Name' VARCHAR(128) NOT NULL,
		'Comics' INT NOT NULL,
		'Series' INT NOT NULL,
		'Stories' INT NOT NULL,
		'Events' INT NOT NULL,
		'Image' VARCHAR(128));'''
cur.execute(statement)

conn.commit()
conn.close()

CACHE_FNAME = "data_cache.json"
try:
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()
except:
	CACHE_DICTION = {}

def get_html(url):
	if url in CACHE_DICTION:
		print("Getting cached data...")
		r = CACHE_DICTION[url]
	else:
		print("Making a request for new data...")
		r = requests.get(url)
		CACHE_DICTION[url] = r
		with open(CACHE_FNAME, 'w') as cf:
			json.dump(CACHE_DICTION, cf, indent = 2)
		r = r.content
	return r

def get_connections(html):
	heros = {}
	superhero = ''
	realname = ''
	link = ''
	string = ''
	biourl = "/on-screen/profile"
	soup = BeautifulSoup(html,'html.parser')

	for site in soup.find_all('div', {'class': "mvl-card mvl-card--explore"}):
		for name in site('p', {'class': "card-body__headline"}):
			superhero = name.text
		for name in site('div', {'class': 'card-footer'}):
			realname = name.text
		for link in site('a', href = True):
			temp = link['href']
			link = baseurl + temp + biourl
			link = link
		heros[superhero] = {'realname': realname, 'link': link}
	
	return heros

def get_powers(html):
	hero_power = {}
	power_list = []
	name = ''
	soup = BeautifulSoup(html,'html.parser')

	for name in soup.find_all('span', {'class': 'masthead__headline'}):
		name = name.text
	for powers in soup.find_all('section', {'id': "sets-5"}):
		for stuff in powers('a', {'role': 'presentation'}):
			#print(stuff.text)
			power_list.append(stuff.text)
	
	hero_power[name] = {'powers': power_list}
	return hero_power


#################################################################################################################################

conn = sqlite3.connect(DBNAME)
cur = conn.cursor()

request_url = 'http://gateway.marvel.com/v1/public/characters'

characters = {}

#API hashing
public = secret.api_key
private = secret.private
ts = time.time()
ts_str = str(int(ts))
m_hash = hashlib.md5()
ts_str_byte = bytes(ts_str, 'utf-8')
private_key_byte = bytes(private, 'utf-8')
public_key_byte = bytes(public, 'utf-8')
m_hash.update(ts_str_byte + private_key_byte + public_key_byte)
m_hash_str = str(m_hash.hexdigest())

params = {'ts': ts_str, 'apikey': public, 'hash': m_hash_str, 'orderBy': '-modified', 'limit': 100}
params1 = {'ts': ts_str, 'apikey': public, 'hash': m_hash_str}

try:
	with open('json_cache.json') as data_file:
		json_data = json.load(data_file)
	print('Getting cached json data')
except:
	print('Requesting json data')
	r = requests.get(request_url, params=params)
	json_data = r.json()
	with open('json_cache.json', 'w') as outfile:
		json.dump(json_data, outfile, indent = 2)

for data in json_data['data']['results']:
	marvel_id = data['id']
	name = data['name']
	comics = data['comics']['available']
	series = data['series']['available']
	stories = data['stories']['available']
	events = data['events']['available']
	path = data['thumbnail']['path']
	ext = data['thumbnail']['extension']
	image = path +"."+ext
	characters[name] = {'id': marvel_id, 'comics': comics, 'series': series, 'stories': stories, 'events': events, 'image': image}
	vals = (marvel_id, name,comics, series, stories, events, image)
	cur.execute("INSERT INTO Characters(MarvelId, Name, Comics, Series, Stories, Events, Image) VALUES (?, ?, ?, ?, ?, ?, ?)", vals)

for people in characters:
	request_url = request_url + '/' + str(characters[people]['id'])
	print(request_url)
	r = requests.get(request_url, params=params1)
	json_data = r.json()

	for data in json_data['data']['results'][0]['urls'][0]:
		print(data)
		#print(data['url'])

	request_url = 'http://gateway.marvel.com/v1/public/characters'

conn.commit()
conn.close()




