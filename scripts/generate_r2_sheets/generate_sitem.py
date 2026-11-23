
# Writes the items of game_element\sitem from the tables of this folder: the items of the Ring palette
# (match_sitem_shape.tsv), the craft items no palette has (sitem_craft_items.tsv), the nation leaders' equipment
# (sitem_leaders.tsv), their parents (sitem_parents.tsv) and the plot items of the Ring (sitem_plot_items.tsv). The
# craft plans themselves are the sheet generator's (../generate_core4_sheets, plans domain).
# Usage: generate_sitem.py [--remove-stale [--code <code folder>]] [leveldesign folder]
#   The leveldesign is by default the one that holds this script; a folder given (a copy, for a test run) is written
#   instead. The tables are read beside the script, whatever the working directory. Python 3.3 or later.
#
# Every row is made and checked first, and nothing is written when a check fails, nor when a run that was stopped left
# a file beside any sheet this run makes. Then the sheets whose content changes are written, LF as the leveldesign
# stores them: each beside its sheet first, then, once all are written, each renamed over it; a failure or an
# interruption deletes what was written beside them, names what could not be deleted, and says how many were replaced.
#
# Stale sheets: a sheet under sitem that starts with the header this script writes (<FORM Version="4.0"
# State="modified">), that no row of this run makes and that no table of this folder names may be the sheet of a row
# that is gone, or a copy someone made of a generated sheet (a copy, or "save as" in Georges, keeps the header). By
# default the script lists them and removes nothing. With --remove-stale it removes those that nothing names, and lists
# the ones it keeps with the file that names each. It looks for each by its whole name, with or without .sitem, in the
# leveldesign and in the data folders of the code checkout that name item sheets (ryzom/common/data_common and
# ryzom/client/data of <leveldesign>/../code, found from this script's place; --code names another checkout); a stale
# sheet it keeps is then read in turn for the stale sheets it names. It does not read translation/ (every item has word
# rows), the build's sheet lists (game_elem/sheets.txt, sheet_id.bin), the players' inventories or the saved
# scenarios: an item only those name is removed.

import os, re, sys

if sys.version_info < (3, 3):
	sys.exit("generate_sitem.py needs Python 3.3 or later: it replaces each sheet in one step (os.replace)")

scriptDir = os.path.dirname(os.path.abspath(__file__))

# The item each craft plan makes and the plan each item names, shared with the plans domain of the sheet generator: one
# table for both keeps a plan and its item pointing at each other
sys.path.insert(0, os.path.join(scriptDir, "..", "generate_core4_sheets"))
import plan_items

def fail(message):
	print(message)
	sys.exit(1)

def loadTsv(filename):
	"""a table of this folder, by its name: read beside the script"""
	table = []
	path = os.path.join(scriptDir, filename)
	if not os.path.isfile(path):
		fail("The table " + path + " is missing: generate_sitem.py reads its tables beside itself")
	with open(path, "r") as f:
		for l in f:
			table += [ l.strip().split("\t") ]
	return table;

USAGE = "Usage: generate_sitem.py [--remove-stale [--code <code folder>]] [leveldesign folder]"
# What the reference scan of --remove-stale reads besides the leveldesign: the data folders of the code checkout that
# name item sheets
CODE_DATA = [ ( "ryzom", "common", "data_common" ), ( "ryzom", "client", "data" ) ]
arguments = sys.argv[1:]
removeStale = False
codePath = os.path.normpath(os.path.join(scriptDir, "..", "..", "..", "code"))
codeGiven = False
rest = []
while arguments:
	a = arguments.pop(0)
	if a == "--remove-stale":
		removeStale = True
	elif a == "--code":
		if not arguments:
			fail(USAGE)
		codePath = arguments.pop(0)
		codeGiven = True
	elif a.startswith("-"):
		fail(USAGE)
	else:
		rest.append(a)
if len(rest) > 1 or (codeGiven and not removeStale):
	fail(USAGE)
if removeStale:
	# the reference scan reads the code checkout's data folders too: they must be there
	for parts in CODE_DATA:
		if not os.path.isdir(os.path.join(codePath, *parts)):
			fail("The folder " + os.path.join(codePath, *parts) + " does not exist: --remove-stale looks for the stale sheets in the "
				+ "data folders of the code checkout too, by default the one beside the leveldesign (" + codePath + "); pass --code "
				+ "<code folder> to name another")
leveldesignPath = os.path.normpath(os.path.join(scriptDir, "..", ".."))
if len(rest) == 1:
	leveldesignPath = rest[0]
if not os.path.isdir(leveldesignPath):
	fail("The leveldesign folder " + leveldesignPath + " does not exist: name the leveldesign folder to write into (or a copy of it for a test run)")
sitemPath = os.path.join(leveldesignPath, "game_element", "sitem")
if not os.path.isdir(sitemPath):
	fail("The item folder " + sitemPath + " does not exist: " + leveldesignPath + " is no leveldesign")

# The header of every sheet this script writes: how a sheet of a row that is gone is known as this script's
SHEET_HEADER = "<?xml version=\"1.0\"?>\n<FORM Version=\"4.0\" State=\"modified\">\n"

# The sheets this run makes: normalized path: (path, content). Nothing is written until every row is made and checked
outputs = {}

class sheet(object):
	"""what the run writes to an item sheet, kept until every row is checked (writeSheets)"""
	def __init__(self, path):
		self.path = path
		self.parts = []
	def __enter__(self):
		return self
	def __exit__(self, kind, value, traceback):
		if kind is None:
			content = "".join(self.parts)
			if not content.startswith(SHEET_HEADER):
				fail("The sheet " + self.path + " does not start with the header of this script's sheets")
			key = os.path.normcase(os.path.normpath(self.path))
			if key in outputs and outputs[key][1] != content:
				fail("The sheet " + self.path + " would be made twice with different contents: two rows of the tables have its name")
			outputs[key] = (self.path, content)
		return False
	def write(self, text):
		self.parts.append(text)
	def flush(self):
		pass

# The labels of the item types (item_type.typ, the sheets write the label) and the code's names for them (the value)
itemTypeValues = {}
itemTypePath = os.path.join(scriptDir, "..", "..", "DFN", "game_elem", "_item", "item_type.typ")
if not os.path.isfile(itemTypePath):
	fail("The item types " + itemTypePath + " are missing: generate_sitem.py reads them from the leveldesign it is in")
with open(itemTypePath, "r") as f:
	for label, value in re.findall(r"<DEFINITION Label=\"([^\"]*)\" Value=\"([^\"]*)\"", f.read()):
		itemTypeValues[label] = value

# The icons the client has: the names of its interface atlases (the client reads a .png name as its .tga). Every icon
# an item gets must be one of them, or the client shows its default icon
atlasIcons = {}
for atlas in [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ]:
	atlasPath = os.path.join(scriptDir, "..", "..", "..", "pipeline", "install", "interfaces", atlas)
	if not os.path.isfile(atlasPath):
		fail("The interface atlas " + atlasPath + " is missing: the icons are checked against it")
	with open(atlasPath, "r") as f:
		for l in f:
			if l.strip():
				atlasIcons[l.split()[0].lower()] = True

def checkIcon(icon, sheet):
	if icon != "" and not icon.lower() in atlasIcons:
		fail("The icon " + icon + " of " + sheet + " is not in the interface atlas (texture_interfaces_*.txt)")

shapeList = {}
for entry in loadTsv("shape_list.txt"):
	shapeList[entry[0].lower()] = True

def checkShape(shape, sheet):
	if not (shape + ".shape").lower() in shapeList:
		fail("The shape " + shape + " of " + sheet + " is not in shape_list.txt (run extract_shapes.py if it is new)")

sitemParents = loadTsv("sitem_parents.tsv")
sitemParsed = loadTsv("sitem_parsed.tsv")
shapeParsed = loadTsv("shape_parsed.tsv")
matchSitemShape = loadTsv("match_sitem_shape.tsv")
sfxPsParsed = loadTsv("sfx_ps_parsed.tsv")
sfxShapeParsed = loadTsv("sfx_shape_parsed.tsv")

sfxPs = {}
sfxShape = {}
for entry in sfxPsParsed:
	sfxPs[entry[0]] = filter(None, entry[1:])
for entry in sfxShapeParsed:
	sfxShape[entry[0]] = filter(None, entry[1:])

itemPlans = plan_items.itemPlans()

sitemTags = {}

# the parents an item can have, in the order of sitem_parents.tsv, with the tags an item must have for each
parentTagList = []

for sitem in sitemParsed:
	sitemTags[sitem[0]] = sitem[2:]
for sitem in sitemParents:
	sitemTags[sitem[0]] = sitem[2:]

# The craft items no palette has (sitem_craft_items.tsv): each named by its translation id, with its shapes and tags
translatedItems = {}
for itemId, row in plan_items.readWords("item"):
	translatedItems[itemId] = True
craftItemNames = {}
for craftItem in loadTsv("sitem_craft_items.tsv"):
	if craftItem[0] == "" or craftItem[0].startswith(";"):
		continue
	if len(craftItem) < 4:
		fail("A line of sitem_craft_items.tsv must be item, shape male, shape female, tags: " + str(craftItem))
	name, shapeMale, shapeFemale = craftItem[0:3]
	if not name in translatedItems:
		fail("The craft item " + name + " is not an item of the translation (item_words_wk.txt)")
	if name in sitemTags or name in craftItemNames:
		fail("The craft item " + name + " is in sitem_craft_items.tsv twice, or also in sitem_parsed.tsv")
	if (shapeMale == "-") != (shapeFemale == "-"):
		fail("The craft item " + name + " has a shape for one gender only")
	craftItemNames[name] = True
	sitemTags[name] = craftItem[3:]
	matchSitemShape += [ [ name, shapeMale, shapeFemale ] ]

# The equipment of the nation leaders (sitem_leaders.tsv): unique items on their own shapes, each a variant of a
# systematic item, which gives its tags (so its parent, type and slot) and, if the table says so, its craft plan
leaderCraftPlanBase = {}
for leader in loadTsv("sitem_leaders.tsv"):
	if len(leader) < 5 or leader[0].startswith(";"):
		continue
	name, base, craftPlan, shapeMale, shapeFemale = leader[0:5]
	if not base in sitemTags:
		fail("Unknown base item " + base + " for the leader item " + name)
	if craftPlan != "base" and craftPlan != "none":
		fail("Craft plan of the leader item " + name + " must be base or none, not " + craftPlan)
	sitemTags[name] = sitemTags[base] + [ "leader" ]
	if craftPlan == "base":
		leaderCraftPlanBase[name] = base
	matchSitemShape += [ [ name, shapeMale, shapeFemale ] ]

# The plot items of the Ring (sitem_plot_items.tsv): the items a scenario author picks from to make a plot item of
# the scenario. They differ in their icon only, which the table gives
plotItems = []
plotItemNames = {}
for plotItem in loadTsv("sitem_plot_items.tsv"):
	if plotItem[0] == "" or plotItem[0].startswith(";"):
		continue
	if len(plotItem) != 3:
		fail("A line of sitem_plot_items.tsv must be item, icon, icon background: " + str(plotItem))
	if not plotItem[0].startswith("r2_"):
		fail("The name of the plot item " + plotItem[0] + " must start with r2_")
	if plotItem[0] in plotItemNames:
		fail("The plot item " + plotItem[0] + " is in sitem_plot_items.tsv twice")
	plotItemNames[plotItem[0]] = True
	plotItems += [ plotItem ]

def oneOf(tags, kinds, what):
	"""the one tag of tags that is a key of kinds; an item with none or several is an error"""
	found = [ tag for tag in tags if tag in kinds ]
	if len(found) != 1:
		fail("The tags " + " ".join(tags) + " must name one " + what + " of " + ", ".join(sorted(kinds.keys())))
	return found[0]

# Range weapons and their ammunition, by the weapon. The code has one skill per kind of shot (skills.h): a bowpistol
# fires as a pistol and a bowrifle as a rifle, so their ammunition fits those too (an ammo fits the weapons of its skill)
RANGE_KINDS = {
	# kind: item type, ammo item type, skill, icon, anim set, category (item_category.typ, the weight class the item's
	# tooltip names: the one-handed guns light, the rifles medium, the launchers heavy)
	"pistol": ("Pistol", "Pistol ammo", "SFR1APM", "rw_pistol.png", "Gun", "light"),
	"bowpistol": ("Bowpistol", "Bowpistol ammo", "SFR1APM", "rw_pistolarc.png", "Gun", "light"),
	"autolauncher": ("Autolauch", "Autolaunch ammo", "SFR2AAM", "rw_autolaunch.png", "Gatling", "Heavy"),
	"bowrifle": ("Bowrifle", "Bowrifle ammo", "SFR2ARM", "rw_bowgun.png", "Bow Rifle", "medium"),
	"launcher": ("Launcher", "Launcher ammo", "SFR2ALM", "rw_launcher.png", "ShotGun", "Heavy"),
	"rifle": ("Rifle", "Rifle ammo", "SFR2ARM", "rw_rifle.png", "ShotGun", "medium"),
}
# The launcher's shot bursts (RANGE_WEAPON_TYPE::Missile): the disc of the Ring creatures' bomb attacks
# (generate_aiaction.py), with the edge factor of the bomb spells (generate_core4_sheets/balancing/magic.py)
LAUNCHER_RADIUS = 4 # TODO: Calibrate
LAUNCHER_EDGE_FACTOR = 0.5 # TODO: Calibrate
# Range weapons ask for a characteristic as the melee weapons do (their original parents, Strength): aiming is balance
RANGE_CHARAC = "WellBalanced"
# A crafted stack of ammunition holds two crafts of the ammunition plans (50 rounds each)
AMMO_STACK = 100 # TODO: Calibrate
# Jewels: item type, slot, icon
JEWEL_KINDS = {
	"anklet": ("Anklet", "Ankle", "pa_anklet.png"),
	"bracelet": ("Bracelet", "Wrist", "pa_bracelet.png"),
	"diadem": ("Diadem", "Headdress", "pa_diadem.png"),
	"earring": ("Earing", "Ears", "pa_earring.png"),
	"pendant": ("Pendant", "Necklace", "pa_pendant.png"),
	"ring": ("Ring", "Fingers", "pa_ring.png"),
}
# Crafting tools: item type (and crafting tool type), icon, anim set. The icons show the tools' shapes (to_ammo is
# the pair of chisels of the melee weapon tool, to_pestle the ammunition tool's mortar, to_melee the tool maker's
# mallet)
TOOL_KINDS = {
	"ammotool": ("AmmoTool", "to_pestle.png", "Mix"),
	"armortool": ("ArmorTool", "to_armor.png", "Make Clothes"),
	"jewelrytool": ("JewelryTool", "to_jewels.png", "Cut"),
	"meleeweapontool": ("MeleeWeaponTool", "to_ammo.png", "Sharpen"),
	"rangeweapontool": ("RangeWeaponTool", "to_range.png", "Hollow Out"),
	"toolmaker": ("ToolMaker", "to_melee.png", "Make Tools"), # the tool plans need it in hand
}
# The construction pieces of the kami and karavan, by their kind: the icons of the building materials. The kami's
# living pieces take the karavan material that does their part (bark the wall, a trunk the column, fibers the filling)
CONSTRUCTION_ICONS = [
	("justice", "mp_batiment_colonne_justice.png"), # before column
	("maduk", "mp_batiment_noyau_maduk.png"),
	("brick", "mp_batiment_brique.png"), ("bark", "mp_batiment_brique.png"),
	("column", "mp_batiment_colonne.png"), ("trunk", "mp_batiment_colonne.png"),
	("ornament", "mp_batiment_ornement.png"), ("bud", "mp_batiment_ornement.png"),
	("cover", "mp_batiment_revetement.png"), ("moss", "mp_batiment_revetement.png"),
	("pedestal", "mp_batiment_socle.png"), ("root", "mp_batiment_socle.png"),
	("statue", "mp_batiment_statue.png"), ("symbol", "mp_batiment_statue.png"),
	("conglomerate", "mp_batiment_comble.png"), ("fibers", "mp_batiment_comble.png"),
]

def itemFamily(tags):
	"""item_family.typ"""
	if "ammo" in tags:
		return "ammo"
	elif "shield" in tags:
		return "shield"
	elif "ranged" in tags:
		return "range weapon"
	elif "melee" in tags:
		return "melee weapon"
	elif "armor" in tags:
		return "armor"
	elif "jewel" in tags:
		return "jewelry"
	elif "crafting" in tags and "tool" in tags:
		return "crafting tool"
	elif "harvest" in tags and "tool" in tags:
		return "harvest tool"
	elif "mission" in tags:
		return "mission item"
	return "undefined"

def itemTypeLabel(tags):
	"""the label of item_type.typ for an item or parent of these tags, undefined when they name no type"""
	itemType = "undefined"
	if "mission" in tags:
		itemType = "undefined" # the code crafts an undefined item type as a mission item (faber_action.cpp)
	elif "jewel" in tags:
		itemType = JEWEL_KINDS[oneOf(tags, JEWEL_KINDS, "jewel")][0]
	elif "tool" in tags:
		if "harvest" in tags:
			itemType = "Shears" # the forage pick
		else:
			itemType = TOOL_KINDS[oneOf(tags, TOOL_KINDS, "crafting tool")][0]
	elif "ammo" in tags:
		itemType = RANGE_KINDS[oneOf(tags, RANGE_KINDS, "range weapon")][1]
	elif "ranged" in tags:
		itemType = RANGE_KINDS[oneOf(tags, RANGE_KINDS, "range weapon")][0]
	elif "magic" in tags:
		if "amplifier" in tags:
			if "gloves" in tags:
				itemType = "Magician Staff"
	elif "melee" in tags:
		if "one-handed" in tags:
			if "dagger" in tags:
				itemType = "Dagger"
			elif "sword" in tags:
				itemType = "Sword"
			elif "mace" in tags:
				itemType = "Mace"
			elif "axe" in tags:
				itemType = "Axe"
			elif "spear" in tags:
				itemType = "Spear"
			elif "staff" in tags:
				itemType = "Staff"
		if "two-handed" in tags:
			if "sword" in tags:
				itemType = "Two Hand Sword"
			elif "axe" in tags:
				itemType = "Two Hand Axe"
			elif "pike" in tags:
				itemType = "Pike"
			elif "mace" in tags:
				itemType = "Two Hand Mace"
	elif "shield" in tags:
		if "buckler" in tags:
			itemType = "Buckler"
		elif "large" in tags:
			itemType = "Shield"
	elif "armor" in tags:
		if "refugee" in tags:
			itemType = "Light "
		elif "light" in tags:
			itemType = "Light "
		elif "medium" in tags:
			itemType = "Medium "
		elif "heavy" in tags:
			itemType = "Heavy "
		if "boots" in tags:
			itemType += "boots"
		elif "gloves" in tags:
			itemType += "gloves"
		elif "pants" in tags:
			itemType += "pants"
		elif "sleeves" in tags:
			itemType += "Sleeves"
		elif "vest" in tags:
			itemType += "vest"
		elif "helmet" in tags and "heavy" in tags:
			itemType += "helmet"
		else:
			itemType = "undefined"
	if not itemType in itemTypeValues:
		fail("The item type " + itemType + " of the tags " + " ".join(tags) + " is not in item_type.typ")
	return itemType

def slotAtom(slot):
	return "<ATOM Name=\"" + slot.lower().replace(" ", "_") + "\" Value=\"" + slot + "\"/>"

def generateParents():
	for sitem in sitemParents:
		name = sitem[0]
		tags = sitem[2:]
		strippedTags = tags[:]
		
		if "parent" in strippedTags:
			strippedTags.remove("parent")
		if "shared" in strippedTags:
			strippedTags.remove("shared")
		if "unspecified" in strippedTags:
			strippedTags.remove("unspecified")
		if "generic" in strippedTags:
			strippedTags.remove("generic")
		if "base" in strippedTags:
			strippedTags.remove("base")
		if "melee" in strippedTags:
			strippedTags.remove("melee")
		if "ranged" in strippedTags:
			strippedTags.remove("ranged")
		if "light" in strippedTags and "caster" in strippedTags:
			strippedTags.remove("light")
		if "light" in strippedTags and "refugee" in strippedTags:
			strippedTags.remove("light")
		if "shared" in tags:
			parentTagList.append((name, strippedTags))
		displayName = " ".join(strippedTags)
		
		family = itemFamily(tags) # item_family.typ
		
		origin = "common" # item_origine.typ
		if "refugee" in tags:
			origin = "refugee"
		elif "tribe" in tags:
			origin = "tribe"
		elif "karavan" in tags:
			origin = "karavan"
		elif "kami" in tags:
			origin = "kami"
		elif "fyros" in tags:
			origin = "fyros"
		elif "matis" in tags:
			origin = "matis"
		elif "zorai" in tags:
			origin = "zorai"
		elif "tryker" in tags:
			origin = "tryker"
		
		dropOrSell = not "refugee" in tags
		
		armorCategory = "unknown" # item_category.typ
		if "heavy" in tags:
			armorCategory = "Heavy"
		elif "medium" in tags:
			armorCategory = "medium"
		elif "light" in tags:
			armorCategory = "light"
		elif "melee" in tags:
			armorCategory = "hands"
		elif "ranged" in tags:
			armorCategory = "hands"
		elif "magic" in tags:
			armorCategory = "hands"
		elif "refugee" in tags:
			armorCategory = "light"
		
		iconOverlay = ""
		if "refugee" in tags:
			iconOverlay = "pw_light.png"
		elif "light" in tags:
			iconOverlay = "pw_light.png"
		elif "medium" in tags:
			iconOverlay = "pw_medium.png"
		elif "heavy" in tags:
			iconOverlay = "pw_heavy.png"
		elif "ammo" in tags:
			iconOverlay = "am_logo.png"
		
		neverHide = False
		icon = ""
		animSet = ""
		itemType = itemTypeLabel(tags) # item_type.typ
		slots = [] # item_slot_type.typ
		skill = ""
		if "magic" in tags:
			if "amplifier" in tags:
				if "gloves" in tags:
					icon = "mg_glove.png"
					neverHide = True
					slots = [ "Two Hands" ]
		elif "ammo" in tags:
			kind = RANGE_KINDS[oneOf(tags, RANGE_KINDS, "range weapon")]
			skill = kind[2]
			icon = kind[3]
			slots = [ "Ammo" ]
		elif "melee" in tags:
			if "one-handed" in tags:
				animSet = "1H"
				slots = [ "Right Hand" ]
				if "dagger" in tags:
					animSet = "Dagger"
					icon = "mw_dagger.png"
					slots += [ "Left Hand" ]
				elif "sword" in tags:
					animSet = "1H Sword"
					icon = "mw_sword.png"
				elif "mace" in tags:
					icon = "mw_mace.png"
				elif "axe" in tags:
					icon = "mw_axe.png"
				elif "spear" in tags:
					icon = "mw_lance.png"
				elif "staff" in tags:
					icon = "mw_staff.png"
			if "two-handed" in tags:
				animSet = "2H"
				slots = [ "Two Hands" ]
				if "sword" in tags:
					animSet = "2H Sword"
					icon = "mw_2h_sword.png"
				elif "axe" in tags:
					icon = "mw_2h_axe.png"
				elif "pike" in tags:
					animSet = "2HLance"
					icon = "mw_2h_lance.png"
				elif "mace" in tags:
					icon = "mw_2h_mace.png"
		elif "ranged" in tags:
			kind = RANGE_KINDS[oneOf(tags, RANGE_KINDS, "range weapon")]
			skill = kind[2]
			icon = kind[3]
			animSet = kind[4]
			weaponCategory = kind[5]
			# a one-handed range weapon leaves the left hand to its ammunition only
			if "one-handed" in tags:
				slots = [ "Right hand exclusive Hand" ]
			elif "two-handed" in tags:
				slots = [ "Two Hands" ]
		elif "shield" in tags:
			slots = [ "Left Hand" ]
			animSet = "Shield"
			if "buckler" in tags:
				icon = "sh_buckler.png"
			elif "large" in tags:
				icon = "sh_large_shield.png"
		elif "jewel" in tags:
			kind = JEWEL_KINDS[oneOf(tags, JEWEL_KINDS, "jewel")]
			slots = [ kind[1] ]
			icon = kind[2]
		elif "tool" in tags:
			slots = [ "Right hand exclusive Hand" ]
			if "harvest" in tags:
				skill = "SH" # the forage skill, as the refugee forage tool
				icon = "to_forage.png"
				animSet = "Pickaxe"
			else:
				kind = TOOL_KINDS[oneOf(tags, TOOL_KINDS, "crafting tool")]
				icon = kind[1]
				animSet = kind[2]
		
		damageType = "undefined" # item_damage_type.typ
		if "piercing" in tags:
			damageType = "Piercing"
		elif "slashing" in tags:
			damageType = "Slashing"
		elif "blunt" in tags or "magic" in tags:
			damageType = "Blunt"
		
		folder = "_"
		if "ammo" in tags:
			folder = "ammo"
		elif "ranged" in tags:
			folder = "range_weapon"
		elif "melee" in tags:
			folder = "melee_weapon"
		elif "armor" in tags:
			folder = "armor"
		elif "shield" in tags:
			folder = "shield"
		elif "jewel" in tags:
			folder = "jewel"
		elif family == "crafting tool":
			folder = "crafting_tool"
		elif family == "harvest tool":
			folder = "harvesting_tool"
		elif "mission" in tags:
			folder = "mission_item"
		
		# the melee parents are the original sheets, which this script does not write
		if "shared" in tags and not "melee" in tags:
			malus = 0
			bulk = 4 # TODO: Calibrate
			equipTicks = 10 # TODO: Calibrate
			stackable = 1
			price = 0
			saleable = True
			if "ammo" in tags:
				# a round: a craft makes a stack of them, so a stack of a craft weighs about as much as a weapon
				bulk = 0.05 # TODO: Calibrate
				if "two-handed" in tags:
					bulk = 0.1 # TODO: Calibrate
				stackable = AMMO_STACK
			elif "jewel" in tags:
				bulk = 1 # TODO: Calibrate
			elif "tool" in tags:
				# as the refugee tools of the original data (itrtar, itrtfo)
				bulk = 10
				equipTicks = 20
				price = 1000
			elif "mission" in tags:
				# pieces of a construction, carried by the stack to the mission and worth nothing to a merchant
				bulk = 2 # TODO: Calibrate
				equipTicks = None
				stackable = 99
				saleable = False
			else:
				if "one-handed" in tags:
					malus += 0.01 # TODO: Calibrate
					bulk += 2 # TODO: Calibrate
					equipTicks += 10 # TODO: Calibrate
				if "two-handed" in tags:
					malus += 0.02 # TODO: Calibrate
					bulk += 4 # TODO: Calibrate
					equipTicks += 20 # TODO: Calibrate
				if "medium" in tags:
					malus += 0.01 # TODO: Calibrate
					bulk += 2 # TODO: Calibrate
					equipTicks += 10 # TODO: Calibrate
				if "heavy" in tags:
					malus += 0.02 # TODO: Calibrate
					bulk += 4 # TODO: Calibrate
					equipTicks += 20 # TODO: Calibrate
				if "buckler" in tags:
					malus += 0.01 # TODO: Calibrate
					bulk += 2 # TODO: Calibrate
					equipTicks += 10 # TODO: Calibrate
				if "large" in tags:
					malus += 0.02 # TODO: Calibrate
					bulk += 4 # TODO: Calibrate
					equipTicks += 20 # TODO: Calibrate
				if "magic" in tags:
					malus = 0
					bulk += 2 # TODO: Calibrate
					equipTicks += 10 # TODO: Calibrate
			comments = "TODO: WearEquipmentMalus, Bulk, Time to Equip In Ticks"

			checkIcon(icon, name)
			checkIcon(iconOverlay, name)
			
			dir = sitemPath + "\\" + folder + "\\_parent"
			path = dir + "\\" + name + ".sitem"

			with sheet(path) as f:
				f.write("<?xml version=\"1.0\"?>\n")
				f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
				f.write("  <STRUCT>\n")
				f.write("    <STRUCT Name=\"basics\">\n")
				f.write("      <ATOM Name=\"name\" Value=\"" + displayName + "\"/>\n")
				if origin != "common":
					f.write("      <ATOM Name=\"origin\" Value=\"" + origin + "\"/>\n")
				if family != "undefined":
					f.write("      <ATOM Name=\"family\" Value=\"" + family + "\"/>\n")
				if not dropOrSell:
					f.write("      <ATOM Name=\"Drop or Sell\" Value=\"false\"/>\n")
				if itemType != "undefined":
					f.write("      <ATOM Name=\"ItemType\" Value=\"" + itemType + "\"/>\n")
				if stackable != 1:
					f.write("      <ATOM Name=\"stackable\" Value=\"" + str(stackable) + "\"/>\n")
				if len(slots) > 0 or malus != 0:
					f.write("      <STRUCT Name=\"EquipmentInfo\">\n")
					if len(slots) > 0:
						f.write("        <ARRAY Name=\"EquipmentSlots\">\n")
						for slot in slots:
							f.write("          " + slotAtom(slot) + "\n")
						f.write("        </ARRAY>\n")
					if malus != 0:
						f.write("        <ATOM Name=\"WearEquipmentMalus\" Value=\"" + str(malus) + "\"/>\n")
					f.write("      </STRUCT>\n")
				f.write("      <ATOM Name=\"Bulk\" Value=\"" + str(bulk) + "\"/>\n")
				if not saleable:
					f.write("      <ATOM Name=\"Saleable\" Value=\"false\"/>\n")
				if price != 0:
					f.write("      <ATOM Name=\"Price\" Value=\"" + str(price) + "\"/>\n")
				if equipTicks != None:
					f.write("      <ATOM Name=\"Time to Equip In Ticks\" Value=\"" + str(equipTicks) + "\"/>\n")
				if family == "range weapon":
					# as the original melee parents ask for their characteristic
					f.write("      <ATOM Name=\"RequiredCharac\" Value=\"" + RANGE_CHARAC + "\"/>\n")
					f.write("      <ATOM Name=\"RequiredCharacQualityFactor\" Value=\"1\"/>\n")
					f.write("      <ATOM Name=\"RequiredCharacQualityOffset\" Value=\"-10\"/>\n")
				f.write("    </STRUCT>\n")
				if "melee" in tags and damageType != "undefined":
					f.write("    <STRUCT Name=\"melee weapon\">\n")
					if damageType != "undefined":
						f.write("      <ATOM Name=\"damage type\" Value=\"" + damageType + "\">\n")
					f.write("    </STRUCT>\n")
				if family == "range weapon":
					f.write("    <STRUCT Name=\"range weapon\">\n")
					f.write("      <ATOM Name=\"category\" Value=\"" + weaponCategory + "\"/>\n")
					f.write("      <ATOM Name=\"skill\" Value=\"" + skill + "\"/>\n")
					if "launcher" in tags:
						f.write("      <ATOM Name=\"RangeWeaponType\" Value=\"Missile\"/>\n")
						f.write("      <ATOM Name=\"MissileRadius\" Value=\"" + str(LAUNCHER_RADIUS) + "\"/>\n")
						f.write("      <ATOM Name=\"MissileMinFactor\" Value=\"" + str(LAUNCHER_EDGE_FACTOR) + "\"/>\n")
					else:
						f.write("      <ATOM Name=\"RangeWeaponType\" Value=\"Generic\"/>\n")
					f.write("    </STRUCT>\n")
				if family == "ammo":
					# the ammunition fits the weapons of its skill (CCharacter::checkIfAmmoCompatibleWithWeapon)
					f.write("    <STRUCT Name=\"ammo\">\n")
					f.write("      <ATOM Name=\"weapon type\" Value=\"" + skill + "\"/>\n")
					f.write("    </STRUCT>\n")
				if "armor" in tags and armorCategory != "unknown":
					f.write("    <STRUCT Name=\"armor\">\n")
					f.write("      <ATOM Name=\"Armor category\" Value=\"" + armorCategory + "\"/>\n")
					f.write("    </STRUCT>\n")
				if "shield" in tags:
					f.write("    <STRUCT Name=\"shield\">\n")
					if "large" in tags:
						f.write("      <ATOM Name=\"Category\" Value=\"large shield\"/>\n")
					else:
						f.write("      <ATOM Name=\"Category\" Value=\"small shield\"/>\n")
					f.write("    </STRUCT>\n")
				if family == "crafting tool":
					f.write("    <STRUCT Name=\"crafting tool\">\n")
					f.write("      <ATOM Name=\"type\" Value=\"" + itemType + "\"/>\n")
					f.write("    </STRUCT>\n")
				if family == "harvest tool":
					f.write("    <STRUCT Name=\"harvest tool\">\n")
					f.write("      <ATOM Name=\"skill\" Value=\"" + skill + "\"/>\n")
					f.write("    </STRUCT>\n")
				f.write("    <STRUCT Name=\"3d\">\n")
				if icon != "":
					f.write("      <ATOM Name=\"icon\" Value=\"" + icon + "\"/>\n")
				if iconOverlay != "":
					f.write("      <ATOM Name=\"icon overlay\" Value=\"" + iconOverlay + "\"/>\n")
				if "armor" in tags:
					f.write("      <ATOM Name=\"color\" Value=\"UserColor\"/>\n")
				if animSet != "":
					f.write("      <ATOM Name=\"anim_set\" Value=\"" + animSet + "\"/>\n")
				if neverHide:
					f.write("      <ATOM Name=\"never hide when equiped\" Value=\"true\"/>\n")
				f.write("    </STRUCT>\n")
				f.write("  </STRUCT>\n")
				f.write("</FORM>\n")
				f.flush()
		# elif "generic" in tags:
		# 	dir = sitemPath + "\\" + folder + "\\_parent\\" + origin
		# 	if not os.path.isdir(dir):
		# 		os.makedirs(dir)
		# 	path = dir + "\\" + name + ".sitem"
		# 	
		# 	print(path)
		# 	with open(path, "w") as f:
		# 		f.write("<?xml version=\"1.0\"?>\n")
		# 		f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
		# 		f.write("</FORM>\n")
		# 		f.flush()

def findSitemParent(tags):
	"""the parent whose tags the item has, the one with the most of them (an ammo is also of its weapon's kind); of two
	as specific, the first of sitem_parents.tsv"""
	best = None
	bestCount = 0
	for parent, pt in parentTagList:
		if len(pt) <= bestCount:
			continue
		all = True
		for tag in pt:
			if not tag in tags:
				all = False
				break
		if all:
			best = parent
			bestCount = len(pt)
	return best

def generateSitems():
	for match in matchSitemShape:
		name = match[0]
		shapeMale = match[1]
		shapeFemale = match[2]
		tags = sitemTags[name]
		strippedTags = tags[:]
		
		if "item" in strippedTags:
			strippedTags.remove("item")
		if "crafted" in strippedTags:
			strippedTags.remove("crafted")
		if "hands" in strippedTags:
			strippedTags.remove("hands")
		if "light" in strippedTags and "caster" in strippedTags:
			strippedTags.remove("light")
		if "light" in strippedTags and "refugee" in strippedTags:
			strippedTags.remove("light")
		if "light" in strippedTags and "underwear" in strippedTags:
			strippedTags.remove("light")
		if "hq" in strippedTags:
			strippedTags.remove("hq")
			#strippedTags = [ "high quality" ] + strippedTags
		if "mq" in strippedTags:
			strippedTags.remove("mq")
			#strippedTags = [ "medium quality" ] + strippedTags
		if "armor" in strippedTags:
			strippedTags.remove("armor")
		if "melee" in strippedTags:
			strippedTags.remove("melee")
		if "ranged" in strippedTags:
			strippedTags.remove("ranged")
		if "color" in strippedTags:
			strippedTags.remove("color")
		if "advantage" in strippedTags:
			strippedTags.remove("advantage")
		if "regular" in strippedTags:
			strippedTags.remove("regular")
		if "colored" in strippedTags:
			strippedTags.remove("colored")
		displayName = " ".join(strippedTags)
		
		if "armor" in tags and "refugee" in tags and "color" in tags:
			# the refugee colours are the original sheets of armor\refugee\default, which name their craft plans
			print("Not written: " + name + ", one of the original refugee colour sheets")
			continue

		family = itemFamily(tags) # item_family.typ
		if family == "undefined":
			fail("No family for the item " + name + ", tags: " + str(tags))

		origin = "common" # item_origine.typ
		iconBackground = ""
		if "starter" in tags:
			origin = "refugee"
			iconBackground = "bk_generic.png"
		elif "tribe" in tags:
			origin = "tribe"
			iconBackground = "bk_generic.png"
		elif "karavan" in tags:
			origin = "karavan"
			iconBackground = "bk_karavan.png"
		elif "kami" in tags:
			origin = "kami"
			iconBackground = "bk_kami.png"
		elif "fyros" in tags:
			origin = "fyros"
			iconBackground = "bk_fyros.png"
		elif "matis" in tags:
			origin = "matis"
			iconBackground = "bk_matis.png"
		elif "zorai" in tags:
			origin = "zorai"
			iconBackground = "bk_zorai.png"
		elif "tryker" in tags:
			origin = "tryker"
			iconBackground = "bk_tryker.png"
		elif "common" in tags:
			origin = "common"
			iconBackground = "bk_generic.png"
		
		mapVariant = "Default"
		if "mq" in tags:
			mapVariant = "Medium Quality"
		elif "hq" in tags or "advantage" in tags:
			mapVariant = "High Quality"
		if "leader" in tags and "armor" in tags:
			mapVariant = "Low Quality" # the variant the lead textures were made for, as in the original leader sheets
		
		itemType = "undefined"
		armorSlot = "Undefined" # item_slot_type.typ
		icon = ""
		if "armor" in tags:
			itemType = itemTypeLabel(tags)
			if "boots" in tags:
				armorSlot = "Feet"
				icon = "ar_botte.png"
			elif "gloves" in tags:
				armorSlot = "Hands"
				icon = "ar_hand.png"
			elif "pants" in tags:
				armorSlot = "Legs"
				icon = "ar_pantabotte.png"
			elif "sleeves" in tags:
				armorSlot = "Arms"
				icon = "ar_armpad.png"
			elif "vest" in tags:
				armorSlot = "Chest"
				icon = "ar_gilet.png"
			elif "helmet" in tags and "heavy" in tags:
				armorSlot = "Head"
				icon = "ar_helmet.png"
		elif "mission" in tags:
			for kind, kindIcon in CONSTRUCTION_ICONS:
				if kind in tags:
					icon = kindIcon
					break
			if icon == "":
				fail("No icon for the construction piece " + name + ", tags: " + str(tags))
		
		color = ""
		if "red" in tags:
			color = "Red"
		elif "black" in tags:
			color = "Black"
		elif "beige" in tags:
			color = "Beige"
		elif "green" in tags:
			color = "Green"
		elif "turquoise" in tags:
			color = "Turquoise"
		elif "blue" in tags:
			color = "Blue"
		elif "violet" in tags:
			color = "Violet"
		elif "white" in tags:
			color = "White"

		damageType = "" # item_damage_type.typ, of an ammunition
		if family == "ammo":
			damageType = { "blunt": "Blunt", "piercing": "Piercing", "slashing": "Slashing" }[oneOf(tags, { "blunt": 1, "piercing": 1, "slashing": 1 }, "damage type")]
		
		subfolder = origin
		###print tags
		if "underwear" in tags:
			subfolder = "underwear"
		
		folder = "_unspecified"
		if "ammo" in tags:
			folder = "ammo\\" + subfolder
		elif "ranged" in tags:
			folder = "range_weapon\\" + subfolder
		elif "melee" in tags:
			folder = "melee_weapon\\" + subfolder
		elif "armor" in tags:
			###print shapeMale
			folder = "armor\\" + subfolder
			if "refugee" in tags:
				folder += "\\refugee_armor"
			elif "caster" in tags:
				folder += "\\caster_armor"
			elif "light" in tags:
				folder += "\\light_armor"
			elif "medium" in tags:
				folder += "\\medium_armor"
			elif "heavy" in tags:
				folder += "\\heavy_armor"
		elif "shield" in tags:
			folder = "shield\\" + subfolder
		elif "jewel" in tags:
			folder = "jewel\\" + subfolder
		elif family == "crafting tool":
			folder = "crafting_tool\\" + subfolder
		elif family == "harvest tool":
			folder = "harvesting_tool\\" + subfolder
		elif "mission" in tags:
			folder = "mission_item\\" + subfolder
		if "leader" in tags:
			folder = folder.split("\\")[0] + "\\" + subfolder + "\\leader"
		
		dir = sitemPath + "\\" + folder
		path = dir + "\\" + name + ".sitem"

		# print(name)
		# print(shapeMale)
		# print(shapeFemale)
		# print(tags)
		
		# The craft plan that makes the item (plan_items.py), the same table the plans domain writes the plans from. A
		# leader item takes the plan of its base item, or none
		craftPlan = None
		if "leader" in tags:
			if name in leaderCraftPlanBase:
				base = leaderCraftPlanBase[name]
				if not base in itemPlans:
					fail("No craft plan for the base item " + base + " of the leader item " + name)
				craftPlan = itemPlans[base]
		elif name in itemPlans:
			craftPlan = itemPlans[name]
			# the plan's craft action is the one of the crafted item's type (faber_action.cpp), so the type the item
			# has must be the one its plan is made for
			kind = plan_items.itemType(name)
			label = itemTypeLabel(tags)
			if itemTypeValues[label] != kind:
				fail("The item " + name + " is a " + label + " (" + itemTypeValues[label] + ") by its tags, its plan " + craftPlan + " makes a " + str(kind))
		
		parent = findSitemParent(tags)
		if not parent:
			fail("No parent for sitem: " + name + ", tags: " + str(tags))

		# An item a character shows has its shapes; jewels and ammunition sit in hidden slots and the construction
		# pieces have none, so they have no shape
		if shapeMale == "-":
			if family != "jewelry" and family != "ammo" and family != "mission item":
				fail("The item " + name + " has no shape, but a character shows a " + family)
		else:
			checkShape(shapeMale, name)
			checkShape(shapeFemale, name)
		checkIcon(icon, name)
		checkIcon(iconBackground, name)
		
		fxTrail = None
		if "kami" in tags and shapeMale + "_trail_kam" in sfxShape:
			fxTrail = shapeMale + "_trail_kam"
		elif "karavan" in tags and shapeMale + "_trail_car" in sfxShape:
			fxTrail = shapeMale + "_trail_car"
		elif shapeMale + "_trail_00" in sfxShape:
			fxTrail = shapeMale + "_trail_00"
		elif shapeMale + "_trail_gen" in sfxShape:
			fxTrail = shapeMale + "_trail_gen"

		fxAdvantage = None
		if "advantage" in tags:
			if not shapeMale in sfxPs:
				fail("No advantage fx " + shapeMale + ".ps for the item " + name)
			fxAdvantage = shapeMale
		if "faction" in tags:
			# the kami and karavan faction items glow with their faction's light
			fxAdvantage = "outpost_" + origin + "_type"
			if not fxAdvantage in sfxPs:
				fail("No faction fx " + fxAdvantage + ".ps for the item " + name)
		fxStatic = None
		if "leader" in tags and shapeMale in sfxPs:
			# the glow of a leader weapon, always on, and as its advantage fx, as in the original leader sheets
			fxAdvantage = shapeMale
			fxStatic = shapeMale

		with sheet(path) as f:
			f.write("<?xml version=\"1.0\"?>\n")
			f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
			if parent:
				f.write("  <PARENT Filename=\"" + parent + ".sitem\"/>\n")
			f.write("  <STRUCT>\n")
			f.write("    <STRUCT Name=\"basics\">\n")
			f.write("      <ATOM Name=\"name\" Value=\"" + displayName + "\"/>\n")
			if origin != "common":
				f.write("      <ATOM Name=\"origin\" Value=\"" + origin + "\"/>\n")
			if itemType != "undefined":
				f.write("      <ATOM Name=\"ItemType\" Value=\"" + itemType + "\"/>\n")
			if armorSlot != "Undefined":
				f.write("      <STRUCT Name=\"EquipmentInfo\">\n")
				f.write("        <ARRAY Name=\"EquipmentSlots\">\n")
				f.write("          <ATOM Value=\"" + armorSlot + "\"/>\n")
				f.write("        </ARRAY>\n")
				f.write("      </STRUCT>\n")
			if craftPlan:
				f.write("      <ATOM Name=\"CraftPlan\" Value=\"" + craftPlan + ".sbrick\"/>\n")
			if "leader" in tags:
				# unique items: no trade
				f.write("      <ATOM Name=\"Drop or Sell\" Value=\"false\"/>\n")
				f.write("      <ATOM Name=\"Saleable\" Value=\"false\"/>\n")
			elif origin == "refugee" and not "refugee" in sitemTags[parent]:
				# the refugee items stay with their owner, as the refugee parent and the original refugee sheets have it
				f.write("      <ATOM Name=\"Drop or Sell\" Value=\"false\"/>\n")
			f.write("    </STRUCT>\n")
			if family == "ammo":
				f.write("    <STRUCT Name=\"ammo\">\n")
				f.write("      <ATOM Name=\"damage type\" Value=\"" + damageType + "\"/>\n")
				f.write("    </STRUCT>\n")
			f.write("    <STRUCT Name=\"3d\">\n")
			if shapeMale != "-":
				f.write("      <ATOM Name=\"shape\" Value=\"" + shapeMale + ".shape\"/>\n")
				f.write("      <ATOM Name=\"shape_female\" Value=\"" + shapeFemale + ".shape\"/>\n")
			if mapVariant != "Default":
				f.write("      <ATOM Name=\"map_variant\" Value=\"" + mapVariant + "\"/>\n")
			if icon != "":
				f.write("      <ATOM Name=\"icon\" Value=\"" + icon + "\"/>\n")
			if iconBackground != "":
				f.write("      <ATOM Name=\"icon background\" Value=\"" + iconBackground + "\"/>\n")
			if color != "":
				f.write("      <ATOM Name=\"color\" Value=\"" + color + "\"/>\n")
			if "preorder" in tags:
				# the Armlet of Atys is worn on the arm: it shows out of combat too
				f.write("      <ATOM Name=\"never hide when equiped\" Value=\"true\"/>\n")
			if fxTrail or fxAdvantage:
				f.write("      <STRUCT Name=\"fx\">\n")
				if fxTrail:
					f.write("        <ATOM Name=\"Trail\" Value=\"" + fxTrail + ".shape\"/>\n")
				if fxAdvantage:
					f.write("        <ATOM Name=\"AdvantageFX\" Value=\"" + fxAdvantage + ".ps\"/>\n")
				if fxStatic:
					f.write("        <ARRAY Name=\"StaticFXs\">\n")
					f.write("          <STRUCT>\n")
					f.write("            <ATOM Name=\"Name\" Value=\"" + fxStatic + ".ps\"/>\n")
					f.write("            <ATOM Name=\"Bone\" Value=\"box_arme\"/>\n")
					f.write("          </STRUCT>\n")
					f.write("        </ARRAY>\n")
				f.write("      </STRUCT>\n")
				if fxAdvantage:
					f.write("      <ATOM Name=\"has_fx\" Value=\"true\"/>")
			f.write("    </STRUCT>\n")
			f.write("  </STRUCT>\n")
			f.write("</FORM>\n")
			f.flush()

def generatePlotItems():
	# What a plot item is, the same for all of them: an item of the family the client and the services know a plot
	# item by (SCROLL_R2 in the code), in stacks of up to 99, of bulk and weight 1, not saleable. The name,
	# description and comment a player sees are those the author gave it in the scenario
	family = "scroll R2, book R2, letter R2" # item_family.typ
	stackable = 99
	bulk = 1
	weight = 1

	dir = sitemPath + "\\scroll"

	for plotItem in plotItems:
		name, icon, iconBackground = plotItem
		displayName = "ring " + name[3:].replace("_", " ")
		path = dir + "\\" + name + ".sitem"

		with sheet(path) as f:
			f.write("<?xml version=\"1.0\"?>\n")
			f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
			f.write("  <STRUCT>\n")
			f.write("    <STRUCT Name=\"basics\">\n")
			f.write("      <ATOM Name=\"name\" Value=\"" + displayName + "\"/>\n")
			f.write("      <ATOM Name=\"family\" Value=\"" + family + "\"/>\n")
			f.write("      <ATOM Name=\"stackable\" Value=\"" + str(stackable) + "\"/>\n")
			f.write("      <ATOM Name=\"Bulk\" Value=\"" + str(bulk) + "\"/>\n")
			f.write("      <ATOM Name=\"Weight\" Value=\"" + str(weight) + "\"/>\n")
			f.write("      <ATOM Name=\"Saleable\" Value=\"false\"/>\n")
			f.write("    </STRUCT>\n")
			f.write("    <STRUCT Name=\"3d\">\n")
			f.write("      <ATOM Name=\"icon\" Value=\"" + icon + "\"/>\n")
			f.write("      <ATOM Name=\"icon background\" Value=\"" + iconBackground + "\"/>\n")
			f.write("    </STRUCT>\n")
			f.write("  </STRUCT>\n")
			f.write("</FORM>\n")
			f.flush()

def readBytes(path):
	with open(path, "rb") as f:
		return f.read()

def findStaleSheets():
	"""the stale sheets: under sitem, with this script's header, made by no row of this run and named by no table of this
	folder (an original sheet a table names stays, the refugee colours). The sheet of a row that is gone, or a copy of a
	generated sheet: which one, the reference scan (findReferences) and the --remove-stale option decide"""
	named = {}
	for table in [ "sitem_parsed.tsv", "match_sitem_shape.tsv", "sitem_craft_items.tsv", "sitem_leaders.tsv", "sitem_parents.tsv",
			"sitem_plot_items.tsv" ]:
		for row in loadTsv(table):
			if row and row[0]:
				named[row[0].lower()] = True
	header = SHEET_HEADER.encode("ascii")
	headerCrlf = SHEET_HEADER.replace("\n", "\r\n").encode("ascii")
	stale = []
	for root, dirs, files in os.walk(sitemPath):
		for f in sorted(files):
			if not f.lower().endswith(".sitem"):
				continue
			path = os.path.join(root, f)
			if os.path.normcase(os.path.normpath(path)) in outputs or f[:-6].lower() in named:
				continue
			start = readBytes(path)[:len(headerCrlf)]
			if start.startswith(header) or start.startswith(headerCrlf):
				stale.append(path)
	return sorted(stale)

def checkCraftedItems(stale):
	"""every item a craft plan makes has a sheet after the run: this script's, or an original one (the refugee colours
	and weapons)"""
	sheets = {}
	gone = dict((os.path.normcase(os.path.normpath(p)), True) for p in stale)
	for root, dirs, files in os.walk(sitemPath):
		for f in files:
			if f.lower().endswith(".sitem") and not os.path.normcase(os.path.normpath(os.path.join(root, f))) in gone:
				sheets[f[:-6].lower()] = True
	for key in outputs:
		sheets[os.path.basename(outputs[key][0])[:-6].lower()] = True
	missing = [ item for item in sorted(itemPlans.keys()) if not item in sheets ]
	if len(missing) > 0:
		fail("Items of craft plans without a sheet (add them to sitem_craft_items.tsv): " + ", ".join(missing))

# What the reference scan does not read, which the listing says
NOT_SCANNED = ("translation/ (every item has word rows), the build's sheet lists (game_elem/sheets.txt, sheet_id.bin), "
	"the players' inventories and the saved scenarios")

def sheetName(path):
	"""the name of a sheet without .sitem, lower case, as bytes for the scan: any name, not only ASCII"""
	return os.path.basename(path)[:-6].lower().encode("utf-8", "surrogateescape")

def findReferences(stale):
	"""{stale sheet: the first file that names it}, by the sheet's whole name as a word of letters, digits and
	underscores (so with or without .sitem), in any case, in the leveldesign and the data folders of the code checkout
	(CODE_DATA). Not read, as in mp_generator: the translation (its word rows name every item), the build's sheet lists
	(game_elem/sheets.txt and sheet_id.bin), git's and Python's folders, and at first the stale sheets themselves: a
	stale sheet that something names is kept, and then read in turn for the stale sheets it names (a kept copy of an
	item keeps the stale parent it names), until no more are kept"""
	if not stale:
		return {}
	# a sheet name is unique across the folders the sheet ids are made from: two stale sheets of one name cannot both be
	# kept or removed by what names them
	byName = {}
	for p in stale:
		if sheetName(p) in byName:
			fail("Two stale sheets have the name " + os.path.basename(p) + ": " + byName[sheetName(p)] + " and " + p + "; sheet names must be unique, remove or rename one before --remove-stale")
		byName[sheetName(p)] = p
	pattern = re.compile(b"(?<![A-Za-z0-9_])(" + b"|".join(re.escape(n) for n in sorted(byName)) + b")(?![A-Za-z0-9_])", re.I)
	staleKeys = set(os.path.normcase(os.path.normpath(p)) for p in stale)
	skipped = set(os.path.normcase(os.path.normpath(os.path.join(leveldesignPath, "game_elem", f))) for f in ( "sheets.txt", "sheet_id.bin" ))
	found = {}
	def scan(path):
		"""the stale sheets not yet kept that a file names, other than itself: noted with the file"""
		kept = []
		for m in pattern.finditer(readBytes(path)):
			sheetPath = byName.get(m.group(1).lower())
			if sheetPath and sheetPath not in found and os.path.normcase(os.path.normpath(sheetPath)) != os.path.normcase(os.path.normpath(path)):
				found[sheetPath] = path
				kept.append(sheetPath)
		return kept
	for top, isLeveldesign in [ ( leveldesignPath, True ) ] + [ ( os.path.join(codePath, *parts), False ) for parts in CODE_DATA ]:
		topKey = os.path.normcase(os.path.normpath(top))
		for root, dirs, files in os.walk(top):
			dirs[:] = sorted(d for d in dirs if d not in ( ".git", "__pycache__" )
				and not (isLeveldesign and os.path.normcase(os.path.normpath(root)) == topKey and d == "translation"))
			for f in sorted(files):
				path = os.path.join(root, f)
				key = os.path.normcase(os.path.normpath(path))
				if key not in skipped and key not in staleKeys:
					scan(path)
	# the kept stale sheets, read in turn, until no more are kept
	pending = sorted(found)
	while pending:
		kept = []
		for path in pending:
			kept += scan(path)
		pending = sorted(kept)
	return found

TEMPORARY_SUFFIX = ".generate_sitem_tmp"

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

def leftover(left, done):
	"""done, or which files and folders could not be deleted"""
	return done if not left else "these could not be deleted, remove them before running again: " + ", ".join(left)

def writeSheets(remove):
	"""the sheets whose content changes, LF as the leveldesign stores them (.gitattributes eol=lf): each written beside
	its sheet, then, once all are, renamed over it; then the removal of the stale sheets to remove"""
	changes = []
	for key in sorted(outputs.keys()):
		path, content = outputs[key]
		# what a stopped run left beside any sheet this run makes, whether it changes this time or not
		if os.path.exists(path + TEMPORARY_SUFFIX):
			fail(path + TEMPORARY_SUFFIX + " is what a run that was stopped wrote beside " + path + ": remove it, then run again (nothing was written)")
		data = content.encode("utf-8")
		if not (os.path.isfile(path) and readBytes(path) == data):
			changes.append((path, data))
	# every change beside its sheet: a failure or an interruption deletes what was written and the folders made for it
	made, temporaries, current = [], [], None
	try:
		for path, data in changes:
			missing = []
			folder = os.path.dirname(path)
			while not os.path.isdir(folder):
				missing.insert(0, folder)
				folder = os.path.dirname(folder)
			for folder in missing:
				current = "the folder " + folder
				os.mkdir(folder)
				made.append(folder)
			current = path + TEMPORARY_SUFFIX
			temporaries.append(current)
			with open(current, "wb") as f:
				f.write(data)
	except BaseException as e:
		left = deleteAll(temporaries)
		for folder in reversed(made):
			try:
				if os.path.isdir(folder) and not os.listdir(folder):
					os.rmdir(folder)
			except OSError:
				left.append(folder)
		state = "no sheet was changed or removed, " + leftover(left, "what was written beside them is deleted")
		if not isinstance(e, OSError):
			print("Stopped while making " + str(current) + ", " + state)
			raise
		fail("Cannot make " + str(current) + " (" + str(e) + "): " + state)
	# then each over its sheet
	replaced = 0
	try:
		for path, data in changes:
			os.replace(path + TEMPORARY_SUFFIX, path)
			print("written: " + path)
			replaced += 1
	except BaseException as e:
		left = deleteAll([ path + TEMPORARY_SUFFIX for path, data in changes[replaced:] ])
		state = ("%d of the %d changed sheets were replaced before it, no stale sheet was removed, " % (replaced, len(changes))
			+ leftover(left, "what was written beside the others is deleted") + ": run again once the cause is fixed")
		if not isinstance(e, OSError):
			print("Stopped while replacing " + changes[replaced][0] + ", " + state)
			raise
		fail("Cannot replace " + changes[replaced][0] + " (" + str(e) + "): " + state)
	done = 0
	try:
		for path in remove:
			os.remove(path)
			print("removed, nothing names it: " + path)
			done += 1
	except BaseException as e:
		state = "every sheet is written and %d of the %d stale sheets to remove were removed before it: run again" % (done, len(remove))
		if not isinstance(e, OSError):
			print("Stopped while removing " + remove[done] + ", " + state)
			raise
		fail("Cannot remove " + remove[done] + " (" + str(e) + "): " + state)
	print("%d sheets made, %d written (the others are as they were), %d removed" % (len(outputs), len(changes), len(remove)))

generateParents()
generateSitems()
generatePlotItems()
staleSheets = findStaleSheets()
removedSheets = []
if staleSheets and not removeStale:
	for path in staleSheets:
		print("stale, not removed: " + path + " (no row makes it and no table names it; --remove-stale removes it if nothing names it)")
elif staleSheets:
	references = findReferences(staleSheets)
	for path in staleSheets:
		if path in references:
			print("stale, kept: " + path + " (named by " + references[path] + ")")
		else:
			removedSheets.append(path)
	print("the stale sheets were looked for in " + leveldesignPath + " and in " + ", ".join(os.path.join(codePath, *p) for p in CODE_DATA)
		+ "; not read: " + NOT_SCANNED + ", so an item only those name is removed")
checkCraftedItems(removedSheets)
writeSheets(removedSheets)
if staleSheets:
	print("%d stale sheets: %d removed, %d kept" % (len(staleSheets), len(removedSheets), len(staleSheets) - len(removedSheets)))
