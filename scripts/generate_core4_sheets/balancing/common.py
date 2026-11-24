# The balancing every domain shares. Ryzom Core's own tuning: no value here comes from the Ryzom Classic data.
#
# Player actions are balanced against the creatures and NPCs of the Ring, whose numbers come from
# ../generate_r2_sheets/balancing_config.py and were tested in game: a level L action meets a level L creature.

import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "generate_r2_sheets"))
import balancing_config as creatures

MAX_LEVEL = 250

# ---- the Sabrina point scale (CPhraseManager::checkPhraseBalance: cost may not exceed credit)
# The translation states the credits ("gives 6 credits", "a magic credit of 250"): a credit brick gives the points its
# text says. A brick that costs gives points on the same scale, its level: a level L action needs credits worth L, so one
# credit brick of the action's level pays for it, and options and stronger parameters ask for more credits.
def sabrinaCost(level, weight=1.0):
	"""the points a costing brick of this level takes, weight scaling it for lighter options (at least 1)"""
	return max(1, int(round(level * weight)))

def sabrinaCredit(points):
	"""the SabrinaCost of a credit brick that gives these points (credits are negative)"""
	return -int(points)

# ---- learning
def learnGate(level):
	"""the skill value a brick of this level needs before a rolemaster sells it: ten levels below the level it is made
	for, so the next brick is in reach while the current one still serves (LearnRequiresOneOfSkills, at most 250)"""
	return max(0, min(MAX_LEVEL, int(level) - 10))

def learnRequires(skills, level):
	"""LearnRequiresOneOfSkills for a list of skill codes: 'SFM 40:SFR 40'"""
	gate = learnGate(level)
	return ":".join("%s %d" % (s, gate) for s in skills)

def spCost(level, weight=1.0):
	"""skill points to buy a brick of this level. A skill level gives 10 points of its type (SpPointMultiplier); a line
	from 1 to 250 gives about 2500, and its bricks cost 5 to 15 each, so a player buys his line and part of another."""
	return max(1, int(round((5 + level / 25.0) * weight)))

# ---- creature references, for domains that tune damage, heal and durations against them
def creatureScore(level):
	"""hit points (and the other scores) of a creature of this level"""
	return creatures.getScore(level)

COMBAT_TIME = creatures.combatTime # seconds to settle an even fight with base damage, all hits landing
BOOSTS = dict(creatures.boosts) # damage factor per kind: melee 1, range 1.5, magic 2, magic over time 3

def interpolate(level, points):
	"""a value from (level, value) points, linear between them and held beyond the ends"""
	points = sorted(points)
	if level <= points[0][0]:
		return points[0][1]
	for (l0, v0), (l1, v1) in zip(points, points[1:]):
		if level <= l1:
			return v0 + (v1 - v0) * (level - l0) / float(l1 - l0)
	return points[-1][1]
