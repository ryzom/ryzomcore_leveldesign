# The craft actions of Ryzom Core, every grade up to 250: the craft roots (bcpa*), the credits that set the quality an
# action makes (bc??ca*, the tool credits bc?tca*, the construction credits bcka?bca*), the boost options (bco?*), and
# the phrases that join a root to a credit (abc<credit>), teach a boost (abco?*) or give another role its crafting start
# (ab{f,m,hf}?aca01). It replaces scripts/generate_r2_sheets/generate_craft_actions.py, which made the four armor
# actions of grade 1 and is to be removed.
#
# What the code does with them (survey_server.md 6): the first brick of a phrase picks the craft phrase class; the
# server reads FOCUS and the CR_* properties from the credit and option bricks only, CR_RECOMMENDED being the action's
# level; the plan comes from the craft window, which offers the known plans of the families the root lists in its
# FPLAN: property (Property 0, read by the client only). The root's faber Tool type must be the type of the crafting
# tool in hand, or the client greys the action (CSPhraseManager::updateMemoryCtrlState); the server never reads it.
#
# The plans (the role E families: civilisation, common, refugee and tribe plans, the kami and karavan faction plans
# BCOKA*, the construction plans BCKAMMI and BCKARMI) and their phrases are made by domains/plans.py; this domain
# offers their families in the roots' FPLAN and reads their family rule from there.

import os, re
import framework
from balancing import common
from balancing import craft as B
import plan_items as PI
from domains.plans import planFamily, isPlan, skill as skillOfItem

OWNS = [
	"sbrick/craft/root",         # the 33 roots and their parents (generate_craft_actions.py wrote six roots here)
	"sbrick/craft/credit",       # the credits by category (generate_craft_actions.py wrote four in credit/recommended)
	"sbrick/craft/option",       # the boost options
	"sphrase/craft/action",      # the craft actions and the crafting starts of the other roles
	"sphrase/craft/option",      # the phrases that teach a boost
	"sphrase/craft/recommended", # where generate_craft_actions.py wrote the armor actions: they move to sphrase/craft/action
]

# civilisation: letter in the family names, CivRestriction (people.typ), the name the texts give it
CIVS = [
	( "f", "fyros", "Fyros" ),
	( "m", "matis", "Matis" ),
	( "t", "tryker", "Tryker" ),
	( "z", "zorai", "Zoraï" ),
]

# The categories of the civilisation roots, in the order of their numbers: the root of civilisation c (0..3) and the
# category of offset k is bcpa(6c + k), as the root names say (bcpa01 Fyros Melee Weapons ... bcpa24 Zorai Jewels).
# A civilisation's action offers its own plan families (own, after BC<civ>) and the shared ones: the common and refugee
# families, as generate_craft_actions.py did, and the tribe and the kami and karavan faction families, which belong to
# no civilisation either. word is what the root and credit names carry; skill trains nothing (the plan's skill gains
# the XP) but is the branch the client checks the tool against and the skill of the learn gates: the deepest skill above
# every plan the action makes (ammunition plans train the range weapon skills, design.md 9).
CATEGORIES = [
	{ "code": "m", "offset": 1, "folder": "melee_weapon", "word": "Melee", "skill": "SCM", "icon": "fp_melee.png",
		"tool": "MeleeWeaponTool", "options": True, "own": [ "MEA" ],
		"shared": [ "BCCMEA", "BCRMEA", "BCBMEA", "BCOKAMM01", "BCOKAMM02", "BCOKARM01", "BCOKARM02" ] },
	{ "code": "r", "offset": 2, "folder": "range_weapon", "word": "Range", "skill": "SCR", "icon": "fp_range.png",
		"tool": "RangeWeaponTool", "options": True, "own": [ "REA" ],
		"shared": [ "BCCREA", "BCBREA", "BCOKAMR01", "BCOKAMR02", "BCOKARR01", "BCOKARR02" ] },
	# ammunition is used up, so it takes no boost
	{ "code": "p", "offset": 3, "folder": "ammo", "word": "Ammo", "skill": "SCR", "icon": "fp_ammo.png", "icon2": "am_logo.png",
		"tool": "AmmoTool", "options": False, "own": [ "PEA" ], "shared": [ "BCCPEA" ] },
	{ "code": "a", "offset": 4, "folder": "armor", "word": "Armor", "skill": "SCA", "icon": "fp_armor.png",
		"tool": "ArmorTool", "options": True, "own": [ "AEA", "AEB", "AEC", "AED" ],
		"shared": [ "BCCAEA", "BCCAEB", "BCCAEC", "BCCAED", "BCRAEA" ] },
	# shields are made with the armor tool (the code has no shield tool); the shield skills are their own branch
	{ "code": "s", "offset": 5, "folder": "shield", "word": "Shield", "skill": "SCAS", "icon": "fp_shield.png",
		"tool": "ArmorTool", "options": True, "own": [ "SEA" ], "shared": [ "BCCSEA" ] },
	# no common jewel family exists (abccjea01-06 are phrases without bricks)
	{ "code": "j", "offset": 6, "folder": "jewel", "word": "Jewel", "skill": "SCJ", "icon": "fp_jewel.png",
		"tool": "JewelryTool", "options": True, "own": [ "JEA" ], "shared": [] },
]

# The generic roots offer the shared families of their category. Their credit families BCCMCA, BCCRCA and BCCPCA have no
# translation rows, so no credit and no action can be made for them: the roots are made so the code's grammar is whole,
# and no phrase teaches them until those credits get rows.
GENERIC = [ ( 25, "m", "BCCMCA" ), ( 26, "r", "BCCRCA" ), ( 27, "p", "BCCPCA" ) ]

# The tool roots, one per civilisation (bcpa30-33), offer the kami and karavan tool plans, the only tool plans there are.
# A tool takes no boost: it is held to work, not worn for its scores.
TOOLS = { "code": "t", "first": 30, "folder": "tool", "word": "Tool", "skill": "SC", "icon": "fp_tools.png",
	"tool": "ToolMaker", "options": False, "own": [], "shared": [ "BCOKAMT01", "BCOKAMT02", "BCOKART01", "BCOKART02" ] }
TOOL_GRADE_IDS = [ 1, 10, 15, 20, 25 ] # the named tool credits, "Tools 1" to "Tools 5"; the others are <GEN> placeholders

# The construction roots: root number, credit family, plan family, background, the name the texts give the faction.
# The code has no construction tool type; the jewelry tool is the one their roots have always asked for. Constructions
# take no boost and train the craft root SC (design.md 9).
CONSTRUCTION = { "folder": "construction", "word": "Construction", "skill": "SC", "icon": "fp_building.png",
	"tool": "JewelryTool", "options": False }
CONSTRUCTIONS = [
	( 28, "BCKAMBCA", "BCKAMMI", "bk_kami.png", "Kami" ),
	( 29, "BCKARBCA", "BCKARMI", "bk_karavan.png", "Karavan" ),
]

# the boost options: family, folder, property, icon
OPTIONS = [
	( "BCOA", "hp", "CR_HP", "ico_heal.png" ),
	( "BCOB", "sap", "CR_SAP", "ico_sap.png" ),
	( "BCOC", "sta", "CR_STA", "ico_stamina.png" ),
	( "BCOD", "focus", "CR_FOCUS", "ico_focus.png" ),
]
OPTION_FAMILIES = [ o[0] for o in OPTIONS ]

# the crafting start of the fight, magic and forage roles: the armor action of grade 1 of a civilisation
START_ROLES = [ "f", "m", "hf" ]

# the ids with the craft prefix that are starts of the craft role in other domains (magic start, basic extraction)
OTHER_DOMAIN_STARTS = re.compile(r"^abc(_magic_start|fepa01)$")

ATLASES = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ] # in pipeline/install/interfaces

# ----------------------------------------------------------------------------------------------------------- checks
def loadAtlas(gen):
	folder = os.path.normpath(os.path.join(framework.LEVELDESIGN, "..", "pipeline", "install", "interfaces"))
	names = set()
	for a in ATLASES:
		path = os.path.join(folder, a)
		if not os.path.isfile(path):
			gen.error("craft: the interface atlas list " + path + " does not exist, so the icons cannot be checked: build the interfaces or fix the path")
			continue
		with open(path, "r", encoding="utf-8", errors="replace") as f:
			for l in f:
				if l.strip():
					names.add(l.split()[0].lower())
	return names

def checkText(gen, brick):
	"""every $ token of the brick's texts names a property the brick has, with an argument it has"""
	row = gen.sbrickWords.get(brick.name)
	if not row:
		return
	properties = brick.effective()[1]
	args = {}
	for p in properties:
		keyword, sep, tail = p.partition(":")
		args[keyword.strip().lower()] = len([ a for a in tail.split(":") if a.strip() ]) if keyword.strip().lower() != "fplan" else 1
	for text in ( row.name, row.description, row.description2 ):
		for m in re.finditer(r"\$(\$|\|?(\d?)\|?([A-Za-z_]+))", text):
			if m.group(1) == "$":
				continue
			key = m.group(3).lower()
			index = int(m.group(2)) if m.group(2) else 0
			if key not in args:
				gen.error(brick.name + " (" + brick.source + "): its text shows $" + m.group(1) + ", but the brick has no " + key.upper() + " property")
			elif index >= args[key]:
				gen.error(brick.name + " (" + brick.source + "): its text shows argument " + str(index) + " of " + key.upper() + ", which has " + str(args[key]))

def checkQualityText(gen, phraseId, quality):
	"""the phrase text states the quality its credit makes ("Lets you make Fyros armor of quality 10.")"""
	row = gen.sphraseWords.get(phraseId)
	if not row:
		gen.error("craft: the action " + phraseId + " has no row in the translation (sphrase_words_wk.txt)")
		return
	m = re.search(r"quality (\d+)", row.description)
	if not m:
		gen.error("craft: the text of " + phraseId + " states no quality (\"" + row.description + "\"), so the grade rule cannot be checked")
	elif int(m.group(1)) != quality:
		gen.error("craft: the text of " + phraseId + " states quality " + m.group(1) + ", the grade rule of balancing/craft.py gives " + str(quality))

def checkName(gen, sheetId, words):
	"""the English name of a brick carries the words its place in the table implies, so a shifted table shows"""
	row = gen.sbrickWords.get(sheetId)
	if not row:
		gen.error("craft: " + sheetId + " has no row in the translation (sbrick_words_wk.txt)")
		return False
	for w in words:
		if w.lower() not in row.name.lower():
			gen.error("craft: " + sheetId + " is named \"" + row.name + "\", the table expects " + " and ".join(words) + " in it")
			return False
	return True

def gradeIds(gen, family):
	"""(id, number) of a credit or option family in the translation, by number"""
	result = []
	for i in gen.sbrickWords.ids("^" + family.lower() + r"\d+$"):
		result.append((i, int(re.match(r"^[a-z]+(\d+)$", i).group(1))))
	return sorted(result, key=lambda x: x[1])

# --------------------------------------------------------------------------------------------------------- generate
def generate(gen):
	atlas = loadAtlas(gen)
	translatedPlanFamilies = set(planFamily(i) for i in gen.sbrickWords.ids(r"^bc") if isPlan(i))
	made = [] # the bricks and parents of this domain, for the icon and text checks
	offered = {} # plan family: the roots that list it

	def checkPlans(where, plans):
		for f in plans:
			offered.setdefault(f, []).append(where)
			if f not in framework.FAMILIES or not framework.familyIs(f, "mandatory") or framework.brickType(f) != "FABER":
				gen.error("craft: " + where + " lists " + f + " in FPLAN:, which is no craft plan family of the code (brick_families.h)")
			elif f not in translatedPlanFamilies:
				gen.error("craft: " + where + " lists " + f + " in FPLAN:, but no plan id of the translation is of that family")

	# ---- roots
	rootParent = gen.parent("_bcpa", "sbrick/craft/root", basics={ "FamilyId": "BCPA", "Action Nature": "CRAFT",
		"Level": B.ROOT_LEVEL, "SPCost": B.rootSpCost() }, client={ "IconOver": "fp_over.png" })
	made.append(rootParent)
	categoryParents = {}
	for cat in CATEGORIES + [ TOOLS, CONSTRUCTION ]:
		client = { "Icon": cat["icon"] }
		if "icon2" in cat:
			client["IconOver2"] = cat["icon2"]
		if not framework.tableHas("crafting_tool_type:TCraftingToolType:stringTable", cat["tool"], True):
			gen.error("craft: tool type " + cat["tool"] + " of the " + cat["folder"] + " roots is not one of the code (crafting_tool_type.cpp)")
		fields = { "basics": { "Skill": cat["skill"], "LearnRequiresOneOfSkills": common.learnRequires([ cat["skill"] ], B.FIRST_QUALITY) },
			"client": client, "faber": { "Tool type": cat["tool"] } }
		if cat["options"]:
			fields["optional"] = OPTION_FAMILIES
		p = gen.parent("_bcpa_" + cat["folder"], "sbrick/craft/root", parent=rootParent, **fields)
		categoryParents[cat["folder"]] = p
		made.append(p)

	def root(index, cat, back, plans, credit, words, civ=None):
		name = "bcpa%02d" % index
		if not checkName(gen, name, words):
			return None
		checkPlans(name, plans)
		basics = { "IndexInFamily": index }
		if civ:
			basics["CivRestriction"] = civ
		b = gen.brick(name, "sbrick/craft/root", "craft root " + " ".join(words), parent=categoryParents[cat["folder"]],
			basics=basics, client={ "IconBack": back }, properties=[ "FPLAN: " + " ".join(plans) ], parameter=[ credit ])
		made.append(b)
		return name

	roots = {} # (civ letter, category code): root name, for the actions
	for c, (letter, civ, civName) in enumerate(CIVS):
		back = "bk_" + civ + "_brick.png"
		for cat in CATEGORIES:
			plans = [ "BC" + letter.upper() + p for p in cat["own"] ] + cat["shared"]
			roots[(letter, cat["code"])] = root(6 * c + cat["offset"], cat, back, plans, "BC" + letter.upper() + cat["code"].upper() + "CA",
				[ civName, cat["word"] ], civ)
		roots[(letter, "t")] = root(TOOLS["first"] + c, TOOLS, back, TOOLS["own"] + TOOLS["shared"], "BC" + letter.upper() + "TCA",
			[ civName, TOOLS["word"] ], civ)
	for index, code, credit in GENERIC:
		cat = [ k for k in CATEGORIES if k["code"] == code ][0]
		root(index, cat, "bk_generic_brick.png", cat["shared"], credit, [ cat["word"] ])
		if gen.sbrickWords.ids("^" + credit.lower() + r"\d+$"):
			gen.error("craft: the translation has " + credit + " credits now: make their actions for bcpa%02d" % index)
	for index, credit, plan, back, faction in CONSTRUCTIONS:
		roots[(faction, "k")] = root(index, CONSTRUCTION, back, [ plan ], credit, [ faction, CONSTRUCTION["word"] ])

	# ---- credits and the actions that join them to their root
	creditParent = gen.parent("_bc_credit", "sbrick/craft/credit",
		client={ "Icon": "ico_level.png", "IconBack": "pa_back.png", "IconOver": "pa_over_more.png" })
	made.append(creditParent)

	def credit(sheetId, folder, parent, number, quality, skill, rootName, words):
		if not checkName(gen, sheetId, words):
			return
		b = gen.brick(sheetId, "sbrick/craft/credit/" + folder, "craft credit " + " ".join(words) + " quality " + str(quality), parent=parent,
			basics={ "IndexInFamily": number, "Level": quality, "SabrinaCost": B.creditSabrina(quality), "SPCost": B.creditSpCost(quality),
				"LearnRequiresOneOfSkills": common.learnRequires([ skill ], quality) },
			properties=[ "CR_RECOMMENDED: %d" % quality, "FOCUS: %d" % B.actionFocus(quality) ])
		made.append(b)
		checkQualityText(gen, "a" + sheetId, quality)
		if rootName:
			gen.phrase("a" + sheetId, "sphrase/craft/action/" + folder, [ rootName, sheetId ], "craft action " + " ".join(words) + " quality " + str(quality))

	def gradedFamily(family, folder, civ, skill, rootName, words):
		basics = { "FamilyId": family }
		if civ:
			basics["CivRestriction"] = civ
		parent = gen.parent("_" + family.lower(), "sbrick/craft/credit/" + folder, parent=creditParent, basics=basics)
		made.append(parent)
		ids = gradeIds(gen, family)
		if [ n for i, n in ids ] != list(range(1, 26)):
			gen.error("craft: the translation gives " + family + " the numbers " + ", ".join(str(n) for i, n in ids) + ", the table expects 01 to 25")
		for i, n in ids:
			credit(i, folder, parent, n, B.creditQuality(n), skill, rootName, words)

	for letter, civ, civName in CIVS:
		for cat in CATEGORIES:
			gradedFamily("BC" + letter.upper() + cat["code"].upper() + "CA", cat["folder"], civ, cat["skill"], roots[(letter, cat["code"])],
				[ civName, cat["word"] ])
		# tool credits: five named grades, the other numbers are placeholders without text
		family = "BC" + letter.upper() + "TCA"
		parent = gen.parent("_" + family.lower(), "sbrick/craft/credit/" + TOOLS["folder"], parent=creditParent,
			basics={ "FamilyId": family, "CivRestriction": civ })
		made.append(parent)
		for i, n in gradeIds(gen, family):
			row = gen.sbrickWords.get(i)
			if row.name.startswith("<GEN>"):
				if n in TOOL_GRADE_IDS:
					gen.error("craft: the tool credit " + i + " is a <GEN> placeholder, the table expects a named grade there")
				gen.exclude("sbrick", i, "tool credit placeholder (<GEN>, no text): tools have five named grades, 01 10 15 20 25 (Tools 1 to 5)")
				continue
			if n not in TOOL_GRADE_IDS:
				gen.error("craft: the tool credit " + i + " has a name (\"" + row.name + "\"), the table expects one only for " + ", ".join("%02d" % g for g in TOOL_GRADE_IDS))
				continue
			grade = TOOL_GRADE_IDS.index(n) + 1
			credit(i, TOOLS["folder"], parent, n, B.toolQuality(grade), TOOLS["skill"], roots[(letter, "t")], [ civName, TOOLS["word"] + "s " + str(grade) ])
	for index, family, plan, back, faction in CONSTRUCTIONS:
		gradedFamily(family, CONSTRUCTION["folder"], None, CONSTRUCTION["skill"], roots[(faction, "k")], [ faction, CONSTRUCTION["word"] ])

	# ---- boost options and the phrases that teach them (not castable: an option alone has no root)
	optionParent = gen.parent("_bc_option", "sbrick/craft/option", client={ "IconBack": "op_back.png", "IconOver": "op_over_more.png" })
	made.append(optionParent)
	for family, folder, keyword, icon in OPTIONS:
		parent = gen.parent("_" + family.lower(), "sbrick/craft/option/" + folder, parent=optionParent, basics={ "FamilyId": family },
			client={ "Icon": icon })
		made.append(parent)
		ids = gradeIds(gen, family)
		if [ n for i, n in ids ] != list(range(1, 26)):
			gen.error("craft: the translation gives " + family + " the numbers " + ", ".join(str(n) for i, n in ids) + ", the table expects 01 to 25")
		for i, n in ids:
			level = B.optionLevel(n)
			b = gen.brick(i, "sbrick/craft/option/" + folder, "craft option " + keyword + " level " + str(level), parent=parent,
				basics={ "IndexInFamily": n, "Level": level, "SabrinaCost": B.boostSabrina(level), "SPCost": B.boostSpCost(level),
					"LearnRequiresOneOfSkills": common.learnRequires([ "SC" ], level) },
				properties=[ "%s: %d" % (keyword, B.boostPoints(level)), "FOCUS: %d" % B.boostFocus(level) ])
			made.append(b)
			if not gen.sphraseWords.get("a" + i):
				gen.error("craft: the option " + i + " has no phrase a" + i + " in the translation")
				continue
			gen.phrase("a" + i, "sphrase/craft/option/" + folder, [ i ], "craft option phrase " + keyword + " level " + str(level), castable=False)

	# ---- the crafting starts of the fight, magic and forage roles: the armor action of grade 1, taught only by a role
	# (their names carry the fight, magic and forage prefixes, so a rolemaster of that kind would sell them for its own
	# skill points) and left out of the progression, which lists the same action as abc?aca01
	for role in START_ROLES:
		for letter, civ, civName in CIVS:
			name = "ab" + role + letter + "aca01"
			if not gen.sphraseWords.get(name):
				gen.error("craft: the crafting start " + name + " has no row in the translation")
				continue
			gen.phrase(name, "sphrase/craft/action/start", [ roots[(letter, "a")], "bc" + letter + "aca01" ], "crafting start of role " + role + ", " + civ,
				showInAPOnlyIfLearnt=True, showInActionProgression=False)

	# ---- checks of this domain
	for s in made:
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("craft: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
		if not s.isParent:
			checkText(gen, s)
	# every plan family is offered by a root, and the skill of each plan it offers lies in the root's branch (the skill
	# the client checks the tool against and the learn gates name): read from the plan ids, so it holds whichever domain
	# runs first
	rootSkills = { n: gen.bricks[n].effective()[0].get("Skill", "") for names in offered.values() for n in names if n in gen.bricks }
	for p, item in PI.plans()[0].items():
		family = planFamily(p)
		if family not in offered:
			gen.error("craft: no root offers the plan family " + family + " of " + p + " (FPLAN)")
			continue
		planSkill = skillOfItem(PI.itemType(item))
		for rootName in offered[family]:
			if rootName in rootSkills and not planSkill.startswith(rootSkills[rootName]):
				gen.error("craft: the root " + rootName + " offers " + family + ", whose plan " + p + " trains " + planSkill
					+ ", outside the root's branch " + rootSkills[rootName])

	# ---- anything else of the craft prefix: the plans and their phrases are the plans domain's (domains/plans.py)
	for i in gen.sbrickWords.ids(r"^bc"):
		if i in gen.bricks or ("sbrick", i) in gen.excluded or isPlan(i):
			continue
		gen.error("craft: the translation id " + i + " has the craft prefix, but neither the craft nor the plans domain has a rule for it")
	for i in gen.sphraseWords.ids(r"^abc"):
		if i in gen.phrases or ("sphrase", i) in gen.excluded or OTHER_DOMAIN_STARTS.match(i) or isPlan(i[1:]):
			continue
		gen.error("craft: the translation id " + i + " has the craft prefix, but neither the craft nor the plans domain has a rule for it")
