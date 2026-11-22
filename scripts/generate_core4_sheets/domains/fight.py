# The fight actions of Ryzom Core, every grade the texts name (up to level 275): the combat root bfpa01, the options
# BFOA and BFOB with their parameters BFMA..BFMH, the aim chain (aim option, body type BFME, location BF?ME, leveled aim
# BFA???ME), the combat credits BFCA..BFCG, and the phrases: abf01, the default attack every role starts with and every
# NPC attacks with (ai_generic_fight_helpers.cpp), the ready-made actions named after their parameter (a + brick id),
# the attacks after an opening, and the upgrades that teach a credit.
#
# What the code does with them (survey_server.md 1, phrase_manager/combat_phrase.cpp): the first brick picks the combat
# phrase class; addBrick reads every brick the same way, by its properties and the sign of its Sabrina value, and never
# looks at a family; the families only make the grammar that checkPhraseValidity applies at memorize. The skill trained
# is the weapon's, so the bricks' Skill trains nothing, but the client reads it: a combat phrase is usable with a weapon
# only when the skills of all its bricks lie on that weapon's branch (CSPhraseManager::skillCompatibleWithCombatPhrase),
# the composer offers only options whose skills stay on one branch and drops options without a skill
# (CDBGroupBuildPhrase::filterSkillSetuped), and the help names the restriction from the uiawr* texts of wk.uxt.
#
# The numbers are in balancing/fight.py. The levels, credits, durations and total damages the texts state are read from
# the texts, so the sheets say what the texts say.
#
# Rearranged against the old layout: every family has a parent sheet that carries what its bricks share (family, skill,
# icons, the properties that do not change with the grade), so a grade sheet holds its level, power, cost, price and
# gate; the four opening credits share a further parent (one opening per phrase, never cyclic), and the leveled aim
# families share one. Folders by role: root, option, modifier/<family>, aim/<body type>, credit/<family>.

import os, re
import framework
from balancing import common
from balancing import fight as B

OWNS = [
	"sbrick/fight", # the root, options, parameters, aim chain and credits (the BIF bricks in sbrick/fight/interface go to misc)
	"sphrase/fight",
]

# the phrase ids with the fight prefix that other domains make: the magic start of the fighter, the crafting starts and
# the basic extraction other roles get
OTHER_DOMAIN_PHRASES = re.compile(r"^abf(_magic_start|[fmtz]aca01|fepa01)$")

ATLASES = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ] # in pipeline/install/interfaces

ROOT = "bfpa01"
ROOT_ICONS = { "Icon": "ico_multi_fight.png", "IconBack": "bk_generic_brick.png" }

# The options of BFOA, each with its parameter family. The skills are the weapons the option fits (the client checks
# them against the weapon in hand), named the way wk.uxt names its weapon restrictions: increase damage and accurate
# attack fit every weapon (uiawrSF); the hit rate raises a "firing rate" (bfoa02), so range weapons; circular attack hits
# "all enemies engaged in melee combat against you", so melee weapons; a cut bleeds, a point goes through armor, a blunt
# blow staggers: bleeding takes "Any Slashing Melee Weapon (not dagger)" (uiawrSFM1S_SFM2S), ignore armor "Any Piercing
# or Dagger Melee Weapon" (uiawrSFM1P_SFM2P_SFMCAD), slow attack "Any Blunt Melee Weapon" (uiawrSFM1B_SFM2B).
# special: SPECIAL_HIT, the residual hit effect the client plays for a strike that adds damage or an effect.
OPTIONS = [
	{ "id": "bfoa01", "words": "Increase Damage", "family": "BFMA", "skills": "SF", "special": True, "icon": "ico_power.png" },
	{ "id": "bfoa02", "words": "Hit Rate", "family": "BFMB", "skills": "SFR", "special": False, "icon": "ico_hit_rate.png" },
	{ "id": "bfoa03", "words": "Accurate Attack", "family": "BFMC", "skills": "SF", "special": False, "icon": "ico_accurate.png" },
	{ "id": "bfoa04", "words": "Bleeding", "family": "BFMD", "skills": "SFM1S:SFM2S", "special": True, "icon": "ico_bleeding.png" },
	{ "id": "bfoa05", "words": "Circular Attack", "family": "BFMF", "skills": "SFM", "special": True, "icon": "ico_circular_attack.png" },
	{ "id": "bfoa06", "words": "Ignore Armor", "family": "BFMG", "skills": "SFM1P:SFM2P:SFMCAD", "special": True, "icon": "ico_armor_penalty.png" },
	{ "id": "bfoa07", "words": "Slow Attack", "family": "BFMH", "skills": "SFM1B:SFM2B", "special": True, "icon": "ico_slow.png" },
]

def num(v):
	"""a number as a property argument: whole numbers without decimals, others with up to three"""
	if float(v) == int(v):
		return str(int(v))
	return ("%.3f" % v).rstrip("0")

# The parameter families: the words their names carry, the animation the strike plays (SET_BEHAVIOUR: the costliest
# brick of a phrase picks it; range attacks always play their own), and the properties every grade shares.
PARAMETERS = {
	"BFMA": { "words": "Increase Damage", "behaviour": "POWERFUL_ATTACK", "shared": [ "INC_DMG: %s:%s" % tuple(num(v) for v in B.INC_DMG) ] },
	"BFMB": { "words": "Hit Rate", "behaviour": None, "shared": [ "LATENCY_FACTOR: %s:%s" % tuple(num(v) for v in B.LATENCY_FACTOR) ] },
	"BFMC": { "words": "Accurate Attack", "behaviour": None, "shared": [ "ATT_SKILL_MOD: %s:%s" % tuple(num(v) for v in B.ATT_SKILL_MOD) ] },
	"BFMD": { "words": "Bleeding", "behaviour": "POWERFUL_ATTACK",
		"shared": [ "BLEED_FACTOR: %s:%s:%s" % (num(B.BLEED_DURATION), num(B.BLEED_FACTOR[0]), num(B.BLEED_FACTOR[1])) ] },
	# the total damage differs per grade: the bricks carry HIT_ALL_AGGRESSORS themselves
	"BFMF": { "words": "Circular Attack", "behaviour": "AREA_ATTACK", "shared": [] },
	"BFMG": { "words": "Ignore Armor", "behaviour": "POWERFUL_ATTACK",
		"shared": [ "ARMOR_MOD: %s:%s:%s" % (B.ARMOR_MOD[0], num(B.ARMOR_MOD[1]), num(B.ARMOR_MOD[2])) ] },
	"BFMH": { "words": "Slow Attack", "behaviour": "POWERFUL_ATTACK",
		"shared": [ "COMBAT_SLOW: %s:%s:%s" % (num(B.COMBAT_SLOW_DURATION), num(B.COMBAT_SLOW[0]), num(B.COMBAT_SLOW[1])) ] },
}

# The aim chain: the option bfob01 takes a body type (BFME), the body type a location (BFHME, BFKME, BFQME), the
# location a leveled aim brick, whose AIM property names the body type and slot of the code (body.cpp,
# slot_equipment.cpp) and whose PowerValue sets the chance to hit that slot (aim factor = PowerValue / reference).
# code: the letter of the ids; index: its BFME number; body: BODY::TBodyType; words: in its names; over: the icon layer
# that tells the three apart.
BODIES = [
	{ "code": "h", "index": 1, "body": "Homin", "words": "Humanoid", "folder": "humanoid", "over": "ico_over_homin.png" },
	{ "code": "k", "index": 2, "body": "LandKitin", "words": "Kitin", "folder": "land_kitin", "over": "ico_over_kitin.png" },
	{ "code": "q", "index": 3, "body": "Quadruped", "words": "Quadruped", "folder": "quadruped", "over": "ico_over_fauna.png" },
]
# code: the letters in the family names (BFA<body><code>ME); index: the location's number; slot: SLOT_EQUIPMENT name;
# the words the humanoid names and the kitin and quadruped names carry. The kitin and quadruped descriptions swap upper
# and lower against their names (survey_translations.md 6.4): the names and the family letters agree, so they decide.
LOCATIONS = [
	{ "code": "h", "index": 1, "slot": "Head", "homin": "Head", "beast": "Head", "icon": "ico_aim_homin_head.png" },
	{ "code": "c", "index": 2, "slot": "Body", "homin": "Chest", "beast": "Body", "icon": "ico_aim_homin_chest.png" },
	{ "code": "a", "index": 3, "slot": "Arms", "homin": "Arms", "beast": "Upper Forelegs", "icon": "ico_aim_homin_arms.png" },
	{ "code": "ha", "index": 4, "slot": "Hands", "homin": "Hands", "beast": "Lower Forelegs", "icon": "ico_aim_homin_hands.png" },
	{ "code": "l", "index": 5, "slot": "Legs", "homin": "Legs", "beast": "Upper Hind Legs", "icon": "ico_aim_homin_legs.png" },
	{ "code": "f", "index": 6, "slot": "Feet", "homin": "Feet", "beast": "Lower Hind Legs", "icon": "ico_aim_homin_feet.png" },
]
AIM_SKILLS = "SF" # aiming works with every weapon

# The credits: the words their names carry, the icon, the opening flag they wait for (BRICK_FLAGS), the weapons they
# fit. Wearing out a weapon needs one in hand: "Any Weapon, but not with Close Combat" (uiawrSFM1_SFM2_SFMCAD_SFR1_SFR2),
# and UsableWithEmptyHands false. The feint is a melee action (the opponent must be engaged on the user,
# CCombatPhrase::validate), so the opening after a feint is melee too.
CREDITS = [
	{ "family": "BFCA", "words": "Stamina Credit", "icon": "ico_stamina.png", "opening": None, "skills": "SF" },
	{ "family": "BFCB", "words": "HP Credit", "icon": "ico_heal.png", "opening": None, "skills": "SF" },
	{ "family": "BFCC", "words": "Opening After Dodge", "icon": "ico_dodge.png", "opening": "Dodge", "skills": "SF" },
	{ "family": "BFCD", "words": "Opening After Parry", "icon": "ico_parry.png", "opening": "Parry", "skills": "SF" },
	{ "family": "BFCE", "words": "Opening After Critical Hit", "icon": "ico_opening_hit.png", "opening": "CriticalHit", "skills": "SF" },
	{ "family": "BFCF", "words": "Wear Out Weapon", "icon": "ico_disarm.png", "opening": None, "skills": "SFM1:SFM2:SFMCAD:SFR1:SFR2" },
	{ "family": "BFCG", "words": "Opening After Feint", "icon": "ico_feint.png", "opening": "Feint", "skills": "SFM" },
]
# The ready-made attacks after an opening: their texts name the parameter by its level ("recommended skill level of
# 20"); phrase family, the option and parameter family of the attack, the opening credit family.
OPENING_ATTACKS = [ ( "abfcc", "bfoa01", "BFMA", "BFCC" ), ( "abfcd", "bfoa03", "BFMC", "BFCD" ) ]
# the upgrades that teach one credit ("Gives you a credit stanza which consumes hit points.")
CREDIT_UPGRADES = [ ( "abfcb", "BFCB" ), ( "abfce", "BFCE" ), ( "abfcf", "BFCF" ), ( "abfcg", "BFCG" ) ]

NOT_TO_APPEAR = "Ne devrait pas apparaître" # the text of the wear credits 6 to 11

# ------------------------------------------------------------------------------------------------------------ helpers
def loadAtlas(gen):
	folder = os.path.normpath(os.path.join(framework.LEVELDESIGN, "..", "pipeline", "install", "interfaces"))
	names = set()
	for a in ATLASES:
		path = os.path.join(folder, a)
		if not os.path.isfile(path):
			gen.error("fight: the interface atlas list " + path + " does not exist, so the icons cannot be checked: build the interfaces or fix the path")
			continue
		with open(path, "r", encoding="utf-8", errors="replace") as f:
			for l in f:
				if l.strip():
					names.add(l.split()[0].lower())
	return names

def loadSkillTree(gen):
	"""skill: (MaxSkillValue, ParentSkill or None), from game_element/xp_table/skills.skill_tree"""
	path = os.path.join(framework.GAME_ELEMENT, "xp_table", "skills.skill_tree")
	tree = {}
	if not os.path.isfile(path):
		gen.error("fight: " + path + " does not exist, so the learn gates cannot be put on the skills of their branch")
		return tree
	with open(path, "r", encoding="utf-8", errors="replace") as f:
		text = f.read()
	for chunk in text.split("<STRUCT Name=\"")[1:]:
		code = re.search(r"<ATOM Name=\"SkillCode\" Value=\"([^\"]+)\"", chunk)
		value = re.search(r"<ATOM Name=\"MaxSkillValue\" Value=\"(\d+)\"", chunk)
		if code and value:
			parent = re.search(r"<ATOM Name=\"ParentSkill\" Value=\"([^\"]+)\"", chunk)
			tree[code.group(1)] = (int(value.group(1)), parent.group(1) if parent else None)
	return tree

def gateSkills(gen, tree, skills, gate):
	"""LearnRequiresOneOfSkills for a brick of these skills and this gate. A skill stays locked until its parent reaches
	its maximum, and a parent's highest value follows its best child, so the gate goes on the branch's skill whose range
	holds the gate value: a slashing brick gated at 15 asks SF 15, at 80 SFM1 80 or SFM2 80, at 190 SFM1S 190."""
	chosen = []
	for s in skills.split(":"):
		if s not in tree:
			gen.error("fight: the skill " + s + " is not in skills.skill_tree")
			continue
		chain = []
		k = s
		while k:
			chain.insert(0, k)
			k = tree.get(k, (0, None))[1]
		pick = next((k for k in chain if tree[k][0] >= gate), s)
		if pick not in chosen:
			chosen.append(pick)
	return ":".join("%s %d" % (k, gate) for k in chosen)

def textNumber(gen, sheetId, pattern, what, kind="sbrick"):
	"""the number a brick's (or phrase's) English text states, by a regular expression with one group"""
	row = gen.sbrickWords.get(sheetId) if kind == "sbrick" else gen.sphraseWords.get(sheetId)
	if not row:
		gen.error("fight: " + sheetId + " has no row in the translation")
		return None
	m = re.search(pattern, row.name + " | " + row.description + " | " + getattr(row, "description2", ""), re.I)
	if not m:
		gen.error("fight: the text of " + sheetId + " states no " + what + " (\"" + row.description + "\")")
		return None
	return int(m.group(1))

def checkName(gen, sheetId, words, kind="sbrick"):
	"""the English name carries the words its place in the tables implies, so a shifted table shows"""
	row = gen.sbrickWords.get(sheetId) if kind == "sbrick" else gen.sphraseWords.get(sheetId)
	if not row:
		gen.error("fight: " + sheetId + " has no row in the translation")
		return False
	for w in words:
		if w.lower() not in row.name.lower():
			gen.error("fight: " + sheetId + " is named \"" + row.name + "\", the tables expect \"" + w + "\" in it")
			return False
	return True

def checkText(gen, brick):
	"""every $ token of the brick's texts names a property the brick has, with an argument it has"""
	row = gen.sbrickWords.get(brick.name)
	if not row:
		return
	args = {}
	for p in brick.effective()[1]:
		keyword, sep, tail = p.partition(":")
		args[keyword.strip().lower()] = len([ a for a in tail.split(":") if a.strip() ])
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

def grades(gen, prefix):
	"""(id, number) of the ids <prefix><two digits> in the translation, by number"""
	result = []
	for i in gen.sbrickWords.ids("^" + prefix + r"\d+$"):
		result.append((i, int(re.match(r"^[a-z]+(\d+)$", i).group(1))))
	return sorted(result, key=lambda x: x[1])

LEVEL_TEXT = r"up to level (?:up to )?(\d+)" # "maximum efficiency for weapons up to level 10", "best used with a weapon of up to level up to 25"

# --------------------------------------------------------------------------------------------------------- generate
def generate(gen):
	# a row of no family whose text is the editor's default ("Put here the Stanza Description."): nothing to make
	gen.exclude("sbrick", "melee_reduce_latency_1", "no brick family and only the editor's default text: no action to make")
	atlas = loadAtlas(gen)
	tree = loadSkillTree(gen)
	made = [] # bricks and parents, for the icon and text checks
	staminaCredits = [] # (points, brick id), for the phrases
	levels = {} # parameter brick id: level
	costs = {} # brick id: Sabrina cost (positive) or credit (negative)

	def brick(name, folder, source, parent, basics, **fields):
		b = gen.brick(name, folder, source, parent=parent, basics=basics, **fields)
		made.append(b)
		costs[name] = basics.get("SabrinaCost", 0)
		return b

	def parent(name, folder, **fields):
		p = gen.parent(name, folder, **fields)
		made.append(p)
		return p

	def learn(skills, level):
		gate = B.learnGate(level)
		return gateSkills(gen, tree, skills, gate)

	for flag in [ c["opening"] for c in CREDITS if c["opening"] ] + [ "Feint" ]:
		if not framework.tableHas("brick_flags:TBrickFlag", flag, True):
			gen.error("fight: the flag " + flag + " is not a BRICK_FLAGS name of the code (brick_flags.cpp)")
	for b in BODIES:
		if not framework.tableHas("body:TBodyType", b["body"], True):
			gen.error("fight: the body type " + b["body"] + " is not one of the code (body.cpp)")
	for l in LOCATIONS:
		if not framework.tableHas("slot_equipment:TSlotEquipment:stringTable", l["slot"], True):
			gen.error("fight: the slot " + l["slot"] + " is not one of the code (slot_equipment.cpp)")
	for p in PARAMETERS.values():
		if p["behaviour"] and not framework.tableHas("mode_and_behaviour:EBehaviour", p["behaviour"], True):
			gen.error("fight: the behaviour " + p["behaviour"] + " is not one of the code (mode_and_behaviour.cpp)")

	# ---- the credits (first: the phrases need the stamina credits)
	credits = {} # family: [ (id, points) ]
	for c in CREDITS:
		family = c["family"]
		folder = "sbrick/fight/credit/" + family.lower()
		basics = { "FamilyId": family, "Skill": c["skills"] }
		if family == "BFCF":
			basics["UsableWithEmptyHands"] = False
		client = { "Icon": c["icon"], "IconBack": "cp_back.png", "IconOver": "cp_over_opening.png" if c["opening"] else "cp_over_more.png" }
		properties = []
		if c["opening"]:
			# one opening per phrase: the code keeps the flags of the last OPENING it reads only
			basics.update({ "ForbiddenDef": "OPENING", "ForbiddenExclude": "OPENING", "AvoidCyclic": True })
			properties = [ "OPENING_1: " + c["opening"] ]
		p = parent("_" + family.lower(), folder, basics=basics, client=client, properties=properties)
		credits[family] = []
		for sheetId, index in grades(gen, family.lower()):
			row = gen.sbrickWords.get(sheetId)
			if NOT_TO_APPEAR.lower() in row.description.lower():
				gen.exclude("sbrick", sheetId, "the text says it must not appear (\"" + NOT_TO_APPEAR + "\")")
				continue
			if not checkName(gen, sheetId, [ c["words"] ]):
				continue
			points = textNumber(gen, sheetId, r"(?:gives|yields) (\d+) credits", "credit")
			if points is None:
				continue
			basics = { "IndexInFamily": index, "Level": points, "SabrinaCost": common.sabrinaCredit(points), "SPCost": B.spCost(points),
				"LearnRequiresOneOfSkills": learn(c["skills"], points) }
			properties = []
			if family == "BFCA":
				factor, const = B.staminaCredit(points)
				properties = [ "STA_WEIGHT_FACTOR: %d:%d" % (factor, const) ]
				staminaCredits.append((points, sheetId))
			elif family == "BFCB":
				properties = [ "HP: %d" % B.hpCredit(points) ]
			elif family == "BFCF":
				lo, hi = B.weaponWear(points)
				basics["PowerValue"] = points # the wear's reference is the phrase's credit
				properties = [ "WEAPON_WEAR_MOD: %s:%s" % (num(lo), num(hi)) ]
			brick(sheetId, folder, family + " credit " + str(points), p, basics, properties=properties)
			credits[family].append((sheetId, points))
	staminaCredits.sort()

	def creditFor(need, where):
		"""the smallest stamina credit that pays this much: [ id ], or [] when nothing is left to pay"""
		if need <= 0:
			return []
		for points, sheetId in staminaCredits:
			if points >= need:
				return [ sheetId ]
		gen.error("fight: " + where + " needs " + str(need) + " credits, more than the largest stamina credit gives")
		return []

	# ---- the root
	p = parent("_bfpa", "sbrick/fight/root", basics={ "FamilyId": "BFPA", "Action Nature": "FIGHT", "Skill": "SF" }, client=ROOT_ICONS,
		optional=[ "BFOA", "BFOB" ], credit=[ c["family"] for c in CREDITS ])
	checkName(gen, ROOT, [ "Default attack" ])
	brick(ROOT, "sbrick/fight/root", "combat root", p, { "IndexInFamily": 1, "Level": 0, "SPCost": B.spCost(0),
		"LearnRequiresOneOfSkills": learn("SF", 0) })

	# ---- options and their parameters
	optionParent = parent("_bfoa", "sbrick/fight/option", basics={ "FamilyId": "BFOA", "SabrinaCost": 0, "Level": 0, "SPCost": B.spCost(0) },
		client={ "IconBack": "op_back.png", "IconOver": "op_over_more.png" })
	for o in OPTIONS:
		family = o["family"]
		info = PARAMETERS[family]
		checkName(gen, o["id"], [ o["words"] ])
		folder = "sbrick/fight/modifier/" + family.lower()
		shared = list(info["shared"]) + ([ "SET_BEHAVIOUR: " + info["behaviour"] ] if info["behaviour"] else [])
		own = 1 if family == "BFMF" else 0 # the circular attack's grades carry their own total damage as Property 0
		pp = parent("_" + family.lower(), folder, basics={ "FamilyId": family, "Skill": o["skills"] },
			client={ "Icon": o["icon"], "IconBack": "pa_back.png", "IconOver": "pa_over_more.png" }, properties=[ None ] * own + shared)
		ids = grades(gen, family.lower())
		if family == "BFMB":
			# The hit rate texts state no level ("Hit Rate +1" .. "+13"): its 13 grades take the 13 levels of increase
			# damage, the other 13 grade option, grade for grade.
			ladder = [ levels[i] for i, n in grades(gen, "bfma") if i in levels ]
			if len(ladder) != len(ids):
				gen.error("fight: the hit rate has " + str(len(ids)) + " grades and increase damage " + str(len(ladder)) + ", so the hit rate cannot take its levels")
				ladder = [ 0 ] * len(ids)
		firstLevel = None
		for k, (sheetId, index) in enumerate(ids):
			if not checkName(gen, sheetId, [ info["words"] ]):
				continue
			level = ladder[k] if family == "BFMB" else textNumber(gen, sheetId, LEVEL_TEXT, "level")
			if not level:
				continue
			levels[sheetId] = level
			firstLevel = level if firstLevel is None else min(firstLevel, level)
			properties = []
			if family == "BFMF":
				total = textNumber(gen, sheetId, r"will not exceed (\d+)% of your normal damage", "total damage")
				if total is None:
					continue
				properties = [ "HIT_ALL_AGGRESSORS: %s:%s" % (num(B.CIRCULAR_MIN), num(total / 100.0)) ]
			if family == "BFMA" and B.INC_DMG[1] == 2.0 and "up to double" not in gen.sbrickWords.get(sheetId).description:
				gen.error("fight: " + sheetId + " no longer says \"up to double\", which INC_DMG's Max of 2 in balancing/fight.py follows")
			if family == "BFMD":
				duration = textNumber(gen, sheetId, r"for (\d+) ?s\b", "bleed duration")
				if duration is not None and duration != B.BLEED_DURATION:
					gen.error("fight: " + sheetId + " says the bleed lasts " + str(duration) + " s, balancing/fight.py has " + num(B.BLEED_DURATION))
			basics = { "IndexInFamily": index, "Level": level, "PowerValue": B.powerValue(level), "SabrinaCost": B.parameterCost(level, family),
				"SPCost": B.spCost(level), "LearnRequiresOneOfSkills": learn(o["skills"], level) }
			brick(sheetId, folder, family + " level " + str(level), pp, basics, properties=properties)
		properties = [ "SPECIAL_HIT" ] if o["special"] else []
		brick(o["id"], "sbrick/fight/option", "option " + o["words"], optionParent,
			{ "IndexInFamily": int(o["id"][-2:]), "Skill": o["skills"], "LearnRequiresOneOfSkills": learn(o["skills"], firstLevel or 0) },
			client={ "Icon": o["icon"] }, properties=properties, parameter=[ family ])

	# ---- the aim chain and the feint (the BFOB options)
	bobParent = parent("_bfob", "sbrick/fight/option", basics={ "FamilyId": "BFOB", "SabrinaCost": 0, "Level": 0, "SPCost": B.spCost(0) },
		client={ "IconBack": "op_back.png", "IconOver": "op_over_more.png" })
	aimLevels = []
	aimPhrases = [] # (phrase id, bricks, folder)
	bodyParent = parent("_bfme", "sbrick/fight/aim", basics={ "FamilyId": "BFME", "Skill": AIM_SKILLS, "SabrinaCost": 0, "Level": 0,
		"SPCost": B.spCost(0) }, client={ "Icon": "ico_aim.png", "IconBack": "pa_back.png" })
	aimParent = parent("_bfaim", "sbrick/fight/aim", basics={ "Skill": AIM_SKILLS }, client={ "IconBack": "pa_back.png", "IconOver": "pa_over_more.png" })
	for body in BODIES:
		folder = "sbrick/fight/aim/" + body["folder"]
		locFamily = "BF" + body["code"].upper() + "ME"
		bodyId = "bfme%02d" % body["index"]
		locParent = parent("_" + locFamily.lower(), folder, basics={ "FamilyId": locFamily, "Skill": AIM_SKILLS, "SabrinaCost": 0, "Level": 0,
			"SPCost": B.spCost(0) }, client={ "IconBack": "pa_back.png", "IconOver": body["over"] })
		for loc in LOCATIONS:
			locId = "bf" + body["code"] + "me%02d" % loc["index"]
			words = loc["homin"] if body["code"] == "h" else loc["beast"]
			aimFamily = "BFA" + body["code"].upper() + loc["code"].upper() + "ME"
			ap = parent("_" + aimFamily.lower(), folder, parent=aimParent, basics={ "FamilyId": aimFamily },
				client={ "Icon": loc["icon"], "IconOver2": body["over"] }, properties=[ "AIM: %s:%s" % (body["body"], loc["slot"]) ])
			first = None
			for sheetId, index in grades(gen, "bfaim" + body["code"] + loc["code"] + "me"):
				if not checkName(gen, sheetId, [ "Aim " + body["words"] + " " + words ]):
					continue
				level = textNumber(gen, sheetId, LEVEL_TEXT, "level")
				if not level:
					continue
				first = level if first is None else min(first, level)
				aimLevels.append(level)
				basics = { "IndexInFamily": index, "Level": level, "PowerValue": B.powerValue(level), "SabrinaCost": B.parameterCost(level, aimFamily),
					"SPCost": B.spCost(level), "LearnRequiresOneOfSkills": learn(AIM_SKILLS, level) }
				brick(sheetId, folder, aimFamily + " level " + str(level), ap, basics)
				aimPhrases.append(("a" + sheetId, [ ROOT, "bfob01", bodyId, locId, sheetId ], body["folder"]))
			if checkName(gen, locId, [ "Aim " + body["words"] + " " + words ]):
				brick(locId, folder, "aim location " + words, locParent, { "IndexInFamily": loc["index"],
					"LearnRequiresOneOfSkills": learn(AIM_SKILLS, first or 0) }, client={ "Icon": loc["icon"] }, parameter=[ aimFamily ])
		if checkName(gen, bodyId, [ "Aim", body["words"] ]): # "Aim Land Kitin"
			brick(bodyId, "sbrick/fight/aim", "aim body type " + body["words"], bodyParent, { "IndexInFamily": body["index"],
				"LearnRequiresOneOfSkills": learn(AIM_SKILLS, min(aimLevels) if aimLevels else 0) }, client={ "IconOver": body["over"] },
				parameter=[ locFamily ])
	firstAim = min(aimLevels) if aimLevels else 0
	checkName(gen, "bfob01", [ "Aim" ])
	brick("bfob01", "sbrick/fight/option", "option aim", bobParent, { "IndexInFamily": 1, "Skill": AIM_SKILLS,
		"LearnRequiresOneOfSkills": learn(AIM_SKILLS, firstAim) }, client={ "Icon": "ico_aim.png" }, parameter=[ "BFME" ])
	# the feint does no damage and only opens the attacks after a feint: it is learnt with the first of them
	firstFeint = min(points for i, points in credits["BFCG"]) if credits["BFCG"] else 0
	checkName(gen, "bfob02", [ "Feint" ])
	brick("bfob02", "sbrick/fight/option", "option feint", bobParent, { "IndexInFamily": 2, "Skill": "SFM",
		"LearnRequiresOneOfSkills": learn("SFM", firstFeint) }, client={ "Icon": "ico_feint.png" }, properties=[ "DEFINE_FLAG: Feint" ])

	# ---- phrases
	def phrase(name, folder, bricks, source, castable=True):
		if not gen.sphraseWords.get(name):
			gen.error("fight: the phrase " + name + " has no row in the translation")
			return
		if castable:
			cost = sum(costs.get(b, 0) for b in bricks if costs.get(b, 0) > 0)
			credit = -sum(costs.get(b, 0) for b in bricks if costs.get(b, 0) < 0)
			bricks = bricks + creditFor(cost - credit, name)
		gen.phrase(name, folder, bricks, source, castable=castable)

	phrase("abf01", "sphrase/fight", [ ROOT ], "the default attack")
	for o in OPTIONS:
		family = o["family"]
		for sheetId, index in grades(gen, family.lower()):
			if sheetId not in levels:
				continue
			name = "a" + sheetId
			row = gen.sphraseWords.get(name)
			if not row:
				continue
			stated = re.search(r"level of (\d+)", row.description)
			if stated and int(stated.group(1)) != levels[sheetId]:
				gen.error("fight: the text of " + name + " states level " + stated.group(1) + ", its brick " + sheetId + " has " + str(levels[sheetId]))
			phrase(name, "sphrase/fight/" + family.lower(), [ ROOT, o["id"], sheetId ], family + " ready-made attack")
	for name, bricks, folder in aimPhrases:
		phrase(name, "sphrase/fight/aim/" + folder, bricks, "ready-made aimed attack")

	# the attacks after an opening: the parameter of the stated level, the opening credit of the same number, and the
	# smallest stamina credit that pays what the opening does not
	for prefix, option, family, credit in OPENING_ATTACKS:
		byLevel = {}
		for sheetId, level in levels.items():
			if sheetId.startswith(family.lower()):
				byLevel.setdefault(level, sheetId)
		openings = dict((int(i[-2:]), i) for i, points in credits[credit])
		for name in gen.sphraseWords.ids("^" + prefix + r"\d+$"):
			number = int(name[-2:])
			level = textNumber(gen, name, r"skill level of (\d+)", "level", kind="sphrase")
			if level is None:
				continue
			if level not in byLevel:
				gen.error("fight: " + name + " names a level " + str(level) + " " + PARAMETERS[family]["words"] + ", which no " + family + " brick has")
				continue
			if number not in openings:
				gen.error("fight: " + name + " has no opening credit " + credit.lower() + "%02d" % number)
				continue
			phrase(name, "sphrase/fight/opening", [ ROOT, option, byLevel[level], openings[number] ], "attack after " + credit + " opening")

	# the upgrades that teach a credit (not castable: a credit alone is no action)
	for prefix, family in CREDIT_UPGRADES:
		byNumber = dict((int(i[-2:]), i) for i, points in credits[family])
		for name in gen.sphraseWords.ids("^" + prefix + r"\d+$"):
			number = int(name[-2:])
			if number in byNumber:
				phrase(name, "sphrase/fight/credit", [ byNumber[number] ], family + " credit upgrade", castable=False)
			elif ("sbrick", name[1:]) in gen.excluded:
				gen.exclude("sphrase", name, "it teaches a brick that is excluded because its text says it must not appear")
	# "Gives a feint option stanza and a 'hit after feint' combat credit stanza": an upgrade too, since the credit it gives
	# needs a feint before it, so the pair cannot be one action
	firstFeintCredit = [ i for i, points in credits["BFCG"] if points == firstFeint ]
	if firstFeintCredit:
		phrase("abfob02", "sphrase/fight/credit", [ "bfob02", firstFeintCredit[0] ], "feint and its first opening", castable=False)

	# ---- checks of this domain
	for s in made:
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("fight: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
		if not s.isParent:
			checkText(gen, s)
	taught = set()
	for p in gen.phrases.values():
		if p.name.startswith("abf"):
			taught.update(p.bricks)
	for b in made:
		if not b.isParent and b.name not in taught:
			gen.error("fight: no phrase teaches " + b.name + ", so no character can learn it")
	for sheetId in gen.sbrickWords.ids(r"^bf"):
		if sheetId not in gen.bricks and ("sbrick", sheetId) not in gen.excluded:
			gen.error("fight: the translation id " + sheetId + " has the fight prefix, but the fight domain has no rule for it")
	for name in gen.sphraseWords.ids(r"^abf"):
		if name not in gen.phrases and ("sphrase", name) not in gen.excluded and not OTHER_DOMAIN_PHRASES.match(name):
			gen.error("fight: the translation id " + name + " has the fight prefix, but the fight domain has no rule for it")
