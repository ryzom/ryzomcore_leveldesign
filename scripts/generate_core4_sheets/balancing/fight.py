# The balancing of the fight actions: the combat root, its options and their parameters, the aim chain and the combat
# credits. Ryzom Core's own tuning: no value here comes from the Ryzom Classic data.
#
# What the code does with these numbers (phrase_manager/combat_phrase.cpp):
# - Every min/max property is a dynamic value. With the reference R = min(skill, weapon quality) of the attacker, a brick
#   gives Max while its PowerValue >= R, and Min + (Max - Min) * PowerValue / R below that (CDynValue::applyValue). The
#   texts state that PowerValue: "maximum efficiency for weapons up to level N" is PowerValue N, and a brick loses
#   strength as the weapon and skill grow past it, which is what makes the next grade worth buying.
# - The phrase success is read in the fight_phrase success table at the relative level
#       skill + credit - largest brick cost - max(total cost, R)
#   The default attack (no cost, no credit) stands at 0, which the table gives 60% full success. A phrase whose credits
#   pay its cost exactly, and whose cost is not above the skill, stands at 0 too; every point of cost above the skill
#   takes a level off, and credit beyond the largest brick adds one. So the Sabrina cost of a brick is the skill at which
#   its phrase is as sure as the default attack: its level, times what its effect is worth (the weights below).
# - The credits only balance the cost at memorize (checkPhraseValidity); the stamina and HP they take are checked at
#   execution (checkPhraseCost). Those amounts are what an action really costs the player.
#
# The player meets the Ring creatures of his level (balancing_config.py, generate_creature.py): a level L creature has
# creatureScore(L) hit points and hits every 3 s for 3/8 of the same score; a player's scores follow the same curve
# (PhysicalCharacteristicsFactor 60 on characteristics of 10 + L), and his reference weapon hits every 4 s for half a
# creature's life (MinDamage and DamageStep that generate_aiaction.py prints). An even fight is two such hits when all
# land (COMBAT_TIME), three or four with the 60% phrase success and the 20% dodge or parry of an even opponent.

from balancing import common

MAX_LEVEL = common.MAX_LEVEL
COMBAT_TIME = common.COMBAT_TIME

# the reference melee weapon of generate_aiaction.py hits 2.5 times in 10 seconds
REFERENCE_ATTACK_TIME = 10.0 / 2.5

# ---- power and cost of the parameters
def powerValue(level):
	"""PowerValue of a brick whose text says "maximum efficiency for weapons up to level N": N itself. Levels above 250
	(the texts go to 265 and 275) stay as stated: such a brick is at Max for every weapon there is."""
	return int(level)

# What each kind of parameter is worth against doubling the damage of one hit, the reference. The cost of a parameter
# is its level times this weight, so a level L phrase of any kind asks the credits that are worth its effect.
WEIGHTS = {
	# up to double damage on the hit (INC_DMG): the reference
	"BFMA": 1.0,
	# halves the attack's latency: the same damage per second as doubling the hit, but with twice the attacks, so half
	# the cost keeps the stamina spent per second the same
	"BFMB": 0.5,
	# +20 to the attacker's level against dodge and parry: takes an even opponent's 20% defense to nothing (dodge_parry
	# table at 0 and -20) and one 20 levels up from 50% to 20%, a quarter to a half of a doubled hit
	"BFMC": 0.5,
	# the hit's damage again as a bleed over the stated 10 s: only what bleeds within an even fight counts
	"BFMD": None, # set below from the bleed duration
	# the hit's damage shared out among all melee aggressors, up to the stated 200% to 500% in all: against two it is
	# a doubled hit
	"BFMF": 1.0,
	# armor absorption to nothing: most Ring creatures stop 0 to 20% of a physical damage type, a few 40 to 80%
	# (creature_fauna.tsv), and armored homins more; worth half a doubled hit against the ones it is chosen for
	"BFMG": 0.5,
	# doubles the opponent's attack latency until the next attack: halving what the opponent deals is worth what
	# doubling one's own damage is, both halve the damage the player takes in the race
	"BFMH": 1.0,
	# hits the chosen slot: its armor, and the slot effect of entities_game_service.cfg (2 s stun on the head, stamina
	# loss on the chest, 8 s slows and debuffs on the limbs), worth about half a doubled hit
	"AIM": 0.5,
}

BLEED_DURATION = 10.0 # stated by the texts ("for 10s"); the domain checks every bleeding text against it
WEIGHTS["BFMD"] = COMBAT_TIME / BLEED_DURATION

def parameterCost(level, family):
	"""the Sabrina cost of a parameter brick of this level. Levels above 250 cost as 250: no skill goes higher, and a
	cost above every skill would keep the phrase below the default attack's success for ever."""
	weight = WEIGHTS["AIM"] if family.startswith("BFA") else WEIGHTS[family]
	return common.sabrinaCost(min(int(level), MAX_LEVEL), weight)

# ---- the effects (Min, Max of the dynamic values; Min is what is left when the weapon outgrows the brick)
INC_DMG = (1.0, 2.0)          # "Increases damage to up to double"
LATENCY_FACTOR = (1.0, 0.5)   # the hit rate grades all reach twice the rate; the grade sets how far up it holds
ATT_SKILL_MOD = (0, 20)       # see the BFMC weight
BLEED_FACTOR = (0.0, 1.0)     # the bleed takes the hit's inflicted damage once more over BLEED_DURATION
CIRCULAR_MIN = 1.0            # the normal damage, shared; Max is the stated total ("will not exceed 200%")
ARMOR_MOD = ("ALL", 1.0, 0.0) # "as if your enemy were not wearing armor" (abfmg*): absorption factor to 0, any armor
# the slow lasts until the player's next attack with the reference weapon, so it is paid again with every attack like
# the other options, and doubles the opponent's latency meanwhile (COMBAT_SLOW counts +100 as +100%)
COMBAT_SLOW_DURATION = REFERENCE_ATTACK_TIME
COMBAT_SLOW = (0, 100)

# ---- the credits
# A credit of N points pays a cost of N (the translation states N: "gives 6 credits"). What it takes from the player:

# Stamina. A stamina credit worth N takes a tenth of the stamina of a level N character: a player who uses an action of
# his level on each of the three or four attacks of an even fight spends a third of his stamina in it, and the 25 to
# 100 s regeneration of balancing_config gives it back between fights.
STAMINA_SHARE = 10.0
# STA_WEIGHT_FACTOR takes StaConst + StaFactor * (weapon weight in kg). Half of the stamina is the constant, so a weapon
# without craft weight (CGameItem::weight is 0 for a weapon that was not crafted) still pays; the other half grows with
# the weight, since a heavier weapon hits harder and slower. The reference is a crafted one-handed weapon: 4 kg
# (SwordWeight and the others in entities_game_service.cfg) times 1 to 2 by its craft, so 6 kg.
REFERENCE_WEAPON_KG = 6.0

def staminaCredit(points):
	"""(StaFactor, StaConst) of a stamina credit of these points. StaFactor is written as a whole number: code_tables.py
	gives it the integer kind of its "$*-i float" comment (the struct reads it with atof)."""
	total = common.creatureScore(points) / STAMINA_SHARE
	return max(1, int(round(total / 2.0 / REFERENCE_WEAPON_KG))), int(round(total / 2.0))

# Hit points. A twentieth of a level N character's hit points: half the stamina share, because a level N creature takes
# 3/8 of them with every hit it lands, so a credit paid in life has to be the cheaper one to be worth choosing.
HP_SHARE = 20.0

def hpCredit(points):
	"""the hit points an HP credit of these points takes"""
	return int(round(common.creatureScore(points) / HP_SHARE))

# Weapon wear. A weapon has 100 durability before its craft bonus (*Durability in entities_game_service.cfg) and loses
# 0.01 with each attack (*WearPerAction): a wear credit of N points takes as much as N attacks do, so forty uses of the
# 250 point one wear out a base weapon. The code scales the wear by the brick's PowerValue (its own points) against the
# phrase's whole credit: it takes all of it when it pays alone, and at least half when other credits pay too.
WEAR_PER_POINT = 0.01

def weaponWear(points):
	"""(Min, Max) item hit points a wear credit of these points takes"""
	return points * WEAR_PER_POINT / 2.0, points * WEAR_PER_POINT

# The opening credits (after a dodge, a parry, a critical hit or a feint) take nothing: the opening they wait for, and
# the action they need first, are their price. The feint option costs nothing either: it does no damage.

# ---- learning
def learnGate(level):
	"""the skill a brick of this level needs before a rolemaster sells it (balancing.common)"""
	return common.learnGate(min(int(level), MAX_LEVEL))

def spCost(level):
	"""the skill point price of a brick of this level (balancing.common); the bricks without a level (root, options,
	aim choices) cost what a level 0 brick does"""
	return common.spCost(min(int(level), MAX_LEVEL))
