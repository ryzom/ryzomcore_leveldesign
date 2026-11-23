# The brick and phrase generator

Every brick (`.sbrick`) and phrase (`.sphrase`) of the player actions comes from here: fight, magic, forage and
harvest, the craft actions and the craft plans, powers and auras, and the rest (interface bricks, timed actions, the
item power enchantment, training, characteristic upgrades, bonuses, titles), for every level up to 250. Change the
tables and the balancing, never the sheets.

Run it with Python 3 from this folder:

```
python generate.py                 # check every domain, write nothing, say what would change
python generate.py --write         # check, then write the sheets and remove the ones in its folders it does not make
python generate.py --domain magic  # one domain (its references to other domains then fail)
python generate.py --coverage      # the translation ids with no sheet yet, and the reasons of the excluded ones
python generate.py --complete      # also require every translation id, the sheets the code names, and what the
                                   # starting roles, missions and items name
python generate.py --atlas <dir>   # the interface atlas lists from that folder
```

The icons are checked against the interface atlas lists (`texture_interfaces_dxtc.txt`, `texture_interfaces_v3.txt`)
of the pipeline beside the leveldesign, `<leveldesign>/../pipeline/install/interfaces`, found from the script's place;
`--atlas` names another folder, and a missing list stops the run with its path and that option (`interface_atlas.py`,
which `../generate_r2_sheets/generate_sitem.py` uses too).

Run `../generate_r2_sheets/generate_sitem.py` first: it writes the items, among them the items the craft plans make,
and the plans domain checks that every plan's item exists. Then build the data (the leveldesign processes of
build_gamedata, which make the sheet ids and pack the sheets).

## What decides what

- **The translation is the list.** A sheet is named by its id in `translation/work/sbrick_words_wk.txt` or
  `sphrase_words_wk.txt`, so the texts apply as they are, in every language. An id that gets no sheet is excluded by its
  domain with a reason (`--coverage` lists them). A new action starts with its translation rows.
- **The code is the rule.** `code_tables.py` holds what the code fixes: the brick families and their kinds, the property
  keywords with their arguments and the counts the parser accepts, the skills, the string tables, the magic actions the
  service builds. Refresh it after a change to those files: `python refresh_code_tables.py <code folder>`.
- **The balancing is Ryzom Core's own.** `balancing/common.py` (the Sabrina point scale, learn gates, skill point
  prices, the creature references of `../generate_r2_sheets/balancing_config.py`) and one file per domain, each value
  a function of the level with the reason beside it.
- **The domains** (`domains/*.py`) arrange the families: parents (files starting with `_`, which get no sheet id) carry
  what a family's bricks share, and each domain owns its folders under `game_element`.

## What it checks before anything is written

Every sheet has its translation row (and every language has it); families, property keywords, argument counts and
types, skills, action natures, civilisations and grammar families are those of the code; family indices are 1 to 64
and unique (the interface families BIF and BIG excepted); every castable phrase passes the server's grammar and cost
check (`CPhraseManager::checkPhraseValidity`, replicated with its 16-bit sums) with its root first; no generated name
exists elsewhere in the folders the sheet ids are made from. The domains add their own: icons against the interface
atlases, the `$` tokens of the texts against the properties, levels and credits against what the texts state.

## The craft plans and their items

`plan_items.py` says which item each plan id makes and what kind of item an id is. The plans domain
(`domains/plans.py`, `balancing/plans.py`) writes a plan brick for every plan of the translation, with the components
its item takes, and `../generate_r2_sheets/generate_sitem.py` writes the items and names in each item the plan that
makes it (`CraftPlan`); both read the same table, so a plan and its item point at each other, and the plans domain
checks that every plan's item has its sheet and names that plan. A plan id that no rule of `plan_items.py` reads is an
error. The plans domain also checks that the raw materials (`game_element/sitem/raw_material`, from mp_generator) serve
every component a plan asks for up to quality 250, by the server's craft rule of the default build: a material counts
when the `CraftCivSpec` of its part for that component type is common or the origin of the plan's item, or that item
is common (the rule of the plan's `CivRestriction` against the material's ecosystem is that of `RYZOM_FORGE` builds).
Parts with a durability of 0 and the families only special items make (the kitin lairs' larva) do not count. And it
checks that the craft task of the Barkdell rite gives three whole sets of what its boots plan asks for (one to craft,
two spare), each counting for the boots.
