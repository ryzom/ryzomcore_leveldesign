# Ryzom Core's raw material tables

The tables `mp_generator` (`code/ryzom/tools/leveldesign/mp_generator`) makes the raw materials from: their families
and stats, which component types of a craft plan each family serves, the creature models and what each gives when
quartered. `make_tables.py` writes them from the rules below, which are Ryzom Core's own balancing; no value is taken
from Nevrax's tables (the old `rm_fam_prop.csv`, `rm_item_parts.csv` and `creature_models.csv` beside the tool are no
longer read). The identification columns of the families (group, location, icon) agree with the old `rm_fam_prop.csv`
kept beside mp_generator.

## Running

```
python make_tables.py                 # the four tables, from the translation, the code and the Ring's creatures
mp_generator                          # from a folder with raw_material_generation.cfg, TablePath naming this folder
python component_sources.py           # component_sources.tsv and the generated part of the interface below
python ../generate_core4_sheets/generate.py --domain forage   # the forage filters still find their materials
```

`make_tables.py` reads, besides the leveldesign that holds it (the DFN types `item_mp_family.typ` and
`item_mp_group.typ`, the translation's `item_words_wk.txt` and `sbrick_words_wk.txt`, the creature sheets and
`../generate_r2_sheets/creature_fauna.tsv`):

- the code's `ryzom/common/src/game_share/rm_family.h` and `rm_family.cpp`, from the code checkout beside the
  leveldesign (`<leveldesign>/../code`; `--code` names another);
- the interface atlas lists `texture_interfaces_dxtc.txt` and `texture_interfaces_v3.txt`, which every icon must be in,
  from the pipeline beside the leveldesign (`<leveldesign>/../pipeline/install/interfaces`; `--atlas` names another).

Both defaults come from the script's own place, not the working folder. A missing input stops it with its path and the
option to pass; it writes the four tables only when every check has passed, each to a temporary file first, then renames
them over the tables.

The tool writes, in the leveldesign: the raw material sheets
(`game_element/sitem/raw_material`, and removes the ones the tables no longer make), the quartering tables of the
creatures (`_<creature>_mp.creature` below `game_elem/creature`), the deposit family list of the World Editor
(`game_element/deposit_system/mps`), the family icons (`_ic_families.forage_source`) and the English names of new
sheets (`translation/work/item_words_wk.txt`).

What the tool owns, and what stops it:

- It makes everything in memory and checks it first. Only when every check has passed does it write the files whose
  content changes, each whole to a temporary file beside it (`<file>.mp_generator_tmp`, every write and the close
  checked); once all of them are written it renames each over its file, then removes the stale ones. A stop before the
  renames, a failed write included, leaves the leveldesign as it was (the temporary files go); a failed rename or
  removal stops the run naming the file, with the files before it done: run again once the cause is fixed. A
  temporary file that a stopped run left beside any file this run makes stops the run before anything is written,
  naming it.
- Its own folders (`raw_material/_parent`, `common`, `desert`, `forest`, `jungle`, `lacustre`, `prime_roots` and
  `deposit_system/mps`) hold only files of the names it gives (`m<family><code><ecosystem><class><variant>.sitem`
  with the folder's ecosystem letter; `_m<family>.sitem`, `_m<ecosystem>.sitem`, `_mc<model>.sitem`;
  `<family>_<number>.mp`). It removes only those, and a file of any other name there, or a folder, stops the run before
  anything is written. On Windows the folder listing does not see files with the system attribute (`desktop.ini`,
  `Thumbs.db`): those are neither checked nor removed.
- In a creature's quartering table it owns the materials of the creature models of its tables (`m<family>c<model>...`):
  those of an earlier run give way to this run's. Every other entry (a hand-placed invasion or deposit item, anything
  else) stays as it is, in front; its own entries are recognised in any case, with or without `.sitem`. A creature's
  `system_mp` placeholder goes once it has materials of its own; a creature that would be left with an empty table, or
  a table with an empty entry (`<STRUCT Name="MPn"/>`), stops the run.
- Before it removes a sheet, a parent or a deposit family file the tables no longer make, it reads the leveldesign
  (all but its own outputs, its tables, the translation and the build's sheet lists) and `raw_material_generation.cfg`
  for that name, with or without its extension, and stops if anything names it. The cfg's CustomizedProperties must
  name sheets the run makes.
- It stops on a table it cannot read as written, naming the table, the line and the rule: a header that is not the one
  `make_tables.py` writes, duplicate columns, lines or codes (a family twice in any case of its letters), a line with an
  empty first cell after the header, a family line with too few cells, an item part or level code line without a cell
  per column, a family or group not in the DFN types, a family number that is not 0 to 9999, a family name with other
  characters than letters, digits, space, ' and -, a craft part twice, a specialty without a weakness, a weakness
  without a specialty or equal to it, stats for a part a family does not serve, a location, an attribute or a
  special-only mark it does not know, a colour that is not a number up to 999, a creature family no model has, a model
  with no creatures, a creature of zone g to j, a creature sheet that does not name its quartering table as parent, two
  creature sheets of one name, a special item that is not six fields with none empty but the article, one given twice,
  with bad letters or with the name of a sheet its family already makes. Cells are read without their surrounding
  blanks, and blank lines are skipped in every table. It also stops on a quartering table entry or a family icon file
  (`_ic_families.forage_source`) it cannot read as written, naming the file and the line or the rule.
- The folders of the creatures and of their quartering tables must exist; the tool creates only the folders of its
  own outputs, when it writes them.

## The tables

All four are `;`-separated, and blank lines are skipped. Each has its header as its first line (in `rm_fam_prop.csv`
and `creature_models.csv` its first cell is empty), and every other line is data: there are no comment lines.

### rm_fam_prop.csv: the families

One line per raw material family (the names are those of `item_mp_family.typ`, the translation's `mpfam` texts).

| Column | What |
| --- | --- |
| 1 | The family. |
| 2 Group | Its group (`item_mp_group.typ`); the forage filters and the missions use it. |
| 3 Craft parts | The component types it serves, as the letters of `RM_FABER_TYPE` (A MpL Blade ... Z MpMF Magic focus); empty for a mission material. The first is its main use. |
| 4 Attributes | `R` used as a craft requirement, `D0`/`D1` cannot or can be dropped and sold (default: craft materials can), separated by `-`. None used. |
| 5 | Not read. |
| 6 Location | `D` deposits, `C` creatures, `G` goo creatures, `I` and the letters of the creature kinds that give them for invasion and goo rewards (special items only). |
| 7 Icon | The icon (an interface atlas name, `.tga` as the sheets write it). |
| 8 to 10 | Not read. |
| 11 to 13 BestA, WorstA1, WorstA2 | In the first part: the stat the family is strong in and the one or two it pays with, by the names of `_item_faber_mp_parameters.dfn`. |
| 14 to 16 BestB, WorstB1, WorstB2 | The same in the second part. |
| 17 Color | An index into the colours the tool gives a class and ecosystem (common Basic and Fine: Beige, Green, Turquoise, Violet; the regions' Choice and above: Red, Blue; prime roots: White, Black). |
| 18 | Not read. |
| 19 Special only | `x` or `X`: the family has only the special items of column 20 on. |
| 20 on | Special items: `<ecosystem><class letter>/singular/article/definite article/plural/plural article`; only the article may be empty. |

### rm_item_parts.csv: the stats of each component type

The header names the stats; a component type carries the stats whose cell has an `X`. It is the code's
`RM_FABER_STAT_TYPE::isStatRelevant` (`rm_family.cpp`): the stats the server adds up for a material in that slot. A
material must carry all of them: a stat its sheet leaves out counts as 0 (the default of `int.typ`). Nevrax's table
had the jewel parts with durability and weight only, so its jewels and settings protected and resisted nothing.

### creature_models.csv: the creature models

Code (the two letters of the creature sheet names, `c<code><ecosystem><zone><digit>`), name (the first word of its
families' names), category. These are the models of the Ring's creature table
(`../generate_r2_sheets/creature_fauna.tsv`) that have creature sheets and families: fauna and flora.

### rm_creature_classes.csv: the class of a creature's materials

The level code of a creature sheet (zone letter and digit: 1 to 4 the four strengths of a zone, 5 to 8 its bosses) and
the class of its craft materials, or `-` for none: local level 6 gets none, as the server never quarters a craft
material from a creature of that level (`egs_static_harvestable.cpp`).

## The model

### Which families

- **Deposits**: the families the forage filters name (`BHFPRMFM*`, `sbrick_words_wk.txt`). Their last word is their
  group (Sap, Amber, Node, Fiber, Bark, Seed, Shell, Resin, Wood, Oil); the families of the filters K to Q are the
  mission materials of Construction, Food, Goo, Insect, Kitin, Harmful (`Nocive`) and Preservative. Besides those, the
  mineral Atrium and the nations' order forms, military packages and tokens (mission items of the deposit system).
- **Creatures**: for each creature model, the families named `<Creature> <Part>` that have material names in
  `item_words_wk.txt`. The names say whether a part is a craft material (Basic ... Supreme) or a mission one
  (Plain ... Magnificient: meat and flesh, skulls, blood, hairs, Arana's moss, the plants' leaves and pistils).
  Kitin flesh is of the Kitin group, the other flesh and meat of Meat.
- **Specials**, kept as the server names them: the invasion kitins' claw (with the kitin trophy) and secretion
  (`m0077ixxcc01`, named in `egs_static_harvestable.cpp`), the goo part, the goo creatures' meat, and the kitin lairs'
  larva, a Supreme material for every component type that only a deposit naming it gives.

No family is new: every name must be in `item_mp_family.typ`.

### What serves what

Each material kind serves two component types: its main use, where its families are strong specialists, and a lesser
one. The uses follow what the material is:

| Kind | Main use | Second use | Why |
| --- | --- | --- | --- |
| Claw | Blade | Point | cuts, and its tip pierces |
| Fang | Blade | Ammo bullet | a long cutting tooth, a projectile tip |
| Mandible | Blade | Shaft | a jaw blade on a long arm |
| Sting | Point | Firing pin | pierces, and drives |
| Beak | Ammo bullet | Point | a hard pointed head |
| Spine | Point | Ammo bullet | needles |
| Pelvis | Hammer | Counterweight | heavy bone |
| Hoof | Counterweight | Hammer | heavy horn |
| Rostrum | Hammer | Shaft | a heavy snout on a long bone |
| Bone | Shaft | Armor clip | long bone, and bone fastenings |
| Tail | Firing pin | Shaft | springy, long |
| Wood (Arana) | Shaft | Armor shell | wood |
| Horn | Barrel | Ammo jacket | hollow horn |
| Trunck | Barrel | Armor shell | a leathery tube |
| Shell (carapace) | Armor shell | Barrel | carapace |
| Leather | Grip | Armor shell | grip wraps, leather armour |
| Skin | Clothes | Lining | soft hide |
| Secretion | Explosive | Lining | volatile, and a coating |
| Moss | Stuffing | Lining | padding |
| Wing | Ammo jacket | Stuffing | fletching and down |
| Whiskers | Stuffing | Trigger | padding, and fine springs |
| Ligament | Armor clip | Trigger | ties and springs |
| Nail | Trigger | Jewel setting | small hard parts |
| Tooth | Jewel setting | Ammo bullet | set like ivory, a projectile tip |
| Eye | Jewel | Magic focus | carries magic |
| Mushroom (Yelk) | Magic focus | Jewel | carries magic |
| Bud | Magic focus | Explosive | carries magic, bursts |

The ten deposit groups serve each of the twenty component types once, so that every plan can also be made from
foraged materials alone: Shell (Blade, Point), Node (Hammer, Counterweight), Wood (Shaft, Barrel), Bark (Armor shell,
Ammo jacket), Fiber (Clothes, Grip), Seed (Ammo bullet, Jewel setting), Amber (Jewel, Magic focus), Oil (Explosive,
Firing pin), Sap (Lining, Stuffing), Resin (Armor clip, Trigger). No material serves the tool parts (S to X): no plan
asks for them.

### The stats

The tool sets every stat a part carries to the level of the material's class (Basic 20, Fine 35, Choice 50, Excellent
65, Supreme 80), then the family's specialty up and its trade-off down: +40 with two weaknesses, +20 with one, -20 each,
so that the stats of a part add up to its class's total (and the class is its `StatEnergy`). A specialty stops at 100
and what it has above (5 at Excellent, 20 at Supreme) goes to the part's other stats, a point each in turn. The one
exception is durability: a material needs at least 1 (the server takes a part with none for absent), so a Basic
material weak in durability has 1 there, a point above its class. The tables say which stats:

- **Main use strong, second use mild**: two weaknesses in the main part, one in the second.
- **The trade-off** of a specialty: damage costs speed and speed damage, range costs damage, beating the dodge costs
  beating the parry and back, dodge costs parry and back, protection costs lightness, guarding against slashing
  leaves blunt blows open (blunt piercing, piercing slashing), an element's protection costs its opposite (fire and
  cold, acid and poison, electricity and shockwave, rot and fire), a resistance costs the unlike ecosystem (desert and
  lakes, forest and jungle, prime roots and desert), a magic's power costs its casting speed and back.
- **The second weakness**: hard materials (claws, bones, shells, wood, amber, seeds, resin ...) are heavy, soft ones
  (skins, secretions, moss, eyes, oil, sap, fibre ...) wear: lightness, or durability.
- **Creature materials take after the creature** (`creature_fauna.tsv`): in a weapon's head (blade, hammer, point) its
  blows: slashing gives damage, piercing beats the dodge, blunt beats the parry; in a barrel, firing pin or ammunition
  piercing gives range instead, and in ammunition slashing gives speed and blunt damage. In what holds a weapon
  (shaft, grip, counterweight, trigger) its defence: dodging creatures give dodge, parrying ones parry. In armour and
  clothes its hide: armoured all round (20 or more against all three) gives the protection factor, otherwise its
  strongest protection, otherwise its defence. In a jewel the element it resists more than the creatures do on
  average; in a jewel setting the resistance of the ecosystem it is most found in; in a magic focus the magic of its
  kind (herbivores heal, carnivores and birds the elements, kitins offensive affliction, plants defensive affliction),
  quick to cast for dodging creatures and strong for parrying ones.
- **Deposit families share out the specialties**: in the order of their family numbers, the families of a group take
  the main stats of a part in turn (heads: damage, speed, beating the parry, beating the dodge, parry, dodge,
  durability; and so on per part, `DEPOSIT_SPECIALTIES` in `make_tables.py`), so each group has a family for each
  specialty a crafter looks for. Their colours go round the same way.

### Classes and qualities

- **Deposits** (the tool): Basic (max quality 50) and Fine (100) in the common ecosystem, Choice (150), Excellent (200)
  and Supreme (250) in each of the five regions. A class covers a band of fifty qualities.
- **Creatures** (`rm_creature_classes.csv`): the class follows the zone of the creature, in the same bands of fifty
  levels (zones a and b up to level 50 Basic, c Fine, d Choice, e Excellent, f Supreme), and a zone's bosses give the
  next class (local level 6, which the server never quarters for craft materials, none). Basic and Fine materials are
  common, Choice and above carry the creature's ecosystem (the tool). Only creatures of the common ecosystem and the
  five regions get materials; the goo and invasion creatures keep what they have (the degenerated bosses, whose parts
  are all mission materials, keep their placeholder too).
- **Quality**: a quartered material has the creature's level as its quality (`Basics.XPLevel`, up to 250): the tool
  writes it as the `MinQuality`/`MaxQuality` of each entry of the creature's quartering table, which is what
  `CCharacter::harvest` gives (without it every quartered material came out at quality 5). Mission materials go by
  zone (Plain in zone a ... Magnificient in f), and the bosses give none. A creature's mission parts are not quartered
  like its craft materials: they reach the bag only for a mission that asks for them (`egs_static_harvestable.cpp`
  keeps them apart, `progression_pve.cpp` hands them out against the player's mission requirements).

## Interface for the craft plans

A plan slot (`Create.MP n`, `Quantity n`) names a component type of `RM_FABER_TYPE`. What serves each is the table
"What serves what" above. What matters for a plan:

- **Quality**: the crafted item's quality is at most the lowest quality among its materials, and at most the craft
  action's recommended level: the `CR_RECOMMENDED` of its option and credit bricks, lowered by the wear of the
  crafter's equipment (`faber_phrase.cpp`, `faber_action.cpp`). A foraged material's quality is at most the
  `deposit_max_quality_250` of its deposit primitive, and the sheet's `MaxQuality` (the class band above) only where
  the deposit gives none (-1, `harvest_source.cpp`); a quartered one has the creature's level.
- **Class** is the stat level, not a quality limit: a q200 item made of Basic materials has weak stats.
- **Civilisation**: a material counts for a component when the `CraftCivSpec` of its part for that component type is
  `common` or the origin of the item the plan makes, or that item is of common origin (the server's craft check of the
  default build, `faber_phrase.cpp`, and the client's craft window; the rule of the plan's `CivRestriction` against the
  material's ecosystem is that of `RYZOM_FORGE` builds). The tool writes the `CraftCivSpec` by the sheet's ecosystem:
  common and prime roots `common`, desert `fyros`, forest `matis`, jungle `zorai`, lakes `tryker`. So a Fyros item
  takes the common, prime roots and desert materials; a tribe, refugee, kami or karavan item the common and prime roots
  ones only; a common item any. Basic and Fine materials are all common, and every deposit family has Choice,
  Excellent and Supreme sheets in prime roots: every item can be made of every class from deposits.
- **Mission materials** (no craft part: construction, food, insects, meat, skulls ...) can only be asked for by sheet,
  in `MP formula n` slots.
- **Where they are**: the material sheets exist for every creature sheet of core4 and every deposit class, but the
  world places little of them yet. Only two creature sheets are placed (the Yubos `chdfa1` in the newbieland and
  `chdla1` at Barkdell), and only two deposit zones exist: Abhaya Wood `m0001dxacb01` in the newbieland, capped at
  quality 10, and Horny Shell `m0053dxacb01` at Barkdell, capped at 20. The rest needs fauna and deposit primitives.
  The ten Basic and Fine materials that `raw_material_generation.cfg` marks Saleable (one family of each deposit group:
  Abhaya Wood, Buo Fiber, Caprice Seed, Glue Resin, Horny Shell, Perfling Bark, Pha Amber, Redhot Sap, Irin Oil, Tansy
  Wood Node) together serve every component type.
- **The newbie set**: the Yubos of zone a and the four strengths of zone b (desert, forest, jungle and lakes) give
  Basic common Eye `m0688chdca01` (Jewel, Magic focus), Nail `m0690chdca01` (Trigger, Jewel setting), Pelvis
  `m0691chdca01` (Hammer, Counterweight), Skin `m0152chdca01` (Clothes, Lining) and Tooth `m0692chdca01` (Jewel
  setting, Ammo bullet); the zone-b boss (`chdfb5`) gives the Fine ones (`m0688chdcb01` ...). The Basic common deposit
  sheets are `m<family>dxacb01`.
- `component_sources.tsv` lists every material sheet with each component type it serves, its family and group, class,
  ecosystem, the `CraftCivSpec` of that part, quality (deposits: up to the sheet's max; creatures: the levels of the
  creatures that give it), the stat it is best in there, and how many creature sheets give it.

Per component type and class, the materials there are (deposits: their max quality and the `CraftCivSpec` of their
parts, common for the common ecosystem and prime roots; creatures: the number of families and the qualities they come
at). The kitin lairs' larva, Supreme for every type, is not counted.

<!-- generated by component_sources.py -->
| Type | Name | Basic | Fine | Choice | Excellent | Supreme |
| --- | --- | --- | --- | --- | --- | --- |
| A MpL | Blade | deposits q50 (common); 7 creature families q2-50 | deposits q100 (common); 10 creature families q62-103 | deposits q150 (common, fyros, matis, tryker, zorai); 21 creature families q108-159 | deposits q200 (common, fyros, matis, tryker, zorai); 32 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 41 creature families q197-250 |
| B MpH | Hammer | deposits q50 (common); 5 creature families q1-42 | deposits q100 (common); 12 creature families q47-95 | deposits q150 (common, fyros, matis, tryker, zorai); 11 creature families q97-145 | deposits q200 (common, fyros, matis, tryker, zorai); 19 creature families q149-208 | deposits q250 (common, fyros, matis, tryker, zorai); 16 creature families q195-250 |
| C MpP | Point | deposits q50 (common); 9 creature families q1-50 | deposits q100 (common); 13 creature families q49-103 | deposits q150 (common, fyros, matis, tryker, zorai); 20 creature families q98-159 | deposits q200 (common, fyros, matis, tryker, zorai); 27 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 31 creature families q197-250 |
| D MpM | Shaft | deposits q50 (common); 12 creature families q1-50 | deposits q100 (common); 14 creature families q62-103 | deposits q150 (common, fyros, matis, tryker, zorai); 25 creature families q108-159 | deposits q200 (common, fyros, matis, tryker, zorai); 37 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 42 creature families q197-250 |
| E MpG | Grip | deposits q50 (common); 6 creature families q1-47 | deposits q100 (common); 7 creature families q62-101 | deposits q150 (common, fyros, matis, tryker, zorai); 10 creature families q108-150 | deposits q200 (common, fyros, matis, tryker, zorai); 10 creature families q153-202 | deposits q250 (common, fyros, matis, tryker, zorai); 13 creature families q203-250 |
| F MpC | Counterweight | deposits q50 (common); 5 creature families q1-42 | deposits q100 (common); 12 creature families q47-95 | deposits q150 (common, fyros, matis, tryker, zorai); 11 creature families q97-145 | deposits q200 (common, fyros, matis, tryker, zorai); 18 creature families q149-196 | deposits q250 (common, fyros, matis, tryker, zorai); 15 creature families q195-250 |
| G MpGA | Trigger | deposits q50 (common); 11 creature families q1-47 | deposits q100 (common); 18 creature families q47-101 | deposits q150 (common, fyros, matis, tryker, zorai); 20 creature families q97-150 | deposits q200 (common, fyros, matis, tryker, zorai); 27 creature families q149-202 | deposits q250 (common, fyros, matis, tryker, zorai); 27 creature families q195-250 |
| H MpPE | Firing pin | deposits q50 (common); 6 creature families q2-50 | deposits q100 (common); 8 creature families q62-103 | deposits q150 (common, fyros, matis, tryker, zorai); 15 creature families q111-159 | deposits q200 (common, fyros, matis, tryker, zorai); 22 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 24 creature families q197-250 |
| I MpCA | Barrel | deposits q50 (common); 5 creature families q1-50 | deposits q100 (common); 8 creature families q57-103 | deposits q150 (common, fyros, matis, tryker, zorai); 11 creature families q102-159 | deposits q200 (common, fyros, matis, tryker, zorai); 19 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 20 creature families q197-250 |
| J MpE | Explosive | deposits q50 (common); 7 creature families q2-50 | deposits q100 (common); 7 creature families q58-100 | deposits q150 (common, fyros, matis, tryker, zorai); 11 creature families q108-159 | deposits q200 (common, fyros, matis, tryker, zorai); 15 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 18 creature families q197-250 |
| K MpEN | Ammo jacket | deposits q50 (common); 5 creature families q1-46 | deposits q100 (common); 7 creature families q57-103 | deposits q150 (common, fyros, matis, tryker, zorai); 8 creature families q102-154 | deposits q200 (common, fyros, matis, tryker, zorai); 7 creature families q153-204 | deposits q250 (common, fyros, matis, tryker, zorai); 6 creature families q200-250 |
| L MpPR | Ammo bullet | deposits q50 (common); 10 creature families q1-47 | deposits q100 (common); 18 creature families q47-101 | deposits q150 (common, fyros, matis, tryker, zorai); 20 creature families q97-150 | deposits q200 (common, fyros, matis, tryker, zorai); 27 creature families q149-202 | deposits q250 (common, fyros, matis, tryker, zorai); 27 creature families q195-250 |
| M MpCR | Armor shell | deposits q50 (common); 10 creature families q1-50 | deposits q100 (common); 13 creature families q60-103 | deposits q150 (common, fyros, matis, tryker, zorai); 19 creature families q103-159 | deposits q200 (common, fyros, matis, tryker, zorai); 28 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 32 creature families q197-250 |
| N MpRI | Lining | deposits q50 (common); 12 creature families q1-50 | deposits q100 (common); 19 creature families q47-100 | deposits q150 (common, fyros, matis, tryker, zorai); 23 creature families q97-159 | deposits q200 (common, fyros, matis, tryker, zorai); 33 creature families q148-211 | deposits q250 (common, fyros, matis, tryker, zorai); 33 creature families q195-250 |
| O MpRE | Stuffing | deposits q50 (common); 8 creature families q1-46 | deposits q100 (common); 10 creature families q49-103 | deposits q150 (common, fyros, matis, tryker, zorai); 13 creature families q108-154 | deposits q200 (common, fyros, matis, tryker, zorai); 11 creature families q154-204 | deposits q250 (common, fyros, matis, tryker, zorai); 12 creature families q199-250 |
| P MpAT | Armor clip | deposits q50 (common); 12 creature families q1-47 | deposits q100 (common); 13 creature families q62-101 | deposits q150 (common, fyros, matis, tryker, zorai); 19 creature families q108-150 | deposits q200 (common, fyros, matis, tryker, zorai); 21 creature families q153-202 | deposits q250 (common, fyros, matis, tryker, zorai); 27 creature families q203-250 |
| Q MpSU | Jewel setting | deposits q50 (common); 9 creature families q1-42 | deposits q100 (common); 19 creature families q47-95 | deposits q150 (common, fyros, matis, tryker, zorai); 17 creature families q97-145 | deposits q200 (common, fyros, matis, tryker, zorai); 28 creature families q149-196 | deposits q250 (common, fyros, matis, tryker, zorai); 22 creature families q195-250 |
| R MpED | Jewel | deposits q50 (common); 5 creature families q1-42 | deposits q100 (common); 12 creature families q47-95 | deposits q150 (common, fyros, matis, tryker, zorai); 11 creature families q97-145 | deposits q200 (common, fyros, matis, tryker, zorai); 18 creature families q149-196 | deposits q250 (common, fyros, matis, tryker, zorai); 15 creature families q195-250 |
| Y MpVE | Clothes | deposits q50 (common); 5 creature families q1-42 | deposits q100 (common); 12 creature families q47-95 | deposits q150 (common, fyros, matis, tryker, zorai); 11 creature families q97-145 | deposits q200 (common, fyros, matis, tryker, zorai); 17 creature families q149-196 | deposits q250 (common, fyros, matis, tryker, zorai); 14 creature families q195-250 |
| Z MpMF | Magic focus | deposits q50 (common); 9 creature families q1-43 | deposits q100 (common); 16 creature families q47-95 | deposits q150 (common, fyros, matis, tryker, zorai); 16 creature families q97-145 | deposits q200 (common, fyros, matis, tryker, zorai); 22 creature families q149-197 | deposits q250 (common, fyros, matis, tryker, zorai); 21 creature families q195-250 |
<!-- end of the generated part -->

## Translations

Sheets that the classic data had keep their names in every language. A sheet the tables make that had none gets an
English name in `item_words_wk.txt` from the tool, in the form of the English translation ("Choice Lakes ...", where
the classic work rows say "Lake"); the other languages need a translation (after this run: 528 sheets, the creature
materials of Choice and above in the regions that the classic creatures did not give; their rows in
`translation/translated` carry the English text for now).
