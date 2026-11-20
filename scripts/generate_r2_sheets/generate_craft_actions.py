# Generates the craft actions that the starting roles teach: for each civilisation and craft category, the root brick
# (bcpa*, it lists the plan families the action offers), the credit brick of the recommended level (bc?aca*) and the
# action itself, the phrase that joins the two (abc?aca*). A civilisation's craft action only offers the plans of its
# own families, plus the common and refugee ones: crafting Tryker armor needs the Tryker armor action.
#
# The table holds the armor category at level 1 for the four civilisations. Other categories (melee and range weapons,
# jewels, ammunition, tools) and the higher levels get their own rows once their families are known.
#
# Run from anywhere with Python 3: python generate_craft_actions.py. It writes into leveldesignRoot, the leveldesign
# folder of the tree. Every check runs before the first sheet is written, and a failed one stops the run without writing
# anything: the folders it writes into exist, no sheet name exists elsewhere in the folders the sheet ids are made from,
# every sheet has its row in the words files of the translation, and every brick its row in sbrick_index.tsv. Each sheet
# is then reported as new, changed or unchanged. The sheets are made from the tables below: change the tables, not the
# sheets.

import os, sys

leveldesignRoot = "R:\\leveldesign"

gameElement = leveldesignRoot + "\\game_element"
rootFolder = gameElement + "\\sbrick\\craft\\root"
creditFolder = gameElement + "\\sbrick\\craft\\credit\\recommended"
phraseFolder = gameElement + "\\sphrase\\craft\\recommended"

# the folders the sheet ids are made from (build_gamedata, process sheet_id): a sheet name must be unique across them
sheetIdFolders = [ leveldesignRoot + "\\game_elem", gameElement, leveldesignRoot + "\\world" ]

# the index that keeps the family index of every brick stable, made by extract_sbrick.py
indexPath = leveldesignRoot + "\\scripts\\generate_r2_sheets\\sbrick_index.tsv"

# the words of every sheet: work\<type>_words_wk.txt, and translated\<type>_words_<language>.txt for every language
translationFolder = leveldesignRoot + "\\translation"

# civilisation: letter in the sheet names, name for CivRestriction and the brick background
civs = [
	( "f", "fyros" ),
	( "m", "matis" ),
	( "t", "tryker" ),
	( "z", "zorai" ),
]

# category: code in the credit family (bc?<code>ca), index of the root brick per civilisation, skill, icon, tool type,
# and the plan families offered besides the civilisation's own (bc?<code>e<a..d>)
categories = [
	{
		"name": "armor",
		"code": "a",
		"rootIndex": { "fyros": 4, "matis": 10, "tryker": 16, "zorai": 22 },
		"skill": "SCA",
		"icon": "fp_armor.png",
		"tool": "ArmorTool",
		"ownPlans": [ "ea", "eb", "ec", "ed" ],
		"otherPlans": [ "BCCAEA", "BCCAEB", "BCCAEC", "BCCAED", "BCRAEA" ],
	},
]

# recommended levels: level, CR_RECOMMENDED value, sabrina cost, skill point cost
levels = [
	( 1, 10, -10, 50 ),
]

def fail(message):
	sys.stderr.write("error: " + message + "\n")
	sys.exit(1)

errors = []

def error(message):
	# collected, so that one run lists every problem; nothing is written when there is one
	errors.append(message)

def xmlAttr(value):
	# the text of a value in a double-quoted XML attribute
	return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;")

def atom(indent, name, value):
	return indent + "<ATOM Name=\"" + xmlAttr(name) + "\" Value=\"" + xmlAttr(value) + "\"/>"

def struct(indent, name):
	return indent + "<STRUCT Name=\"" + xmlAttr(name) + "\">"

# A missing folder means that leveldesignRoot is not the leveldesign folder of a tree. Without this check the walks
# below find nothing and the sheets would go into a tree of their own.
for folder in [ rootFolder, creditFolder, phraseFolder ] + sheetIdFolders + [ translationFolder ]:
	if not os.path.isdir(folder):
		fail("Folder " + folder + " does not exist, so " + leveldesignRoot + " is not the leveldesign folder of a tree: "
			+ "map its drive to the tree to generate into, or set leveldesignRoot at the top of " + os.path.abspath(__file__))

sheets = [] # path, sheet type (extension), lines, table row it comes from
bricks = [] # family, index in family, index as sbrick_index.tsv writes it, sheet name, table row

def addSheet(folder, name, sheetType, lines, source):
	sheets.append((folder + "\\" + name + "." + sheetType, sheetType, lines, source))

for cat in categories:
	for letter, civ in civs:
		credit = "BC" + letter.upper() + cat["code"].upper() + "CA"
		rootIndex = cat["rootIndex"][civ]
		rootName = "bcpa%02d" % rootIndex
		plans = [ "BC" + letter.upper() + cat["code"].upper() + p.upper() for p in cat["ownPlans"] ] + cat["otherPlans"]
		source = cat["name"] + " of " + civ
		bricks.append(( "BCPA", rootIndex, str(rootIndex), rootName, source ))
		addSheet(rootFolder, rootName, "sbrick", [
			struct("    ", "Basics"),
			atom("      ", "FamilyId", "BCPA"),
			atom("      ", "IndexInFamily", str(rootIndex)),
			atom("      ", "Property 0", "FPLAN: " + " ".join(plans)),
			atom("      ", "LearnRequiresOneOfSkills", "SC 0"),
			atom("      ", "Action Nature", "CRAFT"),
			atom("      ", "Skill", cat["skill"]),
			"    </STRUCT>",
			struct("    ", "Client"),
			atom("      ", "Icon", cat["icon"]),
			atom("      ", "IconBack", "bk_" + civ + "_brick.png"),
			atom("      ", "IconOver", "fp_over.png"),
			"    </STRUCT>",
			struct("    ", "Optional"),
			atom("      ", "f0", "BCOA"),
			atom("      ", "f1", "BCOB"),
			atom("      ", "f2", "BCOC"),
			atom("      ", "f3", "BCOD"),
			"    </STRUCT>",
			struct("    ", "Parameter"),
			atom("      ", "f0", credit),
			"    </STRUCT>",
			struct("    ", "faber"),
			atom("      ", "Tool type", cat["tool"]),
			"    </STRUCT>",
		], source)
		for level, recommended, sabrinaCost, spCost in levels:
			creditName = credit.lower() + "%02d" % level
			levelSource = source + ", level " + str(level)
			# IndexInFamily defaults to the number in the sheet name (sbrick DFN: $filename), which is the level
			bricks.append(( credit, level, "%02d" % level, creditName, levelSource ))
			addSheet(creditFolder, creditName, "sbrick", [
				struct("    ", "Basics"),
				atom("      ", "FamilyId", credit),
				atom("      ", "SabrinaCost", str(sabrinaCost)),
				atom("      ", "SPCost", str(spCost)),
				atom("      ", "Property 0", "CR_RECOMMENDED: " + str(recommended)),
				atom("      ", "LearnRequiresOneOfSkills", "SC 0"),
				atom("      ", "CivRestriction", civ),
				"    </STRUCT>",
				struct("    ", "Client"),
				atom("      ", "Icon", "ico_level.png"),
				atom("      ", "IconBack", "pa_back.png"),
				atom("      ", "IconOver", "pa_over_more.png"),
				"    </STRUCT>",
			], levelSource)
			addSheet(phraseFolder, "a" + creditName, "sphrase", [
				atom("    ", "brick 0", rootName + ".sbrick"),
				atom("    ", "brick 1", creditName + ".sbrick"),
			], levelSource)

# A sheet id is the file name, so two rows of the table that give one name would write one sheet twice
generated = {} # file name in lower case: path, table row
for path, sheetType, lines, source in sheets:
	fileName = os.path.basename(path).lower()
	if fileName in generated:
		error("The table makes " + os.path.basename(path) + " twice, for " + generated[fileName][1] + " and for " + source
			+ ": each category of a civilisation needs a root index of its own, and each level a row of its own")
	else:
		generated[fileName] = ( path, source )

# sbrick_index.tsv: family, index in family, sheet name, then item and earlier sheet names of the brick, and __missing
# when the sheet did not exist at the last extract_sbrick.py run. A row keeps an index of a family for one brick.
if not os.path.isfile(indexPath):
	fail("The brick index " + indexPath + " does not exist: it belongs to the leveldesign tree, beside this script")
indexRows = {} # (family, index): list of (line number, sheet name, marked __missing)
indexNames = {} # sheet name: list of (line number, family, index)
with open(indexPath, "r", encoding="utf-8", newline="\n") as f:
	lineNumber = 0
	for l in f:
		lineNumber += 1
		fields = [ field for field in l.rstrip("\r\n").split("\t") if field ]
		if len(fields) < 3 or not fields[1].isdigit():
			error(indexPath + " line " + str(lineNumber) + " is not family, index and sheet name: " + l.rstrip("\r\n"))
			continue
		key = ( fields[0].upper(), int(fields[1]) )
		indexRows.setdefault(key, []).append(( lineNumber, fields[2].lower(), "__missing" in fields[3:] ))
		indexNames.setdefault(fields[2].lower(), []).append(( lineNumber, key[0], key[1] ))

missingMarks = [] # line number, sheet name: rows of generated bricks still marked __missing
for family, index, indexText, name, source in bricks:
	rows = indexRows.get(( family, index ), [])
	if not rows:
		error(indexPath + " has no row for " + family + " " + str(index) + " (" + name + ", " + source + "): add the line "
			+ family + "<TAB>" + indexText + "<TAB>" + name + "<TAB> in the order of the family")
	elif len(rows) > 1:
		error(indexPath + " has " + str(len(rows)) + " rows for " + family + " " + str(index) + ", lines "
			+ ", ".join([ str(row[0]) for row in rows ]) + ": keep the one of the brick that has the index")
	elif rows[0][1] != name:
		error(indexPath + " line " + str(rows[0][0]) + " gives " + family + " " + str(index) + " to " + rows[0][1]
			+ ", not to " + name + " (" + source + "): the EGS keeps one brick per family index (ALREADY ADDED brick), "
			+ "so the index in the table or the row is wrong")
	elif rows[0][2]:
		missingMarks.append(( rows[0][0], name ))
	for lineNumber, otherFamily, otherIndex in indexNames.get(name, []):
		if ( otherFamily, otherIndex ) != ( family, index ):
			error(indexPath + " line " + str(lineNumber) + " gives the sheet name " + name + " to " + otherFamily + " "
				+ str(otherIndex) + ", the table to " + family + " " + str(index) + " (" + source + ")")

# Every sheet needs a row in the work words file and in the translated one of every language, or the client has no
# name and description for it
def loadWordIds(path, sheetType):
	if not os.path.isfile(path):
		error("The words file " + path + " does not exist")
		return None
	with open(path, "rb") as f:
		data = f.read().decode("utf-8-sig")
	lines = data.split("\n")
	header = lines[0].rstrip("\r").split("\t")
	if not (sheetType + " ID") in header:
		error("The words file " + path + " has no column " + sheetType + " ID")
		return None
	column = header.index(sheetType + " ID")
	ids = set()
	for l in lines[1:]:
		fields = l.rstrip("\r").split("\t")
		if len(fields) > column and fields[column]:
			ids.add(fields[column].lower())
	return ids

languagesPath = translationFolder + "\\languages.txt"
if not os.path.isfile(languagesPath):
	fail("The language list " + languagesPath + " does not exist")
with open(languagesPath, "r", encoding="utf-8") as f:
	languages = [ l.strip() for l in f if l.strip() ]
for sheetType in sorted(set([ sheet[1] for sheet in sheets ])):
	wordsPaths = [ translationFolder + "\\work\\" + sheetType + "_words_wk.txt" ]
	for language in languages:
		wordsPaths.append(translationFolder + "\\translated\\" + sheetType + "_words_" + language + ".txt")
	for wordsPath in wordsPaths:
		ids = loadWordIds(wordsPath, sheetType)
		if ids is None:
			continue
		for path, otherType, lines, source in sheets:
			name = os.path.splitext(os.path.basename(path))[0]
			if otherType == sheetType and not name.lower() in ids:
				error(name + " (" + source + ") has no row in " + wordsPath + ": add its words there before generating it")

# A sheet name must exist once in the folders the sheet ids are made from: another file of that name would load twice
def walkError(e):
	error("Cannot list " + str(e.filename) + ": " + str(e.strerror))

for folder in sheetIdFolders:
	for root, dirs, files in os.walk(folder, onerror=walkError):
		for f in files:
			found = generated.get(f.lower())
			if found:
				other = os.path.join(root, f)
				if os.path.normcase(os.path.abspath(other)) != os.path.normcase(os.path.abspath(found[0])):
					error("Sheet " + f + " also exists as " + other + "; move or remove it before generating " + found[0])

if errors:
	for e in errors:
		sys.stderr.write("error: " + e + "\n")
	sys.stderr.write("Nothing was written\n")
	sys.exit(1)

def sheetData(lines):
	text = "<?xml version=\"1.0\"?>\n"
	text += "<FORM Version=\"4.0\" State=\"modified\">\n"
	text += "  <STRUCT>\n"
	for l in lines:
		text += l + "\n"
	text += "  </STRUCT>\n"
	text += "</FORM>\n"
	return text.encode("utf-8")

# An unchanged sheet is not written again, so its time stays that of its last change for the data build
counts = { "new": 0, "changed": 0, "unchanged": 0 }
for path, sheetType, lines, source in sheets:
	data = sheetData(lines)
	if not os.path.isfile(path):
		state = "new"
	else:
		with open(path, "rb") as f:
			state = "unchanged" if f.read() == data else "changed"
	if state != "unchanged":
		with open(path, "wb") as f:
			f.write(data)
	counts[state] += 1
	print(state + " " + path)
print(str(len(sheets)) + " sheets: " + str(counts["new"]) + " new, " + str(counts["changed"]) + " changed, "
	+ str(counts["unchanged"]) + " unchanged")
for lineNumber, name in missingMarks:
	print(indexPath + " line " + str(lineNumber) + " still marks " + name + " __missing: remove the mark, "
		+ "the sheet exists now")
