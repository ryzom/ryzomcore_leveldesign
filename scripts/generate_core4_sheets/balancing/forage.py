# The balancing of forage (prospection, extraction and care) and of quartering. Ryzom Core's own tuning: no value here
# comes from the Ryzom Classic data.
#
# What the code does with these numbers (survey_server.md 5, fg_prospection_phrase.cpp, fg_extraction_phrase.cpp,
# harvest_source.cpp, forage_progress.cpp):
# - An extraction's level is its requested quality (FG_QUALITY): the success roll compares the forage skill of the
#   deposit's ecotype with it, and only a gap of more than 10 below it can fail. A quality brick of quality Q is
#   therefore a level Q action, and the learn gate of common.learnGate (ten below) lets it be bought when it can no
#   longer fail.
# - A care action's level is its total Sabrina cost (CFgExtractionPhrase::build: skill minus sabrinaCost), so a care
#   parameter costs its level.
# - The Sabrina balance (cost not above credit) is checked when a forage phrase is built, every time it runs.
# - Every brick's FOCUS is spent at each extraction cycle, and once per prospection. The focus spent extracting from a
#   prospected source is given back when the session ends (forage_progress.cpp): focus only has to last one session.
# - The source's risk bars rise by a fixed impact per extraction cycle (harvest_source.cpp: MaxDeltaQ 26 times
#   ForageQualityImpactFactor for quality), lowered by the absorption of the property's brick; the damage of an event
#   grows with the speed, rate and quality of the extraction.
#
# Player actions are balanced against the Ring (common.py): the focus pool of a level L character is the Ring's score of
# that level, 60 times a characteristic of 10 + L, and its regeneration follows from the Ring's regeneration times, as
# generate_aiaction.py derives RegenDivisor, RegenReposFactor and RegenOffset for the EGS configuration.

import math
from balancing import common

creatures = common.creatures

# ---- levels
# The forage skills: SH 0-20, SHF 20-50, the five ecotype skills (SHFD desert, SHFF forest, SHFJ jungle, SHFL lakes,
# SHFP prime roots) 50-100, then their advanced (A), expert (E) and master (M) skills to 150, 200 and 250
# (skills.skill_tree: the depth of a skill code sets its maximum).
SKILL_DEPTH_CAPS = [ (2, 20), (3, 50), (4, 100), (5, 150), (6, 200), (7, 250) ]

def skillsForGate(gate, ecotypeSkill=None):
	"""the skill of LearnRequiresOneOfSkills for a gate: one skill on the main line, SH up to its maximum of 20 and SHF
	beyond, whatever ecotype the forager works; or the ecotype skill a terrain brick is for.
	One skill and not an OR of the five ecotypes: the client files a phrase in the action progression by its non-credit
	bricks, and by its full formula only when that is a single value (CSPhraseManager::computePhraseProgression), which
	the AND of skills on one branch is (CSkillValue::andWith keeps the deeper or higher). With an OR at the counterparts,
	"Extraction Counterpart 14" was filed with the starters at SH 0. A value above the skill's own maximum works on both
	sides: a parent's MaxLvlReached follows its best child (CCharacter::addXpToSkillInternal), and so does the client's
	CSkillManager::_MaxChildBaseSkillValue."""
	if ecotypeSkill:
		return [ ecotypeSkill ]
	return [ "SH" ] if gate <= SKILL_DEPTH_CAPS[0][1] else [ "SHF" ]

def learnRequires(level, ecotypeSkill=None):
	gate = common.learnGate(level)
	return ":".join("%s %d" % (s, gate) for s in skillsForGate(gate, ecotypeSkill))

# A family of ordered steps (ranges, angles, speeds, care strengths...) spreads them evenly from the first level of the
# line, learnable at once, to 200, the start of the master skills: the last tier is for the top qualities, and by then a
# forager has every convenience.
FIRST_LEVEL = 10
LAST_STEP_LEVEL = 200

def roundTo5(v):
	return int(5 * math.floor(v / 5.0 + 0.5))

def stepLevel(step, count):
	"""the level of step 1..count of a family"""
	if count == 1:
		return FIRST_LEVEL
	return roundTo5(FIRST_LEVEL + (LAST_STEP_LEVEL - FIRST_LEVEL) * (step - 1) / float(count - 1))

# The terrain specialisations need an ecotype skill, and those open when SHF reaches its maximum of 50.
ECOTYPE_LEVEL = SKILL_DEPTH_CAPS[1][1] + 10
# The group and item part filters are what a beginner needs to find what his craft asks for; the filter on one
# material comes one step later, and so does the extraction's group specialisation, which pays off once the forager
# can find that group.
GROUP_FILTER_LEVEL = FIRST_LEVEL
FAMILY_FILTER_LEVEL = FIRST_LEVEL + 10
EXTRACTION_GROUP_LEVEL = FAMILY_FILTER_LEVEL
# The major filters double the attempts of a search: they mark the advanced skills, from 100, where a prospection
# carries several filters (class, terrain, group) and would otherwise miss often.
MAJOR_FILTER_LEVEL = SKILL_DEPTH_CAPS[2][1] + 10

def classLevel(maxQualityOfClassBelow):
	"""a class filter (up to fine, only choice...) is wanted once the class below runs out: the maximum quality of the
	materials of that class (mp_generator: 50 for basic, 100 for fine...)"""
	return int(maxQualityOfClassBelow)

# Search attempts (FG_ATTEMPTS): a major filter doubles the code's default of 5 tries per source (CFgSearchPhrase
# _NbAttempts). The minor filters write no FG_ATTEMPTS: the code assigns the value of the last brick that has one, so a
# minor filter's 5 would undo a major filter's 10 in the same phrase; without it a phrase gets what its strongest
# filter means.
DEFAULT_ATTEMPTS = 5
MAJOR_ATTEMPTS = 2 * DEFAULT_ATTEMPTS

# ---- credits: their levels and their Sabrina points
def creditLevels(count, dense=5):
	"""the levels of a family of counterparts: the first ones every ten levels, where a beginner gets a new quality
	every ten levels and each step of points matters, then evenly up to 250 (rounded to 5)"""
	levels = [ FIRST_LEVEL * (i + 1) for i in range(dense) ]
	rest = count - dense
	for i in range(1, rest + 1):
		levels.append(roundTo5(levels[dense - 1] + (common.MAX_LEVEL - levels[dense - 1]) * i / float(rest)))
	return levels

# A counterpart of level L pays EXTRACTION_POINTS * L. A level L extraction is a harmful quality brick of quality L
# (L points) with a speed and a rate brick of level up to L (half their level each): 2 L. The rest, L / 2, pays for the
# gentle versions (a quarter more each) or the options: at his own level a forager chooses safety or options, or gives
# up some quality for them. It also lets the counterpart of a brick's own level (or the one below it) pay for the
# phrase that teaches that brick, so no phrase asks for a counterpart above its brick's gate.
EXTRACTION_POINTS = 2.5
# A counterpart of level L pays PROSPECTION_POINTS * L, and a prospection parameter of level l costs l / 4: the best
# step of eight option families, a full prospection of the counterpart's level.
PROSPECTION_POINTS = 2.0

def extractionCredit(level):
	return common.sabrinaCredit(int(round(EXTRACTION_POINTS * level)))

def prospectionCredit(level):
	return common.sabrinaCredit(int(round(PROSPECTION_POINTS * level)))

# ---- Sabrina costs (weights of common.sabrinaCost)
QUALITY_WEIGHT = 1.0          # the quality brick is the action's level
GENTLE_FACTOR = 1.25          # a gentle version costs a quarter more than the harmful one
EXTRACTION_STEP_WEIGHT = 0.5  # speed and rate
EXTRACTION_OPTION_WEIGHT = 0.25 # terrain, group, absorb source damage
PROSPECTION_WEIGHT = 0.25

def qualityCost(quality, gentle):
	return common.sabrinaCost(quality, QUALITY_WEIGHT * (GENTLE_FACTOR if gentle else 1.0))

def extractionStepCost(level, gentle):
	return common.sabrinaCost(level, EXTRACTION_STEP_WEIGHT * (GENTLE_FACTOR if gentle else 1.0))

def extractionOptionCost(level):
	return common.sabrinaCost(level, EXTRACTION_OPTION_WEIGHT)

def careCost(level):
	"""a care parameter costs its level, since the code takes a care action's Sabrina cost as its level"""
	return common.sabrinaCost(level)

def prospectionCost(level):
	return common.sabrinaCost(level, PROSPECTION_WEIGHT)

# ---- focus
def characteristic(level):
	return creatures.minCharacteristic + level

def focusPool(level):
	return common.creatureScore(level)

def focusRegenInAction(level):
	"""focus regenerated per second while acting (CCharacter::computeMaxValue: characteristic / RegenDivisor /
	RegenReposFactor + RegenOffset), with the three settings derived from the Ring's regeneration times as
	generate_aiaction.py derives them for the EGS configuration"""
	regenDivisor = (creatures.regenTimeMax - creatures.regenTimeMin) / creatures.maxScore * creatures.maxCharacteristic
	regenOffset = creatures.minScore / creatures.regenTimeMin - creatures.minCharacteristic / regenDivisor
	reposFactor = creatures.regenTimeMax / creatures.regenTimeSittingMax
	return characteristic(level) / regenDivisor / reposFactor + regenOffset

# The code's default extraction period is 4 s (CFgExtractionPhrase: _RequestedProps S = 0.025 per tick; harvest_source.cpp:
# "6 extractions = 24 seconds with 4 seconds per extraction"), its fastest 1.5 s (MaxS = 1/15 per tick).
DEFAULT_EXTRACTION_PERIOD = 4.0
FASTEST_EXTRACTION_PERIOD = 1.5
# The code's default prospecting time is 15 s (CFgSearchPhrase: _ForageTime 150 ticks).
DEFAULT_PROSPECTION_TIME = 15.0

def extractionFocus(level):
	"""FOCUS of an extraction counterpart of this level, spent at every cycle: what its forager regenerates in one cycle
	at the default speed. At the slowest speed a session costs nothing; every faster speed drains the pool by as much
	as it is faster (at 1.5 s a session at the forager's level, quality and speed, takes about half his pool)"""
	return int(round(DEFAULT_EXTRACTION_PERIOD * focusRegenInAction(level)))

def prospectionFocus(level):
	"""FOCUS of a prospection counterpart of this level, spent once per prospection: what its forager regenerates during
	a prospection at the default time, so prospecting at the default speed can go on, and the accelerated steps drain
	the pool. Deposit tracking spends a tenth of it at every update (ForageFocusRatioOfLocateDeposit), about every 2.5 s"""
	return int(round(DEFAULT_PROSPECTION_TIME * focusRegenInAction(level)))

# ---- extraction properties
SPEED_STEPS = 6

def extractionPeriod(step):
	"""FG_SRC_PRD, seconds per delivery of speed step 1..6: evenly from the code's default to its fastest"""
	return DEFAULT_EXTRACTION_PERIOD - (DEFAULT_EXTRACTION_PERIOD - FASTEST_EXTRACTION_PERIOD) * (step - 1) / float(SPEED_STEPS - 1)

def periodAtLevel(level):
	"""the fastest period a forager of this level can learn"""
	steps = [ s for s in range(1, SPEED_STEPS + 1) if stepLevel(s, SPEED_STEPS) <= level ]
	return extractionPeriod(max(steps) if steps else 1)

# Absorption (FG_ABS_S, FG_ABS_A, FG_ABS_Q): the share of the risk impact of the property a brick removes. The terrain
# and group specialisations multiply it up to 0.8 (ForageExtractionAbsorption*SpecMax in the EGS configuration), so a
# harmful brick keeps some for them to multiply (a tenth: three tenths with a terrain specialisation), and a gentle one
# starts at half of that ceiling.
ABSORPTION_CEILING = 0.8
HARMFUL_ABSORPTION = 0.1
GENTLE_ABSORPTION = ABSORPTION_CEILING / 2

# The risk system of harvest_source.cpp and the EGS configuration: an extraction cycle adds MaxDeltaQ (26, code) times
# ForageQualityImpactFactor (1.5) to the bar bound to quality, less the absorption; a care cycle lasts
# 1 / (ForageCareSpeed 0.05 * 10) = 2 s and lowers a bar by its delta times ForageCareFactor (4).
QUALITY_IMPACT_PER_CYCLE = 26.0 * 1.5
CARE_PERIOD = 1.0 / (0.05 * 10.0)
CARE_FACTOR = 4.0

def careDelta(level):
	"""FG_PRES and FG_STAB of a care parameter of this level: enough to keep up with one harmful extractor working at the
	fastest speed of the same level, on the bar his quality drives"""
	impactPerSecond = QUALITY_IMPACT_PER_CYCLE * (1.0 - HARMFUL_ABSORPTION) / periodAtLevel(level)
	return round(impactPerSecond * CARE_PERIOD / CARE_FACTOR, 1)

def absorbSourceDamagePercent(step):
	"""FG_ABS_SRC_DMG of step 1..5: the share of the source's life impact the forager takes on his own hit points, ten
	more each step, up to half, as the explosion reduction steps go"""
	return 10 * step

def kamiAngerDecrease(items):
	"""KAMI_ANGER_DECREASE of an offering of this many items: each item calms the kamis as much as an hour of rest
	(ForageKamiAngerDecreasePerHour, 830 in the EGS configuration)"""
	return 830.0 * items

# ---- prospection properties
TIME_STEPS = 5

def prospectionTime(step):
	"""FG_TIME of the accelerated prospecting steps 1..5: each takes a sixth of the default 15 s off"""
	return DEFAULT_PROSPECTION_TIME * (1.0 - step / float(TIME_STEPS + 1))

# ---- learning
def spCost(level):
	return common.spCost(level)
