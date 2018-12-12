import requests
from bs4 import BeautifulSoup
import json
import sys
import sqlite3
import secret
import hashlib
import time
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

DBNAME = 'marvel.db'
# conn = sqlite3.connect(DBNAME)
# cur = conn.cursor()

# statement = "DROP TABLE IF EXISTS 'Characters';"
# cur.execute(statement)

# statement = "DROP TABLE IF EXISTS 'Links';"
# cur.execute(statement)

# statement = '''
# 	CREATE TABLE 'Characters' (
# 		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
# 		'MarvelId' INT NOT NULL,
# 		'Name' VARCHAR(128) NOT NULL,
# 		'Comics' INT NOT NULL,
# 		'Series' INT NOT NULL,
# 		'Stories' INT NOT NULL,
# 		'Events' INT NOT NULL);'''
# cur.execute(statement)

# statement = '''
# 	CREATE TABLE 'Links' (
# 		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
# 		'MarvelId' INT NOT NULL,
# 		'Name' VARCHAR(128) NOT NULL,
# 		'Image' VARCHAR(128),
# 		'Wiki' VARCHAR(128),
# 		FOREIGN KEY (Id) REFERENCES Characters(Id));'''
# cur.execute(statement)

# conn.commit()
# conn.close()

#################################################################################################################################

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
		CACHE_DICTION[url] = r.text
		with open(CACHE_FNAME, 'w') as cf:
			json.dump(CACHE_DICTION, cf, indent = 2)
		r = r.content
	return r

def populate(url, params):
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

	i = 0
	for data in json_data['data']['results']:
		if json_data['data']['results'][i]['urls'][1]['type'] == 'wiki':
			marvel_id = data['id']
			name = data['name']
			comics = data['comics']['available']
			series = data['series']['available']
			stories = data['stories']['available']
			events = data['events']['available']
			path = data['thumbnail']['path']
			ext = data['thumbnail']['extension']
			image = path +"."+ext
			wiki = data['urls'][1]['url']		
			characters[name] = {'id': marvel_id, 'comics': comics, 'series': series, 'stories': stories, 'events': events, 'image': image, 'wiki': wiki}
			
			vals = (marvel_id, name,comics, series, stories, events)
			cur.execute("INSERT INTO Characters(MarvelId, Name, Comics, Series, Stories, Events) VALUES (?, ?, ?, ?, ?, ?)", vals)
			vals = (marvel_id, name, image, wiki)
			cur.execute("INSERT INTO Links(MarvelId, Name, Image, Wiki) VALUES (?, ?, ?, ?)", vals)
		i += 1
	statement = 'SELECT Name FROM Characters'
	cur.execute(statement)
	results = cur.fetchall()
	return results

def char_stats(char_id):
	char_id = int(char_id) + 1
	statement = 'SELECT Name, Comics, Series, Stories, Events FROM Characters WHERE Id = ' + str(char_id)
	cur.execute(statement)
	results = cur.fetchall()
	vals = [int(results[0][1]), int(results[0][2]), int(results[0][3]), int(results[0][4])]
	if(vals == [0,0,0,0]):
		print("This hero isn't in anything... yet, try a different hero!")
	else:
		labels = ['Comics','Series','Stories','Events']
		colors = ['#FEBFB3', '#E1396C', '#96D38C', '#D0F9B1']

		trace = go.Pie(labels=labels, values=vals,
			name=str(results[0][0]),
			hoverinfo='label+percent', textinfo='value',
			textfont=dict(size=20),
			marker=dict(colors=colors, 
				line=dict(color='#000000', width=2)))

		py.plot([trace], filename='styled_pie_chart')

def top(mode):
	name = []
	num = []

	statement = 'SELECT Name, '+ str(mode) +' FROM Characters GROUP BY Name ORDER BY ' + str(mode) + ' DESC LIMIT 10'
	cur.execute(statement)
	results = cur.fetchall()

	for heros in results:
		name.append(heros[0])
		num.append(heros[1])

	data = [go.Bar(
		x=name,
		y=num
	)]

	py.plot(data, filename='basic-bar')

def image(char_id):
	char_id = int(char_id) + 1
	statement = 'SELECT Image FROM Links WHERE Id = ' + str(char_id)
	cur.execute(statement)
	result = cur.fetchone()

	img_width = 1600
	img_height = 900
	scale_factor = 0.5

	layout = go.Layout(
    	xaxis = go.layout.XAxis(
        	visible = False,
        	range = [0, img_width*scale_factor]),
    	yaxis = go.layout.YAxis(
        	visible=False,
        	range = [0, img_height*scale_factor],
        	# the scaleanchor attribute ensures that the aspect ratio stays constant
        	scaleanchor = 'x'),
    	width = img_width*scale_factor,
    	height = img_height*scale_factor,
    	margin = {'l': 0, 'r': 0, 't': 0, 'b': 0},
    	images = [go.layout.Image(
        	x=0,
        	sizex=img_width*scale_factor,
        	y=img_height*scale_factor,
        	sizey=img_height*scale_factor,
        	xref="x",
        	yref="y",
        	opacity=1.0,
        	layer="below",
        	sizing="stretch",
        	source=result[0])]
	)
	# we add a scatter trace with data points in opposite corners to give the Autoscale feature a reference point
	fig = go.Figure(data=[{
    	'x': [0, img_width*scale_factor], 
    	'y': [0, img_height*scale_factor], 
    	'mode': 'markers',
    	'marker': {'opacity': 0}}],layout = layout)
	
	py.plot(fig, filename='image')

def map():
	google = 'https://maps.googleapis.com/maps/api/geocode/json?'
	google_api = secret.google
	params = {'key': google_api}

	statement = 'SELECT Wiki FROM Links'
	cur.execute(statement)
	results = cur.fetchall()
	find_location = []
	find_city = []
	i = 0
	location = []
	lat = []
	lng = []
	mapbox_access_token = 'pk.eyJ1IjoiaGFyc2hkIiwiYSI6ImNqcGp4MDZqbTBiaHkzdm5wNHc0Zmg1ZnIifQ.aOUOQYzklE_dab3C4kZZuQ'

	for i in results:
		try:
			html = get_html(i[0])
			soup = BeautifulSoup(html,'html.parser')

			for biogroup in soup.find_all('ul', {'class': "bioGroup"}):
				for location in biogroup('p', {'class': "bioGroupItem__label"}):
					find_location.append(location.text)
				for city in biogroup('ul', {'class': "bioLinks"}):
					find_city.append(city.li)
			i = 0
			index = 0
			for finding in find_location:
				i += 1
				if finding == "Place of Origin":
					index = i
					city = find_city[index-1]
					params = {'key': google_api, 'address': city.text}
					url = google + city.text
					try:
						if url in CACHE_DICTION:
							print("Getting cached data...")
							r = CACHE_DICTION[url]
							r = json.loads(r)
						else:
							print("Making a request for new data...")
							r = requests.get(url, params)
							CACHE_DICTION[url] = r.text
							with open(CACHE_FNAME, 'w') as cf:
								json.dump(CACHE_DICTION, cf, indent = 2)
							r = json.loads(r.text)
						lat.append(r['results'][0]['geometry']['location']['lat'])
						lng.append(r['results'][0]['geometry']['location']['lng'])
					except:
						pass
					index = 0
					find_location = []
					find_city = []
		except:
			print("This character isn't from a known location.")
	data = [
		go.Scattermapbox(
    		lat=lat,
    		lon=lng,
    		mode='markers',
    		marker=dict(
    			size=9
    		),
    		#text=hero,
    	)
	]
	layout = go.Layout(
    	autosize=True,
    	hovermode='closest',
    	mapbox=dict(
        	accesstoken=mapbox_access_token,
        	bearing=0,
        	pitch=0,
        	zoom=3
    	),
	)

	fig = dict(data=data, layout=layout)
	py.plot(fig, filename='Multiple Mapbox')


#################################################################################################################################

if __name__ == "__main__":

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

	listing = populate(request_url, params)
	char_id = 0

	user_input = input("Enter command (or 'help' for options): ")
	while(user_input != "exit"):
		parse = user_input.split()

		if user_input == "list":
			for i in range(0, len(listing)):
				print(i, listing[i][0])
	
		elif(parse[0] == "stats"):
			if(int(parse[1]) < 0 or int(parse[1]) > 90):
				print("incorrect argument - try numbers from 0-100")
			else:
				char_stats(parse[1])
	
		elif(parse[0] == "top"):
			if(parse[1] != "Comics" and parse[1] != "Series" and parse[1] != "Stories" and parse[1] != "Events"):
				print("incorrect argument - try 'Comics', 'Series', 'Stories', or 'Events'")
			else:
				top(parse[1])
	
		elif(parse[0] == "image"):
			image(parse[1])
	
		elif(user_input == "map"):
			map()

		else:
			print("Error, not a valid command")
		user_input = input("Enter command (or 'help' for options): ")

	conn.commit()
	conn.close()	

