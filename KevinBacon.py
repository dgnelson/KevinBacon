
import json
import csv
import networkx as nx
import pickle

print('Loading IMDb data... ')
data1 = json.load(open('data/connections_merged.txt'))
data2 = json.load(open('data/actors.txt'))
data3 = json.load(open('data/titles.txt'))


links = data1['data']
actors = data2['data']
films = data3['data']

bacon_nconst = 'nm0000102'

# Building a dictionary to retrieve actor names with nconsts
# Should this really be done? Sort of frontloading work to
# make later queries faster
print('Building actor dictionaries... ')
nconstToActor = dict()
for actor in actors:
	nconstToActor[actor['nconst']] = actor['primaryName']

actorToNconst = dict()
for actor in actors:
	name = actor['primaryName']
	if name in actorToNconst:
		ls = actorToNconst[name]
		ls.append(actor['nconst'])
		actorToNconst[name] = ls
	else:
		actorToNconst[actor['primaryName']] = [actor['nconst']]

# Replicating actor dictionary but for films
print('Building film dictionaries... ')
tconstToFilm = dict()
for film in films:
	tconstToFilm[film['tconst']] = film['primaryTitle']

filmToTconst = dict()
for film in films:
	title = film['primaryTitle']
	if title in filmToTconst:
		ls = filmToTconst[title]
		ls.append(film['tconst'])
		filmToTconst[title] = ls
	else:
		filmToTconst[film['primaryTitle']] = [film['tconst']]


# need to be able to get name/title from const and get const from name/title
# so should 4 dictionaries exist? or is there a more efficient way
# definitely more upfront work but faster later

def getNconsts(actorName):
	return actorToNconst[actorName]

def getActorName(nconst):
	return nconstToActor[nconst]

def getTconsts(filmTitle):
	return filmToTconst[filmTitle]

def getFilmTitle(tconst):
	return tconstToFilm[tconst]

def decodeFilms(filmList):
	ls = list()
	for film in filmList:
		ls.append(getFilmTitle(film))
	return ls

def decodeActors(actorList):
	ls = list()
	for actor in actorList:
		ls.append(getActorName(actor))
	return ls

def getEdgeWeight1(edge):
	return G.get_edge_data(*edge)['weight']

def getEdgeWeight2(node1,node2):
	return G.get_edge_data(node1,node2)['weight']

def getFilmPath(actorList):
	pairedNodes = [actorList[i:i+2] for i in range(0,len(actorList), 1)]
	pairedNodes = pairedNodes[:-1]
	path = list()
	for pair in pairedNodes:
		path.append(getEdgeWeight2(pair[0],pair[1]))
	return path

# Created because primaryNames in IMDb are not unique... real pain
def findActorConnection1(actor1,actor2):
	paths = list()
	isActor = False
	try:
		nconst1_ls = getNconsts(actor1)
		nconst2_ls = getNconsts(actor2)
		isActor = True
	except:
		print('Name not found in database')

	if isActor:
		for nconst1 in nconst1_ls:
			for nconst2 in nconst2_ls:
				try:
					paths.append(nx.shortest_path(G,source=nconst1,target=nconst2))
				except:
					print('No connection between '+actor1+'('+nconst1+')'+' and '+actor2+'('+nconst2+')'+' exists')				

	return paths

# Just uses actor with lower nconst, which is the more popular actor
def findActorConnection2(actor1,actor2):
	isActor = False
	try:
		nconst1_ls = getNconsts(actor1)
		nconst2_ls = getNconsts(actor2)
		temp1 = list()
		temp2 = list()

		for n1 in nconst1_ls:
			temp1.append((n1,int(n1.replace('nm',''))))
		for n2 in nconst2_ls:
			temp2.append((n2,int(n2.replace('nm',''))))
		min1 = temp1[0]
		min2 = temp2[0]
		for t1 in temp1:
			if t1[1]<min1[1]:
				min1 = t1
		for t2 in temp2:
			if t2[1]<min2[1]:
				min2 = t2

		nconst1 = min1[0]
		nconst2 = min2[0]

		isActor = True
	except:
		print('Name not found in database')

	if isActor:
		try:
			return nx.shortest_path(G,source=nconst1,target=nconst2)
		except:
			print('No connection between '+actor1+'('+nconst1+')'+' and '+actor2+'('+nconst2+')'+' exists')				


# Only implemented for findActorConnection2
# Full actor name ambiguity not controlled for
def generalPathSearch(actor1,actor2):
	actorPath = findActorConnection2(actor1,actor2)
	if actorPath is None:
		return
	elif len(actorPath) == 0:
		print(actor1+' and '+actor2+' are not connected')
	else:
		filmPath = getFilmPath(actorPath)
		if len(filmPath) == 0:
			print('The entries are the same actor')
		else:
			print(actor1+' and '+actor2+' have a separation degree of '+str(len(filmPath)))
			print('Their connection goes as follows:')
			actorPath = decodeActors(actorPath)
			filmPath = decodeFilms(filmPath)
			count = 0
			for f in filmPath:
				print(actorPath[count]+' was with '+actorPath[count+1]+' in '+filmPath[count])
				count += 1


# Only implemented for findActorConnection2
# Full actor name ambiguity not controlled for
def baconize2(actor):
	actorPath = findActorConnection2(actor,'Kevin Bacon')
	if actorPath is None:
		return
	elif len(actorPath) == 0:
		print(actor+'\'s Bacon Number is infinity')
	else:
		filmPath = getFilmPath(actorPath)
		if len(filmPath) == 0:
			print(actor+'\'s Bacon Number is zero')
		else:
			print(actor+'\'s Bacon Number is '+str(len(filmPath)))
			print('Their connection goes as follows:')
			actorPath = decodeActors(actorPath)
			filmPath = decodeFilms(filmPath)
			count = 0
			for title in filmPath:
				print(actorPath[count]+' was with '+actorPath[count+1]+' in '+title)
				count += 1

def baconize1(actor):
	actorPaths = findActorConnection1(actor,'Kevin Bacon')
	for actorPath in actorPaths:
		filmPath = getFilmPath(actorPath)
		names = decodeActors(actorPath)
		titles = decodeFilms(filmPath)
		print('The connection between '+names[0]+'('+actorPath[0]+')'+' and '+names[-1]+'('+actorPath[-1]+')'+' is being considered')
		if len(filmPath) == 0:
			print('The is the same actor/actress')
		else:
			print(names[0]+' and '+names[-1]+' have a separation degree of '+str(len(filmPath)))
			print('Their connection goes as follows:')
			count = 0
			for title in titles:
				print(names[count]+' was with '+names[count+1]+' in '+title)
				count += 1
		print('')


# Creating the key element, the graph
G = nx.Graph()

# Building the graphs with actors as nodes and films as edges
# Note: the basic graph from NetworkX does not allow for multiple
# edges between nodes so only the most recently placed film
# connection will show up as the common film between actors
loadGraph = True
buildGraph = (not loadGraph)
if loadGraph:
	try:
		print('Loading graph...')
		with open('obj/graph.pkl', 'rb') as f:
			G = pickle.load(f)
	except:
		print('Graph could not be loaded, it will be built...')
		buildGraph = True
elif buildGraph:
	print('Building graph...')
	for film in links:
		title = film['tconst']
		actors = film['nconsts']
		for actor in actors:
			G.add_node(actor)
		for actor1 in actors:
			for actor2 in actors:	
				if not (actor1 == actor2):	
					G.add_edge(actor1, actor2, weight=title)
	try:
		print('Saving graph...')
		with open('obj/graph.pkl', 'wb') as f:
			pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
	except:
		print('Graph could not be saved for later use...')


text = input("Please enter an actor or actress: ")
while not (text=='quit'):
	baconize2(text)
	print('\n')
	text = input("Please enter an actor or actress: ")


