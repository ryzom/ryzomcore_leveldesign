
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

def loadTsvWithHeadersNoEmpty(filename):
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
					if len(row[i]) > 0:
						entry[columns[i]] = row[i]
				table[name] = entry
	return table;

creatureFauna = loadTsvWithHeaders("creature_fauna.tsv")
creatureScale = loadTsvWithHeadersNoEmpty("creature_scale.tsv")

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

# Override specified group assist (use gooAggro range if this exists)
groupAggro = {
	"g": {
		# Goo attacks all non-goo
		"a": [ "a_,zp" ],
		"b": [ "b_,c_,h_,p_,zp" ],
		"c": [ "b_,c_,h_,p_,zp" ],
		"h": [ "b_,c_,h_,p_,zp" ],
		"k": [ "k_,b_,c_,h_,p_,zp" ],
		"p": [ "b_,c_,h_,zp" ],
	},
	"i": { "a": [ "zp" ], "b": [ "zp" ], "c": [ "b_,h_,zp" ], "h": [ "zp" ], "k": [ "b_,h_,zp" ], "p": [ "zp" ] },
	"r": { "a": [ "zp" ], "b": [ "zp" ], "c": [ "b_,h_,zp" ], "h": [ "zp" ], "k": [ "b_,h_,zp" ], "p": [ "zp" ] },
	"e": { "a": [ "zp" ], "b": [ "zp" ], "c": [ "b_,h_,zp" ], "h": [ "zp" ], "k": [ "b_,h_,zp" ], "p": [ "zp" ] },
}

# Override specified group assist (use gooAssist range if this exists)
groupAssist = {
	"g": {
		# Goo plants defend plants and themselves
		"a": [ "@" ], "b": [ "@" ], "c": [ "@" ], "h": [ "@" ], "k": [ "@" ],
		"p": [ "@,p_,p_g" ]
	},
}

# Don't aggro ecosystem when specified by _ wildcard
dontAggroAssistEs = [ "g" ]

with open("creature_list.txt", "r") as f:
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

groups = []
for sheet in creatureFauna:
	entry = creatureFauna[sheet]
	id = entry["id"]
	if not id in groups:
		groups += [ id ]
	if id in generate:
		gen = generate[id]
		for eco in gen:
			if eco in groupAggro and not id + eco in groups:
				groups += [ id + eco ]
groups.sort()
print(groups)
def extendGroup(group, me):
	groupv = group.lower().strip().split(",")
	res = []
	for g in groupv:
		print(g)
		if g == "@" and not me in res:
			res += [ me ]
		elif len(g) == 2:
			if g[1] == "_":
				for rg in groups:
					if rg[0] == g[0] and (len(rg) == 2 or not rg[2] in dontAggroAssistEs) and not rg in res:
						res += [ rg ]
			elif not g in res:
				res += [ g ]
		elif len(g) == 3:
			if g[1] == "_":
				for rg in groups:
					if len(rg) == 3 and rg[0] == g[0] and rg[2] == g[2] and not rg in res:
						res += [ rg ]
			elif g[2] == "_":
				for rg in groups:
					if g[0] == rg[0] and g[1] == rg[1] and (len(rg) == 2 or rg[2] not in dontAggroAssistEs) and not rg in res:
						res += [ rg ]
			elif not g in res:
				res += [ g ]
	res.sort()
	return ",".join(res)
print(extendGroup("b_,h_,zp", "ca"))
print(extendGroup("@,p_,p_g", "pa"))
print(extendGroup("ka_,kb_,kc_", "ka"))

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
				# print(entry["name"] + " " + suffix[es] + " " + eco + " " + lvl + " " + name + " " + parent)
				mpDir = "R:/leveldesign/game_elem/creature/" + entry["folder"] + "/_parent_mp/" + folders[eco]
				if not os.path.isdir(mpDir):
					os.makedirs(mpDir)
				sheetDir = "R:/leveldesign/game_elem/creature/" + entry["folder"] + "/" + folders[eco]
				if not os.path.isdir(mpDir):
					os.makedirs(mpDir)
				mpFile = mpDir + "/_" + name + "_mp.creature"
				if not os.path.isfile(mpFile):
					with open(mpFile, "w") as f:
						f.write("<?xml version=\"1.0\"?>\n")
						f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
						f.write("  <STRUCT>\n")
						f.write("    <STRUCT Name=\"Harvest\">\n")
						f.write("      <STRUCT Name=\"MP1\">\n")
						f.write("        <ATOM Name=\"AssociatedItem\" Value=\"system_mp_basic.sitem\"/>\n")
						f.write("      </STRUCT>\n")
						f.write("    </STRUCT>\n")
						f.write("  </STRUCT>\n")
						f.write("</FORM>\n")
