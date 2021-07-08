# Recover creature 3d scale from existing sheets

import os, re

creaturePath = "R:\\leveldesign\\game_elem"

fileMap = {}

def listPath(path):
	for p in os.listdir(path):
		fp = path + "\\" + p
		if os.path.isdir(fp):
			listPath(fp)
		elif os.path.isfile(fp):
			fileMap[p] = fp

listPath(creaturePath)

scaleExpr = "Name=\"Scale\" Value=\"[^\" ]+\""

scaleMap = {}
levels = []

def loadTsvWithHeadersNoEmpty(filename):
	table = {}
	columns = None
	with open(filename, "r") as f:
		for l in f:
			if not columns:
				columns = l.strip().split("\t")
				global levels
				for i in range(1, len(columns)): # Hack
					if columns[i] not in levels:
						levels += [ columns[i] ]
			else:
				row = l.strip().split("\t")
				name = row[0]
				entry = {}
				for i in range(1, len(row)):
					if len(row[i]) > 0: # Don't include empty fields 
						entry[columns[i]] = row[i]
				table[name] = entry
	return table;

if os.path.isfile("creature_scale.tsv"):
	scaleMap = loadTsvWithHeadersNoEmpty("creature_scale.tsv")
levels.sort()

def processCreatureSheet(name):
	global levels
	global scaleMap
	short = name.split(".")[0]
	if len(short) != 6:
		return
	if short[0] != "c":
		return
	group = short[1:4]
	level = short[4:6]
	f = open(fileMap[name], "r")
	sheet = f.read()
	f.close()
	matches = re.findall(scaleExpr, sheet)
	if len(matches) == 1:
		scale = matches[0].split("\"")[-2]
		print(short + ": " + scale)
		if level not in levels:
			levels += [ level ]
		if group not in scaleMap:
			scaleMap[group] = {}
		scaleMap[group][level] = str(float(scale))

for f in fileMap:
	if f.endswith(".creature"):
		processCreatureSheet(f)
levels.sort()

with open("creature_scale.tsv", "w") as f:
	row = "group"
	for level in levels:
		row += "\t" + level
	f.write(row + "\n")
	k = scaleMap.keys()
	k.sort()
	for group in k:
		g = scaleMap[group]
		row = group
		for level in levels:
			row += "\t"
			if level in g:
				row += str(float(g[level]))
		f.write(row + "\n")
	f.flush()

# end of file
