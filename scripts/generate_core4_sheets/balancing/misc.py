# The balancing of the misc domain: the characteristic upgrades (BPP*), the score upgrades of training (BT*) and the
# permanent bonuses (BPB*). Ryzom Core's own tuning: no value here comes from the Ryzom Classic data.
#
# What the code does with these numbers:
# - CHARAC_UPGRADE: Characteristic:Modifier is added to the base characteristic when the brick is learnt
#   (CCharacter::processTrainingBrick), capped at MaxCharacteristicValue (changeCharacteristic). A characteristic point
#   is PhysicalCharacteristicsFactor score points (60 in patchman/default/entities_game_service.cfg, with
#   PhysicalCharacteristicsBaseValue 0): constitution gives hit points, strength stamina, intelligence sap, dexterity
#   focus; the other four set the regeneration of those scores. The characteristic check at login adds up the
#   modifiers of the known training bricks (checkCharacAndScoresValues).
# - SCORE_UPGRADE: Score:Modifier is added to the base score and kept as a permanent score modifier, outside the
#   characteristic and its cap.
# - BONUS_CR_DURABILITY adds to the durability factor of every item the character crafts (faber_action.cpp), after the
#   materials and the plan: the item's maximum hit points are base * (1 + factor), the factor of the materials running
#   from 0 to 1.
# - BONUS_FG_EXTRACTION_TIME_GC adds game cycles (tenths of a second) to the extraction time of every source the
#   character extracts (CHarvestSource::setBonusExtraExtractionTime). A source of quality Q takes
#   ForageExtractionTimeMinGC + Q * ForageExtractionTimeSlopeGC cycles (230 and 2 in the configuration: 25 s at
#   quality 10, 73 s at quality 250).

from balancing import common

# ---- characteristic upgrades
# A creature of level L has the scores of a characteristic of 10 + L (balancing_config.py: minCharacteristic 10, a score
# of 60 per point, the same 60 as PhysicalCharacteristicsFactor), so a characteristic point is worth one creature level.
# A character starts at 10 in each characteristic and the EGS caps them at MaxCharacteristicValue, 260 in the
# configuration: the characteristic of a level 250 creature (balancing_config.py maxCharacteristic).
CHARAC_START = int(common.creatures.minCharacteristic)
CHARAC_MAX = int(common.creatures.maxCharacteristic)

def characStep(count):
	"""the characteristic points of one upgrade: the upgrades of a characteristic (50 in the translation) share the
	points from the start to the cap evenly, so upgrade N brings it to the characteristic of a level N * step creature
	and the last one to the cap. None when they cannot share them evenly."""
	points = CHARAC_MAX - CHARAC_START
	return points // count if points % count == 0 else None

def characLevel(index, step):
	"""the level upgrade number index (1..) is made for: the creature level whose characteristic it brings the
	character to (one characteristic point is one creature level)"""
	return index * step

def characGate(index, step):
	"""the skill value a rolemaster asks before selling upgrade number index: the level it is made for, not ten levels
	below as common.learnGate does for actions. An action of a higher level is held back by the skill of the one who uses
	it (combat and magic scale with the skill), an upgrade is not: it applies in full the moment it is learnt. Gated at
	its own level, a character of skill L has at most the characteristic of a level L creature, which is what the Ring's
	creatures and NPCs were balanced against."""
	return characLevel(index, step)

# The price in skill points. A skill level gives SP_PER_SKILL_LEVEL points of its type (SpPointMultiplier, the DFN
# default 10 that xptable.xp_table keeps), so the levels one upgrade covers give SP_PER_SKILL_LEVEL * step points. Each
# rolemaster type sells four characteristics (rolemaster_flags.cpp: constitution and metabolism everywhere, then
# strength and balance for fight, intelligence and wisdom for magic, dexterity and will for craft and forage), and a
# character needs all four of them at every step to keep the scores of his level. They are not chosen like actions, so
# they are not priced like actions (common.spCost, 5 to 15 points): keeping the four level takes CHARAC_SP_SHARE of the
# points one line of skills gives, about 600 of the 2500 a line from 1 to 250 earns, and the rest buys the actions.
SP_PER_SKILL_LEVEL = 10
CHARACS_PER_ROLEMASTER = 4
CHARAC_SP_SHARE = 0.25

def characPrice(step):
	"""the SPCost of one characteristic upgrade (at least 1)"""
	return max(1, int(round(SP_PER_SKILL_LEVEL * step * CHARAC_SP_SHARE / CHARACS_PER_ROLEMASTER)))

# ---- score upgrades (training)
# No text gives the training bricks a level, no rolemaster sells them (no rolemaster prefix starts with bt) and a
# mission gives them with learn_brick or learn_action, which check nothing: they are rewards the mission designer
# places. Each one adds the score a creature gains in TRAINING_LEVELS_PER_BRICK levels, on top of the characteristic
# and past its cap: the twenty of a score, given over the 250 levels (one every 12 or 13 levels), keep a trained
# character some 8 % above an untrained one of his level, and lift a level 250 character from 15600 to 16800.
TRAINING_LEVELS_PER_BRICK = 1

def scorePerLevel():
	"""the score a creature gains per level (60 in balancing_config.py)"""
	return common.creatureScore(1) - common.creatureScore(0)

def trainingModifier():
	"""the SCORE_UPGRADE modifier of one training brick, the same for each of them and for the four scores (they all
	follow one characteristic each with the same factor)"""
	return int(round(scorePerLevel() * TRAINING_LEVELS_PER_BRICK))

# ---- permanent bonuses
# They are rewards too: no text gives them a level and no rolemaster sells them (bp is no rolemaster prefix, only bpp).
# The texts say the bonuses of a family add up, so each brick gives an equal share of what the whole family is worth.
#
# Durability: the materials give a factor of 0 to 1 (an item of the best materials lasts twice as long as the base); the
# five bonuses together are worth DURABILITY_FAMILY_SHARE of that range, so a crafter who earned them all makes items
# that last as if the materials were a quarter better, without making the materials matter less.
DURABILITY_FAMILY_SHARE = 0.25

def durabilityBonus(count):
	"""the BONUS_CR_DURABILITY of one brick of a family of count bricks"""
	return round(DURABILITY_FAMILY_SHARE / count, 4)

# Extraction time: the five bonuses together add EXTRACTION_FAMILY_SHARE of the shortest extraction time
# (ForageExtractionTimeMinGC, 230 cycles): six seconds in all, a quarter more time on a quality 10 source and about a
# twelfth on a quality 250 one, so the bonus counts most for those who forage low quality materials in quantity.
EXTRACTION_TIME_MIN_GC = 230.0 # ForageExtractionTimeMinGC in patchman/default/entities_game_service.cfg
EXTRACTION_FAMILY_SHARE = 0.25

def extractionTimeBonus(count):
	"""the BONUS_FG_EXTRACTION_TIME_GC of one brick of a family of count bricks, in whole game cycles: the code truncates
	the sum to whole cycles (CCharacter::computeForageBonus)"""
	return int(round(EXTRACTION_TIME_MIN_GC * EXTRACTION_FAMILY_SHARE / count))
