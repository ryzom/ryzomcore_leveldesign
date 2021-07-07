
import os

def loadTsvWithHeaders(filename):
	table = {}
	columns = None
	with open(filename, "r") as f:
		for l in f:
			if not columns:
				columns = l.strip().split("\t")
			else:
				row = l.strip().split("\t")
				name = row[0]
				entry = {}
				for i in range(1, len(row)):
					entry[columns[i]] = row[i]
				table[name] = entry
	return table;

creatureFauna = loadTsvWithHeaders("creature_fauna.tsv")

generate = {}

textures = {
	"l": "Lacustre/Low Quality/Young",
	"d": "Desert/Medium Quality/Normal",
	"j": "Jungle/High Quality/Old",
	"f": "Jungle/High Quality/Old",
	"p": "PrimR",
	"g": "goo",
}

inherit = {
	"i": True,
	"r": True,
	"e": True
}

folders = {
	"l": "lacustre",
	"d": "desert",
	"j": "jungle",
	"f": "forest",
	"p": "primes_racines",
	"g": "goo",
	"i": "invasion",
	"r": "invasion",
	"e": "event",
}

suffix = {
	"l": "lac",
	"d": "des",
	"j": "jun",
	"f": "for",
	"p": "pr",
	"g": "goo",
}

ecosystem = {
	"l": "Lacustre",
	"d": "Desert",
	"j": "Jungle",
	"f": "Forest",
	"p": "PrimeRoots",
	"g": "Goo",
	"i": "Invasion",
	"r": "Raid",
	"e": "Event",
}

with open("creature_missing.txt", "r") as f:
	for l in f:
		c = l.split(".")[0]
		if c.startswith("c") and len(c) == 6:
			id = c[1:3]
			es = c[3:4]
			lvl = c[4:6]
			if id not in generate:
				generate[id] = {}
			g = generate[id]
			if es not in g:
				g[es] = []
			g = g[es]
			if lvl not in g:
				g += [ lvl ]

generatedParents = {}
def generateParent(sheet, eco):
	entry = creatureFauna[sheet]
	es = eco
	print(ecosystem[eco] + " " + entry["name"])
	if eco in inherit:
		es = entry[eco]
	name = "_" + sheet + "_" + suffix[es]
	if name in generatedParents:
		return name
	pathDir = "R:/leveldesign/game_elem/creature/" + entry["folder"] + "/" + folders[es]
	if not os.path.isdir(pathDir):
		os.makedirs(pathDir)
	pathFile = pathDir + "/" + name + ".creature"
	esn = ecosystem[es].lower()
	if esn == "primeroots":
		esn = "prime roots"
	with open(pathFile, "w") as f:
		f.write("<?xml version=\"1.0\"?>\n")
		f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
		f.write("  <PARENT Filename=\"_" + sheet + ".creature\"/>\n")
		f.write("  <STRUCT>\n")
		f.write("    <STRUCT Name=\"Basics\">\n")
		f.write("      <ATOM Name=\"First Name\" Value=\"" + esn + " " + entry["name"].lower() + "\"/>\n")
		f.write("      <ATOM Name=\"Ecosystem\" Value=\"" + ecosystem[es] + "\"/>\n")
		f.write("      <STRUCT Name=\"Equipment\">\n")
		f.write("        <STRUCT Name=\"Body\">\n")
		f.write("          <ATOM Name=\"Texture\" Value=\"" + textures[es] + "\"/>\n")
		f.write("        </STRUCT>\n")
		f.write("      </STRUCT>\n")
		f.write("    </STRUCT>\n")
		f.write("  </STRUCT>\n")
		f.write("</FORM>\n")
	return name

for sheet in creatureFauna:
	entry = creatureFauna[sheet]
	id = entry["id"]
	if id in generate:
		gen = generate[id]
		for eco in gen:
			if eco not in folders:
				print sheet
				print "c" + id + eco
				print gen
			parent = generateParent(sheet, eco)
			es = eco
			if eco in inherit:
				es = entry[eco]
			for lvl in gen[eco]:
				name = "c" + id + eco + lvl
				print(entry["name"] + " " + suffix[es] + " " + eco + " " + lvl + " " + name + " " + parent)
