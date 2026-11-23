# Ryzom Core's raw material tables for mp_generator (ryzom/tools/leveldesign/mp_generator): writes rm_fam_prop.csv,
# rm_item_parts.csv, creature_models.csv and rm_creature_classes.csv into this folder. README.md says what each
# column means and why the values are what they are; the reasons are also beside the values below.
#
# Sources: the translation (which families exist, which creature gives which body part, which deposit families the
# forage filters name), the code (which stats each component type carries, rm_family.cpp), and the creatures of the
# Ring generator (../generate_r2_sheets/creature_fauna.tsv: attack, defence and protections, which the materials of a
# creature take after). No value comes from Nevrax's tables; the identification columns of the families (group,
# location, icon) agree with the old rm_fam_prop.csv kept beside the tool.
#
#   python make_tables.py [--code <code folder>] [--atlas <interface folder>]
#
# Both defaults are found from this script's place: the code checkout beside the leveldesign that holds it
# (<leveldesign>/../code) and the interface atlas lists of the pipeline beside it (<leveldesign>/../pipeline/install/
# interfaces, texture_interfaces_dxtc.txt and texture_interfaces_v3.txt), which the icons are checked against; the
# sheet generator's ../generate_core4_sheets/interface_atlas.py reads them.

import argparse, collections, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELDESIGN = os.path.normpath(os.path.join(HERE, "..", ".."))
R2 = os.path.join(LEVELDESIGN, "scripts", "generate_r2_sheets")
DFN = os.path.join(LEVELDESIGN, "DFN", "game_elem", "_item")
WORK = os.path.join(LEVELDESIGN, "translation", "work")
CREATURES = os.path.join(LEVELDESIGN, "game_elem", "creature")
DEFAULT_CODE = os.path.normpath(os.path.join(LEVELDESIGN, "..", "code"))
# The interface atlas lists, read by the sheet generator's reader (its default: the pipeline beside the leveldesign)
sys.path.insert(0, os.path.join(LEVELDESIGN, "scripts", "generate_core4_sheets"))
import interface_atlas

# What to do when an input of the leveldesign is missing: it is read from the leveldesign that holds this script
IN_LEVELDESIGN = ("this script reads it from the leveldesign that holds it (" + LEVELDESIGN + "), which must have it: to make the tables "
	+ "of another leveldesign, run the copy of the script there")

errors = []
def error(message):
	errors.append(message)

def fail(message):
	print("ERROR: " + message, file=sys.stderr)
	sys.exit(1)

def readText(path, remedy=IN_LEVELDESIGN):
	"""a whole input file, UTF-8 (with or without its mark); a missing or undecodable file stops the script"""
	if not os.path.isfile(path):
		fail(path + " not found: " + remedy)
	try:
		with open(path, "r", encoding="utf-8-sig") as f:
			return f.read()
	except UnicodeDecodeError as e:
		fail(path + " is not UTF-8 text (" + str(e) + "): the inputs are read as they are written, correct the file")

# ------------------------------------------------------------------------------------------------------ the code
STAT_NAMES = None # RM_FABER_STAT_TYPE in enum order: the DFN atom names, which the tool and the sheets use
TYPE_NAMES = None # RM_FABER_TYPE in enum order (MpL ...), the letter is the index (A ...)
TYPE_ENTRIES = None # the DFN struct name of each type ("A MpL (Blade)")
RELEVANT = None # letter: the stats the code adds up for a material in that slot (isStatRelevant)

def readCode(code):
	global STAT_NAMES, TYPE_NAMES, TYPE_ENTRIES, RELEVANT
	folder = os.path.join(code, "ryzom", "common", "src", "game_share")
	remedy = ("the stats and component types are read from the code checkout (" + code + "; by default the one beside the leveldesign, "
		+ DEFAULT_CODE + "): pass --code <code folder> to name another")
	header = readText(os.path.join(folder, "rm_family.h"), remedy)
	source = readText(os.path.join(folder, "rm_family.cpp"), remedy)
	m = re.search(r"enum TRMStatType\s*\{(.*?)NumRMStatType", header, re.S)
	STAT_NAMES = re.findall(r"^\s*(\w+)\s*(?:=\s*0)?\s*,", m.group(1), re.M)
	m = re.search(r"enum TRMFType\s*\{(.*?)Unknown", header, re.S)
	TYPE_NAMES = [ "Mp" + n[2:] for n in re.findall(r"^\s*(MP\w*)\s*(?:=\s*0)?\s*,", m.group(1), re.M) ]
	m = re.search(r"TypeToSheetEntry\[\]\s*=\s*\{(.*?)\};", source, re.S)
	TYPE_ENTRIES = re.findall(r'"([^"]+)"', m.group(1))
	if len(STAT_NAMES) != 34 or len(TYPE_NAMES) != 26 or len(TYPE_ENTRIES) != 26:
		fail("rm_family.h / rm_family.cpp: %d stats, %d types, %d sheet entries; this script knows 34, 26, 26" % (len(STAT_NAMES), len(TYPE_NAMES), len(TYPE_ENTRIES)))
	RELEVANT = {}
	for name, values in re.findall(r"const uint8\s+mp(\w+)\[\]\s*=\s*\{([^}]*)\}", source):
		flags = [ int(v) for v in values.replace(" ", "").replace("\t", "").split(",") if v ]
		index = [ n.upper() for n in TYPE_NAMES ].index("MP" + name.upper())
		RELEVANT[chr(ord("A") + index)] = [ STAT_NAMES[i] for i, v in enumerate(flags) if v ]
	if len(RELEVANT) != 26:
		fail("rm_family.cpp: isStatRelevant has %d rows, 26 expected" % len(RELEVANT))

# --------------------------------------------------------------------------------------------- what serves what
# The component types a craft plan asks for (letters of RM_FABER_TYPE). Each material kind serves two: its main use,
# where its families are strong specialists, and a lesser one. A kind's uses follow what the material is: claws,
# fangs and mandibles cut, stings and beaks pierce, heavy bones (pelvis, hoof, rostrum) make hammer heads and
# counterweights, long bones and tails make shafts, hollow horn and trunk make barrels, hides make grips, clothes and
# linings, carapace makes armour, secretions and buds burst (explosives), feathers make fletching (ammo jacket) and
# down (stuffing), eyes and mushrooms carry magic (jewels, foci), nails and teeth are set (jewel settings).
# "hard" materials pay for a strong specialisation with weight, soft ones with durability (see profile()).
CREATURE_KINDS = {
	# kind: ( main type, second type, icon, hard )
	"Claw": ( "A", "C", "MP_Claw.tga", True ),
	"Fang": ( "A", "L", "MP_Fang.tga", True ),
	"Mandible": ( "A", "D", "MP_Mandible.tga", True ),
	"Sting": ( "C", "H", "MP_Sting.tga", True ),
	"Beak": ( "L", "C", "MP_Beak.tga", True ),
	"Spine": ( "C", "L", "MP_Spine.tga", True ),
	"Pelvis": ( "B", "F", "MP_Pelvis.tga", True ),
	"Hoof": ( "F", "B", "MP_Hoof.tga", True ),
	"Rostrum": ( "B", "D", "MP_Rostrum.tga", True ),
	"Bone": ( "D", "P", "MP_Bone.tga", True ),
	"Tail": ( "H", "D", "MP_Tail.tga", False ),
	"Wood": ( "D", "M", "MP_Wood.tga", True ),
	"Horn": ( "I", "K", "MP_Horn.tga", True ),
	"Trunck": ( "I", "M", "MP_Trunk.tga", False ),
	"Shell": ( "M", "I", "MP_KitinShell.tga", True ),
	"Leather": ( "E", "M", "MP_Leather.tga", False ),
	"Skin": ( "Y", "N", "MP_Skin.tga", False ),
	"Secretion": ( "J", "N", "MP_Kitin_Secretion.tga", False ),
	"Moss": ( "O", "N", "MP_Moss.tga", False ),
	"Wing": ( "K", "O", "MP_Wing.tga", False ),
	"Whiskers": ( "O", "G", "MP_Whiskers.tga", False ),
	"Ligament": ( "P", "G", "MP_Ligament.tga", False ),
	"Nail": ( "G", "Q", "MP_Nail.tga", True ),
	"Tooth": ( "Q", "L", "MP_Tooth.tga", True ),
	"Eye": ( "R", "Z", "MP_Eyes.tga", False ),
	"Mushroom": ( "Z", "R", "MP_Mushroom.tga", False ),
	"Bud": ( "Z", "J", "MP_Bud.tga", False ),
}

# The ten deposit groups of craft materials (their families are the ones the forage filters BHFPRMFM* name). Between
# them they serve each of the twenty component types once, so that every plan can be made from foraged materials
# alone: shells cut and pierce, wood nodes are dense (hammers, counterweights), wood is long and straight (shafts,
# barrels), bark wraps (armour shells, ammo jackets), fibre is woven (clothes, grips), seeds are small and hard
# (bullets, settings), amber holds magic (jewels, foci), oil burns (explosives, firing pins), sap soaks (linings,
# stuffing) and resin binds (armour clips, triggers).
DEPOSIT_GROUPS = {
	# group: ( main type, second type, icon, hard )
	"Shell": ( "A", "C", "MP_Shell.tga", True ),
	"Node": ( "B", "F", "MP_Wood_Node.tga", True ),
	"Wood": ( "D", "I", "MP_Wood.tga", True ),
	"Bark": ( "M", "K", "MP_Bark.tga", True ),
	"Fiber": ( "Y", "E", "MP_Fiber.tga", False ),
	"Seed": ( "L", "Q", "MP_Seed.tga", True ),
	"Amber": ( "R", "Z", "MP_Amber.tga", True ),
	"Oil": ( "J", "H", "MP_Oil.tga", False ),
	"Sap": ( "N", "O", "MP_Sap.tga", False ),
	"Resin": ( "P", "G", "MP_Resin.tga", True ),
}

# The forage filter families (BHFPRMFM<letter>) of the deposit groups without craft use, as the BHFPMB texts name
# the groups (Construction, Food, Goo, Insect, Kitin, Harmful, Preservative)
MISSION_FILTER_GROUPS = { "k": "Construction", "l": "Food", "m": "Goo", "n": "Insect", "o": "Kitin", "p": "Nocive", "q": "Preservative" }
# Spellings of the filter texts that the family type spells otherwise
FAMILY_ALIASES = { "Small Spider Web": "Small Spiders Web", "Large Spider Web": "Large Spiders Web" }

# Deposit materials for missions that no forage filter names: the mineral, and the order forms, packages and tokens of
# the four nations (mission items that the deposit system hands out)
OTHER_DEPOSIT_FAMILIES = [
	( "Atrium", "Mineral", "" ),
	( "Matis Order Form", "Paper", "ICO_mission_message.tga" ), ( "Fyros Order Form", "Paper", "ICO_mission_message.tga" ),
	( "Zorai Order Form", "Paper", "ICO_mission_message.tga" ), ( "Tryker Order Form", "Paper", "ICO_mission_message.tga" ),
	( "Matis Military Package", "Pack", "ICO_mission_package.tga" ), ( "Fyros Military Package", "Pack", "ICO_mission_package.tga" ),
	( "Zorai Military Package", "Pack", "ICO_mission_package.tga" ), ( "Tryker Military Package", "Pack", "ICO_mission_package.tga" ),
	( "Matis Royal Token", "Token", "ICO_mission_art_matis.tga" ), ( "Fyros Imperial Token", "Token", "ICO_mission_art_fyros.tga" ),
	( "Zorai Cho Token", "Token", "ICO_mission_art_zorai.tga" ), ( "Tryker Federation Token", "Token", "ICO_mission_art_tryker.tga" ),
]

# The icons of the mission deposit materials, by the words their names end with (the longest match wins)
MISSION_ICONS = {
	"Leaf": "MP_Leaf.tga", "Resin": "MP_Resin.tga", "Wood": "MP_Wood.tga", "Sawdust": "MP_Sawdust.tga", "Thorn": "MP_Spine.tga",
	"Bark": "MP_Bark.tga", "Straw": "MP_Straw.tga", "Dust": "MP_Dust.tga", "Fiber": "MP_Fiber.tga", "Pearly Shell": "MP_Shell.tga",
	"Pearl": "MP_pearl.tga", "Fish Scale": "MP_Fish_Scale.tga", "Parasite": "MP_Parasite.tga", "Spiders Web": "MP_Spiders_Web.tga",
	"Silk": "MP_Fiber.tga", "Firefly Abdomen": "MP_Firefly_Abdomen.tga", "Butterfly Wing": "MP_Buterfly_blue.tga",
	"Wax": "MP_pollen.tga", "Kitin Cocoon": "MP_Buterfly_cocoon.tga", "Kitin Saliva": "MP_Kitin_Secretion.tga",
	"Kitin Larva": "MP_Larva.tga", "Flower Petal": "MP_flowers.tga", "Bud": "MP_Bud.tga", "Moss": "MP_Moss.tga",
	"Dandelion": "MP_Dandelion.tga", "Reed Stem": "MP_Stem.tga", "Loose Soil": "MP_Fresh_Loose_Soil.tga", "Modified Sap": "MP_Sap.tga",
	"Insect Fossil": "MP_Insect_Fossil.tga", "Plant Fossil": "MP_Plant_Fossil.tga", "Pigment": "MP_Pigment.tga",
	"Goo Residue": "MP_Goo_Residue.tga", "Mushroom": "MP_Mushroom.tga", "Insect Larva": "MP_Larva.tga", "Cereal": "MP_Cereal.tga",
	"Egg": "MP_Egg.tga", "Honey": "MP_Horney.tga", "Aromatic Plant": "MP_flowers.tga", "Wild Berry": "MP_Fruit.tga", "Fruit": "MP_Fruit.tga",
}

# The body parts creatures give for missions (no craft use), their group and icon. Kitin flesh is of the kitin group,
# as the kitins' other mission materials; the flesh of the crustaceans is meat. Arana's moss is its coat (fur).
MISSION_KINDS = {
	"Meat": ( "Meat", "MP_Meat.tga" ), "Flesh": ( "Meat", "MP_Kitin_flesh.tga" ), "Skull": ( "Skull", "MP_skull.tga" ),
	"Blood": ( "Blood", "MP_Blood.tga" ), "Hairs": ( "Fur", "MP_Hairs.tga" ), "Moss": ( "Fur", "MP_Moss.tga" ),
	"Leaf": ( "Aggressive plant", "MP_Leaf.tga" ), "Pistil": ( "Aggressive plant", "MP_pistil.tga" ),
}

# Invasion, goo and kitin lair materials, which the tool makes as special items: kept as the server names them (the
# kitin secretion m0077ixxcc01 is named in egs_static_harvestable.cpp, the kitin trophy is the second item of the
# kitin claw). The kitin larva of the kitin lairs is a Supreme material for any component, found only where a deposit
# names it.
SPECIALS = [
	( "Kitin Claw", "Kitin", "", "Ik", "MP_Claw.tga", [ "CC/Fragment of Kitin Claw/a/the/Fragments of Kitin Claw/the", "CC/Kitin Trophy/a/the/Kitin Trophies/the" ] ),
	( "Kitin Secretion", "Kitin", "", "Ik", "MP_Kitin_Secretion.tga", [ "CC/Kitin Secretion/a/the/Kitin Secretions/the" ] ),
	( "Goo Part", "Meat", "", "Ichbp", "MP_Goo_Residue.tga", [ "CC/Goo Part/a/the/Goo Parts/the" ] ),
	( "Kitin Larva", "Kitin", "ABCDEFGHIJKLMNOPQRYZ", "D", "MP_Larva.tga", [ "CF/Supreme Kitin Larva/a/the/Supreme Kitin Larvas/the" ] ),
]
# The meat of goo creatures, a mission material of the goo ecosystem
GOO_FAMILIES = [ ( "Goo Contaminated Meat", "Meat", "G", "MP_Meat.tga" ) ]

# ---------------------------------------------------------------------------------------------- the stat profiles
# A material's stats in a slot: every stat the code adds up for that slot starts at its class's level (the tool's
# Basic 20 ... Supreme 80), the family's specialty gets more, its trade-off less (the tool: +40 with two weaknesses,
# +20 with one, -20 each, so the total stays that of the class). The main use gets the strong profile (two
# weaknesses), the second use the mild one.
HEADS = "ABC" # the striking part of a melee weapon
HANDLING = "DEFG" # shaft, grip, counterweight, trigger: how the weapon is held
RANGED = "HI" # firing pin, barrel
AMMO = "JKL" # explosive, jacket, bullet
ARMOR = "MNOPY" # armour shell, lining, stuffing, clip, clothes

# What a specialty costs: heavy blows are slow, quick ones light, reach costs damage, guarding against one kind of
# blow leaves another open, toughness weighs, protection weighs, an element's opposite, the ecosystem unlike the
# one resisted, and in magic power costs casting speed and back
TRADE_OFF = {
	"DMG": "Speed", "Speed": "DMG", "Range": "DMG",
	"AdversaryDodgeModifier": "AdversaryParryModifier", "AdversaryParryModifier": "AdversaryDodgeModifier",
	"DodgeModifier": "ParryModifier", "ParryModifier": "DodgeModifier",
	"Durability": "Weight", "Weight": "Durability", "SapLoad": "Durability",
	"ProtectionFactor": "Weight",
	"MaxSlashingProtection": "MaxBluntProtection", "MaxBluntProtection": "MaxPiercingProtection", "MaxPiercingProtection": "MaxSlashingProtection",
	"FireProtection": "ColdProtection", "ColdProtection": "FireProtection", "AcidProtection": "PoisonProtection",
	"PoisonProtection": "AcidProtection", "ElectricityProtection": "ShockWaveProtection", "ShockWaveProtection": "ElectricityProtection",
	"RotProtection": "FireProtection",
	"DesertResistance": "LacustreResistance", "LacustreResistance": "DesertResistance", "ForestResistance": "JungleResistance",
	"JungleResistance": "ForestResistance", "PrimaryRootResistance": "DesertResistance",
}
for school in ( "Elemental", "OffensiveAffliction", "DefensiveAffliction", "Heal" ):
	TRADE_OFF[school + "PowerFactor"] = school + "CastingTimeFactor"
	TRADE_OFF[school + "CastingTimeFactor"] = school + "PowerFactor"

# The deposit families of a group share out the main stats of a slot, so that each group has a family for each
# specialty a crafter looks for (in the order of the families' numbers)
DEPOSIT_SPECIALTIES = {
	"heads": [ "DMG", "Speed", "AdversaryParryModifier", "AdversaryDodgeModifier", "ParryModifier", "DodgeModifier", "Durability" ],
	"handling": [ "ParryModifier", "DodgeModifier", "Speed", "AdversaryDodgeModifier", "AdversaryParryModifier", "Durability" ],
	"ranged": [ "Range", "DMG", "Speed", "AdversaryDodgeModifier", "AdversaryParryModifier", "Durability" ],
	"ammo": [ "DMG", "Range", "Speed", "Durability", "Weight" ],
	"armor": [ "ProtectionFactor", "MaxSlashingProtection", "MaxBluntProtection", "MaxPiercingProtection", "DodgeModifier", "ParryModifier", "Weight" ],
	"Q": [ "DesertResistance", "ForestResistance", "LacustreResistance", "JungleResistance", "PrimaryRootResistance" ],
	"R": [ "FireProtection", "ColdProtection", "AcidProtection", "ElectricityProtection", "ShockWaveProtection", "PoisonProtection", "RotProtection" ],
	"Z": [ "ElementalPowerFactor", "HealPowerFactor", "OffensiveAfflictionPowerFactor", "DefensiveAfflictionPowerFactor",
		"ElementalCastingTimeFactor", "HealCastingTimeFactor", "OffensiveAfflictionCastingTimeFactor", "DefensiveAfflictionCastingTimeFactor" ],
}

def role(letter):
	if letter in HEADS: return "heads"
	if letter in HANDLING: return "handling"
	if letter in RANGED: return "ranged"
	if letter in AMMO: return "ammo"
	if letter in ARMOR: return "armor"
	return letter

def relevant(letter, stat):
	return stat in RELEVANT[letter]

def firstRelevant(letter, stats):
	for s in stats:
		if relevant(letter, s):
			return s
	return None

# The creature's elemental protections, in the order a tie is settled
ELEMENTS = [ ( "acidProtection", "AcidProtection" ), ( "coldProtection", "ColdProtection" ), ( "fireProtection", "FireProtection" ),
	( "rotProtection", "RotProtection" ), ( "shockwaveProtection", "ShockWaveProtection" ), ( "poisonProtection", "PoisonProtection" ),
	( "electricityProtection", "ElectricityProtection" ) ]
RESISTANCES = { "d": "DesertResistance", "f": "ForestResistance", "j": "JungleResistance", "l": "LacustreResistance", "p": "PrimaryRootResistance" }
SCHOOLS = { "herbivore": "Heal", "carnivore": "Elemental", "bird": "Elemental", "kitin": "OffensiveAffliction", "plant": "DefensiveAffliction" }

class Creature:
	"""what a creature's materials take after (creature_fauna.tsv): its blows, its defence, its hide, its element,
	its ecosystem and its kind"""
	def __init__(self, row, habitat, elementMeans):
		self.code = row["id"]
		self.name = row["name"]
		self.attack = row["attack"]
		self.defense = row["defenseMode"]
		self.type = row["type"]
		self.physical = [ int(row["slashingProtection"] or 0), int(row["bluntProtection"] or 0), int(row["piercingProtection"] or 0) ]
		self.elements = [ int(row[c] or 0) for c, n in ELEMENTS ]
		self.habitat = habitat
		self.elementMeans = elementMeans

	def specialty(self, letter):
		r = role(letter)
		if r in ( "heads", "ranged", "ammo" ):
			# its blows: slashing creatures give damage, piercing ones reach (or beat the dodge where a slot has no
			# range), blunt ones beat the parry (or hit hard in ammunition); the plants' strikes count as damage
			if self.attack == "piercing":
				return firstRelevant(letter, [ "Range", "AdversaryDodgeModifier" ]) if r != "heads" else "AdversaryDodgeModifier"
			if self.attack == "blunt":
				return firstRelevant(letter, [ "AdversaryParryModifier", "DMG", "Durability" ])
			if r == "ammo":
				return firstRelevant(letter, [ "Speed" ]) if self.attack == "slashing" else firstRelevant(letter, [ "DMG", "Speed" ])
			return "DMG"
		if r == "handling":
			# its defence: a dodging creature's parts make for dodging, a parrying one's for parrying
			return "DodgeModifier" if self.defense == "dodge" else "ParryModifier"
		if r == "armor":
			# its hide: armoured all round gives protection, else its strongest protection, else its defence
			if min(self.physical) >= 20:
				return "ProtectionFactor"
			best = max(self.physical)
			if best > 0:
				return [ "MaxSlashingProtection", "MaxBluntProtection", "MaxPiercingProtection" ][self.physical.index(best)]
			return "DodgeModifier" if self.defense == "dodge" else "ParryModifier"
		if letter == "R":
			# the element it resists more than the other creatures do
			scores = [ v - m for v, m in zip(self.elements, self.elementMeans) ]
			return ELEMENTS[scores.index(max(scores))][1]
		if letter == "Q":
			# the ecosystem it lives in most
			return RESISTANCES[self.habitat]
		if letter == "Z":
			# the magic of its kind (herbivores heal, carnivores and birds strike with the elements, kitins afflict,
			# plants ward), quick to cast for dodging creatures, strong for parrying ones
			school = SCHOOLS.get(self.type, "Elemental")
			return school + ("CastingTimeFactor" if self.defense == "dodge" else "PowerFactor")
		error("no specialty rule for type " + letter)
		return None

def profile(letter, best, hard, strong):
	"""best stat, worst stats of a family in a slot"""
	if not relevant(letter, best):
		error("specialty %s is not a stat of type %s" % (best, letter))
	worst = TRADE_OFF.get(best)
	if worst is None or not relevant(letter, worst):
		worst = firstRelevant(letter, [ s for s in ( "Weight", "Durability" ) if s != best ])
	worsts = [ worst ]
	if strong:
		# the second weakness: hard materials are heavy, soft ones wear
		for s in ( ( "Weight", "Durability" ) if hard else ( "Durability", "Weight" ) ):
			if s != best and s not in worsts and relevant(letter, s):
				worsts.append(s)
				break
	return best, worsts

# ------------------------------------------------------------------------------------------------- reading data
def readTyp(name):
	text = readText(os.path.join(DFN, name))
	return { label: int(value) for label, value in re.findall(r'Label="([^"]*)" Value="(\d+)"', text) }

def readWords(name):
	rows = {}
	for line in readText(os.path.join(WORK, name)).splitlines()[1:]:
		cols = line.split("\t")
		if len(cols) > 1:
			rows[cols[0]] = cols[1]
	return rows

def readTsv(path):
	lines = readText(path).splitlines()
	header = lines[0].split("\t")
	rows = []
	for line in lines[1:]:
		cols = [ c[1:-1] if len(c) >= 2 and c[0] == '"' and c[-1] == '"' else c for c in line.split("\t") ]
		rows.append(dict(zip(header, cols + [ "" ] * (len(header) - len(cols)))))
	return rows

def readAtlas(folder):
	"""the names of the interface atlases (the client reads a .png name as its .tga): every icon must be one of them; a
	list that is missing stops the script with its path and the --atlas option (interface_atlas.py)"""
	if folder:
		interface_atlas.setFolder(folder)
	try:
		return interface_atlas.names()
	except interface_atlas.Missing as e:
		fail(str(e))

def creatureSheets():
	"""code: { ecosystem letter: number of creature sheets } of the creatures of core4 (c<code><eco><zone><digit>) in
	the ecosystems that get raw materials, as mp_generator takes them: the common one and the five regions (the goo and
	invasion creatures keep what they have)"""
	counts = collections.defaultdict(collections.Counter)
	for root, dirs, files in os.walk(CREATURES):
		for f in files:
			m = re.match(r"^c([a-z]{2})([cdfjlp])([a-j])([1-8])\.creature$", f)
			if m:
				counts[m.group(1)][m.group(2)] += 1
	return counts

# ------------------------------------------------------------------------------------------------------- tables
def main():
	parser = argparse.ArgumentParser(description="write Ryzom Core's raw material tables for mp_generator")
	parser.add_argument("--code", default=DEFAULT_CODE, help="the code checkout, for rm_family.h/.cpp (default: " + DEFAULT_CODE + ")")
	parser.add_argument("--atlas", help="the folder of the interface atlas lists " + " and ".join(interface_atlas.LISTS)
		+ " (default: " + interface_atlas.DEFAULT_FOLDER + ")")
	args = parser.parse_args()
	readCode(os.path.normpath(os.path.abspath(args.code)))

	if not os.path.isdir(CREATURES):
		fail("the creature sheets " + CREATURES + " not found: " + IN_LEVELDESIGN)
	families = readTyp("item_mp_family.typ")
	groups = readTyp("item_mp_group.typ")
	itemWords = readWords("item_words_wk.txt")
	sbrickWords = readWords("sbrick_words_wk.txt")
	atlas = readAtlas(args.atlas)
	sheets = creatureSheets()

	def checkFamily(name):
		if name not in families:
			error("family " + name + " is not in item_mp_family.typ: this script makes no new family")
	def checkGroup(name):
		if name not in groups:
			error("group " + name + " is not in item_mp_group.typ")
	def checkIcon(icon):
		if icon and re.sub(r"\.tga$", ".png", icon.lower()) not in atlas and icon.lower() not in atlas:
			error("icon " + icon + " is in no interface atlas")

	rows = [] # rm_fam_prop.csv rows (lists of cells)
	def row(name, group, parts, location, icon, profiles=(), color="", specialOnly=False, specials=()):
		checkFamily(name)
		checkGroup(group)
		checkIcon(icon)
		cells = [ name, group, parts, "", "", location, icon, "", "", "" ]
		for i in range(2):
			if i < len(profiles):
				best, worsts = profiles[i]
				cells += [ best, worsts[0] if worsts else "", worsts[1] if len(worsts) > 1 else "" ]
			else:
				cells += [ "", "", "" ]
		cells += [ str(color), "", "x" if specialOnly else "" ]
		cells += list(specials)
		rows.append(cells)

	# ---- deposits: the families the forage filters name, by filter letter
	filterFamilies = collections.defaultdict(list)
	for sheetId, text in sbrickWords.items():
		m = re.match(r"^bhfprmfm([a-z])(\d\d)$", sheetId, re.I)
		if m and m.group(2) != "01":
			name = re.sub(r" (Prospection|Prospecting)$", "", text)
			filterFamilies[m.group(1).lower()].append(FAMILY_ALIASES.get(name, name))
	craftDeposits = collections.defaultdict(list)
	missionDeposits = []
	for letter, names in sorted(filterFamilies.items()):
		if letter in MISSION_FILTER_GROUPS:
			missionDeposits += [ ( n, MISSION_FILTER_GROUPS[letter] ) for n in names ]
			continue
		for n in names:
			group = "Node" if n.endswith("Wood Node") else n.split(" ")[-1]
			if group not in DEPOSIT_GROUPS:
				error("filter family " + n + " (BHFPRMFM" + letter.upper() + ") is of no deposit group of craft materials")
				continue
			craftDeposits[group].append(n)
	for group, ( main, second, icon, hard ) in DEPOSIT_GROUPS.items():
		names = sorted(craftDeposits[group], key=lambda n: families.get(n, 0))
		if not names:
			error("deposit group " + group + " has no family")
		for i, name in enumerate(names):
			profiles = []
			for k, letter in enumerate(( main, second )):
				specialties = [ st for st in DEPOSIT_SPECIALTIES[role(letter)] if relevant(letter, st) ]
				profiles.append(profile(letter, specialties[i % len(specialties)], hard, k == 0))
			# the families of a group come in each colour (the tool picks the colour of an ecosystem and class by
			# this index)
			row(name, group, main + second, "D", icon, profiles, color=i)
	specialNames = set(s[0] for s in SPECIALS)
	for name, group in missionDeposits:
		if name in specialNames:
			continue
		words = sorted(( w for w in MISSION_ICONS if name.endswith(w) ), key=len)
		if not words:
			error("no icon for the mission deposit family " + name)
			continue
		row(name, group, "", "D", MISSION_ICONS[words[-1]])
	for name, group, icon in OTHER_DEPOSIT_FAMILIES:
		row(name, group, "", "D", icon)

	# ---- creatures: the models of the Ring's creature table that the creature sheets have, and the body parts the
	# translation names for each (a family "<Creature> <Part>" with material names); the names say whether a part is a
	# craft material (Basic ... Supreme) or a mission one (Plain ... Magnificient)
	fauna = [ r for r in readTsv(os.path.join(R2, "creature_fauna.tsv")) if r["folder"] in ( "fauna", "flora" ) and r["id"] in sheets ]
	byName = { r["name"]: r for r in fauna }
	familyNames = collections.defaultdict(list) # family name: item names of its sheets
	for sheetId, text in itemWords.items():
		m = re.match(r"^m(\d{4})c([a-z]{2})", sheetId)
		if m:
			familyNames[int(m.group(1))].append(text)
	familyByNumber = { v: k for k, v in families.items() }
	creatureParts = collections.defaultdict(list) # creature name: [ ( part, family ) ]
	for number, names in familyNames.items():
		family = familyByNumber.get(number, "")
		words = family.split(" ", 1)
		if len(words) == 2 and words[0] in byName:
			creatureParts[words[0]].append(( words[1], family, names ))

	# what the creatures' elements are measured against: the mean protection of the creatures that give materials
	traitsOf = [ r for r in fauna if creatureParts.get(r["name"]) ]
	means = [ sum(int(r[c] or 0) for r in traitsOf) / float(len(traitsOf)) for c, n in ELEMENTS ]
	def habitat(code):
		counts = sheets[code]
		order = "dfjlp"
		return max(order, key=lambda e: ( counts[e], -order.index(e) ))

	models = []
	kindRank = collections.Counter()
	for r in sorted(traitsOf, key=lambda r: r["id"]):
		creature = Creature(r, habitat(r["id"]), means)
		models.append(( r["id"], r["name"], r["category"] ))
		for part, family, names in sorted(creatureParts[r["name"]]):
			craft = any(re.search(r"\b(Basic|Fine|Choice|Excellent|Supreme)\b", n) for n in names)
			mission = any(re.search(r"\b(Plain|Average|Prime(?! Root)|Select|Superb|Magnificient)\b", n) for n in names)
			if craft == mission:
				error(family + ": its material names do not say whether it is a craft or a mission material")
				continue
			if mission:
				if part not in MISSION_KINDS:
					error(family + ": no group for the mission part " + part)
					continue
				group, icon = MISSION_KINDS[part]
				if part == "Flesh" and r["type"] == "kitin":
					group = "Kitin"
				row(family, group, "", "C", icon)
				continue
			if part not in CREATURE_KINDS:
				error(family + ": no craft use for the part " + part)
				continue
			main, second, icon, hard = CREATURE_KINDS[part]
			profiles = [ profile(letter, creature.specialty(letter), hard, k == 0) for k, letter in enumerate(( main, second )) ]
			row(family, "Creature", main + second, "C", icon, profiles, color=kindRank[part])
			kindRank[part] += 1

	for name, group, parts, location, icon, specials in SPECIALS:
		row(name, group, parts, location, icon, specialOnly=True, specials=specials)
	for name, group, location, icon in GOO_FAMILIES:
		row(name, group, "", location, icon)

	# ---- every component type of a plan has deposit and creature materials. That is enough for the items of every
	# origin: a material counts for an item when the CraftCivSpec of its part for the component type is common or the
	# item's origin, or the item is common (the server's craft check of the default build; the ecosystem against the
	# plan's CivRestriction is the rule of RYZOM_FORGE builds). mp_generator writes a CraftCivSpec by the ecosystem of
	# the sheet (common and prime roots common, desert fyros, forest matis, jungle zorai, lakes tryker), and makes every
	# deposit family Basic and Fine in the common ecosystem and Choice, Excellent and Supreme in prime roots too: so a
	# type a deposit family serves has common materials of every class, which every item takes, up to quality 250
	# (domains/plans.py of generate_core4_sheets checks each plan against the sheets)
	served = collections.defaultdict(set)
	for cells in rows:
		if cells[5] in ( "D", "C" ) and cells[18] != "x":
			for letter in cells[2]:
				served[letter].add(cells[5])
	for i, name in enumerate(TYPE_NAMES):
		letter = chr(ord("A") + i)
		if letter in "STUVWX":
			continue # the tool parts: no plan asks for them
		if served[letter] != { "D", "C" }:
			error("component type %s %s is served by %s only" % (letter, name, ", ".join(sorted(served[letter])) or "nothing"))
	names = [ cells[0] for cells in rows ]
	for n, c in collections.Counter(names).items():
		if c > 1:
			error("family " + n + " has " + str(c) + " rows")

	if errors:
		for e in errors:
			print("ERROR: " + e, file=sys.stderr)
		sys.exit(1)

	# ---- the four tables, made in memory, then written (writeTables)
	tables = [] # (table file, content)
	def write(name, lines):
		content = "".join(";".join(line) + "\n" for line in lines)
		try:
			data = content.encode("ascii")
		except UnicodeEncodeError as e:
			fail(name + " would hold a character other than ASCII (" + str(e) + "): no table was changed")
		tables.append(( os.path.join(HERE, name), data ))

	header = [ "", "Group", "Craft parts", "Attributes", "", "Location", "Icon", "", "", "", "BestA", "WorstA1", "WorstA2",
		"BestB", "WorstB1", "WorstB2", "Color", "", "Special only", "Special items" ]
	write("rm_fam_prop.csv", [ header ] + rows)
	write("rm_item_parts.csv", [ [ "Part", "Name" ] + STAT_NAMES ] + [ [ chr(ord("A") + i), TYPE_ENTRIES[i][2:] ]
		+ [ "X" if s in RELEVANT[chr(ord("A") + i)] else "" for s in STAT_NAMES ] for i in range(26) ])
	write("creature_models.csv", [ [ "", "Name", "Category" ] ] + [ [ c, n, g ] for c, n, g in models ])
	# The class of a creature's craft materials by its level code (zone letter, then 1-4 for the four strengths of a zone
	# and 5-8 for its bosses): the zones follow the bands of fifty levels the deposits' classes cover (a and b up to 50
	# Basic, c up to 100 Fine, d up to 150 Choice, e up to 200 Excellent, f up to 250 Supreme), and a boss gives the next
	# class. Local level 6 gets none (-): the server never quarters a craft material from a creature of that level
	# (egs_static_harvestable.cpp gives it no quantity), so its materials would be sheets nobody gets
	classes = [ "Basic", "Fine", "Choice", "Excellent", "Supreme" ]
	def creatureClass(zone, digit):
		if digit == 6:
			return "-"
		return classes[min(len(classes) - 1, max(0, "abcdef".index(zone) - 1) + (1 if digit >= 5 else 0))]
	write("rm_creature_classes.csv", [ [ "Level", "Class" ] ] + [ [ zone + str(digit), creatureClass(zone, digit) ]
		for zone in "abcdef" for digit in range(1, 9) ])
	writeTables(tables)
	print("%d families (%d creature models), written to %s" % (len(rows), len(models), HERE))

TEMPORARY_SUFFIX = ".make_tables_tmp"

def deleteAll(paths):
	"""delete the files that exist of these, each removal guarded so that the stop or interruption being handled is the
	one reported; the ones that could not be deleted"""
	left = []
	for path in paths:
		try:
			if os.path.exists(path):
				os.remove(path)
		except OSError:
			left.append(path)
	return left

def deleted(left):
	return "the temporary files are deleted" if not left else "these temporary files could not be deleted, remove them: " + ", ".join(left)

def writeTables(tables):
	"""each table to a temporary file beside it, then, once all four are written, each renamed over its table (a step the
	file system does at once). A failure or an interruption before the renames deletes the temporary files and leaves
	the tables as they were; one during the renames deletes those not renamed yet and says how many were replaced."""
	for path, data in tables:
		if os.path.exists(path + TEMPORARY_SUFFIX):
			fail(path + TEMPORARY_SUFFIX + " is the temporary file of a run that was stopped: remove it, then run again (no table was changed)")
	written = []
	try:
		for path, data in tables:
			written.append(path + TEMPORARY_SUFFIX)
			with open(path + TEMPORARY_SUFFIX, "wb") as f:
				f.write(data)
	except BaseException as e:
		state = "no table was changed, " + deleted(deleteAll(written))
		if not isinstance(e, OSError):
			print("ERROR: stopped while writing " + written[-1] + ", " + state, file=sys.stderr)
			raise
		fail("cannot write " + written[-1] + " (" + str(e) + "): " + state)
	replaced = 0
	try:
		for path, data in tables:
			os.replace(path + TEMPORARY_SUFFIX, path)
			replaced += 1
	except BaseException as e:
		left = deleteAll([ path + TEMPORARY_SUFFIX for path, data in tables[replaced:] ])
		state = "%d of the %d tables were replaced before it, %s: run again" % (replaced, len(tables), deleted(left))
		if not isinstance(e, OSError):
			print("ERROR: stopped while replacing " + tables[replaced][0] + ", " + state, file=sys.stderr)
			raise
		fail("cannot rename " + tables[replaced][0] + TEMPORARY_SUFFIX + " over " + tables[replaced][0] + " (" + str(e) + "): " + state)

if __name__ == "__main__":
	main()
