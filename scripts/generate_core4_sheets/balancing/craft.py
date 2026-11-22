# The balancing of the craft actions: the roots, the credits that set the quality an action makes, and the boost
# options. Ryzom Core's own tuning: no value here comes from the Ryzom Classic data.
#
# What the code does with these numbers (faber_phrase.cpp, faber_action.cpp):
# - CR_RECOMMENDED is the action's level. The item comes out at min(lowest material quality, recommended) times the
#   success factor, and the success roll compares the plan's skill with that same minimum. A higher grade therefore
#   also makes every lower quality: what it costs more is focus, and what it gives more is room for boosts.
# - FOCUS is summed over the credit and the option bricks and taken from the crafter when the item is made; a crafter
#   with less focus than that cannot start.
# - CR_HP, CR_SAP, CR_STA and CR_FOCUS are summed and added to the item's score buffs, scaled by the success factor
#   and by min(material quality, recommended) / the action's nominal level, so materials below it give less boost.
# - The Sabrina cost of the options must not exceed the credit (checkPhraseValidity at memorize).

from balancing import common

# ---- grades
# The phrase texts state the qualities ("Lets you make Fyros armor of quality 10" for grade 1, 250 for grade 25): the
# domain checks every phrase against these two rules.
def creditQuality(grade):
	"""the quality a civilisation or construction credit of this grade (1..25) makes"""
	return 10 * grade

def toolQuality(grade):
	"""the quality a tool credit of this grade (Tools 1..5, ids 01, 10, 15, 20, 25) makes"""
	return 50 * grade

def optionLevel(grade):
	"""the level of a boost option of this grade (Boost 1..25). The texts state no level: the options take the grades of
	the credits, so a boost of grade N belongs with an action of grade N"""
	return 10 * grade

# The roots are learnt with the first grade of their action and carry no level of their own (the client draws no level
# on a root); the help shows Basics.Level, so they get the first level rather than the number in their name.
ROOT_LEVEL = 1
FIRST_QUALITY = creditQuality(1)

# ---- focus
# The focus pool of a character of level L is the Ring's score of that level: a characteristic of 10 + L times 60
# (PhysicalCharacteristicsFactor in the EGS configuration; a new character starts with characteristics of 10, so with
# the level 0 pool). Focus is to crafting what stamina is to fight and sap to magic: the credit, the brick that pays for
# the action, carries it.
CRAFTS_PER_POOL = 10 # a full pool pays for ten plain crafts of the crafter's level before a rest: an armor set and a few jewels

def focusPool(level):
	return common.creatureScore(level)

def actionFocus(quality):
	"""the focus a plain craft of this quality takes (FOCUS of the credit)"""
	return int(round(focusPool(quality) / float(CRAFTS_PER_POOL)))

def boostFocus(level):
	"""the focus a boost option of this level adds: half a plain craft of its level, so a craft with one full boost costs
	half again as much, and splitting a budget into several small boosts costs more than one large one"""
	return int(round(actionFocus(level) / 2.0))

# ---- boosts
# A boost of level L adds L points to its score. The code's own yardstick: a heavy armor piece of quality Q adds Q hit
# points by itself, a medium one Q / 2 (CGameItem::armorHpBuff). A full boost on every piece of a level 250 outfit (some
# fifteen items) raises a score of 15600 by about a quarter, worth having without replacing the characteristics.
# The points are linear in the level, so the Sabrina budget below gives the same total however it is split.
def boostPoints(level):
	return int(level)

# ---- Sabrina points (common.sabrinaCost and sabrinaCredit)
# A credit of quality Q gives Q points and a boost of level L costs L, so the boosts of an action add up to its quality
# at most: a quality 250 action carries one boost of 250, or four of about 60. The root costs nothing.
def creditSabrina(quality):
	return common.sabrinaCredit(quality)

def boostSabrina(level):
	return common.sabrinaCost(level)

# ---- learning (common.learnRequires and spCost)
# The roots come with the first grade of their action, at the first level's gate and price; credits and options at the
# gate and price of their own level. A crafter may skip grades: the top grade makes every lower quality, at its own
# focus cost, so no brick chain is written.
def rootSpCost():
	return common.spCost(FIRST_QUALITY)

def creditSpCost(quality):
	return common.spCost(quality)

def boostSpCost(level):
	return common.spCost(level)
