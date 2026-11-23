# The item each craft plan makes, read from the plan's id (its translation id), and the kind of an item, read from the
# item's id. Two scripts share it: the plans domain (domains/plans.py), which writes the plan bricks, and
# ../generate_r2_sheets/generate_sitem.py, which writes the items and names in each item the plan that makes it
# (CraftPlan). One table for both keeps a plan and its item pointing at each other.
#
# No imports beyond the standard library: generate_sitem.py imports it from its own folder.
#
# The plan ids follow the craft grammar of the translation (survey_translations.md 2.3): BC + origin + category + E +
# variant + number, and for most of them the item code after an underscore (bcfaec01_fahb makes icfahb). The ids
# without an item code are read from their number, as the family's names give it (bcfjea01 "Anklet - Basic Quality",
# bcfrea04 "Pistol - Basic Quality"); the tables below are those names, nothing else.

import io, os, re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSLATION = os.path.normpath(os.path.join(HERE, "..", "..", "translation"))

# the ids of the craft plans: civilisation, common, tribe and refugee plans (role E), the tribe heavy armor of Erouk'an
# and the Marauders, the kami and karavan shields, the faction items and the constructions
PLAN_ID = re.compile(r"^(bc[fmtzcbr][mrpajs]e[a-d]\d\d|bcbah[bghpsv]|bcka[mr]sea\d\d$|bcka[mr]mi_|bcoka[mr]e[mrt])")

# ---------------------------------------------------------------------------------------------- items without a code
# jewels by number: "Anklet", "Bracelet", "Diadem", "Earring", "Pendant", "Ring"
JEWELS = [ "a", "b", "d", "e", "p", "r" ]
# range weapons by number: "Autolauncher", "Bowrifle", "Launcher", "Pistol", "Bowpistol", "Rifle"
RANGE = [ "2a", "2b", "2l", "1p", "1b", "2r" ]
# ammunition by number, three damage types (smashing, piercing, slashing) per weapon: "Autolauncher", "Bowrifle",
# "Grenade", "Launcher", "Bowpistol", "Pistol", "Rifle", and the Tryker "Harpoon" (22 to 24)
AMMO = [ "2a", "2b", "1g", "2l", "1b", "1p", "2r", "1h" ]
AMMO_DAMAGE = [ "b", "p", "s" ]
# caster armor by number (bc?aea17..21; the pants are bc?aed07..09 with their item code): "Caster Boots", "Caster
# Gloves", "Caster Sleeves", "Caster Vest"
CASTER = { 17: "cb", 18: "cg", 20: "cs", 21: "cv" }
# underwear by number: "Light Panties", "Light Bra". They make the underwear of the Ring's palette (ic?auwp, ic?auwv,
# sitem_parsed.tsv), whose sheet ids scenarios keep: the translation's own ids for the same garments (ic?aup, ic?auv)
# would be second sheets of the same shapes
UNDERWEAR = { 22: "auwp", 23: "auwv" }
# the named items without a code, by family and number: their names say what they are
SPECIAL = {
	("fr", 7): "2ab", ("fr", 8): "2lb",                                       # Burning Autolauncher, Burning Launcher
	("mr", 7): "1pl", ("mr", 8): "2rl",                                       # Living Pistol, Living Rifle
	("tr", 7): "2h", ("tr", 8): "1bw", ("tr", 9): "2hw",                      # Harpoon Gun, Waving Bowpistol, Waving Harpoon Gun
	("zr", 7): "2be", ("zr", 8): "2le",                                       # Electric Bowrifle, Electric Launcher
	("mm", 11): "1pdl", ("mm", 12): "2ssl", ("mm", 13): "2ppl", ("mm", 14): "1psl", # Living Dagger, Long Sword, Pike, Spear
	("tm", 11): "2ssw", ("tm", 12): "1pdw", ("tm", 13): "1ssw",               # Waving Long Sword, Dagger, Sword
	("zm", 11): "1pse", ("zm", 12): "2bme", ("zm", 13): "1bme",               # Electric Spear, Long Mace, Mace
	("cm", 15): "2ms",                                                        # the common magic amplifier
	("rm", 6): "1pd", ("rm", 10): "1ss", ("rm", 15): "2ms",                   # Refugee Dagger, Sword, Magic Amplifier
	("ms", 3): "bl", ("ts", 3): "bw", ("zs", 3): "be",                        # Living, Waving, Electric Buckler
	("cs", 1): "b", ("cs", 2): "s",                                           # Buckler, Shield
}
# whole item ids for plans whose item has no code of the grammar
NAMED = {
	"bccmea16": "ic_candy_stick", # the candy cane of the winter events (bccmea16 has no text yet)
	"bccsea03": "pre_order",      # the Armlet of Atys, worn as a buckler (bccsea03 has no text yet)
}
# refugee armor: "Refugee <Colour> <Piece>" (bcraea01 "Refugee Black Boots" makes icraba), and the three refugee light
# pieces (bcraeb07 "Refugee Boots" makes icralb)
REFUGEE_PIECES = { "boots": "b", "gloves": "g", "pants": "p", "sleeves": "s", "vest": "v" }
REFUGEE_COLOURS = { "black": "a", "beige": "e", "green": "g", "red": "r", "turquoise": "t", "blue": "u", "violet": "v", "white": "w" }
REFUGEE_LIGHT = { 7: "b", 8: "g", 10: "s" }

# Plans that make no item, with the reason. A known reason (the code has no item type for it, a placeholder without a
# text) is excluded by the plans domain with it; an id no rule of this file reads is an error there (Reason.known)
class Reason(str):
	"""why a plan makes no item; known is False where this file has no rule for the id"""
	def __new__(cls, text, known):
		reason = str.__new__(cls, text)
		reason.known = known
		return reason

NO_ITEM_TYPE = "the code has no item type for it (item_type.h has no %s), so no item can be crafted"
PLACEHOLDER = "a <GEN> placeholder without a text: neither its name nor its number says which item it makes"

def readWords(sheetType):
	"""the (id, row) pairs of the work file of a sheet type, ids lower case, in file order"""
	path = os.path.join(TRANSLATION, "work", sheetType + "_words_wk.txt")
	with io.open(path, "r", encoding="utf-8-sig") as f:
		lines = f.read().split("\n")
	header = lines[0].rstrip("\r").split("\t")
	rows = []
	for l in lines[1:]:
		l = l.rstrip("\r")
		if l:
			row = dict(zip(header, l.split("\t")))
			if row.get(sheetType + " ID"):
				rows.append((row[sheetType + " ID"].lower(), row))
	return rows

def englishNames(sheetType):
	path = os.path.join(TRANSLATION, "translated", sheetType + "_words_en.txt")
	with io.open(path, "r", encoding="utf-8-sig") as f:
		lines = f.read().split("\n")
	header = lines[0].rstrip("\r").split("\t")
	names = {}
	for l in lines[1:]:
		row = dict(zip(header, l.rstrip("\r").split("\t")))
		if row.get(sheetType + " ID"):
			names[row[sheetType + " ID"].lower()] = row.get("name", "")
	return names

def planItem(planId, englishName):
	"""(item id, None) for a plan, or (None, reason) when no item can be made"""
	p = planId.lower()
	m = re.match(r"^bck(am|ar)mi_ep2_(.+)$", p) # constructions: bckammi_ep2_maj_maduk_core makes ep2_major_maduk_core
	if m:
		return "ep2_" + re.sub(r"^min_", "minor_", re.sub(r"^maj_", "major_", m.group(2))), None
	m = re.match(r"^bck(am|ar)sea0(\d)$", p) # kami and karavan shields: bckamsea01 makes ickamss_ep2_1
	if m:
		return "ick" + m.group(1) + "ss_ep2_" + m.group(2), None
	m = re.match(r"^bcoka([mr])e([mrt])(.+)_([12])$", p) # faction items: bcokamem1bm_1 makes icokamm1bm_1
	if m:
		return "icoka" + m.group(1) + m.group(2) + m.group(3) + "_" + m.group(4), None
	m = re.match(r"^bcbah([bghpsv])(_m)?$", p) # Erouk'an's armor, and the Marauders' knowledge of the same pieces
	if m:
		return "iccah" + m.group(1) + "_b", None
	if p in NAMED:
		return NAMED[p], None
	if p == "bccmea17":
		# the translation's only text for it is <GEN>bccmea17, and number 17 of the common melee plans names nothing
		return None, Reason(PLACEHOLDER, True)
	m = re.match(r"^bc[fmtzcbr][mrpajs]e[a-d]\d\d_([a-z][a-z0-9]*(_[a-z0-9]+)?)$", p) # the item code after the number (_2, _b ...)
	if m:
		return "ic" + m.group(1), None
	m = re.match(r"^bc([fmtzcbr])([mrpajs])e([a-d])(\d\d)(_[23])?$", p)
	if not m:
		return None, Reason("the plan id follows no rule of plan_items.py", False)
	origin, category, variant, number, quality = m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5) or ""
	code = None
	if origin == "r" and category == "a":
		words = englishName.lower().split()
		if variant == "a" and len(words) == 3 and words[0] == "refugee" and words[1] in REFUGEE_COLOURS and words[2] in REFUGEE_PIECES:
			return "icra" + REFUGEE_PIECES[words[2]] + REFUGEE_COLOURS[words[1]], None
		if variant == "b" and number in REFUGEE_LIGHT:
			return "icral" + REFUGEE_LIGHT[number], None
		return None, Reason("the refugee plan's name \"" + englishName + "\" names no colour and piece plan_items.py knows", False)
	if (origin + category, number) in SPECIAL:
		code = category + SPECIAL[(origin + category, number)]
	elif category == "j" and 1 <= number <= len(JEWELS):
		code = "j" + JEWELS[number - 1]
	elif category == "r" and 1 <= number <= len(RANGE):
		code = "r" + RANGE[number - 1]
	elif category == "p" and 1 <= number <= 3 * len(AMMO):
		code = "p" + AMMO[(number - 1) // 3] + AMMO_DAMAGE[(number - 1) % 3]
	elif category == "m" and number == 9:
		code = "m1bs" # the staff of every family
	elif category == "a" and number in CASTER:
		code = "a" + CASTER[number]
	elif category == "a" and number in UNDERWEAR:
		code = UNDERWEAR[number]
	if code is None:
		return None, Reason("the plan number %d of %s follows no rule of plan_items.py" % (number, p), False)
	item = "ic" + origin + code + quality
	kind = itemType(item)
	if kind in ("HARPOON", "GRENADE_AMMO", "HARPOON_AMMO"):
		return None, Reason(NO_ITEM_TYPE % { "HARPOON": "harpoon", "GRENADE_AMMO": "grenade ammunition", "HARPOON_AMMO": "harpoon ammunition" }[kind], True)
	return item, None

def plans():
	"""(OrderedDict plan id: item id, dict plan id: reason it makes no item), in the order of the translation"""
	names = englishNames("sbrick")
	made, unmade = OrderedDict(), OrderedDict()
	for planId, row in readWords("sbrick"):
		if not PLAN_ID.match(planId):
			continue
		item, reason = planItem(planId, names.get(planId, ""))
		if item:
			made[planId] = item
		else:
			unmade[planId] = reason
	return made, unmade

def itemPlans():
	"""item id: the plan the item names in CraftPlan. Where two plans make one item (Erouk'an's armor and the
	Marauders' knowledge of it, bcbah? and bcbah?_m), the item names the plan its name belongs to, Erouk'an's"""
	made = plans()[0]
	result = {}
	for planId, item in made.items():
		if item not in result or (result[item].endswith("_m") and not planId.endswith("_m")):
			result[item] = planId
	return result

# ------------------------------------------------------------------------------------------------------- item kinds
MELEE = { "1bm": "MACE", "1bs": "STAFF", "1pd": "DAGGER", "1ps": "SPEAR", "1sa": "AXE", "1ss": "SWORD",
	"2bm": "TWO_HAND_MACE", "2pp": "PIKE", "2sa": "TWO_HAND_AXE", "2ss": "TWO_HAND_SWORD", "2ms": "MAGICIAN_STAFF" }
RANGE_TYPES = { "1b": "BOWPISTOL", "1p": "PISTOL", "2a": "AUTOLAUCH", "2b": "BOWRIFLE", "2l": "LAUNCHER", "2r": "RIFLE",
	"2h": "HARPOON" }
AMMO_TYPES = { "1b": "BOWPISTOL_AMMO", "1p": "PISTOL_AMMO", "2a": "AUTOLAUNCH_AMMO", "2b": "BOWRIFLE_AMMO",
	"2l": "LAUNCHER_AMMO", "2r": "RIFLE_AMMO", "1g": "GRENADE_AMMO", "1h": "HARPOON_AMMO" }
ARMOR_CLASS = { "l": "LIGHT", "c": "LIGHT", "m": "MEDIUM", "h": "HEAVY" } # caster armor is light armor to the code
PIECES = { "b": "BOOTS", "g": "GLOVES", "p": "PANTS", "s": "SLEEVES", "v": "VEST", "h": "HELMET" }
JEWEL_TYPES = { "a": "ANKLET", "b": "BRACELET", "d": "DIADEM", "e": "EARING", "p": "PENDANT", "r": "RING" }
TOOL_TYPES = { "ammo": "AmmoTool", "armor": "ArmorTool", "jewel": "JewelryTool", "mwea": "MeleeWeaponTool",
	"rwea": "RangeWeaponTool", "forage": "SHEARS" }
ORIGIN = r"(?:oka[mr]|ka[mr]|hb|[fmtzcbr])" # hb: the high tribes (ichbm*)

def itemType(item):
	"""the ITEM_TYPE of the code (item_type.cpp) an item id stands for, or None"""
	i = item.lower()
	if i.startswith("ep2_"):
		return "UNDEFINED" # the construction pieces: the code crafts an undefined item type as a mission item
	if i == "ic_candy_stick":
		return "STAFF"
	if i == "pre_order":
		return "BUCKLER"
	m = re.match(r"^ic" + ORIGIN + r"m([12](?:bm|bs|pd|ps|sa|ss|pp|ms))", i)
	if m:
		return MELEE.get(m.group(1))
	m = re.match(r"^ic" + ORIGIN + r"r([12][abplrh])", i)
	if m:
		return RANGE_TYPES.get(m.group(1))
	m = re.match(r"^ic" + ORIGIN + r"p([12][abplrgh])[bps]", i)
	if m:
		return AMMO_TYPES.get(m.group(1))
	m = re.match(r"^ic" + ORIGIN + r"s(s|b)", i)
	if m:
		return "SHIELD" if m.group(1) == "s" else "BUCKLER"
	m = re.match(r"^ic" + ORIGIN + r"j([abdepr])", i)
	if m:
		return JEWEL_TYPES[m.group(1)]
	m = re.match(r"^icoka[mr]t(ammo|armor|jewel|mwea|rwea|forage)_", i)
	if m:
		return TOOL_TYPES[m.group(1)]
	m = re.match(r"^icra[bgpsv][aegrtuvw]$", i) # refugee armor, light to the code
	if m:
		return "LIGHT_" + PIECES[i[4]]
	m = re.match(r"^icral([bgpsv])$", i)
	if m:
		return "LIGHT_" + PIECES[m.group(1)]
	m = re.match(r"^ic[rc]ar([pv])$", i) # refugee light pants and vest, and their common version
	if m:
		return "LIGHT_" + PIECES[m.group(1)]
	m = re.match(r"^ic" + ORIGIN + r"auw?([pv])$", i) # underwear: panties (pants) and bra (vest)
	if m:
		return "LIGHT_" + PIECES[m.group(1)]
	m = re.match(r"^ic" + ORIGIN + r"a([lcmh])([bgpsvh])", i)
	if m:
		if m.group(2) == "h" and m.group(1) != "h":
			return None
		return ARMOR_CLASS[m.group(1)] + "_" + PIECES[m.group(2)]
	return None
