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
# (Basics.Skill), the civilisation whose ecosystem's materials it takes (CivRestriction), and the stat factors. The
# plan's tool type is shown in its help; the server checks the tool of the root. A plan phrase only teaches its brick
# (not castable): rolemasters sell the nations' plans, missions teach the others (MISSIONS_ONLY_ORIGINS below), by
# the phrase (learn_action) or the brick (learn_brick).

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
CIV_ECOSYSTEM = { "fyros": "desert", "matis": "forest", "tryker": "lacustre", "zorai": "jungle" }

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
def readTyp(path):
	with open(path, "r", encoding="utf-8", errors="replace") as f:
		return dict(re.findall(r'Label="([^"]*)" Value="([^"]*)"', f.read()))

def readDfnElements(path):
	with open(path, "r", encoding="utf-8", errors="replace") as f:
		return re.findall(r'<ELEMENT Name="([^"]+)"', f.read())

def readAtoms(path):
	with open(path, "r", encoding="utf-8", errors="replace") as f:
		text = f.read().split("<LOG>")[0]
	return re.findall(r'<PARENT Filename="([^"]+)"', text), dict(re.findall(r'<ATOM Name="([^"]+)" Value="([^"]*)"', text)), \
		re.findall(r'<STRUCT Name="[A-Z] (Mp[A-Za-z]+) \(', text)

CREATURES = os.path.join(framework.LEVELDESIGN, "game_elem", "creature")
PRIMITIVES = os.path.join(framework.LEVELDESIGN, "primitives")

class Materials:
	"""The raw materials of core4 (mp_generator's sheets under sitem/raw_material): for each sheet, the component types
	it serves, its ecosystem, and the highest quality it comes at:
	- a deposit material ('d' in its name, CREATURE_OR_DEPOSIT_MP_CHAR) at its sheet's MaxQuality, what a deposit
	  of that quality gives;
	- a quartered material ('c') at the highest level of the creatures that give it: the quality of its entry in a
	  creature's quartering table (_<creature>_mp.creature, MinQuality and MaxQuality, the creature's level, which
	  CCharacter::harvest gives), counted for every creature sheet under game_elem/creature that has that table as a
	  parent, placed in the world or not. The material sheets' own MaxQuality (250 for all of them) does not limit them.
	And what the world gives today: the quartered materials of the creature sheets the primitives name, and the exact
	materials of the deposit zones up to their deposit_max_quality_250."""
	def __init__(self, gen):
		base = os.path.join(framework.GAME_ELEMENT, "sitem", "raw_material")
		parents = {}
		for f in os.listdir(os.path.join(base, "_parent")):
			parents[f.lower()] = readAtoms(os.path.join(base, "_parent", f))[1]
		self.sheets = {} # sheet name: (component types it serves, ecosystem, sheet MaxQuality, 'c' or 'd')
		for root, dirs, files in os.walk(base):
			if os.path.basename(root) == "_parent":
				continue
			for f in files:
				if not (f.endswith(".sitem") and len(f) > 6 and f[0] == "m" and f[5] in "cd"):
					continue
				sheetParents, atoms, parts = readAtoms(os.path.join(root, f))
				merged = {}
				for p in sheetParents:
					merged.update(parents.get(p.lower(), {}))
				merged.update(atoms)
				self.sheets[f[:-6].lower()] = (set(parts), merged.get("Ecosystem", "").lower(), int(merged.get("MaxQuality", "0")), f[5])
		if not self.sheets:
			raise framework.Stop("no raw material sheet under " + base + ": run mp_generator first")
		# the quartering tables, and the creature sheets that use them
		tables, creatureTables = {}, {}
		for root, dirs, files in os.walk(CREATURES):
			for f in files:
				fl = f.lower()
				if not fl.endswith(".creature"):
					continue
				with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
					text = fh.read().split("<LOG>")[0]
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
				with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
					text = fh.read()
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

	def accepts(self, sheet, civ):
		"""the server's rule (faber_phrase.cpp): a plan of a civilisation refuses another civilisation's ecosystem"""
		ecosystem = self.sheets[sheet][1]
		return not (civ and ecosystem in CIV_ECOSYSTEM.values() and ecosystem != CIV_ECOSYSTEM[civ])

	def best(self, faberType, civ, today=False):
		"""the highest quality of the materials a plan of this civilisation (None: common) accepts for a component type:
		of all the materials (deposits at their sheet's maximum, quartered ones at their creatures' levels), or of those
		the world gives today"""
		q = 0
		for sheet, (parts, ecosystem, maxq, kind) in self.sheets.items():
			if faberType in parts and self.accepts(sheet, civ):
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

def readItems(sheets=None):
	"""({item id: (ItemType value, stackable)} of the item sheets, resolved through their parents, {item ids of
	generate_sitem.py's craft table})"""
	typ = readTyp(os.path.join(DFN, "item_type.typ"))
	sheets = sheets or itemSheets()
	cache = {}
	def atoms(name, depth=0):
		"""the atoms of an item sheet over those of its parents"""
		if name in cache:
			return cache[name]
		path = sheets.get(name)
		if not path or depth > 8:
			return {}
		parents, own, parts = readAtoms(path)
		merged = {}
		for p in parents:
			merged.update(atoms(p.lower().replace(".sitem", ""), depth + 1))
		merged.update(own)
		cache[name] = merged
		return merged
	items = {}
	for name in sheets:
		if not name.startswith("_"):
			a = atoms(name)
			# no ItemType reads as UNDEFINED (item_type.cpp: the conversion's value for an unknown name)
			items[name] = (typ.get(a["ItemType"], a["ItemType"]) if a.get("ItemType") else "UNDEFINED", int(a.get("stackable", "1") or "1"))
	table = set()
	if os.path.isfile(ITEM_TABLE):
		with open(ITEM_TABLE, "r", encoding="utf-8") as f:
			for l in f:
				cells = l.rstrip("\r\n").split("\t")
				if cells and cells[0] and not cells[0].startswith(";") and not cells[0].startswith("#"):
					table.add(cells[0].lower())
	return items, table

# The missions that teach a plan and give the materials for one craft of it: what they give must be what the plan asks
# for (Jan, 2026-11-21: "the Barkdell rite's craft task gives what the boots plan asks for"), so a change of the plan
# shows here. The mission primitive, the primitive that holds its compiled script (the mission compiler's output, which
# the service reads), the plan phrase its craft task teaches.
CRAFT_TASKS = [
	# Tryker Story 4, the Barkdell rite
	( "primitives/tryker/nland/missions_tryker_story4.primitive", "primitives/tryker/nland/urban_tryker_story4.primitive", "abctaea01_talb" ),
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

def checkCraftTask(gen, path, compiled, phrase, plan, faberLabels, materials):
	"""the materials the mission's recv_item gives, by component type of the plan, against the plan's quantities, and the
	compiled script against the mission"""
	where = "plans: the craft task of " + path + " teaching " + phrase
	with open(os.path.join(framework.LEVELDESIGN, *path.split("/")), "r", encoding="utf-8", errors="replace") as f:
		text = f.read()
	missions = [ m for m in text.split("<STRING>mission_tree</STRING>")[1:] if re.search(r"<STRING>" + re.escape(phrase) + r"</STRING>", m) ]
	if len(missions) != 1:
		gen.error(where + ": " + str(len(missions)) + " missions of the file teach it, the check expects one")
		return
	nodes = primNodes(missions[0])
	items = { n["name"][0]: n["item_sheet"][0].lower() for n in nodes if n.get("class") == [ "var_item" ] and n.get("item_sheet") }
	counts = { n["name"][0]: int(n["quantity"][0]) for n in nodes if n.get("class") == [ "var_quantity" ] and n.get("quantity") }
	wanted = collections.OrderedDict((faberLabels[c], q) for c, q in plan["components"])
	given = [] # (sheet, quantity, the plan's component types it serves)
	for n in nodes:
		if n.get("class") != [ "recv_item" ]:
			continue
		for line in n.get("item/quantity/quality", []):
			words = line.split()
			if len(words) < 2 or words[0].strip("$") not in items:
				continue
			sheet = items[words[0].strip("$")]
			if sheet not in materials.sheets:
				continue # the tool, not a material
			quantity = counts.get(words[1].strip("$"))
			types = [ t for t in wanted if t in materials.sheets[sheet][0] ]
			if not types:
				gen.error(where + ": it gives " + sheet + ", which serves none of the plan's components " + ", ".join(wanted))
			elif not materials.accepts(sheet, plan["civ"]):
				gen.error(where + ": it gives " + sheet + " of the " + materials.sheets[sheet][1] + " ecosystem, which a " + plan["civ"] + " plan refuses")
			elif quantity is None:
				gen.error(where + ": it gives " + sheet + " without a quantity variable")
			else:
				given.append((sheet, quantity, types))
	# the crafter places every unit in a slot it serves: the units given must fill the plan's slots exactly
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
			+ "the slots of the plan " + phrase[1:] + " exactly: " + ", ".join("%s %d" % kv for kv in wanted.items()))
	# the compiled script gives the same materials (recv_item : <sheet> <quantity> <quality> : <npc>)
	with open(os.path.join(framework.LEVELDESIGN, *compiled.split("/")), "r", encoding="utf-8", errors="replace") as f:
		scripts = [ s for s in re.findall(r"<NAME>script</NAME>(.*?)</PROPERTY>", f.read(), re.S)
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
		with open(path, "r", encoding="utf-8", errors="replace") as f:
			for l in f:
				if l.strip():
					names.add(l.split()[0].lower())
	return names

# --------------------------------------------------------------------------------------------------------- generate
def generate(gen):
	made, unmade = PI.plans()
	atlas = loadAtlas(gen)
	materials = Materials(gen)
	items, itemTable = readItems()
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
		level = B.planLevel(e["tier"], skillName)
		gateSkills, gate = B.gateSkills(skillName, level, framework.SKILLS)
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

	# ---- the plans that make no item, and the plan phrases that have no plan
	for p, reason in unmade.items():
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
	pending = 0
	for p, e in info.items():
		where = p + " (plan of " + e["item"] + ")"
		# the item the plan makes: a sheet whose item type is the plan's, or one generate_sitem.py's table will write
		if e["item"] in items:
			itemType, stackable = items[e["item"]]
			if itemType != e["type"]:
				gen.error("plans: " + where + ": the item sheet's ItemType is " + str(itemType) + ", plan_items.py says " + e["type"])
			built = e["brick"].effective()[4]["Create"]["Nb built items"]
			if built > 1 and stackable < built:
				gen.error("plans: " + where + " makes %d at a time, the item stacks to %d (basics.stackable)" % (built, stackable))
		elif e["item"] in itemTable:
			pending += 1
		else:
			gen.error("plans: " + where + ": no item sheet and no row in " + ITEM_TABLE + " (generate_sitem.py makes the items)")
		# components: a label of the type file whose value the code knows, served by materials the plan accepts
		for component, quantity in e["components"]:
			value = faberLabels.get(component)
			if value is None or value not in faberCode:
				gen.error("plans: " + where + ": component " + component + " is not a label of item_mp_faber_type.typ the code knows")
				continue
			best = materials.best(value, e["civ"])
			if not best:
				gen.error("plans: " + where + ": no raw material serves " + component + " (" + value + ") for a " + (e["civ"] or "common")
					+ " plan (sitem/raw_material, at a creature's level or a deposit's)")
			elif best < common.MAX_LEVEL:
				gen.error("plans: " + where + ": the materials that serve " + component + " (" + value + ") for a " + (e["civ"] or "common")
					+ " plan stop at quality %d, below %d" % (best, common.MAX_LEVEL))
			today = materials.best(value, e["civ"], today=True)
			e["today"] = min(e.get("today", common.MAX_LEVEL), today)
		basics, properties, client, grammar, faber = e["brick"].effective()
		for k in faber:
			if k not in faberFields:
				gen.error("plans: " + where + ": faber." + k + " is not a field of _item_faber.dfn")
		for k in faber.get("Create", {}):
			if k not in createFields:
				gen.error("plans: " + where + ": faber.Create." + k + " is not a field of _item_faber_plan.dfn")
		if basics.get("Skill") not in framework.SKILLS:
			gen.error("plans: " + where + ": skill " + str(basics.get("Skill")) + " is not a skill of the code")
	for s in madeSheets:
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("plans: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
	for path, compiled, phrase in CRAFT_TASKS:
		if phrase[1:] not in info:
			gen.error("plans: the craft task of " + path + " teaches " + phrase + ", whose plan this domain does not make")
		else:
			checkCraftTask(gen, path, compiled, phrase, info[phrase[1:]], faberLabels, materials)
	# what today's world gives: the plans whose every component a placed creature or a deposit zone serves, and the
	# highest quality they can be made at from it (a note: the world is being built, the check above is what the
	# materials can give)
	makeable = [ e["today"] for e in info.values() if e.get("today") ]
	gen.note("plans: from what the world gives today (%d placed creature sheets of %d with a quartering table: %s; deposit zones: %s), "
		"%d of %d plans can be made, at quality %d at most; the others lack a component no placed creature or deposit gives"
		% (len(materials.placed), materials.creatureCount, ", ".join(materials.placed) or "none",
		", ".join("%s to %d" % kv for kv in sorted(materials.deposits.items())) or "none",
		len(makeable), len(info), max(makeable) if makeable else 0))
	if pending:
		gen.note("plans: %d plans make items that generate_sitem.py's next run writes (%s): run it before writing the sheets"
			% (pending, os.path.basename(ITEM_TABLE)))
	# that a craft root offers every plan family, with the plans' skills in its branch, is checked by domains/craft.py
