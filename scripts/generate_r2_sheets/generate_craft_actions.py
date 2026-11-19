# Generates the craft actions that the starting roles teach: for each civilisation and craft category, the root brick
# (bcpa*, it lists the plan families the action offers), the credit brick of the recommended level (bc?aca*) and the
# action itself, the phrase that joins the two (abc?aca*). A civilisation's craft action only offers the plans of its
# own families, plus the common and refugee ones: crafting Tryker armor needs the Tryker armor action.
#
# The table holds the armor category at level 1 for the four civilisations. Other categories (melee and range weapons,
# jewels, ammunition, tools) and the higher levels get their own rows once their families are known.
#
# Run from anywhere with Python 3: python generate_craft_actions.py. Every sheet name is checked before the first one is
# written, so a stray copy elsewhere in game_element stops the run without writing anything.

import os

leveldesign = "R:\\leveldesign\\game_element"
rootFolder = leveldesign + "\\sbrick\\craft\\root"
creditFolder = leveldesign + "\\sbrick\\craft\\credit\\recommended"
phraseFolder = leveldesign + "\\sphrase\\craft\\recommended"

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

def checkUnique(name, path):
	# a sheet name must exist once in game_element; another file of that name elsewhere would load twice
	for root, dirs, files in os.walk(leveldesign):
		for f in files:
			if f.lower() == name.lower():
				other = os.path.join(root, f)
				if os.path.normcase(os.path.abspath(other)) != os.path.normcase(os.path.abspath(path)):
					raise Exception("Sheet " + name + " also exists as " + other + "; move or remove it before generating " + path)

sheets = []

def writeSheet(path, lines):
	# collected first, written once every name is known to be unique
	sheets.append((path, lines))

def saveSheet(path, lines):
	folder = os.path.dirname(path)
	if not os.path.isdir(folder):
		os.makedirs(folder)
	with open(path, "w", newline="\n") as f:
		f.write("<?xml version=\"1.0\"?>\n")
		f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
		f.write("  <STRUCT>\n")
		for l in lines:
			f.write(l + "\n")
		f.write("  </STRUCT>\n")
		f.write("</FORM>\n")
	print(path)

for cat in categories:
	for letter, civ in civs:
		credit = "BC" + letter.upper() + cat["code"].upper() + "CA"
		rootIndex = cat["rootIndex"][civ]
		rootName = "bcpa%02d" % rootIndex
		plans = [ "BC" + letter.upper() + cat["code"].upper() + p.upper() for p in cat["ownPlans"] ] + cat["otherPlans"]
		writeSheet(rootFolder + "\\" + rootName + ".sbrick", [
			"    <STRUCT Name=\"Basics\">",
			"      <ATOM Name=\"FamilyId\" Value=\"BCPA\"/>",
			"      <ATOM Name=\"IndexInFamily\" Value=\"" + str(rootIndex) + "\"/>",
			"      <ATOM Name=\"Property 0\" Value=\"FPLAN: " + " ".join(plans) + "\"/>",
			"      <ATOM Name=\"LearnRequiresOneOfSkills\" Value=\"SC 0\"/>",
			"      <ATOM Name=\"Action Nature\" Value=\"CRAFT\"/>",
			"      <ATOM Name=\"Skill\" Value=\"" + cat["skill"] + "\"/>",
			"    </STRUCT>",
			"    <STRUCT Name=\"Client\">",
			"      <ATOM Name=\"Icon\" Value=\"" + cat["icon"] + "\"/>",
			"      <ATOM Name=\"IconBack\" Value=\"bk_" + civ + "_brick.png\"/>",
			"      <ATOM Name=\"IconOver\" Value=\"fp_over.png\"/>",
			"    </STRUCT>",
			"    <STRUCT Name=\"Optional\">",
			"      <ATOM Name=\"f0\" Value=\"BCOA\"/>",
			"      <ATOM Name=\"f1\" Value=\"BCOB\"/>",
			"      <ATOM Name=\"f2\" Value=\"BCOC\"/>",
			"      <ATOM Name=\"f3\" Value=\"BCOD\"/>",
			"    </STRUCT>",
			"    <STRUCT Name=\"Parameter\">",
			"      <ATOM Name=\"f0\" Value=\"" + credit + "\"/>",
			"    </STRUCT>",
			"    <STRUCT Name=\"faber\">",
			"      <ATOM Name=\"Tool type\" Value=\"" + cat["tool"] + "\"/>",
			"    </STRUCT>",
		])
		for level, recommended, sabrinaCost, spCost in levels:
			creditName = credit.lower() + "%02d" % level
			writeSheet(creditFolder + "\\" + creditName + ".sbrick", [
				"    <STRUCT Name=\"Basics\">",
				"      <ATOM Name=\"FamilyId\" Value=\"" + credit + "\"/>",
				# IndexInFamily defaults to the number in the sheet name (sbrick DFN: $filename), which is the level
				"      <ATOM Name=\"SabrinaCost\" Value=\"" + str(sabrinaCost) + "\"/>",
				"      <ATOM Name=\"SPCost\" Value=\"" + str(spCost) + "\"/>",
				"      <ATOM Name=\"Property 0\" Value=\"CR_RECOMMENDED: " + str(recommended) + "\"/>",
				"      <ATOM Name=\"LearnRequiresOneOfSkills\" Value=\"SC 0\"/>",
				"      <ATOM Name=\"CivRestriction\" Value=\"" + civ + "\"/>",
				"    </STRUCT>",
				"    <STRUCT Name=\"Client\">",
				"      <ATOM Name=\"Icon\" Value=\"ico_level.png\"/>",
				"      <ATOM Name=\"IconBack\" Value=\"pa_back.png\"/>",
				"      <ATOM Name=\"IconOver\" Value=\"pa_over_more.png\"/>",
				"    </STRUCT>",
			])
			writeSheet(phraseFolder + "\\a" + creditName + ".sphrase", [
				"    <ATOM Name=\"brick 0\" Value=\"" + rootName + ".sbrick\"/>",
				"    <ATOM Name=\"brick 1\" Value=\"" + creditName + ".sbrick\"/>",
			])

for path, lines in sheets:
	checkUnique(os.path.basename(path), path)
for path, lines in sheets:
	saveSheet(path, lines)
