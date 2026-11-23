# The special powers and auras of Ryzom Core, every level up to 250: the roots (bsxpa*), the power effects (BSXEA) and
# aura effects (BSXEB) with their parameters, the disable time credits (bsxca*), the item powers (bsxpa03, BSCEA, BSCM*)
# and the potion variants (bsp*), and the phrases abs*: the ready-made powers and auras rolemasters sell, and the item
# effects (absp_*, absc_*) a consumable item names as its Consumable.EffectPhrase.
#
# What the code does with them (survey_server.md 2, phrase_manager/special_power_phrase.cpp): a phrase whose first brick
# is of the BSXPA type runs at once (executeNoTime), with no Sabrina sum, no skill and no XP; every SP_* property of
# every brick makes one power, which checks and sets its own disable time (forbidPower, by POWERS type) or, for an aura,
# the user's aura disable time and the targets'. SP_RECAST_TIME (the BSXCA credits) is read by the heal power only, so
# only the self heals pay with a credit; the other powers cost no points and carry their disable time themselves.
# The grammar still counts at memorize (checkPhraseValidity), and the composer offers what the roots list.
#
# The client greys a power phrase while the power is disabled, and draws its recast, from the brick flags its bricks
# name with NEEDED_BRICK_FLAG (client_sheets/sbrick_sheet.cpp, sphrase_manager.cpp getRegenTickRange): the server sets
# FLAGS:BRICK_TICK_RANGE:<32 + power type> (BRICK_FLAGS::powerTypeToFlag), the client reads the bit of the flag name.
# The server has no consumer for the tag, the client has. Both numberings agree from Taunt to EnchantWeapon and for
# Aura, and only those are named here (brick_flags.h has ChgCharac..ModForageSuccess before HealHpC, power_types.h the
# reverse, so the consumable power flags do not line up: see the report).

import os, re
import framework
from balancing import common
from balancing import powers as B

OWNS = [ "sbrick/power", "sphrase/power" ]

ATLASES = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ] # in pipeline/install/interfaces

ANY = [ "SF", "SM", "SC", "SH" ] # a power any profession learns: one of the four skill roots

# The power type of every heal of a player: the four self heals share one recast, as the four effect texts share
# "Instantly restores a great number of": a player picks the score he needs, and the instant heals cannot be stacked.
# Heal is the one heal type the brick flags and the powertype words both know (the Concentration types have neither a
# matching flag past the shared numbering nor a powertype_words row).
PLAYER_HEAL_TYPE = "Heal"
# The potion and consumable heals use the consumable types, so the player's own heal on recast does not refuse them
SCORES = {
	"hp": ( "HitPoints", "HealHpC", "ico_heal.png" ),
	"stamina": ( "Stamina", "HealStaC", "ico_stamina.png" ),
	"sap": ( "Sap", "HealSapC", "ico_sap.png" ),
	"focus": ( "Focus", "HealFocusC", "ico_focus.png" ),
}

# The power effects (BSXEA) in their index order, with the parameter family each opens, the brick flag the client
# greys the phrase by, the skills that gate it (the phrase prefix says which rolemaster sells it: bsf fight, bsm magic,
# bsg craft and forage, bsx and bsd any), and the phrases (prefix + two-digit ordinal of the parameter).
POWER_EFFECTS = [
	{ "effect": "bsfea01", "family": "BSFMA", "key": "taunt", "folder": "taunt", "flag": "Taunt", "skills": [ "SF" ],
		"icon": "ico_taunt.png", "phrase": "absf_taunt_", "first": B.FIRST_LEVEL["taunt"] },
	{ "effect": "bsfea02", "family": "BSFMB", "key": "shielding", "folder": "shielding", "flag": "Shielding", "skills": [ "SF" ],
		"icon": "ico_shielding.png", "phrase": "absf_shielding_", "first": B.FIRST_LEVEL["shielding"] },
	{ "effect": "bsdea03", "family": "BSDMA", "key": "speeding_up", "folder": "speeding_up", "flag": "SpeedingUp", "skills": ANY,
		"icon": "ico_speeding_up.png", "phrase": "absx_speeding_up_", "first": B.FIRST_LEVEL["speeding_up"] },
	# the escape power: usable while afraid, asleep or stunned, the states it is for (BYPASS_CHECK)
	{ "effect": "bsxea04", "family": "BSXMB", "key": "invulnerability", "folder": "invulnerability", "flag": "Invulnerability",
		"skills": ANY, "icon": "ico_invulnerability.png", "phrase": "absx_invulnerability_", "first": B.FIRST_LEVEL["invulnerability"],
		"bypass": [ "Fear", "Sleep", "Stun" ] },
	{ "effect": "bsfea05", "family": "BSFMF", "key": "berserk", "folder": "berserk", "flag": "Berserk", "skills": [ "SF" ],
		"icon": "ico_berserk.png", "phrase": "absf_berserk_", "first": B.FIRST_LEVEL["berserk"] },
	# a group heal more than a magic power: the healing branch gates it
	{ "effect": "bsmea06", "family": "BSMMC", "key": "balance_hp", "folder": "balance_hp", "flag": "BalanceHp", "skills": [ "SMDH" ],
		"icon": "ico_balance_hp.png", "phrase": "absm_balance_hp_", "first": B.FIRST_LEVEL["balance_hp"] },
	{ "effect": "bsxea07", "family": "BSXMC", "key": "heal", "score": "hp", "folder": "heal", "flag": "Heal", "skills": ANY,
		"icon": "ico_heal.png", "phrase": "absx_heal_hp_", "potion": "bspxmc", "potionPhrase": "absp_heal_hp_" },
	{ "effect": "bsfea08", "family": "BSFMH", "key": "heal", "score": "stamina", "folder": "heal", "flag": "Heal", "skills": [ "SF" ],
		"icon": "ico_stamina.png", "phrase": "absf_heal_stamina_", "potion": "bspfmh", "potionPhrase": "absp_heal_stamina_" },
	{ "effect": "bsmea09", "family": "BSMMD", "key": "heal", "score": "sap", "folder": "heal", "flag": "Heal", "skills": [ "SM" ],
		"icon": "ico_sap.png", "phrase": "absm_heal_sap_", "potion": "bspmmd", "potionPhrase": "absp_heal_sap_" },
	# focus is the craft and forage resource
	{ "effect": "bsgea10", "family": "BSGMA", "key": "heal", "score": "focus", "folder": "heal", "flag": "Heal", "skills": [ "SC", "SH" ],
		"icon": "ico_focus.png", "phrase": "absg_heal_focus_", "potion": "bspgma", "potionPhrase": "absp_heal_focus_" },
	# the weapon enchantment needs a melee weapon in hand (client and CSpecialPowerEnchantWeapon): melee fighting gates it.
	# No translation row names a phrase for it, so its bricks are made and nothing sells them yet (see the report).
	{ "effect": "bsxea11", "family": "BSGMB", "key": "enchant", "folder": "enchant_weapon", "flag": "EnchantWeapon",
		"skills": [ "SFM" ], "icon": "fp_melee.png", "phrase": None, "first": B.FIRST_LEVEL["enchant"] },
]

# The aura effects (BSXEB) in their index order. The walls are the four "racial auras" of the combat code: each is
# taught by the rolemasters of its civilisation (CivRestriction), fire Fyros, thorns Matis, water Tryker, lightning Zorai.
AURA_EFFECTS = [
	{ "effect": "bsxeb01", "family": "BSXMA", "key": "regen", "tag": "SP_LIFE_AURA", "folder": "aura", "skills": ANY,
		"icon": "ico_heal.png", "phrase": "absx_life_aura_", "first": B.FIRST_LEVEL["regen_aura"] },
	{ "effect": "bsxeb02", "family": "BSFMC", "key": "regen", "tag": "SP_STAMINA_AURA", "folder": "aura", "skills": [ "SF" ],
		"icon": "ico_stamina.png", "phrase": "absf_stamina_aura_", "first": B.FIRST_LEVEL["regen_aura"] },
	{ "effect": "bsxeb03", "family": "BSMMA", "key": "regen", "tag": "SP_SAP_AURA", "folder": "aura", "skills": [ "SM" ],
		"icon": "ico_sap.png", "phrase": "absm_sap_aura_", "first": B.FIRST_LEVEL["regen_aura"] },
	{ "effect": "bsfeb04", "family": "BSFMD", "key": "protection", "tag": "SP_MELEE_PROTECTION_AURA", "folder": "protection",
		"skills": [ "SF" ], "icon": "ico_shielding.png", "phrase": "absf_protection_", "first": B.FIRST_LEVEL["protection"] },
	{ "effect": "bsfeb05", "family": "BSFME", "key": "protection", "tag": "SP_RANGE_PROTECTION_AURA", "folder": "protection",
		"skills": [ "SF" ], "icon": "ico_umbrella.png", "phrase": "absf_umbrella_", "first": B.FIRST_LEVEL["protection"] },
	# the magic afflictions are fear, sleep and stun: the shield against magic is raised under them
	{ "effect": "bsmeb06", "family": "BSMMB", "key": "protection", "tag": "SP_MAGIC_PROTECTION_AURA", "folder": "protection",
		"skills": [ "SM" ], "icon": "ico_anti_magic_shield.png", "phrase": "absm_anti_magic_shield_", "first": B.FIRST_LEVEL["protection"],
		"bypass": [ "Fear", "Sleep", "Stun" ] },
	{ "effect": "bsfeb07", "family": "BSFMG", "key": "war_cry", "tag": "SP_WAR_CRY_AURA", "folder": "war_cry", "skills": [ "SF" ],
		"icon": "ico_war_cry.png", "phrase": "absf_war_cry_", "first": B.FIRST_LEVEL["war_cry"] },
	{ "effect": "bsfeb08", "family": "BSFMI", "key": "fire_wall", "tag": "SP_FIRE_WALL_AURA", "folder": "wall", "skills": [ "SF" ],
		"civ": "fyros", "icon": "ico_fire.png", "phrase": "absf_fire_wall_", "first": B.FIRST_LEVEL["wall"] },
	{ "effect": "bsfeb09", "family": "BSFMJ", "key": "thorn_wall", "tag": "SP_THORN_WALL_AURA", "folder": "wall", "skills": [ "SF" ],
		"civ": "matis", "icon": "ico_poison.png", "phrase": "absf_thorn_wall_", "first": B.FIRST_LEVEL["wall"] },
	{ "effect": "bsfeb10", "family": "BSFMK", "key": "water_wall", "tag": "SP_WATER_WALL_AURA", "folder": "wall", "skills": [ "SF" ],
		"civ": "tryker", "icon": "ico_shockwave.png", "phrase": "absf_water_wall_", "first": B.FIRST_LEVEL["wall"] },
	{ "effect": "bsfeb11", "family": "BSFML", "key": "lightning_wall", "tag": "SP_LIGHTNING_WALL_AURA", "folder": "wall",
		"skills": [ "SF" ], "civ": "zorai", "icon": "ico_electric.png", "phrase": "absf_lightning_wall_", "first": B.FIRST_LEVEL["wall"] },
]

# The weapon enchantment: bsgmb01..07 choose the element and open its strength family, in the order of the families
# in brick_families.h; the code's damage type names (damage_types.cpp: SHOCK, not SHOCKWAVE)
ENCHANT_ELEMENTS = [
	( "BSGMBA", "ACID", "ico_acid.png" ),
	( "BSGMBC", "COLD", "ico_cold.png" ),
	( "BSGMBE", "ELECTRICITY", "ico_electric.png" ),
	( "BSGMBF", "FIRE", "ico_fire.png" ),
	( "BSGMBP", "POISON", "ico_poison.png" ),
	( "BSGMBR", "ROT", "ico_rot.png" ),
	( "BSGMBS", "SHOCK", "ico_shockwave.png" ),
]

# The item powers: bsxpa03 opens the consumable effects, each of which opens its score's consumable heal, in the order
# of the consumable power types (power_types.h: HealHpC, HealSapC, HealStaC, HealFocusC); the translation rows are <GEN>
CONSUMABLE = [ ( "bscea01", "BSCMA", "hp" ), ( "bscea02", "BSCMB", "sap" ), ( "bscea03", "BSCMC", "stamina" ), ( "bscea04", "BSCMD", "focus" ) ]

# ---------------------------------------------------------------------------------------------------------- helpers
def num(v):
	"""a property argument: whole numbers without decimals, as the client prints them"""
	if isinstance(v, float):
		if v.is_integer():
			return str(int(v))
		return ("%.3f" % v).rstrip("0").rstrip(".")
	return str(v)

def prop(tag, *args):
	return tag + ": " + ":".join(num(a) for a in args)

def ordinal(sheetId):
	return int(re.search(r"(\d+)$", sheetId).group(1))

def familyIds(gen, prefix):
	"""the ids prefix<two digits> of the translation, by number (the bsp* variants have their own prefix)"""
	ids = gen.sbrickWords.ids("^" + prefix + r"\d\d$")
	return sorted(ids, key=ordinal)

def learn(skills, level):
	return { "LearnRequiresOneOfSkills": common.learnRequires(skills, level), "SPCost": B.spCost(level) }

def loadAtlas(gen):
	"""the icon names of the interface atlases (framework.atlasNames: a list that is missing stops the run, naming its
	path and the --atlas option of generate.py)"""
	return framework.atlasNames()

def textNumber(gen, sheetId, pattern, what):
	"""a number the English text of a brick states, which is the spec of the value"""
	row = gen.sbrickWords.get(sheetId)
	m = re.search(pattern, row.description if row else "")
	if not m:
		gen.error("powers: the text of " + sheetId + " no longer states " + what + " (\"" + (row.description if row else "") + "\")")
		return None
	return m

# ---------------------------------------------------------------------------------------------------------- generate
def generate(gen):
	atlas = loadAtlas(gen)
	made = []

	def brick(name, folder, source, parent, **fields):
		if not gen.sbrickWords.get(name):
			gen.error("powers: " + name + " has no row in the translation")
		b = gen.brick(name, folder, source, parent=parent, **fields)
		made.append(b)
		return b

	def parent(name, folder, parentSheet=None, **fields):
		p = gen.parent(name, folder, parent=parentSheet, **fields)
		made.append(p)
		return p

	def phrase(name, folder, bricks, source, **flags):
		if not gen.sphraseWords.get(name):
			gen.error("powers: the phrase " + name + " has no row in the translation")
			return
		gen.phrase(name, folder, bricks, source, **flags)

	# Every power brick runs at once: no cast time. The client shows the smallest range of a phrase's bricks (0 is
	# "Self"), so the roots, effects and credits are out of the way at 255 and each parameter states its own.
	top = parent("_bs_power", "sbrick/power", basics={ "SabrinaCost": 0, "MinCastTime": 0, "MaxCastTime": 0, "MinRange": 255, "MaxRange": 255 })

	# ---- roots
	rootParent = parent("_bsxpa", "sbrick/power/root", top, basics={ "FamilyId": "BSXPA" })
	firstAura = min(a["first"] for a in AURA_EFFECTS)
	brick("bsxpa01", "sbrick/power/root", "power root", rootParent,
		basics=dict({ "IndexInFamily": 1, "Level": 1 }, **learn(ANY, 1)),
		client={ "Icon": "bk_power.png", "IconBack": "bk_power.png" },
		mandatory=[ "BSXEA" ], credit=[ "BSXCA" ])
	# every aura shares the user's aura disable time, which the server writes on the Aura flag
	brick("bsxpa02", "sbrick/power/root", "aura root", rootParent,
		basics=dict({ "IndexInFamily": 2, "Level": firstAura }, **learn(ANY, firstAura)),
		properties=[ prop("NEEDED_BRICK_FLAG", "Aura") ],
		client={ "Icon": "bk_aura.png", "IconBack": "bk_aura.png" },
		mandatory=[ "BSXEB" ])
	# the item powers: only an item's EffectPhrase runs them, nobody learns them
	brick("bsxpa03", "sbrick/power/root", "item power root", rootParent,
		basics={ "IndexInFamily": 3, "Level": 1 },
		client={ "Icon": "bk_conso.png", "IconBack": "bk_conso.png" },
		mandatory=[ "BSCEA" ])

	# ---- disable time credits: they pay a self heal of their level with its recast
	creditParent = parent("_bsxca", "sbrick/power/credit", top, basics={ "FamilyId": "BSXCA" },
		client={ "Icon": "ico_time.png", "IconBack": "cp_back.png", "IconOver": "cp_over_more.png" })
	credits = familyIds(gen, "bsxca")
	for c in credits:
		level = B.healGrid(ordinal(c))
		brick(c, "sbrick/power/credit", "disable time credit", creditParent,
			basics=dict({ "IndexInFamily": ordinal(c), "Level": level, "SabrinaCost": B.sabrinaCredit(level) }, **learn(ANY, level)),
			properties=[ prop("SP_RECAST_TIME", float(B.healRecast(level))) ])

	# ---- power effects and their parameters
	effectParent = parent("_bsxea", "sbrick/power/effect", top, basics={ "FamilyId": "BSXEA" }, client={ "IconBack": "ef_back.png" })
	shieldingRange = textNumber(gen, "bsfea02", r"less than (\d+) meters", "the shielding range")
	shieldingRange = int(shieldingRange.group(1)) if shieldingRange else 0
	for p in POWER_EFFECTS:
		ids = familyIds(gen, p["family"].lower())
		if p["key"] == "heal":
			levels = [ B.healGrid(ordinal(i)) for i in ids ]
		elif p["key"] == "enchant":
			levels = None
		else:
			levels = B.spread(len(ids), p["first"])
		first = levels[0] if levels else p["first"]
		properties = [ prop("NEEDED_BRICK_FLAG", p["flag"]) ] + [ prop("BYPASS_CHECK", f) for f in p.get("bypass", []) ]
		brick(p["effect"], "sbrick/power/effect", "power effect " + p["family"], effectParent,
			basics=dict({ "IndexInFamily": ordinal(p["effect"]), "Level": first }, **learn(p["skills"], first)),
			properties=properties, client={ "Icon": p["icon"] }, parameter=[ p["family"] ])
		folder = "sbrick/power/" + p["folder"]
		fam = parent("_" + p["family"].lower(), folder, top, basics={ "FamilyId": p["family"] },
			client={ "Icon": p["icon"], "IconBack": "pa_back.png", "IconOver": "pa_over_more.png" })
		if p["key"] == "enchant":
			makeEnchant(gen, brick, parent, top, p, folder, ids, fam)
			continue
		if not ids:
			gen.error("powers: the translation has no id of the family " + p["family"])
			continue
		for sheetId, level in zip(ids, levels):
			basics = dict({ "IndexInFamily": ordinal(sheetId), "Level": level }, **learn(p["skills"], level))
			range_ = 0
			if p["key"] == "taunt":
				properties = [ prop("SP_TAUNT", B.tauntPower(level), float(B.TAUNT_RANGE), float(B.tauntDisable(level))) ]
				range_ = B.TAUNT_RANGE
			elif p["key"] == "shielding":
				properties = [ prop("SP_SHIELDING", B.shieldingFactor(level, "none"), B.shieldingMax(level, "none"),
					B.shieldingFactor(level, "buckler"), B.shieldingMax(level, "buckler"),
					B.shieldingFactor(level, "shield"), B.shieldingMax(level, "shield"),
					float(B.shieldingDuration(level)), float(B.shieldingDisable(level))) ]
				range_ = shieldingRange
			elif p["key"] == "speeding_up":
				properties = [ prop("SP_SPEEDING_UP", B.SPEEDING_UP_MOD, float(B.speedingUpDuration(level)), float(B.speedingUpDisable(level))) ]
			elif p["key"] == "invulnerability":
				properties = [ prop("SP_INVULNERABILITY", float(B.immunityDuration(level)), float(B.invulnerabilityDisable(level))) ]
			elif p["key"] == "berserk":
				properties = [ prop("SP_BERSERK", float(B.berserkDisable(level)), float(B.berserkDuration(level)), float(B.berserkBleed(level)),
					float(B.BERSERK_TICK), B.berserkBonus(level)) ]
			elif p["key"] == "balance_hp":
				m = textNumber(gen, sheetId, r"(with a (\d+)% loss|without any loss)", "its loss")
				loss = (int(m.group(2)) if m.group(2) else 0) if m else 0
				properties = [ prop("SP_BALANCE", float(B.balanceDisable(level)), "HitPoints", float(B.auraRadius(level)), float(loss)) ]
				range_ = B.auraRadius(level)
			elif p["key"] == "heal":
				basics["SabrinaCost"] = B.sabrinaCost(level)
				properties = [ prop("SP_HEAL", SCORES[p["score"]][0], B.healValue(level), 0.0, 0.0, PLAYER_HEAL_TYPE) ]
			basics["MinRange"] = basics["MaxRange"] = range_
			brick(sheetId, folder, "power " + p["family"], fam, basics=basics, properties=properties)
			if p["phrase"]:
				bricks = [ "bsxpa01", p["effect"], sheetId ]
				if p["key"] == "heal":
					bricks.append("bsxca%02d" % ordinal(sheetId)) # the credit of the same level pays the heal
				phrase(p["phrase"] + "%02d" % ordinal(sheetId), "sphrase/power/power", bricks, "power " + p["family"])
		# the potion variants: indexed from 63 down in the same family, run by items, never learnt
		if p.get("potion"):
			for sheetId in familyIds(gen, p["potion"]):
				n = ordinal(sheetId)
				level = B.potionHealGrid(n)
				brick(sheetId, "sbrick/power/potion", "potion " + p["family"], fam,
					basics={ "IndexInFamily": 64 - n, "Level": level, "MinRange": 0, "MaxRange": 0 },
					properties=[ prop("SP_HEAL", SCORES[p["score"]][0], B.potionHealValue(level), 0.0, 0.0, SCORES[p["score"]][1]) ])
		elif p["key"] in ( "invulnerability", "speeding_up" ):
			# SP_INVULNERABILITY and SP_SPEEDING_UP take no power type (special_power_phrase.cpp): these potions are the
			# player's own Invulnerability and SpeedingUp powers. The power's recast refuses the potion, and the potion
			# holds the power back for its own duration (the code forbids the type for disable time + duration; the
			# disable time here is 0). Kept so, on purpose: a shared timer is what stops a player from chaining his
			# invulnerability with potions, and it keeps two speed effects from stacking. No item names them yet; a
			# potion with a timer of its own needs a power type argument in the code first.
			potionPrefix = "bsp" + p["family"][2:].lower()
			for sheetId in familyIds(gen, potionPrefix):
				n = ordinal(sheetId)
				level = B.potionGrid(n)
				if p["key"] == "invulnerability":
					properties = [ prop("SP_INVULNERABILITY", float(B.immunityDuration(level)), 0.0) ]
				else:
					properties = [ prop("SP_SPEEDING_UP", B.SPEEDING_UP_MOD, float(B.speedingUpDuration(level)), 0.0) ]
				brick(sheetId, "sbrick/power/potion", "potion " + p["family"], fam,
					basics={ "IndexInFamily": 64 - n, "Level": level, "MinRange": 0, "MaxRange": 0 }, properties=properties)
				phrase("absp_" + p["key"] + "_%02d" % n, "sphrase/power/item", [ "bsxpa01", p["effect"], sheetId ], "potion " + p["family"],
					usableByPlayer=False, showInActionProgression=False)
	# the potion heal phrases: the ids say which of the 25 potion levels have one
	for p in POWER_EFFECTS:
		if not p.get("potionPhrase"):
			continue
		for name in gen.sphraseWords.ids("^" + p["potionPhrase"] + r"\d\d$"):
			n = ordinal(name)
			sheetId = p["potion"] + "%02d" % n
			phrase(name, "sphrase/power/item", [ "bsxpa01", p["effect"], sheetId ], "potion " + p["family"],
				usableByPlayer=False, showInActionProgression=False)

	# ---- aura effects and their parameters
	auraParent = parent("_bsxeb", "sbrick/power/effect", top, basics={ "FamilyId": "BSXEB" }, client={ "IconBack": "ef_back.png" })
	for a in AURA_EFFECTS:
		ids = familyIds(gen, a["family"].lower())
		levels = B.spread(len(ids), a["first"])
		civ = { "CivRestriction": a["civ"] } if a.get("civ") else {}
		brick(a["effect"], "sbrick/power/effect", "aura effect " + a["family"], auraParent,
			basics=dict(dict({ "IndexInFamily": ordinal(a["effect"]), "Level": levels[0] }, **learn(a["skills"], levels[0])), **civ),
			properties=[ prop("BYPASS_CHECK", f) for f in a.get("bypass", []) ], client={ "Icon": a["icon"] }, parameter=[ a["family"] ])
		folder = "sbrick/power/" + a["folder"]
		fam = parent("_" + a["family"].lower(), folder, top, basics=dict({ "FamilyId": a["family"], "MinRange": 0, "MaxRange": 0 }, **civ),
			client={ "Icon": a["icon"], "IconBack": "pa_back.png", "IconOver": "pa_over_more.png" })
		for sheetId, level in zip(ids, levels):
			radius = float(B.auraRadius(level))
			properties = []
			if a["key"] == "regen":
				properties = [ prop(a["tag"], B.regenAuraMod(level), float(B.REGEN_AURA_DURATION), radius,
					float(B.regenAuraTargetDisable(level)), float(B.regenAuraUserDisable(level))) ]
			elif a["key"] == "protection":
				disable = float(B.protectionDisable(level))
				properties = [ prop(a["tag"], radius, float(B.immunityDuration(level)), disable, disable) ]
			else:
				disable = float(B.teamAuraDisable(level))
				value = { "war_cry": B.warCryBonus, "fire_wall": B.fireWallDamage, "thorn_wall": B.thornWallSlow,
					"water_wall": B.waterWallAbsorb, "lightning_wall": B.lightningWallDebuff }[a["key"]](level)
				properties = [ prop(a["tag"], radius, float(B.TEAM_AURA_DURATION), disable, disable, value) ]
				if a["key"] == "thorn_wall":
					properties.append(prop("INFO", value)) # the text's $INFO (client only): the slow, the wall's value
			brick(sheetId, folder, "aura " + a["family"], fam,
				basics=dict({ "IndexInFamily": ordinal(sheetId), "Level": level }, **learn(a["skills"], level)), properties=properties)
			phrase(a["phrase"] + "%02d" % ordinal(sheetId), "sphrase/power/aura", [ "bsxpa02", a["effect"], sheetId ], "aura " + a["family"])

	# ---- item powers: consumable heals of a share of the user's own maximum
	consumableParent = parent("_bscea", "sbrick/power/effect", top, basics={ "FamilyId": "BSCEA" }, client={ "IconBack": "ef_back.png" })
	for effect, family, score in CONSUMABLE:
		scoreName, powerType, icon = SCORES[score]
		brick(effect, "sbrick/power/effect", "consumable effect " + family, consumableParent,
			basics={ "IndexInFamily": ordinal(effect), "Level": 1 }, client={ "Icon": icon }, parameter=[ family ])
		fam = parent("_" + family.lower(), "sbrick/power/consumable", top, basics={ "FamilyId": family, "MinRange": 0, "MaxRange": 0 },
			client={ "Icon": icon, "IconBack": "pa_back.png", "IconOver": "pa_over_more.png" })
		for sheetId in familyIds(gen, family.lower()):
			brick(sheetId, "sbrick/power/consumable", "consumable " + family, fam,
				basics={ "IndexInFamily": ordinal(sheetId), "Level": 1 },
				properties=[ prop("SP_HEAL", scoreName, 0, float(B.CONSUMABLE_HEAL_PERCENT), 0.0, powerType) ])
			name = "absc_heal_" + score + "_%02d" % ordinal(sheetId)
			phrase(name, "sphrase/power/item", [ "bsxpa03", effect, sheetId ], "consumable " + family,
				usableByPlayer=False, showInActionProgression=False)

	checks(gen, made, atlas)

def makeEnchant(gen, brick, parent, top, p, folder, ids, fam):
	"""bsxea11 opens BSGMB, whose bricks choose the element and open its strengths"""
	if len(ids) != len(ENCHANT_ELEMENTS):
		gen.error("powers: BSGMB has %d ids in the translation, the enchantment knows %d elements" % (len(ids), len(ENCHANT_ELEMENTS)))
		return
	first = B.ENCHANT_LEVELS[0]
	for sheetId, (family, damageType, icon) in zip(ids, ENCHANT_ELEMENTS):
		brick(sheetId, folder, "enchant weapon element " + family, fam,
			basics=dict({ "IndexInFamily": ordinal(sheetId), "Level": first, "MinRange": 0, "MaxRange": 0 }, **learn(p["skills"], first)),
			client={ "IconOver2": icon }, parameter=[ family ])
		strength = parent("_" + family.lower(), folder, top, basics={ "FamilyId": family, "MinRange": 0, "MaxRange": 0 },
			client={ "Icon": p["icon"], "IconBack": "pa_back.png", "IconOver": "pa_over_more.png", "IconOver2": icon })
		strengths = familyIds(gen, family.lower())
		if len(strengths) != len(B.ENCHANT_LEVELS):
			gen.error("powers: %s has %d ids, the balancing has %d enchantment levels" % (family, len(strengths), len(B.ENCHANT_LEVELS)))
			continue
		for s, level in zip(strengths, B.ENCHANT_LEVELS):
			dps = B.enchantDps(level)
			brick(s, folder, "enchant weapon " + family, strength,
				basics=dict({ "IndexInFamily": ordinal(s), "Level": level }, **learn(p["skills"], level)),
				properties=[ prop("SP_ENCHANT_WEAPON", float(B.enchantDisable(level)), float(B.enchantDuration(level)), damageType,
					dps, int(round(dps))) ])
	gen.note("powers: the weapon enchantment bricks (bsxea11, BSGMB*) have no phrase in the translation, so no rolemaster sells them")

# ----------------------------------------------------------------------------------------------------------- checks
ENUM_ARGS = {
	# tag: (argument index, code table, what), the strings the server converts and silently turns unknown
	"sp_heal": [ (0, "scores:TScores:stringTable", "score"), (4, "power_types:TPowerType", "power type") ],
	"sp_balance": [ (1, "scores:TScores:stringTable", "score") ],
	"sp_enchant_weapon": [ (2, "damage_types:EDamageType", "damage type") ],
	"bypass_check": [ (0, "bypass_check_flags:TCheckFlagType", "check flag") ],
	"needed_brick_flag": [ (0, "brick_flags:TBrickFlag", "brick flag") ],
}

def checks(gen, made, atlas):
	powerTypes = framework.table("power_types:TPowerType")
	lastShared = powerTypes.index("EnchantWeapon")
	for s in made:
		basics, properties, client, grammar, faber = s.effective()
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("powers: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
		for p in properties:
			keyword, sep, tail = p.partition(":")
			keyword = keyword.strip().lower()
			args = tail.strip().split(":")
			for index, key, what in ENUM_ARGS.get(keyword, []):
				if index < len(args) and not framework.tableHas(key, args[index]):
					gen.error("powers: " + s.name + ": '" + p + "' names the " + what + " " + args[index] + ", which the code does not know (" + key + ")")
			# the flag the client watches must be the slot the server writes: the numberings agree up to EnchantWeapon
			if keyword == "needed_brick_flag" and args[0] != "Aura" and (args[0] not in powerTypes or powerTypes.index(args[0]) > lastShared):
				gen.error("powers: " + s.name + ": the brick flag " + args[0] + " is not one where BRICK_FLAGS and POWERS agree (Taunt to EnchantWeapon, Aura)")
		if not s.isParent:
			checkText(gen, s, properties)

def checkText(gen, brick, properties):
	"""every $ token of the brick's texts names a property the brick has, with an argument it has"""
	row = gen.sbrickWords.get(brick.name)
	if not row:
		return
	args = {}
	for p in properties:
		keyword, sep, tail = p.partition(":")
		args[keyword.strip().lower()] = len(tail.split(":"))
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
