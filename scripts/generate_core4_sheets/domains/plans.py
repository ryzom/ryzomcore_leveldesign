# The craft plans of Ryzom Core: one plan brick for every plan id of the translation (Jan: "make everything craftable
# incl refugee stuff") and the phrase that teaches it where the translation has one. The plans of the civilisations
# (three qualities of every item), the common and refugee plans, the tribe plans (and Erouk'an's armor with the
# Marauders' knowledge of it), the kami and karavan faction items and shields, and the kami and karavan construction
# pieces. It replaces the plan bricks and phrases ../generate_r2_sheets/generate_sitem.py wrote and the Nevrax copies
# beside them; generate_sitem.py writes the items, and plan_items.py (beside this folder's generate.py) says which item
# each plan makes, for both.
#
# What the code does with a plan (survey_server.md 6): the craft window offers the known plans of the families the root
# lists in FPLAN (domains/craft.py); the plan brick carries the item it makes (faber.Create.Crafted Item, an item whose
# ITEM_TYPE has a faber action), its components (MP 1..5 with Quantity 1..5, contiguous from 1: the client stops at
# the first empty slot), the skill that gains the XP and whose value is compared with the material quality
# (Basics.Skill), its civilisation (CivRestriction: in RYZOM_FORGE builds the ecosystems whose materials it takes),
# and the stat factors. Which materials go into a plan is decided by the item it makes (the server's craft check of
# the default build): a material counts for a component when the CraftCivSpec of its part for that component type is
# common or the item's origin, or the item is common (Materials.counts). The plan's tool type is shown in its help, and
# the client makes a craft action usable only with that tool in hand (CSPhraseManager, the faber plan's tool type); the
# server checks only that a crafting tool is in hand (faber_phrase.cpp). A plan phrase only teaches its brick (not
# castable): rolemasters sell the nations' plans, missions teach the others (MISSIONS_ONLY_ORIGINS below), by the
# phrase (learn_action) or the brick (learn_brick).

import collections, os, re
import framework
import plan_items as PI
from balancing import common
from balancing import plans as B

OWNS = [
	"sbrick/craft/plan",          # the plan bricks and their parents, by category and origin
	"sphrase/craft/plan",         # the phrases that teach them
	"sbrick/craft/effect",        # where generate_sitem.py wrote the plan bricks: they move to sbrick/craft/plan
	"sphrase/craft/effect",       # and their phrases
	"sphrase/craft/ammo",         # Nevrax copies of four plan phrases each
	"sphrase/craft/jewel",
	"sphrase/craft/range_weapon",
]

# The items generate_sitem.py writes for plans whose item has no sheet yet (its table of craft items, first column the
# item id): a plan may name such an item, which the next run of generate_sitem.py writes.
ITEM_TABLE = os.path.join(framework.LEVELDESIGN, "scripts", "generate_r2_sheets", "sitem_craft_items.tsv")

ATLASES = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ] # in pipeline/install/interfaces
DFN = os.path.join(framework.LEVELDESIGN, "DFN", "game_elem", "_item")

# --------------------------------------------------------------------------------------------- families and kinds
def isPlan(sheetId):
	"""a craft plan id of the translation (plan_items.PLAN_ID)"""
	return PI.PLAN_ID.match(sheetId.lower()) is not None

def planFamily(sheetId):
	"""the family of a plan: the letters before its number, except where the names put a plan in another family
	(survey_translations.md 6.2) and where this domain moves it so the code can offer it:
	- the caster armor plans named as light armor (bc?aea17..21) are caster plans (BC?AED);
	- the tribe heavy armor of Erouk'an and the Marauders sits with the common heavy armor (BCCAEC);
	- the kami and karavan shields and the tribe shields (bcbrea19..24) sit with the common shields (BCCSEA): in the
	  tribe range family the range weapon roots offered them, made with a range weapon tool;
	- the refugee light pieces bcraeb07, 08, 10 sit with the refugee armor (BCRAEA): the code has no BCRAEB."""
	i = sheetId.lower()
	m = re.match(r"^bcoka([mr])e([mrt]).*_([12])$", i)
	if m: # faction items: bcoka<kami or karavan>e<melee, range or tool><item>_<grade>
		return "BCOKA" + m.group(1).upper() + m.group(2).upper() + "0" + m.group(3)
	if re.match(r"^bcka[mr]sea", i) or re.match(r"^bcbrea(19|2[0-4])_", i):
		return "BCCSEA"
	if i.startswith("bcbah"):
		return "BCCAEC"
	if i.startswith("bcraeb"):
		return "BCRAEA"
	m = re.match(r"^bc([fmtz])aea(1[7-9]|2[01])(_|$)", i)
	if m:
		return "BC" + m.group(1).upper() + "AED"
	m = re.match(r"^([a-z]+)", i)
	return m.group(1).upper() if m else None

CIVS = { "f": "fyros", "m": "matis", "t": "tryker", "z": "zorai" }

def origin(planId):
	"""(origin folder, civilisation letter or None) of a plan"""
	i = planId.lower()
	if re.match(r"^bc(oka|ka)m", i):
		return "kami", None
	if re.match(r"^bc(oka|ka)r", i):
		return "karavan", None
	letter = i[2]
	if letter in CIVS:
		return CIVS[letter], letter
	return { "c": "common", "b": "tribe", "r": "refugee" }[letter], None

# the category of an item type: folder, tool type of the plan (the tool of the roots that offer it), plan icon
MELEE_TYPES = [ "DAGGER", "SWORD", "MACE", "AXE", "SPEAR", "STAFF", "TWO_HAND_SWORD", "TWO_HAND_AXE", "PIKE", "TWO_HAND_MACE",
	"MAGICIAN_STAFF" ]
RANGE_TYPES = [ "PISTOL", "BOWPISTOL", "RIFLE", "BOWRIFLE", "AUTOLAUCH", "LAUNCHER" ]
JEWEL_TYPES = [ "ANKLET", "BRACELET", "DIADEM", "EARING", "PENDANT", "RING" ]
TOOL_TYPES = [ "ArmorTool", "AmmoTool", "JewelryTool", "MeleeWeaponTool", "RangeWeaponTool", "SHEARS" ]

def category(itemType):
	if itemType in MELEE_TYPES:
		return "melee_weapon"
	if itemType in RANGE_TYPES:
		return "range_weapon"
	if itemType.endswith("_AMMO"):
		return "ammo"
	if itemType in ( "SHIELD", "BUCKLER" ):
		return "shield"
	if itemType in JEWEL_TYPES:
		return "jewel"
	if itemType in TOOL_TYPES:
		return "tool"
	if itemType == "UNDEFINED":
		return "construction"
	return "armor"

# the tool of the roots that offer each category (domains/craft.py): shields with the armor tool, constructions with
# the jewelry tool, tools with the tool maker
CATEGORY_TOOL = { "melee_weapon": "MeleeWeaponTool", "range_weapon": "RangeWeaponTool", "ammo": "AmmoTool", "armor": "ArmorTool",
	"shield": "ArmorTool", "jewel": "JewelryTool", "tool": "ToolMaker", "construction": "JewelryTool" }

# the plan's icon is its item's icon (the interface atlas names the item sheets use)
ICONS = {
	"DAGGER": "mw_dagger.png", "SWORD": "mw_sword.png", "MACE": "mw_mace.png", "AXE": "mw_axe.png", "SPEAR": "mw_lance.png",
	"STAFF": "mw_staff.png", "TWO_HAND_SWORD": "mw_2h_sword.png", "TWO_HAND_AXE": "mw_2h_axe.png", "PIKE": "mw_2h_lance.png",
	"TWO_HAND_MACE": "mw_2h_mace.png", "MAGICIAN_STAFF": "mg_glove.png",
	"PISTOL": "rw_pistol.png", "BOWPISTOL": "rw_pistolarc.png", "RIFLE": "rw_rifle.png", "BOWRIFLE": "rw_bowgun.png",
	"AUTOLAUCH": "rw_autolaunch.png", "LAUNCHER": "rw_launcher.png",
	"SHIELD": "sh_large_shield.png", "BUCKLER": "sh_buckler.png",
	"ANKLET": "pa_anklet.png", "BRACELET": "pa_bracelet.png", "DIADEM": "pa_diadem.png", "EARING": "pa_earring.png",
	"PENDANT": "pa_pendant.png", "RING": "pa_ring.png",
	"ArmorTool": "to_armor.png", "AmmoTool": "to_ammo.png", "JewelryTool": "to_jewels.png", "MeleeWeaponTool": "to_melee.png",
	"RangeWeaponTool": "to_range.png", "SHEARS": "to_forage.png",
	"UNDEFINED": "fp_building.png",
	"BOOTS": "ar_botte.png", "GLOVES": "ar_hand.png", "PANTS": "ar_pantabotte.png", "SLEEVES": "ar_armpad.png",
	"VEST": "ar_gilet.png", "HELMET": "ar_helmet.png",
}
AMMO_OVERLAY = "am_logo.png" # over the weapon's icon, as the ammunition roots show it

def icon(itemType):
	if itemType.endswith("_AMMO"):
		return ICONS[itemType[:-len("_AMMO")].replace("AUTOLAUNCH", "AUTOLAUCH")]
	if itemType in ICONS:
		return ICONS[itemType]
	return ICONS[itemType.partition("_")[2]]

def iconBack(originName):
	if originName in CIVS.values():
		return "bk_" + originName + "_brick.png"
	if originName in ( "kami", "karavan" ):
		return "bk_" + originName + ".png"
	return "bk_generic_brick.png"

# The skill of a plan: the master leaf of its item (survey_translations.md 5.2); the code has no bowpistol or bowrifle
# skill (skills.cpp), so they train the pistol and rifle crafting; ammunition trains the skill of its weapon and a
# tool the branch of what it serves, the pick and the constructions the craft root (design.md 9)
SKILLS = {
	"DAGGER": "SCM1DEM", "SWORD": "SCM1SEM", "MACE": "SCM1MEM", "AXE": "SCM1AEM", "SPEAR": "SCM1PEM", "STAFF": "SCM1TEM",
	"TWO_HAND_SWORD": "SCM2SEM", "TWO_HAND_AXE": "SCM2AEM", "PIKE": "SCM2PEM", "TWO_HAND_MACE": "SCM2MEM", "MAGICIAN_STAFF": "SCMCAEM",
	"PISTOL": "SCR1PEM", "BOWPISTOL": "SCR1PEM", "RIFLE": "SCR2REM", "BOWRIFLE": "SCR2REM", "AUTOLAUCH": "SCR2AEM", "LAUNCHER": "SCR2LEM",
	"SHIELD": "SCASSEM", "BUCKLER": "SCASBEM",
	"ANKLET": "SCJAAEM", "BRACELET": "SCJBAEM", "DIADEM": "SCJDAEM", "EARING": "SCJEAEM", "PENDANT": "SCJPAEM", "RING": "SCJRAEM",
	"ArmorTool": "SCA", "AmmoTool": "SCR", "JewelryTool": "SCJ", "MeleeWeaponTool": "SCM", "RangeWeaponTool": "SCR", "SHEARS": "SC",
	"UNDEFINED": "SC",
}
ARMOR_SKILL_CLASS = { "LIGHT": "L", "MEDIUM": "M", "HEAVY": "H" }
ARMOR_SKILL_PIECE = { "BOOTS": "B", "GLOVES": "G", "PANTS": "P", "SLEEVES": "S", "VEST": "V", "HELMET": "H" }

def skill(itemType):
	if itemType.endswith("_AMMO"):
		return SKILLS[itemType[:-len("_AMMO")].replace("AUTOLAUNCH", "AUTOLAUCH")]
	if itemType in SKILLS:
		return SKILLS[itemType]
	armorClass, sep, piece = itemType.partition("_")
	return "SCA" + ARMOR_SKILL_CLASS[armorClass] + ARMOR_SKILL_PIECE[piece] + "EM"

def isAdvantage(item):
	"""a named item with an advantage (burning, electric, living, waving), the letter after the item code"""
	i = re.sub(r"_[23]$", "", item)
	return re.match(r"^ic[fmtz](m[12][a-z]{2}|r[12][a-z]|s[bs])[belw]$", i) is not None

def tier(planId, item, itemType, originName):
	"""the tier of a plan (balancing/plans.py TIERS)"""
	p = planId.lower()
	if itemType == "UNDEFINED":
		return "construction"
	m = re.match(r"^bcoka[mr]e.*_([12])$", p) or re.match(r"^bcka[mr]sea0([1-3])$", p)
	if m:
		return "faction" + m.group(1)
	if itemType.endswith("_AMMO"):
		return "single"
	if originName == "tribe":
		return "high" # the tribes' named items, each a reward of its tribe
	if originName in ( "common", "refugee" ):
		return "basic" # the generic and refugee plans ("Generic Light Boots Plan", "Refugee Black Boots Plan")
	if item.endswith("_2"):
		return "medium"
	if item.endswith("_3") or isAdvantage(item):
		return "high"
	return "basic"

UNDERWEAR_ITEM = r"^ic[fmtz]auw?[pv]$" # the palette's underwear (ic?auwp, ic?auwv) and the translation's ids for it

def units(itemType, item):
	if re.match(UNDERWEAR_ITEM, item):
		return B.UNDERWEAR_UNITS
	return B.baseUnits(itemType, item)

def components(itemType, item):
	if itemType == "UNDEFINED":
		return B.constructionParts(item)
	if re.match(UNDERWEAR_ITEM, item):
		return B.UNDERWEAR
	if re.match(r"^ic[fmtzc]ac[bgpsv]", item) or re.match(r"^icra", item) or re.match(r"^iccar[pv]$", item):
		return B.ROBE # caster armor and the refugee garments: no padding
	return B.COMPONENTS.get(itemType)

# Jan, 2026-11-23: the plans of no nation (common, refugee, tribe and Marauder, the kami and karavan faction items and
# shields, the constructions) are taught by missions only, as Nevrax had them: their phrases are not shown to a
# rolemaster's customers (ShowInAPOnlyIfLearnt, which the rolemaster also refuses to sell). The nations' plans are sold.
# A mission teaches a phrase (learn_action) or a brick (learn_brick) without checking the brick's learn requirements:
# the skill gates and the faction fame of such a plan apply only if a rolemaster sold it, so a mission that teaches a
# faction plan checks the fame itself.
MISSIONS_ONLY_ORIGINS = ( "common", "refugee", "tribe", "kami", "karavan" )

# ------------------------------------------------------------------------------------------------- reading core4 data
def readText(path):
	"""a whole file, UTF-8 as the leveldesign stores it: a missing or undecodable one stops the run"""
	try:
		with open(path, "r", encoding="utf-8-sig") as f:
			return f.read()
	except FileNotFoundError:
		raise framework.Stop("plans: " + path + " not found")
	except UnicodeDecodeError as e:
		raise framework.Stop("plans: " + path + " is not UTF-8 text (" + str(e) + "): correct the file")

def readTyp(path):
	return dict(re.findall(r'Label="([^"]*)" Value="([^"]*)"', readText(path)))

def typDefault(path):
	"""the Default of a type file: the value the services read where a sheet gives none"""
	m = re.search(r'<TYPE [^>]*Default="([^"]*)"', readText(path))
	if not m:
		raise framework.Stop("plans: " + path + " gives no Default, which a sheet that leaves the value out reads")
	return m.group(1)

def readDfnElements(path):
	return re.findall(r'<ELEMENT Name="([^"]+)"', readText(path))

def readAtoms(path):
	text = readText(path).split("<LOG>")[0]
	return re.findall(r'<PARENT Filename="([^"]+)"', text), dict(re.findall(r'<ATOM Name="([^"]+)" Value="([^"]*)"', text)), \
		re.findall(r'<STRUCT Name="[A-Z] (Mp[A-Za-z]+) \(', text)

def readMaterialParts(path):
	"""the item parts of a raw material sheet: {faber type (MpL ...): (CraftCivSpec or None where the part gives none,
	Durability or 0)}. The server takes a part for absent when its Durability is 0 (egs_static_game_item.cpp)"""
	text = readText(path).split("<LOG>")[0]
	parts = {}
	for faberType, body in re.findall(r'<STRUCT Name="[A-Z] (Mp[A-Za-z]+) \([^"]*\)">(.*?)</STRUCT>', text, re.S):
		atoms = dict(re.findall(r'<ATOM Name="([^"]+)" Value="([^"]*)"', body))
		durability = atoms.get("Durability", "0")
		parts[faberType] = (atoms.get("CraftCivSpec"), int(durability) if durability.isdigit() else 0)
	return parts

# The raw material tables of mp_generator (scripts/raw_material_tables): the families that only special items make
FAMILY_TABLE = os.path.join(framework.LEVELDESIGN, "scripts", "raw_material_tables", "rm_fam_prop.csv")

def specialOnlyFamilies():
	"""the families of rm_fam_prop.csv marked special only (the kitin lairs' larva, the invasion and goo rewards): their
	sheets are special items, found only where a deposit or a creature names one, not materials a crafter can gather"""
	lines = [ l for l in readText(FAMILY_TABLE).split("\n") if l.strip() ]
	header = lines[0].split(";") if lines else []
	if len(header) < 19 or header[1] != "Group" or header[18] != "Special only":
		raise framework.Stop("plans: " + FAMILY_TABLE + " does not start with the header make_tables.py writes (;Group;...;Special only;...)")
	return set(cells[0].strip() for cells in (l.split(";") for l in lines[1:]) if len(cells) > 18 and cells[18].strip().lower() == "x")

CREATURES = os.path.join(framework.LEVELDESIGN, "game_elem", "creature")
PRIMITIVES = os.path.join(framework.LEVELDESIGN, "primitives")

class Materials:
	"""The raw materials of core4 (mp_generator's sheets under sitem/raw_material): for each sheet, the component types
	it can serve with the CraftCivSpec of each of those parts, its ecosystem, and the highest quality it comes at:
	- a deposit material ('d' in its name, CREATURE_OR_DEPOSIT_MP_CHAR) at its sheet's MaxQuality, what a deposit
	  of that quality gives;
	- a quartered material ('c') at the highest level of the creatures that give it: the quality of its entry in a
	  creature's quartering table (_<creature>_mp.creature, MinQuality and MaxQuality, the creature's level, which
	  CCharacter::harvest gives), counted for every creature sheet under game_elem/creature that has that table as a
	  parent, placed in the world or not. The material sheets' own MaxQuality (250 for all of them) does not limit them.
	A sheet of a family that only special items make (rm_fam_prop.csv, the kitin lairs' larva) counts for nothing, nor
	does a part whose Durability is 0, which the server takes for absent. A parent a sheet names must exist.
	And what the world gives today: the quartered materials of the creature sheets the primitives name, and the exact
	materials of the deposit zones up to their deposit_max_quality_250."""
	def __init__(self, gen):
		base = os.path.join(framework.GAME_ELEMENT, "sitem", "raw_material")
		# a part that names no CraftCivSpec reads the Default of its type, as an item that names no origin
		self.defaultCivSpec = typDefault(os.path.join(DFN, "item_origine.typ"))
		special = specialOnlyFamilies()
		parents = {}
		for f in os.listdir(os.path.join(base, "_parent")):
			parentParents, atoms, parentParts = readAtoms(os.path.join(base, "_parent", f))
			if parentParts:
				gen.error("plans: the raw material parent " + f + " has item parts (" + ", ".join(parentParts) + "): this check reads the "
					+ "parts of each sheet itself, as mp_generator writes them")
			parents[f.lower()] = atoms
		self.sheets = {} # sheet name: ({component type: CraftCivSpec of the part}, ecosystem, sheet MaxQuality, 'c' or 'd')
		self.allSheets = set() # every raw material sheet, the special items included
		self.specialSheets = 0
		for root, dirs, files in os.walk(base):
			if os.path.basename(root) == "_parent":
				continue
			for f in files:
				if not (f.endswith(".sitem") and len(f) > 6 and f[0] == "m" and f[5] in "cd"):
					continue
				path = os.path.join(root, f)
				self.allSheets.add(f[:-6].lower())
				sheetParents, atoms, names = readAtoms(path)
				merged = {}
				for p in sheetParents:
					if p.lower() not in parents:
						gen.error("plans: the raw material " + f + " names the parent " + p + ", which is not in " + os.path.join(base, "_parent")
							+ ": run mp_generator, which writes the parents")
						continue
					merged.update(parents[p.lower()])
				merged.update(atoms)
				if merged.get("Family", "") in special:
					self.specialSheets += 1
					continue
				parts = {}
				for faberType, (civSpec, durability) in readMaterialParts(path).items():
					if durability > 0:
						parts[faberType] = (civSpec or self.defaultCivSpec).lower()
				self.sheets[f[:-6].lower()] = (parts, merged.get("Ecosystem", "").lower(), int(merged.get("MaxQuality", "0")), f[5])
		if not self.sheets:
			raise framework.Stop("no raw material sheet under " + base + ": run mp_generator first")
		# the quartering tables, and the creature sheets that use them
		tables, creatureTables = {}, {}
		for root, dirs, files in os.walk(CREATURES):
			for f in files:
				fl = f.lower()
				if not fl.endswith(".creature"):
					continue
				text = readText(os.path.join(root, f)).split("<LOG>")[0]
				if fl.startswith("_") and fl.endswith("_mp.creature"):
					tables[fl] = [ (m.group(3).lower(), int(m.group(2))) for m in re.finditer(r'MinQuality" Value="(\d+)"/>\s*<ATOM Name="MaxQuality" '
						r'Value="(\d+)"/>\s*<ATOM Name="AssociatedItem" Value="([^".]+)\.sitem"', text) ]
				elif not fl.startswith("_"):
					creatureTables[fl[:-9]] = [ p.lower() for p in re.findall(r'<PARENT Filename="([^"]+_mp\.creature)"', text, re.I) ]
		self.quality = {} # quartered material: highest quality any creature sheet gives it at
		def quartered(creatures):
			result = {}
			for c in creatures:
				for t in creatureTables.get(c, []):
					for sheet, q in tables.get(t, []):
						result[sheet] = max(result.get(sheet, 0), q)
			return result
		self.quality = quartered(creatureTables)
		self.creatureCount = len([ c for c, t in creatureTables.items() if t ])
		# today's world: the creature sheets the primitives name, the deposit zones' materials
		placed = set()
		self.deposits = {} # exact material of a deposit zone: its highest quality there
		for root, dirs, files in os.walk(PRIMITIVES):
			for f in files:
				if not f.endswith(".primitive"):
					continue
				text = readText(os.path.join(root, f))
				placed.update(c for c in re.findall(r"<STRING>([a-z0-9_]+)</STRING>", text) if creatureTables.get(c)) # with a quartering table
				if "depositzone" in text:
					for n in primNodes(text):
						if n.get("class") == [ "depositzone" ] and n.get("exact_mp_item"):
							sheet = n["exact_mp_item"][0].lower()
							q = int((n.get("deposit_max_quality_250") or [ "250" ])[0])
							self.deposits[sheet] = max(self.deposits.get(sheet, 0), q)
		self.placed = sorted(placed)
		self.reachable = quartered(placed)
		for sheet, q in self.deposits.items():
			if sheet in self.sheets:
				self.reachable[sheet] = max(self.reachable.get(sheet, 0), min(q, self.sheets[sheet][2]))

	def serves(self, sheet, faberType):
		"""whether a material has a part for a component type (one the server reads: Durability above 0)"""
		return faberType in self.sheets[sheet][0]

	def counts(self, sheet, faberType, origin):
		"""the server's craft check of the default build: a material counts for a component of a plan when the
		CraftCivSpec of its part for that type is common or the origin of the item the plan makes, or the item is common
		(the rule of a plan's CivRestriction against the material's ecosystem is that of RYZOM_FORGE builds)"""
		civSpec = self.sheets[sheet][0].get(faberType)
		return civSpec is not None and (civSpec == "common" or civSpec == origin or origin == "common")

	def best(self, faberType, origin, today=False):
		"""the highest quality of the materials that count for a component type of a plan whose item has this origin:
		of all the materials (deposits at their sheet's maximum, quartered ones at their creatures' levels), or of those
		the world gives today"""
		q = 0
		for sheet, (parts, ecosystem, maxq, kind) in self.sheets.items():
			if self.counts(sheet, faberType, origin):
				if today:
					q = max(q, self.reachable.get(sheet, 0))
				else:
					q = max(q, maxq if kind == "d" else self.quality.get(sheet, 0))
		return q

def itemSheets():
	"""{item id: path} of the item sheets under sitem (raw materials aside)"""
	sheets = {}
	for root, dirs, files in os.walk(os.path.join(framework.GAME_ELEMENT, "sitem")):
		if "raw_material" in root:
			continue
		for f in files:
			if f.lower().endswith(".sitem"):
				sheets[f[:-6].lower()] = os.path.join(root, f)
	return sheets

class Item:
	"""an item sheet resolved through its parents: its ItemType value, stackable, origin (the label, lower case; the
	Default of item_origine.typ where no sheet gives one), the plan it names (CraftPlan, or ""), and what keeps its
	parents from being read (a parent that does not exist, a chain of parents deeper than 8)"""
	def __init__(self, itemType, stackable, origin, craftPlan, broken):
		self.type, self.stackable, self.origin, self.craftPlan, self.broken = itemType, stackable, origin, craftPlan, broken

def readItems(sheets=None):
	"""({item id: Item} of the item sheets, {item ids of generate_sitem.py's craft table})"""
	typ = readTyp(os.path.join(DFN, "item_type.typ"))
	defaultOrigin = typDefault(os.path.join(DFN, "item_origine.typ"))
	sheets = sheets or itemSheets()
	cache = {}
	def atoms(name, depth=0):
		"""(the atoms of an item sheet over those of its parents, what keeps its parents from being read, whether the
		depth limit cut the chain). A result the depth cut is not cached: the same sheet reached nearer the item reads
		its whole chain"""
		if name in cache:
			return cache[name] + (False,)
		if depth > 8:
			return {}, [ name + " is a parent more than 8 deep (a loop of parents?)" ], True
		path = sheets.get(name)
		if not path:
			return {}, [ "the parent " + name + ".sitem does not exist" ], False
		parents, own, parts = readAtoms(path)
		merged, broken, cut = {}, [], False
		for p in parents:
			a, b, c = atoms(p.lower().replace(".sitem", ""), depth + 1)
			merged.update(a)
			broken += b
			cut = cut or c
		merged.update(own)
		if not cut:
			cache[name] = (merged, broken)
		return merged, broken, cut
	items = {}
	for name in sheets:
		if not name.startswith("_"):
			a, broken, cut = atoms(name)
			# no ItemType reads as UNDEFINED (item_type.cpp: the conversion's value for an unknown name)
			items[name] = Item(typ.get(a["ItemType"], a["ItemType"]) if a.get("ItemType") else "UNDEFINED", int(a.get("stackable", "1") or "1"),
				(a.get("origin") or defaultOrigin).lower(), a.get("CraftPlan", ""), broken)
	table = set()
	if os.path.isfile(ITEM_TABLE):
		for l in readText(ITEM_TABLE).split("\n"):
			cells = l.rstrip("\r").split("\t")
			if cells and cells[0] and not cells[0].startswith(";") and not cells[0].startswith("#"):
				table.add(cells[0].lower())
	return items, table

# The missions that teach a plan and give the materials for crafts of it: what they give must be whole sets of what the
# plan asks for (Jan, 2026-11-21: "the Barkdell rite's craft task gives what the boots plan asks for"; 2026-11-23: two
# spare sets beyond the one the plan needs, as a failed craft can destroy the materials), so a change of the plan
# shows here. The mission primitive, the primitive that holds its compiled script (the mission compiler's output, which
# the service reads), the plan phrase its craft task teaches, and the number of sets it gives.
CRAFT_TASKS = [
	# Tryker Story 4, the Barkdell rite
	( "primitives/tryker/nland/missions_tryker_story4.primitive", "primitives/tryker/nland/urban_tryker_story4.primitive", "abctaea01_talb", 3 ),
]

def primNodes(text):
	"""the properties of each node of a primitive slice (CPrimNode, CPrimZone ...): [{name: [strings]}]"""
	nodes = []
	for chunk in re.split(r'<CHILD TYPE="[A-Za-z]+">', text)[1:]:
		props = {}
		for m in re.finditer(r"<NAME>([^<]+)</NAME>((?:\s*<STRING>[^<]*</STRING>)*)", chunk):
			props.setdefault(m.group(1), re.findall(r"<STRING>([^<]*)</STRING>", m.group(2)))
		nodes.append(props)
	return nodes

def checkCraftTask(gen, path, compiled, phrase, sets, plan, faberLabels, materials):
	"""the materials the mission's recv_item gives, by component type of the plan, against the plan's quantities times
	the sets it gives, each counting for the plan's item by the server's rule, and the compiled script against the
	mission"""
	where = "plans: the craft task of " + path + " teaching " + phrase
	text = readText(os.path.join(framework.LEVELDESIGN, *path.split("/")))
	missions = [ m for m in text.split("<STRING>mission_tree</STRING>")[1:] if re.search(r"<STRING>" + re.escape(phrase) + r"</STRING>", m) ]
	if len(missions) != 1:
		gen.error(where + ": " + str(len(missions)) + " missions of the file teach it, the check expects one")
		return
	nodes = primNodes(missions[0])
	items = { n["name"][0]: n["item_sheet"][0].lower() for n in nodes if n.get("class") == [ "var_item" ] and n.get("item_sheet") }
	counts = { n["name"][0]: int(n["quantity"][0]) for n in nodes if n.get("class") == [ "var_quantity" ] and n.get("quantity") }
	wanted = collections.OrderedDict((faberLabels[c], q * sets) for c, q in plan["components"])
	given = [] # (sheet, quantity, the plan's component types it serves)
	for n in nodes:
		if n.get("class") != [ "recv_item" ]:
			continue
		for line in n.get("item/quantity/quality", []):
			words = line.split()
			if len(words) < 2 or words[0].strip("$") not in items:
				continue
			sheet = items[words[0].strip("$")]
			if sheet in materials.allSheets and sheet not in materials.sheets:
				gen.error(where + ": it gives " + sheet + ", a special item of a family that only special items make, which counts for no plan here")
				continue
			if sheet not in materials.sheets:
				continue # the tool, not a material
			quantity = counts.get(words[1].strip("$"))
			types = [ t for t in wanted if materials.serves(sheet, t) ]
			# judged by the origin of the item the plan makes, as the server does (not the folder of the plan id)
			refused = [ t for t in types if not materials.counts(sheet, t, plan["itemOrigin"]) ]
			if not types:
				gen.error(where + ": it gives " + sheet + ", which serves none of the plan's components " + ", ".join(wanted))
			elif refused:
				gen.error(where + ": it gives " + sheet + ", whose part for " + ", ".join(refused) + " is of the CraftCivSpec "
					+ ", ".join(materials.sheets[sheet][0][t] for t in refused) + ", which an item of origin " + plan["itemOrigin"] + " (" + plan["item"]
					+ ") does not take: give a material whose parts are common or " + plan["itemOrigin"])
			elif quantity is None:
				gen.error(where + ": it gives " + sheet + " without a quantity variable")
			else:
				given.append((sheet, quantity, types))
	# the crafter places every unit in a slot it serves: the units given must fill the plan's slots, times the sets,
	# exactly
	def fits(i, left):
		if i == len(given):
			return all(v == 0 for v in left.values())
		sheet, quantity, types = given[i]
		def spread(k, rest, left):
			if k == len(types) - 1:
				if rest > left[types[k]]:
					return False
				left = dict(left); left[types[k]] -= rest
				return fits(i + 1, left)
			for q in range(min(rest, left[types[k]]), -1, -1):
				l = dict(left); l[types[k]] -= q
				if spread(k + 1, rest - q, l):
					return True
			return False
		return spread(0, quantity, left)
	if not fits(0, dict(wanted)):
		gen.error(where + ": it gives " + ", ".join("%s %d (%s)" % (s, q, "/".join(t)) for s, q, t in given) + ", which cannot fill "
			+ "the slots of the plan " + phrase[1:] + " " + str(sets) + " times exactly: " + ", ".join("%s %d" % kv for kv in wanted.items()))
	# the compiled script gives the same materials (recv_item : <sheet> <quantity> <quality> : <npc>)
	scripts = [ s for s in re.findall(r"<NAME>script</NAME>(.*?)</PROPERTY>", readText(os.path.join(framework.LEVELDESIGN, *compiled.split("/"))), re.S)
		if re.search(r"learn_action :[^<]*\b" + re.escape(phrase) + r"\b", s) ]
	if len(scripts) != 1:
		gen.error(where + ": " + str(len(scripts)) + " compiled scripts in " + compiled + " teach it, the check expects one")
		return
	compiledGiven = collections.Counter()
	for sheet, quantity in re.findall(r"<STRING>recv_item : (\S+) (\d+) \d+ :", scripts[0]):
		if sheet.lower() in materials.sheets:
			compiledGiven[sheet.lower()] += int(quantity)
	sourceGiven = collections.Counter()
	for sheet, quantity, types in given:
		sourceGiven[sheet] += quantity
	if compiledGiven != sourceGiven:
		gen.error(where + ": its compiled script in " + compiled + " gives " + ", ".join("%s %d" % kv for kv in sorted(compiledGiven.items()))
			+ ", the mission " + ", ".join("%s %d" % kv for kv in sorted(sourceGiven.items())) + ": compile the mission again")

def loadAtlas(gen):
	folder = os.path.normpath(os.path.join(framework.LEVELDESIGN, "..", "pipeline", "install", "interfaces"))
	names = set()
	for a in ATLASES:
		path = os.path.join(folder, a)
		if not os.path.isfile(path):
			gen.error("plans: the interface atlas list " + path + " does not exist, so the icons cannot be checked: build the interfaces or fix the path")
			continue
		for l in readText(path).split("\n"):
			if l.strip():
				names.add(l.split()[0].lower())
	return names

def loadSkillTree(gen):
	"""{skill: (MaxSkillValue, parent skill or None)} of game_element/xp_table/skills.skill_tree, the caps the plan
	levels and learn gates follow"""
	path = os.path.join(framework.GAME_ELEMENT, "xp_table", "skills.skill_tree")
	tree = {}
	for chunk in readText(path).split("<STRUCT Name=\"")[1:]:
		code = re.search(r"<ATOM Name=\"SkillCode\" Value=\"([^\"]+)\"", chunk)
		value = re.search(r"<ATOM Name=\"MaxSkillValue\" Value=\"(\d+)\"", chunk)
		if code and value:
			parent = re.search(r"<ATOM Name=\"ParentSkill\" Value=\"([^\"]+)\"", chunk)
			tree[code.group(1)] = (int(value.group(1)), parent.group(1) if parent else None)
	for s, (cap, parent) in sorted(tree.items()):
		if parent is not None and parent not in tree:
			raise framework.Stop("plans: the skill " + s + " of " + path + " names the parent " + parent + ", which the tree does not have")
	return tree

# --------------------------------------------------------------------------------------------------------- generate
def generate(gen):
	made, unmade = PI.plans()
	atlas = loadAtlas(gen)
	materials = Materials(gen)
	items, itemTable = readItems()
	itemPlans = PI.itemPlans()
	tree = loadSkillTree(gen)
	faberLabels = readTyp(os.path.join(DFN, "item_mp_faber_type.typ"))
	faberCode = set(framework.table("rm_family:TRMFType:stringTable"))
	faberFields = set(readDfnElements(os.path.join(DFN, "_item_faber.dfn")))
	createFields = set(readDfnElements(os.path.join(DFN, "_item_faber_plan.dfn")))
	itemTypes = set(framework.table("item_type:TItemType:stringTable")) | { "UNDEFINED" }
	tools = framework.table("crafting_tool_type:TCraftingToolType:stringTable")

	# ---- what each plan is
	info = collections.OrderedDict()
	for p, item in made.items():
		itemType = PI.itemType(item)
		originName, civLetter = origin(p)
		if itemType not in itemTypes:
			gen.error("plans: " + p + " makes " + item + " of item type " + str(itemType) + ", which the code does not know (item_type.cpp)")
			continue
		t = tier(p, item, itemType, originName)
		parts = components(itemType, item)
		n = units(itemType, item)
		if not parts or not n:
			gen.error("plans: " + p + " makes " + item + " (" + itemType + "), for which balancing/plans.py has no components or units")
			continue
		info[p] = { "item": item, "type": itemType, "origin": originName, "civ": CIVS.get(civLetter), "tier": t,
			"family": planFamily(p), "category": category(itemType),
			"components": B.quantities(parts, n * B.tierSize(t)) }

	# ---- families: index by plan id within the family (no character keeps a plan: the indices are free)
	byFamily = collections.OrderedDict()
	for p, e in info.items():
		byFamily.setdefault(e["family"], []).append(p)
	for family, ids in byFamily.items():
		if family not in framework.FAMILIES or not framework.familyIs(family, "mandatory") or framework.brickType(family) != "FABER":
			gen.error("plans: family " + family + " of " + ", ".join(ids[:3]) + " is no craft plan family of the code (brick_families.h)")
		if len(ids) > 64:
			gen.error("plans: family " + family + " has " + str(len(ids)) + " plans, a family holds 64")
		for n, p in enumerate(sorted(ids)):
			info[p]["index"] = n + 1

	# ---- parents: one for all plans, one per category (the tool), one per family (FamilyId, civilisation, back)
	root = gen.parent("_bcplan", "sbrick/craft/plan", basics={ "Action Nature": "CRAFT" }, client={ "IconOver": "fp_over.png" })
	madeSheets = [ root ]
	categoryParents = {}
	for cat in sorted(set(e["category"] for e in info.values())):
		if CATEGORY_TOOL[cat] not in tools:
			gen.error("plans: tool type " + CATEGORY_TOOL[cat] + " is not one of the code (crafting_tool_type.cpp)")
		categoryParents[cat] = gen.parent("_bcplan_" + cat, "sbrick/craft/plan/" + cat, parent=root, faber={ "Tool type": CATEGORY_TOOL[cat] })
		madeSheets.append(categoryParents[cat])
	familyParents = {}
	for family, ids in byFamily.items():
		cats = set(info[p]["category"] for p in ids)
		if len(cats) > 1:
			gen.error("plans: family " + family + " holds plans of " + ", ".join(sorted(cats)) + ": a family's plans share one craft tool")
		cat = info[ids[0]]["category"]
		originName, civLetter = origin(family.lower())
		familyParents[family] = gen.parent("_" + family.lower(), "sbrick/craft/plan/" + cat + "/" + originName, parent=categoryParents[cat],
			basics={ "FamilyId": family, "CivRestriction": CIVS.get(civLetter, "common") }, client={ "IconBack": iconBack(originName) })
		madeSheets.append(familyParents[family])

	# ---- the plan bricks and their phrases
	for p, e in info.items():
		parent = familyParents[e["family"]]
		parentBasics, parentProps, parentClient, parentGrammar, parentFaber = parent.effective()
		skillName = skill(e["type"])
		if skillName not in tree:
			raise framework.Stop("plans: " + p + ": the skill " + skillName + " of its item is not in skills.skill_tree, which gives its cap")
		level = B.planLevel(e["tier"], skillName, tree)
		gateSkills, gate = B.gateSkills(skillName, level, tree)
		basics = { "IndexInFamily": e["index"], "Level": level, "SPCost": B.spCost(level),
			"LearnRequiresOneOfSkills": ":".join("%s %d" % (s, gate) for s in gateSkills), "Skill": skillName }
		if not gateSkills or any(s not in framework.SKILLS for s in gateSkills):
			gen.error("plans: " + p + ": the gate skills " + ", ".join(gateSkills) + " are not skills of the code")
		civ = e["civ"] or "common"
		if civ != parentBasics.get("CivRestriction"):
			basics["CivRestriction"] = civ
		fame = B.factionFame(e["tier"])
		if fame is not None:
			basics["Faction"] = e["origin"] # the kami or karavan fame (_faction.typ)
			basics["Minimum fame"] = fame
		client = { "Icon": icon(e["type"]) }
		if e["type"].endswith("_AMMO"):
			client["IconOver2"] = AMMO_OVERLAY
		if iconBack(e["origin"]) != parentClient.get("IconBack"):
			client["IconBack"] = iconBack(e["origin"])
		create = collections.OrderedDict([ ("Crafted Item", e["item"] + ".sitem"),
			("Nb built items", B.AMMO_PER_CRAFT if e["type"].endswith("_AMMO") else 1) ])
		if len(e["components"]) > 5:
			gen.error("plans: " + p + " takes " + str(len(e["components"])) + " component types, a plan has five places")
		for n, (component, quantity) in enumerate(e["components"]):
			create["MP %d" % (n + 1)] = component
			create["Quantity %d" % (n + 1)] = quantity
		faber = collections.OrderedDict([ ("Create", create) ])
		for k, v in sorted(B.statFactors(e["components"], e["tier"]).items()):
			faber[k] = v
		b = gen.brick(p, parent.folder, "plan " + e["tier"] + " " + e["item"] + " (" + e["type"] + ")", parent=parent,
			basics=basics, client=client, faber=faber)
		madeSheets.append(b)
		e["brick"] = b
		phrase = "a" + p
		if gen.sphraseWords.get(phrase):
			gen.phrase(phrase, "sphrase/craft/plan/" + e["category"] + "/" + e["origin"], [ p ], "plan phrase " + p, castable=False,
				showInAPOnlyIfLearnt=e["origin"] in MISSIONS_ONLY_ORIGINS)

	# ---- the plans that make no item, and the plan phrases that have no plan. An id plan_items.py has no rule for is an
	# error: a new plan id of the translation needs its rule, or it would get no brick unseen
	for p, reason in unmade.items():
		if not reason.known:
			gen.error("plans: " + p + " makes no item: " + reason + ": give plan_items.py a rule for it")
			continue
		gen.exclude("sbrick", p, "plan: " + reason)
		if gen.sphraseWords.get("a" + p):
			gen.exclude("sphrase", "a" + p, "plan phrase: its plan makes no item: " + reason)
	for i in gen.sphraseWords.ids(r"^abc"):
		if i in gen.phrases or ("sphrase", i) in gen.excluded or not isPlan(i[1:]):
			continue
		if i[1:] in made:
			continue # made above
		if not gen.sbrickWords.get(i[1:]):
			gen.exclude("sphrase", i, "plan phrase without a plan: the translation has no brick for it" + (", and the code no family "
				+ planFamily(i[1:]) if planFamily(i[1:]) not in framework.FAMILIES else ""))
		else:
			gen.error("plans: the phrase " + i + " names the plan " + i[1:] + ", which this domain neither makes nor excludes")

	# ---- checks of this domain
	for p, e in info.items():
		where = p + " (plan of " + e["item"] + ")"
		basics, properties, client, grammar, faber = e["brick"].effective()
		for k in faber:
			if k not in faberFields:
				gen.error("plans: " + where + ": faber." + k + " is not a field of _item_faber.dfn")
		for k in faber.get("Create", {}):
			if k not in createFields:
				gen.error("plans: " + where + ": faber.Create." + k + " is not a field of _item_faber_plan.dfn")
		if basics.get("Skill") not in framework.SKILLS:
			gen.error("plans: " + where + ": skill " + str(basics.get("Skill")) + " is not a skill of the code")
		# the item the plan makes: a sheet whose item type is the plan's and which names the plan (CraftPlan, the one
		# plan_items.py gives the item: generate_sitem.py writes it, a hand-kept sheet must say the same), its parents
		# all there. Its origin decides which materials the plan takes, so it must exist: generate_sitem.py writes the
		# items of its table, and runs first
		if e["item"] in items:
			it = items[e["item"]]
			if it.type != e["type"]:
				gen.error("plans: " + where + ": the item sheet's ItemType is " + str(it.type) + ", plan_items.py says " + e["type"])
			built = e["brick"].effective()[4]["Create"]["Nb built items"]
			if built > 1 and it.stackable < built:
				gen.error("plans: " + where + " makes %d at a time, the item stacks to %d (basics.stackable)" % (built, it.stackable))
			if it.broken:
				gen.error("plans: " + where + ": the item sheet's parents cannot be read (" + "; ".join(it.broken) + "), so its origin is unknown")
			if it.craftPlan.lower() != itemPlans[e["item"]] + ".sbrick":
				gen.error("plans: " + where + ": the item sheet names the plan " + (it.craftPlan or "none") + " (CraftPlan), plan_items.py says "
					+ itemPlans[e["item"]] + " makes it: correct the sheet" + ("" if e["item"] not in itemTable else ", which generate_sitem.py writes"))
			e["itemOrigin"] = it.origin
		elif e["item"] in itemTable:
			gen.error("plans: " + where + ": the item has no sheet yet, and its origin decides which materials the plan takes: run "
				+ "../generate_r2_sheets/generate_sitem.py first, which writes it from " + os.path.basename(ITEM_TABLE))
			continue
		else:
			gen.error("plans: " + where + ": no item sheet and no row in " + ITEM_TABLE + " (generate_sitem.py makes the items)")
			continue
		# components: a label of the type file whose value the code knows, served by materials that count for the item
		for component, quantity in e["components"]:
			value = faberLabels.get(component)
			if value is None or value not in faberCode:
				gen.error("plans: " + where + ": component " + component + " is not a label of item_mp_faber_type.typ the code knows")
				continue
			best = materials.best(value, e["itemOrigin"])
			if not best:
				gen.error("plans: " + where + ": no raw material serves " + component + " (" + value + ") for an item of origin " + e["itemOrigin"]
					+ " (a part of CraftCivSpec common or " + e["itemOrigin"] + ", Durability above 0, of a family not only of special items; "
					+ "sitem/raw_material, at a creature's level or a deposit's)")
			elif best < common.MAX_LEVEL:
				gen.error("plans: " + where + ": the materials that serve " + component + " (" + value + ") for an item of origin " + e["itemOrigin"]
					+ " stop at quality %d, below %d" % (best, common.MAX_LEVEL))
			e.setdefault("best", common.MAX_LEVEL)
			e["best"] = min(e["best"], best)
			today = materials.best(value, e["itemOrigin"], today=True)
			e["today"] = min(e.get("today", common.MAX_LEVEL), today)
	for s in madeSheets:
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("plans: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
	for path, compiled, phrase, sets in CRAFT_TASKS:
		if phrase[1:] not in info or "itemOrigin" not in info[phrase[1:]]:
			gen.error("plans: the craft task of " + path + " teaches " + phrase + ", whose plan this domain does not make, or whose item has no sheet")
		else:
			checkCraftTask(gen, path, compiled, phrase, sets, info[phrase[1:]], faberLabels, materials)
	# the plans that can be made from the materials, by the origin of their item: every component served, by materials
	# that count for that origin, up to the quality the materials reach (all of them up to the cap, or the checks above
	# say which not)
	byOrigin = collections.OrderedDict()
	for e in info.values():
		if "itemOrigin" in e:
			counts = byOrigin.setdefault(e["itemOrigin"], [ 0, 0 ])
			counts[0] += 1
			if e.get("best", 0) >= common.MAX_LEVEL:
				counts[1] += 1
	gen.note("plans: by the origin of the item they make, the plans whose every component the raw materials serve up to quality %d "
		"(a part of CraftCivSpec common or that origin, any for a common item; %d sheets of families only of special items not counted): %s"
		% (common.MAX_LEVEL, materials.specialSheets, ", ".join("%s %d of %d" % (o, c[1], c[0]) for o, c in sorted(byOrigin.items()))))
	# what today's world gives: the plans whose every component a placed creature or a deposit zone serves, and the
	# highest quality they can be made at from it (a note: the world is being built, the check above is what the
	# materials can give)
	makeable = [ e["today"] for e in info.values() if e.get("today") ]
	gen.note("plans: from what the world gives today (%d placed creature sheets of %d with a quartering table: %s; deposit zones: %s), "
		"%d of %d plans can be made, at quality %d at most; the others lack a component no placed creature or deposit gives"
		% (len(materials.placed), materials.creatureCount, ", ".join(materials.placed) or "none",
		", ".join("%s to %d" % kv for kv in sorted(materials.deposits.items())) or "none",
		len(makeable), len(info), max(makeable) if makeable else 0))
	# that a craft root offers every plan family, with the plans' skills in its branch, is checked by domains/craft.py
