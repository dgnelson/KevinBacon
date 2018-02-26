
import json
import csv

file = 'imdb_data/title.principals.tsv'

data={}

with open('data/connections_singled.txt', 'w') as outfile,open(file,"r") as f:
	firstRow = True
	for line in f:
		if firstRow:
			firstRow=False
		else:
			sp=line.split('\t')
			if (sp[3] == 'actor') or (sp[3] == 'actress'):
				data.setdefault("data",[]).append({"tconst": sp[0],"nconst": sp[2]})
	json.dump(data, outfile)


data1 = json.load(open('data/connections_singled.txt'))

films = data1['data']

filmDictionary = dict()
for film in films:
	filmid = film['tconst']
	if filmid in filmDictionary:
		ls = filmDictionary[filmid]
		ls.append(film['nconst'])
		filmDictionary[filmid] = ls
	else:
		nameList = list()
		nameList.append(film['nconst'])
		filmDictionary[filmid] = nameList

data={}

with open('data/connections_merged.txt', 'w') as outfile:
	firstRow = True
	for k,v in filmDictionary.items():
		data.setdefault("data",[]).append({"tconst": k,"nconsts": v})

	json.dump(data, outfile)




file = 'imdb_data/title.basics.tsv'

data={}

with open('data/titles.txt', 'w') as outfile,open(file,"r") as f:
	firstRow = True
	for line in f:
		if firstRow:
			firstRow=False
		else:	
			sp=line.split('\t')
			data.setdefault("data",[]).append({"tconst": sp[0],"primaryTitle": sp[2]})
	json.dump(data, outfile)



file = 'imdb_data/name.basics.tsv'

data={}

with open('data/actors.txt', 'w') as outfile,open(file,"r") as f:
	firstRow = True
	for line in f:
		if firstRow:
			firstRow=False
		else:	
			sp=line.split('\t')
			# primaryName  = sp[1].partition('\\N')[0]
			data.setdefault("data",[]).append({"nconst": sp[0],"primaryName": sp[1]})
	json.dump(data, outfile)







