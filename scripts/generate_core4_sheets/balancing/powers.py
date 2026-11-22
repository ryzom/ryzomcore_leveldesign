# The balancing of the special powers and auras (sbrick/power). Ryzom Core's own tuning: no value here comes from the
# Ryzom Classic data. Every value is a function of the level the brick is made for, measured against the Ring creatures
# and the EGS settings the Ring balance wrote (balancing_config.py, and printEgsConfiguration in generate_aiaction.py,
# whose numbers are in patchman's entities_game_service.cfg).
#
# What the code does with each value is in domains/powers.py; the references are:
#   score(L)         the hit points of a level L creature, and the hit points, sap, stamina and focus of a level L player
#                    (the EGS multiplies a characteristic by maxScore / maxCharacteristic, and a player who bought his
#                    characteristics at the pace of his level has 10 + L)
#   standingRegen(L) what a level L player regains per second while standing
#   creatureHit(L)   one hit of a level L creature, creatureDps(L) its damage per second
#   playerHit(L)     one hit of the reference weapon of a level L fighter, playerDps(L) per second

import math
from balancing import common

creatures = common.creatures
MAX_LEVEL = common.MAX_LEVEL
COMBAT_TIME = common.COMBAT_TIME

# ---- references
def score(level):
	return common.creatureScore(level)

def characteristic(level):
	"""the characteristic a player of this level has bought, which makes his scores those of a creature of the level"""
	return creatures.minCharacteristic + level

# Regen, as printEgsConfiguration (generate_aiaction.py, which writes sheets when imported) derives the EGS settings
# RegenDivisor, RegenReposFactor and RegenOffset from the Ring's regen times; standing, the regen is the sitting one
# divided by RegenReposFactor, plus the offset (CCharacter::computeMaxValue).
REGEN_DIVISOR = (creatures.regenTimeMax - creatures.regenTimeMin) / creatures.maxScore * creatures.maxCharacteristic
REGEN_REPOS_FACTOR = creatures.regenTimeMax / creatures.regenTimeSittingMax
REGEN_OFFSET = creatures.minScore / creatures.regenTimeMin - creatures.minCharacteristic / REGEN_DIVISOR

def standingRegen(level):
	return characteristic(level) / REGEN_DIVISOR / REGEN_REPOS_FACTOR + REGEN_OFFSET

CREATURE_ATTACK_TIME = 3.0 # generate_creature.py attackTime: a Ring creature hits every 3 s (that script writes sheets when imported)
REFERENCE_HIT_TIME = 10.0 / 2.5 # generate_aiaction.py meleeReferenceHitRate: the reference two-handed sword hits 2.5 times in 10 s

def creatureDps(level):
	"""generate_creature.py: a creature's hits take a player of its level down in COMBAT_TIME"""
	return score(level) * common.BOOSTS["melee"] / COMBAT_TIME

def creatureHit(level):
	return creatureDps(level) * CREATURE_ATTACK_TIME

def playerHit(level):
	"""the EGS weapon damage table (MinDamage + DamageStep * level, printEgsConfiguration): the reference weapon of a
	level L fighter takes a level L creature down in COMBAT_TIME"""
	return score(level) * REFERENCE_HIT_TIME * common.BOOSTS["melee"] / COMBAT_TIME

def playerDps(level):
	return playerHit(level) / REFERENCE_HIT_TIME

def whole(value):
	return int(round(value))

# ---- levels
# The ids of the power families are ordinals ("Taunt power 1" to "12"), and no text states a level: a family spreads
# its ordinals from the level it opens at to MAX_LEVEL, rounded to five so the brick levels read as the other domains'.
LEVEL_STEP = 5

def spread(count, first):
	"""the levels of a family of count ordinals, from first to MAX_LEVEL"""
	if count == 1:
		return [ first ]
	levels = []
	for i in range(count):
		if i == 0:
			levels.append(first)
		elif i == count - 1:
			levels.append(MAX_LEVEL)
		else:
			v = first + (MAX_LEVEL - first) * i / float(count - 1)
			levels.append(int(round(v / LEVEL_STEP)) * LEVEL_STEP)
	for a, b in zip(levels, levels[1:]):
		if b <= a:
			raise ValueError("the levels of a family of %d from %d do not rise: %s" % (count, first, levels))
	return levels

def healGrid(ordinal):
	"""the self heals and the disable time credits have 26 ordinals: 1, then every ten levels to 250"""
	return max(1, 10 * (ordinal - 1))

def potionHealGrid(ordinal):
	"""the 25 potion heals (bsp*): every ten levels from 10, as their phrases' numbers match 1 to 5, 15, 20, 25"""
	return 10 * ordinal

def potionGrid(ordinal):
	"""the 5 potion invulnerabilities and speeds: every fifty levels"""
	return 50 * ordinal

# Where a family opens. A fighter starts with a taunt and a shielding (his three-point starting role), so they open at 1,
# as do the self heals. The regen auras and the speed come with the first team fights and travels; berserk after the
# first weapon levels. The immunities, the war cry, the walls, the HP balance and the weapon enchantment change a fight
# outright and open at 50, the end of the starting lands' levels (balancing_config.py bossLevels b5).
FIRST_LEVEL = {
	"taunt": 1, "shielding": 1, "speeding_up": 10, "invulnerability": creatures.bossLevels["b5"], "berserk": 20,
	"balance_hp": creatures.bossLevels["b5"], "regen_aura": 10, "protection": creatures.bossLevels["b5"],
	"war_cry": creatures.bossLevels["b5"], "wall": creatures.bossLevels["b5"], "enchant": creatures.bossLevels["b5"],
}
ENCHANT_LEVELS = spread(3, FIRST_LEVEL["enchant"]) # three strengths per element

# ---- taunt (SP_TAUNT: TauntPower:Range:DisableTime)
# A taunt works for sure on a creature whose TauntLevel is at most its power (the success table decides above it). The
# Ring gives a creature of level L a TauntLevel of its base level, which varies by levelVariance and by the ecosystem's
# levelOffset: the power covers the highest of both for the ordinary lands, so a level L taunt holds every plain
# creature of level L, while the goo, invasion and raid offsets stay a gamble.
TAUNT_MARGIN = (creatures.levelVariance[1] - 1) + max(creatures.levelOffset[e] for e in "djflp")

def tauntPower(level):
	return level + TAUNT_MARGIN

# Past the 15 m a Ring creature aggroes at (generate_creature.py, the default aggro), so the taunter pulls a creature
# off a team-mate it is on without walking into its aggro first.
TAUNT_RANGE = 20

def tauntDisable(level):
	"""one taunt per fight: an even fight lasts COMBAT_TIME with every hit landing, about twice that with the misses"""
	return whole(2 * COMBAT_TIME)

# ---- shielding (SP_SHIELDING: per hit on the protected target, the bodyguard takes factor % of it, at most max points)
# The share grows with the shield (a bigger shield takes more of the blow) and with the level, so a higher brick is worth
# more than its cap. The cap is the share of one hit of a creature of the brick's level: a stronger creature's hits
# go mostly through, which keeps the bricks in step with the levels.
SHIELDING_SHARE = {
	"none": [ (1, 15), (MAX_LEVEL, 30) ],
	"buckler": [ (1, 30), (MAX_LEVEL, 50) ],
	"shield": [ (1, 45), (MAX_LEVEL, 70) ],
}

def shieldingFactor(level, shield):
	return whole(common.interpolate(level, SHIELDING_SHARE[shield]))

def shieldingMax(level, shield):
	return whole(shieldingFactor(level, shield) / 100.0 * creatureHit(level))

def shieldingDuration(level):
	"""a fight with its approach and misses: three even fights' time"""
	return whole(3 * COMBAT_TIME)

def shieldingDisable(level):
	"""counted from its end (CSpecialPowerShielding): up half the time"""
	return shieldingDuration(level)

# ---- self heals (SP_HEAL: AffectedScore:HealValue:HealFactorValue:DisableTime:PowerType)
# "Instantly restores a great number of hit points" (the effect texts): half the pool of the level the brick is made
# for. The recast is the time the body takes to regain as much standing, so a heal gives at once what rest would give,
# and the power at most doubles a player's recovery: from 18 s at level 1 to about two minutes at 250, about one heal
# per fight at every level. The whole recast is in the disable time credit (BSXCA) the phrase pays the heal with.
HEAL_SHARE = 0.5

def healValue(level):
	return whole(HEAL_SHARE * score(level))

def healRecast(level):
	return whole(healValue(level) / standingRegen(level))

# Potion heals (the bsp* variants, executed by an item's EffectPhrase): half a self heal, so the power stays the better
# heal and a potion tops it up. They set no disable time: the item's own overdose timer (Consumable.OverdoseTimer)
# is the limit, and their power types are the consumable ones, so the player's own heal on recast does not refuse them.
POTION_HEAL_SHARE = 0.25

def potionHealValue(level):
	return whole(POTION_HEAL_SHARE * score(level))

# Consumable heals (BSCM*, the absc phrases): a share of the user's own maximum (HealFactorValue, in %), so one sheet
# serves every level; an item naming the phrase sets the overdose timer. Half a self heal, as the potions.
CONSUMABLE_HEAL_PERCENT = whole(100 * POTION_HEAL_SHARE)

# ---- regen auras (SP_LIFE_AURA, SP_STAMINA_AURA, SP_SAP_AURA: RegenMod:Duration:Radius:TargetDisableTime:UserDisableTime)
# The code adds RegenMod / 10 points per second to the regen of the user and his team-mates in the radius
# (CRegenAuraEffect). Over its duration the aura gives each of them half a pool of its level, a self heal's worth
# spread over the team and the time. It lasts four even fights' time, the fight and the rest after it.
REGEN_AURA_DURATION = whole(4 * COMBAT_TIME)
REGEN_AURA_POOL_SHARE = HEAL_SHARE

def regenAuraMod(level):
	return whole(10 * REGEN_AURA_POOL_SHARE * score(level) / REGEN_AURA_DURATION)

def auraRadius(level):
	"""a close group at the first levels, a spread raid at the last"""
	return whole(common.interpolate(level, [ (1, 10), (MAX_LEVEL, 25) ]))

# The aura reaches the whole team and costs no credit, so per person it gives half of what the self heal of its level
# gives over time: the same half pool, once every two recasts of that heal. The self heal stays the stronger help for
# the one in trouble, the aura pays off from a team of three. Tied to healRecast, both grow with the level alike (a
# fixed reuse would let the aura outheal the self heal from level 50 on, for every team-mate).
REGEN_AURA_RECAST_FACTOR = 2.0

def regenAuraUserDisable(level):
	"""the user casts no aura of any kind for two self heal recasts of the level (the code counts it from the cast),
	and never less than the aura lasts"""
	return max(REGEN_AURA_DURATION, whole(REGEN_AURA_RECAST_FACTOR * healRecast(level)))

def regenAuraTargetDisable(level):
	"""a team-mate takes the same aura from another user only after as long, so two users cannot chain it"""
	return regenAuraUserDisable(level)

# ---- protection auras and invulnerability (immunity to melee, range or magic for the team; all attacks for oneself)
# An immunity holds for part of an even fight, longer at the higher levels, and is an emergency: it comes back after
# minutes, and a protection aura keeps the user from every other aura as long.
def immunityDuration(level):
	return whole(common.interpolate(level, [ (FIRST_LEVEL["protection"], 5), (MAX_LEVEL, 10) ]))

def protectionDisable(level):
	return whole(common.interpolate(level, [ (FIRST_LEVEL["protection"], 300), (MAX_LEVEL, 240) ]))

def invulnerabilityDisable(level):
	"""counted from its end (CSpecialPowerBasic); the higher bricks come back sooner"""
	return whole(common.interpolate(level, [ (FIRST_LEVEL["invulnerability"], 600), (MAX_LEVEL, 300) ]))

# ---- speeding up (SP_SPEEDING_UP: SpeedMod %:Duration:DisableTime)
SPEEDING_UP_MOD = 100 # "You run twice as fast" (the texts): +100 % of the base speed (CChangeMoveSpeedEffect)

def speedingUpDuration(level):
	return whole(common.interpolate(level, [ (FIRST_LEVEL["speeding_up"], 20), (MAX_LEVEL, 60) ]))

def speedingUpDisable(level):
	"""counted from its end: a travel power, the higher bricks run longer and come back sooner"""
	return whole(common.interpolate(level, [ (FIRST_LEVEL["speeding_up"], 120), (MAX_LEVEL, 60) ]))

# ---- berserk (SP_BERSERK: DisableTime:Duration:DamagePerUpdate:UpdateFrequency:DamageBonus)
# The code adds DamageBonus to the base damage of each melee hit (CCombatPhrase::computeBaseDamage) and takes
# DamagePerUpdate hit points every UpdateFrequency seconds for the whole duration. A quarter more damage per hit, for
# a fifth of the pool over the duration: worth it in a long fight or against several, a loss in a short one.
BERSERK_DAMAGE_SHARE = 0.25
BERSERK_BLEED_SHARE = 0.2
BERSERK_TICK = 2.0 # the update frequency of the Ring's damage over time (generate_aiaction.py dotFrequency)

def berserkDuration(level):
	return whole(3 * COMBAT_TIME)

def berserkDisable(level):
	"""counted from its end"""
	return 2 * berserkDuration(level)

def berserkBonus(level):
	return whole(BERSERK_DAMAGE_SHARE * playerHit(level))

def berserkBleed(level):
	ticks = berserkDuration(level) / BERSERK_TICK
	return whole(BERSERK_BLEED_SHARE * score(level) / ticks)

# ---- war cry and the walls (team auras: Radius:Duration:TargetDisableTime:UserDisableTime:Value)
TEAM_AURA_DURATION = whole(4 * COMBAT_TIME)

def teamAuraDisable(level):
	"""stronger than a regen aura, so up a third of the time"""
	return 3 * TEAM_AURA_DURATION

def warCryBonus(level):
	"""% added to the damage factor of every hit of the team (computeBaseDamage)"""
	return whole(common.interpolate(level, [ (FIRST_LEVEL["war_cry"], 10), (MAX_LEVEL, 30) ]))

def fireWallDamage(level):
	"""hit points every melee attacker loses per hit it lands: a fifth of the hit of a creature of the level"""
	return whole(0.2 * creatureHit(level))

def thornWallSlow(level):
	"""% added to the attack latency of every melee attacker for the HitArmsSlowDuration of the EGS, around the 30 %
	a hit on the arms gives (HitArmsSlowFactor, entities_game_service.cfg)"""
	return whole(common.interpolate(level, [ (FIRST_LEVEL["wall"], 20), (MAX_LEVEL, 40) ]))

def waterWallAbsorb(level):
	"""% of every melee hit taken that the water absorbs"""
	return whole(common.interpolate(level, [ (FIRST_LEVEL["wall"], 10), (MAX_LEVEL, 30) ]))

def lightningWallDebuff(level):
	"""skill points taken from every melee attacker for the HitHandsDebuffDuration of the EGS, around the -20 a hit on
	the hands gives (HitHandsDebuffValue); negative, as the code adds it to the attack skill"""
	return -whole(common.interpolate(level, [ (FIRST_LEVEL["wall"], 10), (MAX_LEVEL, 30) ]))

# ---- HP balance (SP_BALANCE: DisableTime:AffectedScore:Range:LossFactor %); the loss is the text's ("with a 30% loss")
def balanceDisable(level):
	return whole(common.interpolate(level, [ (FIRST_LEVEL["balance_hp"], 300), (MAX_LEVEL, 180) ]))

# ---- weapon enchantment (SP_ENCHANT_WEAPON: DisableTime:Duration:DamageType:DpsBonus:DamageBonus)
# The code turns DpsBonus into elemental damage on each hit of the melee weapon (DpsBonus * 10 / hit rate), which the
# target's magic resistance can stop; DamageBonus is only the effect's value. A quarter of the dps of a fighter of the
# level, for eight even fights' time.
ENCHANT_DPS_SHARE = 0.25

def enchantDuration(level):
	return whole(8 * COMBAT_TIME)

def enchantDisable(level):
	"""counted from its end"""
	return enchantDuration(level)

def enchantDps(level):
	return round(ENCHANT_DPS_SHARE * playerDps(level), 1)

# ---- learning
def spCost(level):
	return common.spCost(level)

def sabrinaCost(level):
	"""a self heal costs points worth its level, which a disable time credit of its level pays"""
	return common.sabrinaCost(level)

def sabrinaCredit(level):
	return common.sabrinaCredit(level)
