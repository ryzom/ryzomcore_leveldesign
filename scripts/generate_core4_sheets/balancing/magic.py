# The balancing of the magic domain. Ryzom Core's own tuning: no value here comes from the Ryzom Classic data.
#
# A spell of level L meets a creature of level L as the Ring creatures' own spells do (generate_aiaction.py): a cast
# that takes T seconds deals score(L) * T * boost / COMBAT_TIME, score being the hit points of a level L creature and,
# through the characteristics (60 points of score per point, 10 + L at level L), every score of a level L character.
# Magic's boost is 2 (an even fight settles in half the melee time), over time 3. Every amount below is a function of
# the level; the constants say what they stand for.
#
# What the code does with these numbers is in survey_server.md 3 and 4: the casting and the range are computed from the
# bricks' windows and the casting time and range credits (CMagicPhrase::build), the success roll compares the average
# skill plus the credit with the cost and the dearest brick, and the link spells hold for as long as the caster pays
# the link cost every update period and the target fails its resist roll against the link power.

import math
from balancing import common

MAX_LEVEL = common.MAX_LEVEL

# ---- times, from the EGS configuration (patchman/default/entities_game_service.cfg), not from the bricks
POST_CAST_LATENCY = 1.0 # PostCastLatency = 10 ticks: every cast is followed by a second before the next action
LINK_UPDATE_PERIOD = 4.0 # UpdatePeriodFear .. UpdatePeriodDot = 40 ticks: a link pays and is resisted every 4 s

# ---- casting time and range (the bricks' windows, in tenths of a second and in meters)
# The server takes the largest MinCastTime and the smallest MaxCastTime of a phrase's bricks, the client the largest of
# both, so every magic brick carries the same MaxCastTime and the root raises MinCastTime. For the range the server
# takes the largest MinRange and the client the smallest, so every brick carries MinRange 0 and the root lowers MaxRange.
BASE_CAST_TIME = 2.0 # a spell without a casting time credit; with the post cast latency, the Ring's mean creature spell time of 3 s
# A double plan works two effects in one cast: its cycle is the two single cycles it replaces (2 + 1 + 2 = 5 s cast, then
# the latency), so it is no better per second than two casts. What it gives is both effects landing together.
DOUBLE_CAST_TIME = 2 * BASE_CAST_TIME + POST_CAST_LATENCY
MAX_CAST_TIME = 10.0 # a casting time credit worth the whole cost: the spell costs no sap and takes five times as long
TARGET_RANGE = 30 # meters without a range credit; a range credit worth the whole cost brings the target to touch range
SELF_RANGE = 0 # the self plans: the client shows the range 0 as "Self"

def castTime(double=False):
	return DOUBLE_CAST_TIME if double else BASE_CAST_TIME

def cycleTime(double=False):
	"""seconds from one cast to the next without a casting time credit"""
	return castTime(double) + POST_CAST_LATENCY

def tenths(seconds):
	return int(round(seconds * 10.0))

# ---- energy: what a credit costs
# A sap credit worth C costs a tenth of the pool of a level C character: ten spells of one's level per full pool, as
# craft's CRAFTS_PER_POOL. The pool is affine in the level (the 600 points of the first characteristics, 10 levels' worth),
# so a credit split over two currencies costs more than one credit of the whole value, and one credit of the phrase's
# cost is the cheapest way to pay it.
SPELLS_PER_POOL = 10

def pool(level):
	return common.creatureScore(level)

def creditEnergy(credit):
	"""the sap a sap credit (BMCA) of this value consumes"""
	return int(round(pool(credit) / float(SPELLS_PER_POOL)))

# ---- no energy loops
# The heals and gifts convert one score into another: a heal sap into hit points, a life gift hit points into another's
# hit points, a gift hit points or sap into sap or stamina. No chain of them, by one caster or several, may return more
# than its credits consumed: the product of the ratios (amount given / energy its cheapest credit consumes) around any
# cycle stays at LOOP_RETURN or below. The margin covers a magic focus, which raises heals and gifts by its power factor
# (up to a third on one step of a cycle). The heals stay the strong conversion, sap into hit points, the healer's role;
# the steps that lead back (hit points into hit points, hit points or sap into sap) are the ones that pay for it.
LOOP_RETURN = 0.75

# A targeted heal undoes, over one cast, what an even melee creature deals in that time (the Ring's melee boost): pool
# * 3 s * 1 / 8 s, 3.75 times the sap its credit consumes.
HEAL_RATIO = cycleTime() * common.BOOSTS["melee"] / common.COMBAT_TIME * SPELLS_PER_POOL
# A self heal is half of it: a caster alone still needs a healer.
SELF_HEAL_RATIO = HEAL_RATIO / 2.0

# A life credit pays with hit points, which a heal can buy too (the life gift): for hit points into hit points to stay at
# LOOP_RETURN, a life credit costs HEAL_RATIO / LOOP_RETURN = 5 times the energy of a sap credit of its value. Hit points
# are the score one dies of; paying a spell with them is the costly way.
LIFE_CREDIT_FACTOR = HEAL_RATIO / LOOP_RETURN

def lifeCreditCost(credit):
	"""the hit points a life credit (BMCP) of this value consumes"""
	return int(math.ceil(creditEnergy(credit) * LIFE_CREDIT_FACTOR))

# The gifts give sap or stamina. Paid with sap, a gift moves sap to another at LOOP_RETURN (sap into sap); paid with hit
# points, as their texts say, it gives LOOP_RETURN / LIFE_CREDIT_FACTOR = 0.15 per hit point, so a heal and a gift
# around (sap, hit points, sap) return 3.75 * 0.15 = 0.56. A self gift gives two thirds of that: sap into one's own sap
# 0.5, hit points into one's own sap 0.1, and with a self heal (sap, hit points, sap) 1.875 * 0.1 = 0.19. Stamina buys
# nothing back in magic; its gifts follow the sap gifts.
GIFT_RATIO = LOOP_RETURN
SELF_GIFT_RATIO = LOOP_RETURN * 2.0 / 3.0

# ---- effects
def directDamage(level):
	"""MA_DMG of a direct damage parameter: a level L creature's spell of the same time (boost magic)"""
	return int(round(pool(level) * cycleTime() * common.BOOSTS["magic"] / common.COMBAT_TIME))

def drainPerSecond(level):
	"""MA_DMG of a drain parameter, per second. A drain is a link: the caster holds it and can do nothing else, so its
	damage per second of the caster's time takes the over time boost against the direct spell's boost (1.5 times the
	direct damage per second), paid by the link cost and lost at the first resisted update"""
	return int(round(pool(level) * common.BOOSTS["magic_dot"] / common.COMBAT_TIME))

# the amounts are rounded down and the life credit's cost up, so that rounding never lifts a ratio above its value
def heal(level):
	"""MA_HEAL hit points of a targeted heal"""
	return int(math.floor(creditEnergy(level) * HEAL_RATIO))

def selfHeal(level):
	"""MA_HEAL hit points of a self heal"""
	return int(math.floor(creditEnergy(level) * SELF_HEAL_RATIO))

def gift(level):
	"""sap or stamina a targeted gift gives"""
	return int(math.floor(creditEnergy(level) * GIFT_RATIO))

def selfGift(level):
	"""sap or stamina a self gift gives"""
	return int(math.floor(creditEnergy(level) * SELF_GIFT_RATIO))

# ---- links
# A link costs sap every update period. A drain costs per second what casting direct spells of its level costs; a
# control link (fear, sleep, stun, blind, root, madness, slows) half of it, as it deals no damage.
DRAIN_LINK_COST_FACTOR = 1.0
AFFLICTION_LINK_COST_FACTOR = 0.5

def linkCost(level, factor):
	"""MA_LINK_COST: the sap paid every update period"""
	return max(1, int(round(creditEnergy(level) * LINK_UPDATE_PERIOD / cycleTime() * factor)))

def linkPower(level):
	"""MA_LINK_POWER: the caster's skill in the resist rolls is capped at it. The texts: recommended for enemies whose
	skill does not exceed it, so it is the level"""
	return int(level)

# The strength of the scaled afflictions (MA_EFFECT_MOD): blind and madness the chance in percent that an action fails
# or hits its author, slow attack the percent added to the attack and casting time, slow movement the percent taken
# from the speed (negative). The Ring's creature curses use 75 at every level (generate_aiaction.py EffectValue): the
# level shows in the link power, which decides whom the affliction holds and for how long, not in the strength.
AFFLICTION_STRENGTH = 75

# ---- the sap crystal (MA:reload): its load is in Sabrina points, which an enchantment spends per use
# To settle with the items (item_sap_recharge.sitem and crystalized_spell.sitem do not exist yet, so no phrase casts the
# crystal): an enchantment spends its load in Sabrina points, which are linear in the level, while a heal's amount
# follows the affine pool, so a load spent on enchanted heals of low level can return more than the crystal's sap cost.
# The no-loop rule for enchantments belongs with that work.
CRYSTAL_CHARGES = 10 # a crystal of level L recharges ten uses of an enchanted spell of level L

def crystalSapLoad(level):
	return int(CRYSTAL_CHARGES * level)

# ---- options
# An option of level L costs half its level in Sabrina points: a level L spell with an option of its level needs half
# again its credit, and the option's level is still above the cost it adds, so the option is not the spell's level.
OPTION_WEIGHT = 0.5

def optionCost(level):
	return common.sabrinaCost(level, OPTION_WEIGHT)

# Area options: n targets (2 to 8, as the texts say). If all n are reached, an area spell does sqrt(n) times the damage
# of the single spell, so the main target takes 1 / sqrt(n) of it (bomb and spray, AREA_TARGETS) or the ricochets
# decay (chain).
def areaMainFactor(targets):
	"""TargetFactor of AREA_TARGETS: the phrase divides by targets * factor, so each target takes 1 / sqrt(n)"""
	return 1.0 / math.sqrt(targets)

BOMB_EDGE_FACTOR = 0.5 # the bomb's damage falls from full at the centre to half at its edge

def bombRadius(targets):
	"""meters: the disc grows with the room n targets take, 3.5 m for 2 and 7.1 m for 8"""
	return round(2.5 * math.sqrt(targets), 1)

def chainRange(targets):
	"""meters between two targets of a ricochet: 5 m for 2, 11 m for 8"""
	return float(3 + targets)

def chainFactor(targets):
	"""the factor of each ricochet. The code applies it from the main target on (CEntityRangeSelector::getFactor), so
	the n targets take f, f^2 ... f^n: f is chosen so that their sum is sqrt(n)"""
	want = math.sqrt(targets)
	low, high = 0.0, 1.0
	for i in range(60):
		f = (low + high) / 2.0
		if sum(f ** k for k in range(1, targets + 1)) < want:
			low = f
		else:
			high = f
	return round((low + high) / 2.0, 3)

def sprayAngle(targets):
	"""degrees of the cone (the code wants less than 180): 30 for 2 targets to 60 for 8"""
	return int(30 + 5 * (targets - 2))

def sprayLength(targets):
	"""meters from the target to the far end of the cone: 8 for 2 targets to 14 for 8"""
	return float(6 + targets)

SPRAY_BASE = 1.0 # meters, the width of the cone at the target

# Vampirism: the hit points taken back from the damage of one cast, at most a quarter of a direct spell of the
# option's level, a third of a self heal's worth of hit points on every damage cast
VAMPIRISE_SHARE = 0.25

def vampirise(level):
	return int(round(directDamage(level) * VAMPIRISE_SHARE))

# Concentration: MA_BREAK_RES adds to the caster's skill in the roll against an interruption. 20 points are two steps
# of the break_cast_resist table (60 % at an even level to 80 %), at every level; the level of the brick is the cost of
# the phrases it covers in full (the code scales the bonus down by power / cost above it).
CONCENTRATION_BONUS = 20

def concentrationPower(level):
	return int(level)

# ---- double plans
# A second effect in one phrase would save the fixed part of a credit's energy (one credit of 2L costs less than two of
# L, by the first characteristics' 10 levels): a double plan costs those 10 Sabrina points, so two effects of level L
# need a credit of 2L + 10, whose energy is that of two credits of L. Per effect, a double spell then costs what two
# single spells cost, and with DOUBLE_CAST_TIME it gives what they give per second.
DOUBLE_PLAN_COST = int(common.creatures.minCharacteristic)

# ---- learning
# The double plans combine two effects: they come with the second tier of the magic tree (SMD and SMO end at 50).
DOUBLE_PLAN_LEVEL = 50

def gateSkill(branch, value):
	"""the skill a gate of this value names on a magic branch (SMOE, SMOA, SMDA, SMDH or a shorter one): SM up to 20,
	the second tier up to 50, the branch above. A parent's MaxLvlReached follows its best child, so a gate on SM or SMO
	is met by the deeper skills too, and a beginner's gate names a skill he has"""
	if value <= 20:
		return "SM"
	if value <= 50:
		return branch[:3]
	return branch

def learnRequires(branch, level):
	gate = common.learnGate(level)
	return "%s %d" % (gateSkill(branch, gate), gate)

CREDIT_SP_WEIGHT = 0.5 # four credit families of 17 to 23 values: half the price of a parameter of that level

def spCost(level, weight=1.0):
	return common.spCost(level, weight)
