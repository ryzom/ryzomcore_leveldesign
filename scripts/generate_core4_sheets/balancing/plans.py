# The balancing of the craft plans: which components an item takes, how many of each, the tiers of the plans (basic,
# medium and high quality, the faction grades), what they gate and what they give. Ryzom Core's own tuning: no value
# here comes from the Ryzom Classic data.
#
# What the code does with a plan (faber_phrase.cpp, faber_action.cpp, egs_static_brick.cpp loadFaber):
# - The crafter puts in exactly the plan's quantity of each component type (Create.MP n, Quantity n), each unit a raw
#   material that serves that type. The item's quality is min(lowest material quality, the action's grade) times the
#   success factor: a plan does not cap the quality, the credit and the materials do.
# - Every stat of the item is the mean of that stat over all the units put in (each unit counts once, so a component
#   with more units weighs more), clamped to 0..1, stretched, then multiplied by the plan's factor for that stat
#   (Durability Factor, DMG Factor ...; 1.0 when the plan does not set it; the result may go above 1). Every stat is
#   better higher (weight too: CGameItem::weight takes 2 - stat).
# - The XP of a craft is scaled by the units used over NBMeanCraftRawMaterials (10): a bigger plan pays more XP.
# - A material counts for a component when the CraftCivSpec of its part for that type is common or the origin of the
#   item the plan makes, or that item is common (the craft check of the default build): the common and prime roots
#   materials go into every item, desert ones into Fyros items, forest Matis, lakes Tryker, jungle Zorai. (RYZOM_FORGE
#   builds check the plan's CivRestriction against the material's ecosystem instead.)

import math
from balancing import common

# ---------------------------------------------------------------------------------------------------- tiers
# A tier says when a plan is learnt (its level: the learn gate and the skill point price of that level), how much
# material it takes (size, a multiplier on the item's base units) and how good the item can be (factor, on every stat
# the item's components carry).
# - The quality plans of the civilisations: the medium plan comes when the crafter's category skill (SCA, SCM ...)
#   nears its end at 50, the high plan when the class skill (SCAH, SCM1 ...) nears 100. Each tier takes half again and
#   twice the material of the basic one and lifts the ceiling of every stat by a tenth: the basic plan reaches 80% of
#   what the materials allow, the high plan all of it. More material for a better item, and more XP for the work.
# - Ammunition has one plan per round and no tiers: its plan reaches the whole range.
# - The faction grades (kami and karavan items, grade 1 Tekorn, Armilo, Greslin; grade 2 Vedice, Rubbarn, Egiros; the
#   three kami and karavan shields) go past the high plans: their factor goes above 1, which the code allows on purpose
#   ("result factors are unclamped"). They also ask for fame (FACTION_FAME below).
# - The constructions (kami and karavan building pieces) are mission items whose stats the code ignores. They train the
#   craft root SC, which stops at 20, so they are basic plans of its range (planLevel below).
TIERS = {
	#                level size factor
	"basic":        ( 10, 1.0, 0.8 ),
	"medium":       ( 50, 1.5, 0.9 ),
	"high":         ( 100, 2.0, 1.0 ),
	"single":       ( 10, 1.0, 1.0 ),
	"faction1":     ( 100, 2.0, 1.0 ),
	"faction2":     ( 150, 2.5, 1.1 ),
	"faction3":     ( 200, 3.0, 1.2 ),
	"construction": ( 10, 1.0, None ),
}

def tierLevel(tier):
	return TIERS[tier][0]

def tierSize(tier):
	return TIERS[tier][1]

def tierFactor(tier):
	"""the factor on every stat the item's components carry, or None to write no factor"""
	return TIERS[tier][2]

# Fame of the kami or karavan a faction plan needs (Basics.Faction and Minimum fame; fame points of 6000, kFameMultipler).
# Grade 1 at 30, the fame a character needs to declare for the faction (FameMinToDeclare); grade 2 at 60, above the 50 an
# undeclared character cannot pass (FameMaxDefault), so only a declared follower learns it.
FAME_POINT = 6000
FACTION_FAME = { "faction1": 30, "faction2": 60, "faction3": 60 }

def factionFame(tier):
	return FACTION_FAME[tier] * FAME_POINT if tier in FACTION_FAME else None

# ---------------------------------------------------------------------------------------------- learning
# The skill trains to the plan's item (its master leaf, as SCAHBEM heavy boots); the gate is the level of the tier ten
# levels early (common.learnGate), on the ancestor of that skill a crafter is training at that value: the first skill on
# the way from the craft root SC to the leaf whose maximum is above the gate (skills.skill_tree, MaxSkillValue: SC to
# 20, the category SCA to 50, the class SCAH to 100 ...). The rolemaster check reads the highest value the character
# reached in exactly that skill (MaxLvlReached), so the gate must name a skill the crafter has at that point, not the
# leaf. A plan whose own skill stops at or below the gate (the tools and constructions train SC, SCA ...) is gated on
# the first skills below its own whose maximum is above it: one of them is enough. The tree is the domain's reading of
# skills.skill_tree: {skill: (MaxSkillValue, parent skill or None)}.

def skillCap(skill, tree):
	return tree[skill][0]

# A plan's level never passes the cap of its own skill: the success roll compares that skill with min(the materials'
# quality, the action's grade) (faber_action.cpp rollSuccessFactor), and a skill stops at its cap, so a plan of a
# higher level would be learnt for qualities its crafter cannot make. It holds the plans whose skill is shallow: the
# constructions and the pick train SC (to 20), the crafting tools their category (SCA, SCJ, SCM, SCR, to 50).
def planLevel(tier, skill, tree):
	return min(tierLevel(tier), skillCap(skill, tree))

def gateSkills(skill, level, tree):
	"""([skill codes], value) for LearnRequiresOneOfSkills"""
	gate = common.learnGate(level)
	chain = []
	k = skill
	while k:
		chain.insert(0, k)
		k = tree[k][1]
	for k in chain:
		if gate < tree[k][0]:
			return [ k ], gate
	below = [ skill ]
	while below and all(tree[s][0] <= gate for s in below):
		below = sorted(s for s, (cap, parent) in tree.items() if parent in below)
	return below, gate

def spCost(level):
	return common.spCost(level)

# ---------------------------------------------------------------------------------------------- components
# What an item is made of, by its item type (plan_items.itemType): component type (the label of item_mp_faber_type.typ)
# and its share of the item's units. The components follow what the item is; the shares say how much of the item each
# part is, and so how much it weighs in the item's stats.
BLADE, HAMMER, POINT, SHAFT, GRIP, COUNTERWEIGHT = ( "Raw Material for Blade", "Raw Material for Hammer",
	"Raw Material for Point", "Raw Material for Shaft", "Raw Material for Grip", "Raw Material for Counterweight" )
TRIGGER, FIRING_PIN, BARREL = "Raw Material for Trigger", "Raw Material for Firing pin", "Raw Material for Barrel"
EXPLOSIVE, JACKET, BULLET = "Raw Material for Explosive", "Raw Material for Ammo jacket", "Raw Material for Ammo bullet"
SHELL, LINING, STUFFING, CLIP = ( "Raw Material for Armor shell", "Raw Material for Armor interior coating",
	"Raw Material for Armor interior stuffing", "Raw Material for Armor clip" )
SUPPORT, STONE = "Raw Material for Jewel stone support", "Raw Material for Jewel stone"
CLOTHES, FOCUS = "Raw Material for Clothes", "Raw Material for Magic Focus"

# melee weapons: the striking part by damage type (an edge cuts, a point pierces, a head smashes), a shaft where the
# weapon has a haft, the grip, and a counterweight where the weapon is swung around its balance
SWUNG_EDGE = [ (BLADE, 0.4), (SHAFT, 0.2), (GRIP, 0.2), (COUNTERWEIGHT, 0.2) ]  # swords: tang, hilt and pommel
HAFTED_EDGE = [ (BLADE, 0.4), (SHAFT, 0.3), (GRIP, 0.2), (COUNTERWEIGHT, 0.1) ] # axes
HAFTED_HEAD = [ (HAMMER, 0.4), (SHAFT, 0.3), (GRIP, 0.2), (COUNTERWEIGHT, 0.1) ] # maces
POLE = [ (POINT, 0.3), (SHAFT, 0.5), (GRIP, 0.2) ]                                # spears and pikes: mostly shaft
DAGGER = [ (POINT, 0.5), (GRIP, 0.3), (COUNTERWEIGHT, 0.2) ]                     # no haft
STAFF = [ (SHAFT, 0.6), (GRIP, 0.2), (HAMMER, 0.2) ]                              # a pole weighted at the ends
AMPLIFIER = [ (FOCUS, 0.5), (GRIP, 0.3), (SHAFT, 0.2) ]                           # the focus carries the magic stats
# range weapons: barrel, firing pin and trigger make the shot, the grip holds it, a stock (shaft) braces the long ones
HANDGUN = [ (BARREL, 0.3), (FIRING_PIN, 0.2), (TRIGGER, 0.2), (GRIP, 0.3) ]
LONGGUN = [ (BARREL, 0.3), (FIRING_PIN, 0.2), (TRIGGER, 0.15), (GRIP, 0.15), (SHAFT, 0.2) ]
HEAVYGUN = [ (BARREL, 0.4), (FIRING_PIN, 0.2), (TRIGGER, 0.1), (GRIP, 0.1), (SHAFT, 0.2) ]
# ammunition: the casing, the projectile and the charge; a launcher's round is mostly charge
ROUND = [ (JACKET, 0.3), (BULLET, 0.5), (EXPLOSIVE, 0.2) ]
BURST = [ (JACKET, 0.3), (BULLET, 0.4), (EXPLOSIVE, 0.3) ]
SHELL_ROUND = [ (JACKET, 0.25), (BULLET, 0.25), (EXPLOSIVE, 0.5) ]
# armor: light armor is cloth, medium armor half shell, heavy armor mostly shell; all lined, padded and fastened
LIGHT = [ (CLOTHES, 0.5), (LINING, 0.2), (STUFFING, 0.1), (CLIP, 0.2) ]
MEDIUM = [ (SHELL, 0.3), (LINING, 0.3), (STUFFING, 0.2), (CLIP, 0.2) ]
HEAVY = [ (SHELL, 0.5), (LINING, 0.2), (STUFFING, 0.15), (CLIP, 0.15) ]
ROBE = [ (CLOTHES, 0.6), (LINING, 0.2), (CLIP, 0.2) ]        # caster and refugee pieces: unpadded garments
UNDERWEAR = [ (CLOTHES, 1.0) ]
# shields: a shell on a padded, strapped frame
SHIELD = [ (SHELL, 0.6), (CLIP, 0.2), (LINING, 0.2) ]
# jewels: a setting and its stone (the setting carries the resistances, the stone the protections)
JEWEL = [ (SUPPORT, 0.5), (STONE, 0.5) ]
# crafting tools and the pick: a handle (shaft and grip) and the working head (a needle or a point, a hammer)
def tool(head):
	return [ (SHAFT, 0.4), (GRIP, 0.3), (head, 0.3) ]

COMPONENTS = {
	"DAGGER": DAGGER, "SWORD": SWUNG_EDGE, "MACE": HAFTED_HEAD, "AXE": HAFTED_EDGE, "SPEAR": POLE, "STAFF": STAFF,
	"TWO_HAND_SWORD": SWUNG_EDGE, "TWO_HAND_AXE": HAFTED_EDGE, "PIKE": POLE, "TWO_HAND_MACE": HAFTED_HEAD,
	"MAGICIAN_STAFF": AMPLIFIER,
	"PISTOL": HANDGUN, "BOWPISTOL": HANDGUN, "RIFLE": LONGGUN, "BOWRIFLE": LONGGUN, "AUTOLAUCH": HEAVYGUN, "LAUNCHER": HEAVYGUN,
	"PISTOL_AMMO": ROUND, "BOWPISTOL_AMMO": ROUND, "RIFLE_AMMO": ROUND, "BOWRIFLE_AMMO": ROUND, "AUTOLAUNCH_AMMO": BURST,
	"LAUNCHER_AMMO": SHELL_ROUND,
	"SHIELD": SHIELD, "BUCKLER": SHIELD,
	"ANKLET": JEWEL, "BRACELET": JEWEL, "DIADEM": JEWEL, "EARING": JEWEL, "PENDANT": JEWEL, "RING": JEWEL,
	"ArmorTool": tool(POINT), "AmmoTool": tool(HAMMER), "JewelryTool": tool(HAMMER), "MeleeWeaponTool": tool(HAMMER),
	"RangeWeaponTool": tool(HAMMER), "SHEARS": tool(POINT),
}
for piece in ( "BOOTS", "GLOVES", "PANTS", "SLEEVES", "VEST" ):
	COMPONENTS["LIGHT_" + piece] = LIGHT
	COMPONENTS["MEDIUM_" + piece] = MEDIUM
for piece in ( "BOOTS", "GLOVES", "PANTS", "SLEEVES", "VEST", "HELMET" ):
	COMPONENTS["HEAVY_" + piece] = HEAVY

# The construction pieces (plan_items: ep2_*), by what their names say they are: the kami pieces are grown (bark, fibre,
# root and trunk, moss, buds, the core and symbol of a Ma-Duk), the karavan pieces built (bricks, filler, columns,
# plates, pedestals, statues, ornaments). The first word that matches decides.
CONSTRUCTION_PARTS = [
	( "bark", [ (SHELL, 0.6), (CLIP, 0.4) ] ),
	( "fibers", [ (CLOTHES, 0.6), (LINING, 0.4) ] ),
	( "root", [ (SHAFT, 0.6), (COUNTERWEIGHT, 0.4) ] ),
	( "trunk", [ (SHAFT, 0.6), (COUNTERWEIGHT, 0.4) ] ),
	( "moss", [ (STUFFING, 0.6), (LINING, 0.4) ] ),
	( "bud", [ (FOCUS, 0.5), (STONE, 0.5) ] ),
	( "maduk", [ (FOCUS, 0.4), (STONE, 0.3), (SUPPORT, 0.3) ] ),
	( "symbol", [ (STONE, 0.5), (SUPPORT, 0.5) ] ),
	( "brick", [ (COUNTERWEIGHT, 0.6), (SHELL, 0.4) ] ),
	( "conglomerate", [ (COUNTERWEIGHT, 0.5), (STUFFING, 0.5) ] ),
	( "column", [ (SHAFT, 0.6), (COUNTERWEIGHT, 0.4) ] ),
	( "cover", [ (SHELL, 0.6), (CLIP, 0.4) ] ),
	( "pedestal", [ (COUNTERWEIGHT, 0.6), (SHELL, 0.4) ] ),
	( "statue", [ (COUNTERWEIGHT, 0.4), (STONE, 0.3), (SUPPORT, 0.3) ] ),
	( "ornament", [ (STONE, 0.5), (SUPPORT, 0.5) ] ),
]

def constructionParts(item):
	for word, parts in CONSTRUCTION_PARTS:
		if word in item.split("_") or word in item:
			return parts
	return None

# ---------------------------------------------------------------------------------------------- quantities
# Base units of an item (of a basic plan): what a crafter gathers for it. The code's yardstick is a mean of 10 materials
# a craft (NBMeanCraftRawMaterials, which scales the XP): a one-handed weapon or a light vest is about that, a jewel or
# a pair of light gloves about half, a heavy vest twice; a medium piece takes half again its light one, a heavy piece
# twice. A batch of ammunition (AMMO_PER_CRAFT rounds) costs about as much as a jewel.
LIGHT_UNITS = { "BOOTS": 6, "GLOVES": 6, "SLEEVES": 6, "PANTS": 8, "VEST": 10, "HELMET": 6 }
ARMOR_CLASS_SCALE = { "LIGHT": 1.0, "MEDIUM": 1.5, "HEAVY": 2.0 }
UNITS = {
	"DAGGER": 6, "SWORD": 8, "MACE": 8, "AXE": 8, "SPEAR": 8, "STAFF": 8,
	"TWO_HAND_SWORD": 12, "TWO_HAND_AXE": 12, "PIKE": 12, "TWO_HAND_MACE": 12, "MAGICIAN_STAFF": 10,
	"PISTOL": 8, "BOWPISTOL": 8, "RIFLE": 12, "BOWRIFLE": 12, "AUTOLAUCH": 14, "LAUNCHER": 14,
	"BUCKLER": 8, "SHIELD": 12,
	"ANKLET": 4, "BRACELET": 4, "DIADEM": 4, "EARING": 4, "PENDANT": 4, "RING": 4,
	"ArmorTool": 6, "AmmoTool": 6, "JewelryTool": 6, "MeleeWeaponTool": 6, "RangeWeaponTool": 6, "SHEARS": 6,
}
AMMO_UNITS = 4
UNDERWEAR_UNITS = 4 # a light piece of the smallest kind
# the construction pieces: the minor ones about a weapon's worth, the major ones twice
CONSTRUCTION_UNITS = { "small": 10, "minor": 10, "low": 10, "large": 20, "major": 20, "high": 20 }

def baseUnits(itemType, item):
	if itemType == "UNDEFINED":
		for word in item.split("_"):
			if word in CONSTRUCTION_UNITS:
				return CONSTRUCTION_UNITS[word]
		return None
	if itemType.endswith("_AMMO"):
		return AMMO_UNITS
	if itemType in UNITS:
		return UNITS[itemType]
	armorClass, sep, piece = itemType.partition("_")
	if armorClass in ARMOR_CLASS_SCALE and piece in LIGHT_UNITS:
		return LIGHT_UNITS[piece] * ARMOR_CLASS_SCALE[armorClass]
	return None

def quantities(components, units):
	"""[(component, quantity)]: the units (rounded) split by the shares, the rounding left over going to the largest
	remainders, so the quantities add up to the item's units; every component at least one"""
	total = max(len(components), int(math.floor(units + 0.5)))
	exact = [ total * share / sum(s for c, s in components) for c, share in components ]
	counts = [ max(1, int(math.floor(e))) for e in exact ]
	order = sorted(range(len(components)), key=lambda i: (-(exact[i] - counts[i]), i))
	k = 0
	while sum(counts) < total:
		counts[order[k % len(order)]] += 1
		k += 1
	return [ (c, n) for (c, s), n in zip(components, counts) ]

# Ammunition: rounds a craft makes (Nb built items). A range attack takes one round (combat_phrase.cpp consumeAmmos(1));
# an even fight lasts about COMBAT_TIME / the range boost (5 s) of attacks, so 50 rounds see a hunter through some ten
# fights, about what one craft of an item of that cost should give.
AMMO_PER_CRAFT = 50

# ---------------------------------------------------------------------------------------------- stats
# The stats each component type carries (rm_family.cpp isStatRelevant, the code's table), as the faber factor names of
# _item_faber.dfn: the plan writes its tier factor on the stats its components carry.
WEAPON_STATS = [ "Durability Factor", "Weight Factor", "SapLoad Factor", "DMG Factor", "Speed Factor", "Dodge Factor",
	"Parry Factor", "Adversary Dodge Modifier Factor", "Adversary Parry Modifier Factor" ]
ARMOR_STATS = [ "Durability Factor", "Weight Factor", "Dodge Factor", "Parry Factor", "Protection Factor",
	"Slashing Protection Factor", "Blunt Protection Factor", "Piercing Protection Factor" ]
AMMO_STATS = [ "Durability Factor", "Weight Factor", "DMG Factor", "Speed Factor", "Range Factor" ]
STATS = {
	BLADE: WEAPON_STATS, HAMMER: WEAPON_STATS, POINT: WEAPON_STATS, SHAFT: WEAPON_STATS,
	GRIP: [ s for s in WEAPON_STATS if s != "DMG Factor" ], COUNTERWEIGHT: [ s for s in WEAPON_STATS if s != "DMG Factor" ],
	TRIGGER: [ s for s in WEAPON_STATS if s != "DMG Factor" ], FIRING_PIN: WEAPON_STATS + [ "Range Factor" ],
	BARREL: WEAPON_STATS + [ "Range Factor" ],
	EXPLOSIVE: AMMO_STATS, JACKET: [ s for s in AMMO_STATS if s != "DMG Factor" ], BULLET: AMMO_STATS,
	SHELL: ARMOR_STATS, LINING: ARMOR_STATS, STUFFING: ARMOR_STATS, CLIP: ARMOR_STATS, CLOTHES: ARMOR_STATS,
	SUPPORT: [ "Durability Factor", "Weight Factor", "Desert Resistance Factor", "Forest Resistance Factor",
		"Lacustre Resistance Factor", "Jungle Resistance Factor", "PrimaryRoot Resistance Factor" ],
	STONE: [ "Durability Factor", "Weight Factor", "Acid Protection Factor", "Cold Protection Factor", "Fire Protection Factor",
		"Rot Protection Factor", "ShockWave Protection Factor", "Poison Protection Factor", "Electricity Protection Factor" ],
	FOCUS: [ "Durability Factor", "Weight Factor", "SapLoad Factor", "Elemental Casting Time Factor", "Elemental Power Factor",
		"Offensive Affliction Casting Time Factor", "Offensive Affliction Power Factor", "Heal Casting Time Factor",
		"Heal Power Factor", "Defensive Affliction Casting Time Factor", "Defensive Affliction Power Factor" ],
}

def statFactors(components, tier):
	"""{faber factor name: value} for the stats the components carry, or {} when the tier writes none"""
	factor = tierFactor(tier)
	if factor is None or factor == 1.0:
		return {} # 1.0 is the default of every factor (_item_faber.dfn)
	names = []
	for c, q in components:
		for s in STATS[c]:
			if s not in names:
				names.append(s)
	return { s: factor for s in names }
