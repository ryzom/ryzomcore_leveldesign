# The magic of Ryzom Core, every level up to 250: the spell plans (roots BMPA), the effects (BM??EA, the mandatory
# bricks), their parameters (BM??M?, the bricks that carry the values and the level), the options (area BMOF BMOG BMOH,
# concentration BMOR, vampirism BMOV), the credits (sap BMCA, life BMCP, casting time BMCC, range BMCR), the ready-made
# spells abm_mt_* and abm_ml_*, the phrases that teach one brick (abm<parameter>, abm_<option>_*, abm_credit_*, the
# plans abm_double_* ...) and the Magic Start of the craft, fight and forage roles.
#
# What the code does with them (survey_server.md 3 and 4, phrase_manager/magic_phrase.cpp, magic_action_*.cpp):
# - the first brick picks the magic phrase class; a brick whose first property is MA:<type> opens an effect, which takes
#   that brick and the next ones up to the brick that holds MA_END (the rest of that brick is not read). Here the
#   parameter brick, with its family's parent, holds the whole effect: MA:<type>, the effect's tags, SET_BEHAVIOUR,
#   MA_END. The cast animation comes from the costliest brick's SET_BEHAVIOUR and a brick that costs nothing cannot set
#   it, so it belongs on the parameter, the brick that costs;
# - the action's skill is the MA brick's or, looking back, the effect brick's: the effect brick carries the skill (a
#   magic mandatory brick without one fails the build), the leaf of its branch, so the focus bonus (the first four
#   letters SMOE SMOA SMDA SMDH) applies and the XP goes to the nearest unlocked skill. No other brick carries a skill:
#   the success roll averages the skills of every brick, and a root or credit on SM (at most 20) would drag it down;
# - a phrase's nature comes from its bricks (two different ones make it NEUTRAL), and the client picks the success table
#   from the root's: the root and the effect carry the same nature, the other bricks none;
# - the cast time is the bricks' largest MinCastTime plus a share of the window up to MaxCastTime that the casting time
#   credit buys, the range the smallest MaxRange minus the share the range credit buys (balancing/magic.py says why
#   every brick carries the same MaxCastTime and MinRange).
# Heal over time (MA:mlc) and cure (MA:mtcb) are built again in the code, but no translated family names them: this
# domain makes none (no id is invented). MA:mlosmp only lowers the speed: it is the slow movement spell.

import os, re
import framework
from balancing import common
from balancing import magic as B

OWNS = [ "sbrick/magic", "sphrase/magic" ]

ATLASES = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ] # in pipeline/install/interfaces

CREDIT_FAMILIES = [ "BMCA", "BMCP", "BMCC", "BMCR" ]
# The plans whose spells make energy (heals, gifts, the crystal's sap load) take only the credits that cost energy: a
# casting time or range credit costs none, so a heal it paid would make hit points from nothing (balancing/magic.py,
# no energy loops)
ENERGY_CREDIT_FAMILIES = [ "BMCA", "BMCP" ]
AREA_OPTIONS = [ "BMOF", "BMOG", "BMOH" ]
# vampirism works on the direct damage action only: a drain link keeps the vampirism of its own effect group, and an
# option brick comes after the group's MA_END (CMagicActionDot), so it is offered with the plans that hold a missile.
# It is capped per target and action (CMagicActionBasicDamage::applyOnEntity), so with an area it would take back its
# cap from every target: an area option and vampirism exclude each other, and so do two area options (the phrase
# builds one area, the first, and the second's AREA_TARGETS would overwrite the first's)
DAMAGE_OPTIONS = AREA_OPTIONS + [ "BMOV", "BMOR" ]
TARGET_OPTIONS = AREA_OPTIONS + [ "BMOR" ]
# the heal plans take no area: an area gives up to sqrt(8) times the amount for half its level in cost, which would let
# a heal paid with life return more hit points than it costs
CURATIVE_OPTIONS = [ "BMOR" ]
SELF_OPTIONS = [ "BMOR" ]
AREA_WORD, VAMPIRISM_WORD = "MagicArea", "MagicVampirism" # ForbiddenDef / ForbiddenExclude words

# The plans, BMPA01 to BMPA16, from their texts. mandatory: the effect families of the spell (twice the same for the
# double plans; the code allows a family twice); branch: the skill branch of the learn gate; link: an effect that is a
# link (the over icon). The four self plans share the one self effect family the code has: a root cannot be held to
# one effect of a family without ForbiddenDef/ForbiddenExclude, which the client's composer does not apply to the root,
# so each of them makes every self spell and the ready-made spells use the plan their text names.
ROOTS = {
	1: { "mandatory": [ "BMOETEA" ], "options": DAMAGE_OPTIONS, "kind": "offensive", "branch": "SMOE" },
	2: { "mandatory": [ "BMOELEA" ], "options": TARGET_OPTIONS, "kind": "offensive", "branch": "SMOE", "link": True },
	3: { "mandatory": [ "BMOALEA" ], "options": TARGET_OPTIONS, "kind": "offensive", "branch": "SMOA", "link": True },
	4: { "mandatory": [ "BMDHTEA" ], "options": CURATIVE_OPTIONS, "kind": "curative", "branch": "SMDH" },
	# fear, sleep and stun are cast on an enemy: offensive in nature (the action validates its target as offensive)
	5: { "mandatory": [ "BMDALEA" ], "options": TARGET_OPTIONS, "kind": "celestial", "branch": "SMDA", "link": True },
	6: { "mandatory": [ "BMSTEA" ], "options": SELF_OPTIONS, "kind": "self", "branch": "SMDH" },
	7: { "mandatory": [ "BMOETEA", "BMOETEA" ], "options": DAMAGE_OPTIONS, "kind": "offensive", "branch": "SMO", "double": True },
	8: { "mandatory": [ "BMOETEA", "BMOELEA" ], "options": DAMAGE_OPTIONS, "kind": "offensive", "branch": "SMO", "double": True, "link": True },
	9: { "mandatory": [ "BMOETEA", "BMOALEA" ], "options": DAMAGE_OPTIONS, "kind": "offensive", "branch": "SMO", "double": True, "link": True },
	10: { "mandatory": [ "BMOELEA", "BMOELEA" ], "options": TARGET_OPTIONS, "kind": "offensive", "branch": "SMO", "double": True, "link": True },
	11: { "mandatory": [ "BMOELEA", "BMOALEA" ], "options": TARGET_OPTIONS, "kind": "offensive", "branch": "SMO", "double": True, "link": True },
	12: { "mandatory": [ "BMDHTEA", "BMDHTEA" ], "options": CURATIVE_OPTIONS, "kind": "curative", "branch": "SMD", "double": True },
	13: { "mandatory": [ "BMSTEA", "BMSTEA" ], "options": SELF_OPTIONS, "kind": "self", "branch": "SMDH", "double": True },
	14: { "mandatory": [ "BMSTEA" ], "options": SELF_OPTIONS, "kind": "self", "branch": "SMDH" },
	15: { "mandatory": [ "BMSTEA" ], "options": SELF_OPTIONS, "kind": "self", "branch": "SMDH" },
	# the crystal: RECHARGE halves the cast time (CMagicPhrase::execute) and gives no XP, as making a crystal is no fight
	16: { "mandatory": [ "BMSTEA" ], "options": SELF_OPTIONS, "kind": "recharge", "branch": "SMDH" },
}
ENERGY_KINDS = ( "curative", "self", "recharge" ) # the plans that take only ENERGY_CREDIT_FAMILIES
ROOT_LOOK = {
	# kind: nature, icon, background, self only
	"offensive": ( "OFFENSIVE_MAGIC", "ico_atysian.png", "mp_back_offensive.png", False ),
	"celestial": ( "OFFENSIVE_MAGIC", "ico_celestial.png", "mp_back_offensive.png", False ),
	"curative": ( "CURATIVE_MAGIC", "ico_celestial.png", "mp_back_curative.png", False ),
	"self": ( "CURATIVE_MAGIC", "ico_primal.png", "mp_back_selfonly.png", True ),
	"recharge": ( "RECHARGE", "ico_primal.png", "mp_back_selfonly.png", True ),
}
LINK_OVER = "mp_over_link.png"

# The elements, in the order of the effect numbers 01 to 07 (BMOETEA01 Acid Damage ... BMOETEA07 Shockwave Damage):
# the parameter family letter, the word the texts use, MA_DMG_TYPE, the icon, the cast animation
ELEMENTS = [
	( "A", "Acid", "ACID", "ico_acid.png", "CAST_ACID" ),
	( "C", "Cold", "COLD", "ico_cold.png", "CAST_COLD" ),
	( "R", "Rot", "ROT", "ico_rot.png", "CAST_ROT" ),
	( "E", "Electricity", "ELECTRICITY", "ico_electric.png", "CAST_ELEC" ),
	( "F", "Fire", "FIRE", "ico_fire.png", "CAST_FIRE" ),
	( "P", "Poison", "POISON", "ico_poison.png", "CAST_POISON" ),
	( "S", "Shockwave", "SHOCK", "ico_shockwave.png", "CAST_SHOCK" ),
]

# The effect families: skill (the leaf of the branch), nature, folder; their members: effect number, parameter family,
# effect spec. The spec says which MA type the parameter builds and with what.
def effectTable():
	t = {}
	t["BMOETEA"] = { "skill": "SMOEAEM", "nature": "OFFENSIVE_MAGIC", "folder": "direct_damage", "members": [] }
	t["BMOELEA"] = { "skill": "SMOEAEM", "nature": "OFFENSIVE_MAGIC", "folder": "drain", "members": [] }
	for i, (letter, word, dmgType, icon, behaviour) in enumerate(ELEMENTS):
		t["BMOETEA"]["members"].append(( i + 1, "BMOETM" + letter, { "ma": "moet", "word": word, "dmgType": dmgType, "icon": icon, "behaviour": behaviour } ))
		t["BMOELEA"]["members"].append(( i + 1, "BMOELM" + letter, { "ma": "moel", "word": word, "dmgType": dmgType, "icon": icon, "behaviour": behaviour } ))
	# fear, sleep and stun take their effect from being there: their link carries no strength (MA_EFFECT_MOD has no use)
	t["BMDALEA"] = { "skill": "SMDAAEM", "nature": "OFFENSIVE_MAGIC", "folder": "affliction", "members": [
		( 1, "BMDALMF", { "ma": "mdal", "effect": "Fear", "icon": "ico_fear.png", "behaviour": "CAST_FEAR" } ),
		( 2, "BMDALMM", { "ma": "mdal", "effect": "Mezz", "icon": "ico_mezz.png", "behaviour": "CAST_SLEEP" } ),
		( 3, "BMDALMS", { "ma": "mdal", "effect": "Stun", "icon": "ico_stunn.png", "behaviour": "CAST_STUN" } ) ] }
	# blind and madness: chance in percent; slow attack: percent added to the attack and casting time (CCombatPhrase,
	# CMagicPhrase::execute); root needs no strength; slow movement is a speed link (MA:mlosmp, a negative percent)
	t["BMOALEA"] = { "skill": "SMOAAEM", "nature": "OFFENSIVE_MAGIC", "folder": "affliction", "members": [
		( 1, "BMOALMB", { "ma": "moal", "effect": "Blind", "strength": B.AFFLICTION_STRENGTH, "icon": "ico_blind.png", "behaviour": "CAST_BLIND" } ),
		( 2, "BMOALMR", { "ma": "moal", "effect": "Root", "icon": "ico_root.png", "behaviour": "CAST_ROOT" } ),
		( 3, "BMOALMD", { "ma": "moal", "effect": "Madness", "strength": B.AFFLICTION_STRENGTH, "icon": "ico_madness.png", "behaviour": "CAST_MAD" } ),
		( 4, "BMOALMA", { "ma": "moal", "effect": "SlowAttack", "strength": B.AFFLICTION_STRENGTH, "icon": "ico_slow.png", "behaviour": "CAST_SLOW" } ),
		( 5, "BMOALMM", { "ma": "mlosmp", "effect": "SlowMove", "strength": -B.AFFLICTION_STRENGTH, "icon": "ico_slow.png", "behaviour": "CAST_SLOW" } ) ] }
	t["BMDHTEA"] = { "skill": "SMDHAEM", "nature": "CURATIVE_MAGIC", "folder": "heal", "members": [
		( 1, "BMDHTMP", { "ma": "mdht", "score": 0, "amount": B.heal, "icon": "ico_heal.png", "behaviour": "CAST_HEALHP" } ),
		( 2, "BMDHTMA", { "ma": "mdht", "score": 1, "amount": B.gift, "icon": "ico_sap.png", "behaviour": "CAST_CUR" } ),
		( 3, "BMDHTMT", { "ma": "mdht", "score": 2, "amount": B.gift, "icon": "ico_stamina.png", "behaviour": "CAST_CUR" } ) ] }
	# self magic trains the healing branch (design.md 9); the crystal is made by the sap recharge effect, whose upgrade
	# phrase abmstmc00005 calls BMSTMC its power stanza
	t["BMSTEA"] = { "skill": "SMDHAEM", "nature": "CURATIVE_MAGIC", "folder": "self", "self": True, "members": [
		( 1, "BMSTMP", { "ma": "mdht", "score": 0, "amount": B.selfHeal, "icon": "ico_heal.png", "behaviour": "CAST_HEALHP" } ),
		( 2, "BMSTMA", { "ma": "mdht", "score": 1, "amount": B.selfGift, "icon": "ico_sap.png", "behaviour": "CAST_CUR" } ),
		( 3, "BMSTMT", { "ma": "mdht", "score": 2, "amount": B.selfGift, "icon": "ico_stamina.png", "behaviour": "CAST_CUR" } ),
		( 4, "BMSTMC", { "ma": "reload", "nature": "RECHARGE", "icon": "ico_create_sapload.png", "behaviour": "CAST_MIX" } ) ] }
	return t

# The ready-made spells: the phrase id before its level, the plan, the effect, the parameter family, the credit that
# pays. The credit is the one the text names (life gift, the gifts and the self gifts "use some of your hit points",
# the self heal is "in exchange for some sap"), sap for the others; one credit of the spell's level pays its cost.
SPELLS = [
	( "abm_mt_acid", 1, "bmoetea01", "BMOETMA", "BMCA" ),
	( "abm_mt_cold", 1, "bmoetea02", "BMOETMC", "BMCA" ),
	( "abm_mt_rot", 1, "bmoetea03", "BMOETMR", "BMCA" ),
	( "abm_mt_electric", 1, "bmoetea04", "BMOETME", "BMCA" ),
	( "abm_mt_fire", 1, "bmoetea05", "BMOETMF", "BMCA" ),
	( "abm_mt_poison", 1, "bmoetea06", "BMOETMP", "BMCA" ),
	( "abm_mt_shockwave", 1, "bmoetea07", "BMOETMS", "BMCA" ),
	( "abm_ml_acid", 2, "bmoelea01", "BMOELMA", "BMCA" ),
	( "abm_ml_cold", 2, "bmoelea02", "BMOELMC", "BMCA" ),
	( "abm_ml_rot", 2, "bmoelea03", "BMOELMR", "BMCA" ),
	( "abm_ml_electric", 2, "bmoelea04", "BMOELME", "BMCA" ),
	( "abm_ml_fire", 2, "bmoelea05", "BMOELMF", "BMCA" ),
	( "abm_ml_poison", 2, "bmoelea06", "BMOELMP", "BMCA" ),
	( "abm_ml_shockwave", 2, "bmoelea07", "BMOELMS", "BMCA" ),
	( "abm_ml_blind", 3, "bmoalea01", "BMOALMB", "BMCA" ),
	( "abm_ml_root", 3, "bmoalea02", "BMOALMR", "BMCA" ),
	( "abm_ml_madness", 3, "bmoalea03", "BMOALMD", "BMCA" ),
	( "abm_ml_slow_attack", 3, "bmoalea04", "BMOALMA", "BMCA" ),
	( "abm_ml_slow_move", 3, "bmoalea05", "BMOALMM", "BMCA" ),
	( "abm_mt_heal", 4, "bmdhtea01", "BMDHTMP", "BMCA" ),
	( "abm_mt_life_gift", 4, "bmdhtea01", "BMDHTMP", "BMCP" ),
	( "abm_mt_sap_gift", 4, "bmdhtea02", "BMDHTMA", "BMCP" ),
	( "abm_mt_sta_gift", 4, "bmdhtea03", "BMDHTMT", "BMCP" ),
	( "abm_ml_fear", 5, "bmdalea01", "BMDALMF", "BMCA" ),
	( "abm_ml_mesmerize", 5, "bmdalea02", "BMDALMM", "BMCA" ),
	( "abm_ml_stun", 5, "bmdalea03", "BMDALMS", "BMCA" ),
	( "abm_mt_self_heal", 6, "bmstea01", "BMSTMP", "BMCA" ),
	( "abm_mt_self_sap_gift", 14, "bmstea02", "BMSTMA", "BMCP" ),
	( "abm_mt_self_sta_gift", 15, "bmstea03", "BMSTMT", "BMCP" ),
	( "abm_mt_create_sap_crystal", 16, "bmstea04", "BMSTMC", "BMCA" ),
]

# The phrases that teach one plan: the phrase, the plan (their names match: "Atysian Double Missile Spell Plan")
PLAN_PHRASES = [ ( "abm_double_dd", 7 ), ( "abm_dd_dot", 8 ), ( "abm_dd_affliction", 9 ), ( "abm_double_dot", 10 ),
	( "abm_dot_affliction", 11 ), ( "abm_double_heal", 12 ), ( "abm_double_self_heal", 13 ) ]

OPTION_PHRASES = { "abm_bomb": "BMOF", "abm_ricochet": "BMOG", "abm_spray": "BMOH", "abm_vampirism": "BMOV", "abm_concentrate": "BMOR" }
CREDIT_PHRASES = { "abm_credit_sap": "BMCA", "abm_credit_hp": "BMCP", "abm_credit_casting_time": "BMCC", "abm_credit_range": "BMCR" }

# The Magic Start of the other roles: the caster's first spell (abm_mt_acid_00003). Their names carry the craft, fight
# and forage prefixes, so a rolemaster of that kind would sell them for its own skill points: taught by a role only.
MAGIC_STARTS = [ "abc_magic_start", "abf_magic_start", "abhf_magic_start" ]
MAGIC_START_SPELL = "abm_mt_acid_00003"

# The craft and forage domains make these: crafting starts and the basic extraction of the caster role
OTHER_DOMAINS = re.compile(r"^abm[fmtz]aca01$|^abmfepa01$")

# Ids without a family in the code, and what they duplicate
NO_FAMILY_CRYSTAL = ("no family in the code (brick_families.cpp has no BMTCFEA nor BMTCFME): a second set of the sap "
	"crystal bricks beside the effect BMSTEA04 and its parameters BMSTMC, which have the same texts and a family")
NO_FAMILY_SELF = ("no family in the code (BMSTPEA, BMSTAEA, BMSTTEA): the self heal, self sap gift and self stamina "
	"gift effects again, which are BMSTEA01 to 03")
# The crystal spell makes item_sap_recharge.sitem (createRechargeItem), and crystallizing a spell crystalized_spell.sitem:
# neither item exists yet. Its bricks are made; its spells wait for the items.
CRYSTAL_SPELLS = "abm_mt_create_sap_crystal"
CRYSTAL_ITEMS_MISSING = ("the sap crystal spell makes item_sap_recharge.sitem (and crystallizing a spell crystalized_spell.sitem), "
	"which do not exist yet (they come with the item work): it would take sap and dappers and make nothing. Its bricks are made")
NO_FAMILY_CRYSTAL_PHRASE = "teaches a BMTCFME brick, which gets no sheet (no family in the code); abmstmc* teach the crystal parameters"

def levelOf(sheetId):
	return int(re.search(r"(\d+)$", sheetId).group(1))

def num(v):
	"""a property value: whole numbers without a point, others with at most three decimals"""
	if isinstance(v, float) and abs(v - round(v)) > 1e-9:
		return ("%.3f" % v).rstrip("0").rstrip(".")
	return str(int(round(v)))

def prop(keyword, *args):
	return keyword + (":" + ":".join(a if isinstance(a, str) else num(a) for a in args) if args else "")

def loadAtlas(gen):
	"""the icon names of the interface atlases (framework.atlasNames: a list that is missing stops the run, naming its
	path and the --atlas option of generate.py)"""
	return framework.atlasNames()

TOKEN = re.compile(r"\$(\$|(\|)?(\d)?([A-Za-z_]+))")

def checkText(gen, brick, textNotes):
	"""every $ token of the brick's texts names a property the brick has, with the argument the token reads"""
	row = gen.sbrickWords.get(brick.name)
	if not row:
		return
	properties = {}
	for p in brick.effective()[1]:
		keyword, sep, tail = p.partition(":")
		properties[keyword.strip().lower()] = tail.split(":") if tail else []
	for text in ( row.name, row.description, row.description2 ):
		for m in TOKEN.finditer(text or ""):
			if m.group(1) == "$":
				continue
			index = int(m.group(3) or 0)
			key = m.group(4).lower()
			if key not in properties:
				gen.error("magic: " + brick.name + " text '" + m.group(0) + "' names " + key + ", which the brick does not have")
			elif index >= len(properties[key]):
				gen.error("magic: " + brick.name + " text '" + m.group(0) + "' reads argument " + str(index) + " of " + key + ", which has " + str(len(properties[key])))
			else:
				try:
					value = float(properties[key][index])
				except ValueError:
					value = 1.0
				if value == 0.0:
					textNotes.append(brick.name + " '" + m.group(0) + "' (shows 0)")

def checkEnergyLoops(gen):
	"""The rule of balancing/magic.py: no cycle of heals and gifts returns more than LOOP_RETURN of the energy its
	credits consumed. Each heal or gift brick converts the score of the credit that pays it into the score it gives, at
	its amount over the energy of the cheapest credit that pays it (one credit of the brick's cost, the next value up on
	the grid; a split credit costs more, and a double plan costs back what its second effect saves). A plan that makes
	energy and takes a casting time or range credit or an area option would break the rule: that is checked too."""
	pays = { "BMCA": "sap", "BMCP": "hp" }
	gives = { 0: "hp", 1: "sap", 2: "sta" }
	grid = {}
	for family in pays:
		grid[family] = sorted((levelOf(b), b) for b in gen.bricks if re.match(r"^" + family.lower() + r"\d{5}$", b))
	def cheapest(family, cost):
		for value, name in grid[family]:
			if value >= cost:
				return gen.bricks[name]
		return None
	# the double plans of the heals and the self spells: the same effect twice for the plan's cost on top
	doubles = { "BMDHTEA": int(gen.bricks["bmpa12"].effective()[0].get("SabrinaCost", 0)),
		"BMSTEA": int(gen.bricks["bmpa13"].effective()[0].get("SabrinaCost", 0)) }
	best = {} # (from, to): the best ratio over every heal and gift brick, alone and doubled
	for name, b in gen.bricks.items():
		effect = { "BMDHTMP": "BMDHTEA", "BMDHTMA": "BMDHTEA", "BMDHTMT": "BMDHTEA", "BMSTMP": "BMSTEA", "BMSTMA": "BMSTEA", "BMSTMT": "BMSTEA" }.get(b.family())
		if not effect:
			continue
		heal = [ p for p in b.effective()[1] if p.upper().startswith("MA_HEAL:") ][0]
		amounts = [ int(v) for v in heal.split(":")[1:] ]
		score = [ i for i, v in enumerate(amounts) if v ][0]
		cost = int(b.effective()[0]["SabrinaCost"])
		for times, total in ( ( 1, cost ), ( 2, 2 * cost + doubles[effect] ) ):
			for family, currency in pays.items():
				c = cheapest(family, total)
				if c:
					energy = int(c.effective()[1][0].split(":")[1])
					key = ( currency, gives[score] )
					best[key] = max(best.get(key, 0.0), times * amounts[score] / float(energy))
	# the cycles: a score into itself, and sap and hit points into each other (stamina buys nothing back in magic)
	for cycle in ( [ ( "hp", "hp" ) ], [ ( "sap", "sap" ) ], [ ( "sap", "hp" ), ( "hp", "sap" ) ] ):
		r = 1.0
		for step in cycle:
			r *= best.get(step, 0.0)
		if r > B.LOOP_RETURN + 0.02:
			gen.error("magic: the heals and gifts make energy around " + " -> ".join(a for a, b in cycle) + " -> " + cycle[0][0]
				+ ": they return %.2f of the credits' energy, more than LOOP_RETURN %.2f" % (r, B.LOOP_RETURN))
	gen.note("magic: heal and gift conversions, the best over the levels, per energy of the credit that pays them: "
		+ ", ".join("%s->%s %.2f" % (a, b, best[(a, b)]) for a, b in sorted(best)))
	for name, b in gen.bricks.items():
		if b.family() == "BMPA":
			grammar = b.effective()[3]
			energyPlan = any(f in ( "BMDHTEA", "BMSTEA" ) for f in grammar["Mandatory"])
			if energyPlan and ( set(grammar["Credit"]) - set(ENERGY_CREDIT_FAMILIES) or set(grammar["Optional"]) & set(AREA_OPTIONS) ):
				gen.error("magic: the plan " + name + " makes energy but takes a casting time or range credit or an area option")

def generate(gen):
	atlas = loadAtlas(gen)
	behaviours = set(framework.table("mode_and_behaviour:EBehaviour"))
	effectFamilies = set(framework.table("effect_families:TEffectFamily"))
	effects = effectTable()
	made = [] # the bricks and parents of this domain, for the icon and text checks
	textNotes = []

	def parent(name, folder, up, **fields):
		p = gen.parent(name, ("sbrick/magic/" + folder).rstrip("/"), up, **fields)
		made.append(p)
		return p

	def brick(name, folder, source, up, **fields):
		b = gen.brick(name, "sbrick/magic/" + folder, source, up, **fields)
		made.append(b)
		return b

	def ids(family):
		"""the translation ids of a level-numbered family, by level"""
		found = gen.sbrickWords.ids(r"^" + family.lower() + r"\d{5}$")
		if not found:
			gen.error("magic: the family " + family + " has no translation id")
		return sorted(found, key=levelOf)

	# every magic brick: the cast time window (MinCastTime raised by the root) and the range window (MaxRange lowered by
	# the root), the same on every brick so that the client and the server compute the same time and range
	top = parent("_magic", "", None, basics={ "MinCastTime": 0, "MaxCastTime": B.tenths(B.MAX_CAST_TIME), "MinRange": 0, "MaxRange": 255 })

	# ---- parameters, first: the roots and effects take their first level from them
	paramFirst = {} # parameter family: lowest level
	paramOf = {} # parameter family: (effect family, effect brick)
	for effectFamily, e in effects.items():
		for number, paramFamily, spec in e["members"]:
			effectName = "%s%02d" % (effectFamily.lower(), number)
			paramOf[paramFamily] = (effectFamily, effectName, spec)
			found = ids(paramFamily)
			if not found:
				continue
			paramFirst[paramFamily] = levelOf(found[0])
			ma = spec["ma"]
			# The family's parent holds the head of the effect: MA:<type>, the tags every level shares and SET_BEHAVIOUR,
			# in Property 0 on without a gap; each brick adds its numbers after them and MA_END last. (A gap in a parent's
			# properties would be right in the sheets, which Georges merges by number, but framework.Brick.effective()
			# closes the parent's gaps before it lays the brick's properties over them, so the checks would see others.)
			head = [ prop("MA", ma) ]
			if "dmgType" in spec:
				head.append(prop("MA_DMG_TYPE", spec["dmgType"]))
			if "effect" in spec:
				head.append(prop("MA_EFFECT", spec["effect"]))
			if "strength" in spec:
				head.append(prop("MA_EFFECT_MOD", spec["strength"]))
			if ma == "mlosmp":
				head.append(prop("MA_STAT", "Speed", "Speed")) # MA_STAT Stat:Type; for the type Speed the stat is not read
			head.append(prop("SET_BEHAVIOUR", spec["behaviour"]))
			if spec["behaviour"] not in behaviours:
				gen.error("magic: " + paramFamily + " SET_BEHAVIOUR " + spec["behaviour"] + " is no behaviour of the code")
			if "effect" in spec and spec["effect"] not in effectFamilies:
				gen.error("magic: " + paramFamily + " MA_EFFECT " + spec["effect"] + " is no effect family of the code")
			folder = "parameter/" + paramFamily.lower()
			p = parent("_" + paramFamily.lower(), folder, top, basics={ "FamilyId": paramFamily },
				properties=head, client={ "Icon": spec["icon"], "IconBack": "pa_back.png" })
			branch = effects[effectFamily]["skill"][:4]
			effectRow = gen.sbrickWords.get(effectName)
			for rank, i in enumerate(found):
				level = levelOf(i)
				row = gen.sbrickWords.get(i)
				# the parameter's name is the effect's with an ordinal (the crystal's is "Create Crystal", its effect
				# "Sap Recharge Weapon")
				if ma != "reload" and effectRow and not row.name.lower().startswith(effectRow.name.lower()):
					gen.error("magic: " + i + " '" + row.name + "' is not named after its effect " + effectName + " '" + effectRow.name + "'")
				if ma == "moet":
					values = [ prop("MA_DMG", B.directDamage(level), 0, 0) ]
				elif ma == "moel":
					values = [ prop("MA_DMG", B.drainPerSecond(level), 0, 0), prop("MA_LINK_COST", B.linkCost(level, B.DRAIN_LINK_COST_FACTOR)),
						prop("MA_LINK_POWER", B.linkPower(level)) ]
				elif ma in ( "mdal", "moal", "mlosmp" ):
					values = [ prop("MA_LINK_COST", B.linkCost(level, B.AFFLICTION_LINK_COST_FACTOR)), prop("MA_LINK_POWER", B.linkPower(level)) ]
				elif ma == "mdht":
					heal = [ 0, 0, 0 ]
					heal[spec["score"]] = spec["amount"](level)
					values = [ prop("MA_HEAL", *heal) ]
				elif ma == "reload":
					values = [ prop("MA_RECHARGE", B.crystalSapLoad(level)) ]
				brick(i, folder, "magic parameter " + paramFamily + " level " + str(level), p,
					basics={ "IndexInFamily": rank + 1, "Level": level, "SabrinaCost": common.sabrinaCost(level),
						"SPCost": B.spCost(level), "LearnRequiresOneOfSkills": B.learnRequires(branch, level),
						"LearnRequiresBricks": effectName },
					properties=[ None ] * len(head) + values + [ prop("MA_END") ])

	# ---- effects
	for effectFamily, e in effects.items():
		basics = { "FamilyId": effectFamily, "Skill": e["skill"], "Action Nature": e["nature"], "SabrinaCost": 0, "Level": 0 }
		if e.get("self"):
			basics["TargetRestriction"] = "SelfOnly"
		p = parent("_" + effectFamily.lower(), "effect/" + e["folder"], top, basics=basics, client={ "IconBack": "ef_back.png" })
		numbers = []
		for number, paramFamily, spec in e["members"]:
			name = "%s%02d" % (effectFamily.lower(), number)
			numbers.append(name)
			row = gen.sbrickWords.get(name)
			if not row:
				gen.error("magic: the effect " + name + " has no translation row")
				continue
			if "word" in spec and spec["word"].lower() not in row.name.lower():
				gen.error("magic: the effect " + name + " '" + row.name + "' is not the " + spec["word"] + " effect the parameter family " + paramFamily + " is for")
			first = paramFirst.get(paramFamily, 0)
			fields = { "IndexInFamily": number, "SPCost": B.spCost(first), "LearnRequiresOneOfSkills": B.learnRequires(e["skill"][:4], first) }
			if "nature" in spec:
				fields["Action Nature"] = spec["nature"]
			brick(name, "effect/" + e["folder"], "magic effect " + row.name, p, basics=fields, client={ "Icon": spec["icon"] }, parameter=[ paramFamily ])
		left = [ i for i in gen.sbrickWords.ids(r"^" + effectFamily.lower() + r"\d\d$") if i not in numbers ]
		if left:
			gen.error("magic: the effect family " + effectFamily + " has translation ids no member stands for: " + ", ".join(left))

	# ---- plans
	rootParent = parent("_bmpa", "root", top, basics={ "FamilyId": "BMPA", "Level": 0 })
	rootFirst = {}
	for number, r in sorted(ROOTS.items()):
		name = "bmpa%02d" % number
		row = gen.sbrickWords.get(name)
		if not row:
			gen.error("magic: the plan " + name + " has no translation row")
			continue
		nature, icon, back, selfOnly = ROOT_LOOK[r["kind"]]
		firsts = []
		for f in r["mandatory"]:
			for n, paramFamily, spec in effects[f]["members"]:
				if paramFamily in paramFirst:
					firsts.append(paramFirst[paramFamily])
		first = B.DOUBLE_PLAN_LEVEL if r.get("double") else min(firsts)
		rootFirst[number] = first
		basics = { "IndexInFamily": number, "Action Nature": nature, "MinCastTime": B.tenths(B.castTime(r.get("double", False))),
			"SabrinaCost": B.DOUBLE_PLAN_COST if r.get("double") else 0,
			"MaxRange": B.SELF_RANGE if selfOnly else B.TARGET_RANGE, "SPCost": B.spCost(first),
			"LearnRequiresOneOfSkills": B.learnRequires(r["branch"], first) }
		if selfOnly:
			basics["TargetRestriction"] = "SelfOnly"
		client = { "Icon": icon, "IconBack": back }
		if r.get("link"):
			client["IconOver"] = LINK_OVER
		brick(name, "root", "magic plan " + row.name, rootParent, basics=basics, client=client,
			mandatory=r["mandatory"], optional=r["options"], credit=ENERGY_CREDIT_FAMILIES if r["kind"] in ENERGY_KINDS else CREDIT_FAMILIES)
	left = [ i for i in gen.sbrickWords.ids(r"^bmpa\d+$") if levelOf(i) not in ROOTS ]
	if left:
		gen.error("magic: plans without a rule: " + ", ".join(left))

	# ---- options
	def option(family, icon, values):
		basics = { "FamilyId": family }
		if family in AREA_OPTIONS:
			basics.update({ "ForbiddenDef": AREA_WORD, "ForbiddenExclude": AREA_WORD + ":" + VAMPIRISM_WORD })
		elif family == "BMOV":
			basics.update({ "ForbiddenDef": VAMPIRISM_WORD, "ForbiddenExclude": AREA_WORD })
		p = parent("_" + family.lower(), "option/" + family.lower(), top, basics=basics, client={ "Icon": icon, "IconBack": "op_back.png" })
		for rank, i in enumerate(ids(family)):
			level = levelOf(i)
			brick(i, "option/" + family.lower(), "magic option " + family + " level " + str(level), p,
				basics={ "IndexInFamily": rank + 1, "Level": level, "SabrinaCost": B.optionCost(level), "SPCost": B.spCost(level),
					"LearnRequiresOneOfSkills": B.learnRequires("SM", level) },
				properties=values(rank, level))

	def areaTargets(rank):
		return rank + 2 # the seven levels of each area option reach 2 to 8 targets, as the texts say

	option("BMOF", "ico_bomb.png", lambda rank, level: [
		prop("AREA_BOMB", B.bombRadius(areaTargets(rank)), B.BOMB_EDGE_FACTOR, areaTargets(rank)),
		prop("AREA_TARGETS", B.areaMainFactor(areaTargets(rank)), areaTargets(rank)) ])
	option("BMOG", "ico_ricochet.png", lambda rank, level: [
		prop("AREA_CHAIN", B.chainRange(areaTargets(rank)), areaTargets(rank), B.chainFactor(areaTargets(rank))) ])
	option("BMOH", "ico_spray.png", lambda rank, level: [
		prop("AREA_SPRAY", B.sprayAngle(areaTargets(rank)), B.sprayLength(areaTargets(rank)), B.SPRAY_BASE, areaTargets(rank)),
		prop("AREA_TARGETS", B.areaMainFactor(areaTargets(rank)), areaTargets(rank)) ])
	option("BMOV", "ico_vampire.png", lambda rank, level: [ prop("MA_VAMPIRISE", B.vampirise(level)) ])
	option("BMOR", "ico_concentration.png", lambda rank, level: [ prop("MA_BREAK_RES", B.CONCENTRATION_BONUS, B.concentrationPower(level)) ])
	# the targets the texts state: "a maximum of N targets" (bomb, spray), "up to N targets" (the ricochet phrases)
	for family, phrase in ( ( "BMOF", None ), ( "BMOH", None ), ( "BMOG", "abm_ricochet" ) ):
		for rank, i in enumerate(gen.sbrickWords.ids(r"^" + family.lower() + r"\d{5}$")):
			text = gen.sphraseWords.get(phrase + "_" + i[-5:]).description if phrase else gen.sbrickWords.get(i).description
			m = re.search(r"(?:maximum of|up to) (\d+) targets", text or "")
			if not m or int(m.group(1)) != areaTargets(rank):
				gen.error("magic: " + i + " reaches " + str(areaTargets(rank)) + " targets, its text says " + (m.group(1) if m else "nothing"))

	# ---- credits: the id carries the credit value (the BMCR descriptions say the ordinal instead, "a magic credit of
	# 17" for bmcr00120, where the other three families say the value)
	def credit(family, icon, over, values):
		p = parent("_" + family.lower(), "credit/" + family.lower(), top, basics={ "FamilyId": family }, client={ "Icon": icon, "IconBack": "cp_back.png", "IconOver": over })
		for rank, i in enumerate(ids(family)):
			value = levelOf(i)
			brick(i, "credit/" + family.lower(), "magic credit " + family + " " + str(value), p,
				basics={ "IndexInFamily": rank + 1, "Level": value, "SabrinaCost": common.sabrinaCredit(value),
					"SPCost": B.spCost(value, B.CREDIT_SP_WEIGHT), "LearnRequiresOneOfSkills": B.learnRequires("SM", value) },
				properties=[ values(value) ])

	credit("BMCA", "ico_sap.png", "cp_over_more.png", lambda c: prop("SAP", B.creditEnergy(c)))
	credit("BMCP", "ico_heal.png", "cp_over_more.png", lambda c: prop("HP", B.lifeCreditCost(c)))
	# MA_CASTING_TIME and MA_RANGE make a brick a casting time or range credit worth its SabrinaCost; the server reads
	# only the presence of the first and that the second is not 0, the client sums the second's value as the credit
	credit("BMCC", "ico_time.png", "cp_over_more.png", lambda c: prop("MA_CASTING_TIME", c))
	credit("BMCR", "ico_range.png", "cp_over_less.png", lambda c: prop("MA_RANGE", c))
	for i in gen.sbrickWords.ids(r"^bmcr\d{5}$"):
		if levelOf(i) > 127:
			gen.error("magic: " + i + ": MA_RANGE is a sint8, a range credit cannot be worth more than 127")

	# ---- ids without a family
	for i in gen.sbrickWords.ids(r"^bmtcf"):
		gen.exclude("sbrick", i, NO_FAMILY_CRYSTAL)
	for i in gen.sbrickWords.ids(r"^bmst[pat]ea\d+$"):
		gen.exclude("sbrick", i, NO_FAMILY_SELF)

	# ---- the ready-made spells
	spellKinds = set()
	for kind, root, effect, paramFamily, creditFamily in SPELLS:
		spellKinds.add(kind)
		found = gen.sphraseWords.ids(r"^" + kind + r"_\d{5}$")
		if not found:
			gen.error("magic: no translation id for the spells " + kind)
		effectFamily, effectName, spec = paramOf[paramFamily]
		if effectName != effect:
			gen.error("magic: " + kind + " names the effect " + effect + ", the parameter family " + paramFamily + " belongs to " + effectName)
		folder = "sphrase/magic/spell/" + effects[effectFamily]["folder"]
		if kind == CRYSTAL_SPELLS:
			for i in found:
				gen.exclude("sphrase", i, CRYSTAL_ITEMS_MISSING)
			continue
		for i in found:
			level = levelOf(i)
			param = paramFamily.lower() + "%05d" % level
			pay = creditFamily.lower() + "%05d" % level
			missing = [ b for b in ( param, pay ) if b not in gen.bricks ]
			if missing:
				gen.error("magic: the spell " + i + " needs " + ", ".join(missing) + ", which the translation has no id for")
				continue
			gen.phrase(i, folder, [ "bmpa%02d" % root, effect, param, pay ], "magic spell " + kind + " level " + str(level))

	# ---- the phrases that teach one parameter (the upgrades)
	for i in gen.sphraseWords.ids(r"^abm[a-z]+\d{5}$"):
		b = i[1:]
		if i.startswith("abmtcf"):
			gen.exclude("sphrase", i, NO_FAMILY_CRYSTAL_PHRASE)
		elif b in gen.bricks:
			family = re.sub(r"\d+$", "", b)
			gen.phrase(i, "sphrase/magic/upgrade/" + family, [ b ], "magic upgrade " + b, castable=False)
		else:
			first = paramFirst.get(re.sub(r"\d+$", "", b).upper())
			gen.exclude("sphrase", i, "names a level its family has no brick for (it starts at " + str(first) + "): the translation has no id " + b)

	# ---- the phrases that teach a plan, an option or a credit
	for i, number in PLAN_PHRASES:
		row, plan = gen.sphraseWords.get(i), gen.sbrickWords.get("bmpa%02d" % number)
		if row and plan and not row.name.lower().startswith(plan.name.lower()):
			gen.error("magic: " + i + " '" + row.name + "' is not the plan bmpa%02d '%s'" % (number, plan.name))
		gen.phrase(i, "sphrase/magic/plan", [ "bmpa%02d" % number ], "magic plan phrase", castable=False)
	for kinds, folder in ( ( OPTION_PHRASES, "option" ), ( CREDIT_PHRASES, "credit" ) ):
		for kind, family in kinds.items():
			found = gen.sphraseWords.ids(r"^" + kind + r"_\d{5}$")
			if not found:
				gen.error("magic: no translation id for the phrases " + kind)
			for i in found:
				b = family.lower() + i[-5:]
				if b not in gen.bricks:
					gen.error("magic: " + i + " teaches " + b + ", which the translation has no id for")
					continue
				gen.phrase(i, "sphrase/magic/" + folder, [ b ], "magic " + folder + " phrase " + b, castable=False)

	# ---- the Magic Start of the craft, fight and forage roles
	for i in MAGIC_STARTS:
		if MAGIC_START_SPELL in gen.phrases:
			gen.phrase(i, "sphrase/magic/start", list(gen.phrases[MAGIC_START_SPELL].bricks), "magic start of a role",
				showInAPOnlyIfLearnt=True, showInActionProgression=False)

	# ---- checks of this domain
	checkEnergyLoops(gen)
	for b in gen.bricks.values():
		if b in made and b.family() in paramOf:
			properties = b.effective()[1]
			keywords = [ p.partition(":")[0].strip().upper() for p in properties ]
			if keywords[0] != "MA" or keywords[-1] != "MA_END" or keywords.count("MA_END") != 1 or "SET_BEHAVIOUR" not in keywords:
				gen.error("magic: " + b.name + ": an effect is MA first, SET_BEHAVIOUR and MA_END last, not " + ", ".join(properties))
	for s in made:
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("magic: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
		if not s.isParent:
			checkText(gen, s, textNotes)
	if textNotes:
		gen.note("magic: texts whose token reads an argument that is 0 for this brick (the text is wrong): " + ", ".join(textNotes))
	for i in gen.sbrickWords.ids(r"^bm"):
		if i not in gen.bricks and ("sbrick", i) not in gen.excluded:
			gen.error("magic: the translation id " + i + " has the magic prefix, but the magic domain has no rule for it")
	for i in gen.sphraseWords.ids(r"^abm"):
		if i not in gen.phrases and ("sphrase", i) not in gen.excluded and not OTHER_DOMAINS.match(i):
			gen.error("magic: the translation id " + i + " has the magic prefix, but the magic domain has no rule for it")
