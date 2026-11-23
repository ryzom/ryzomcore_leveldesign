# Generate sitem
- Run extract_palette.py to generate sitem_list.txt and creature_list.txt from the R2 palette and merge in the _wk lists
- Run extract_parents.py to generate the parents txt files from the above, and missing sheets
- Run scheme_sitem_parser.py to generate sitem_parsed.tsv from sitem_list.txt minus missing_sheets.txt
- Run extract_shapes.py to list all shapes into shape_list.txt
- Run scheme_shape_parser.py to generate shape_parsed from shape_list.txt excluding _mission_ shapes
- Run sitem_shape_matcher.py to generate match_sitem_shape.tsv from shape_parsed.tsv and sitem_parsed.tsv
- Run generate_sitem.py to generate sitems from the tsv, the craft items no palette has from sitem_craft_items.tsv, the
  nation leader items from sitem_leaders.tsv, and the plot items of the Ring from sitem_plot_items.tsv. It writes into
  the leveldesign that holds it, or into the leveldesign folder its argument names (a copy, for a test run), and reads
  its tables beside itself, whatever the working directory:
  generate_sitem.py [--remove-stale [--code <code folder>]] [leveldesign folder]
- It makes and checks every row first and writes nothing on a failure, nor when a run that was stopped left a file
  beside any sheet it makes (<sheet>.generate_sitem_tmp). Then it writes the sheets whose content changes (LF, as the
  leveldesign stores them): each beside its sheet first, then, once all are written, each renamed over its sheet; a
  failure or an interruption deletes what was written beside them, names what it could not delete, and says how many
  sheets were replaced
- Stale sheets are those under sitem that start with its header (<FORM Version="4.0" State="modified">), that no row
  makes and that no table of this folder names: the sheet of a row that is gone, or a copy someone made of a generated
  sheet (a copy, or "save as" in Georges, keeps the header). By default it lists them and removes nothing. With
  --remove-stale it removes those that nothing names and lists the ones it keeps with the file that names each. It
  looks for them by their whole name, with or without .sitem, in the leveldesign and in the data folders of the code
  checkout that name item sheets (ryzom/common/data_common and ryzom/client/data of <leveldesign>/../code, found from
  the script's place; --code <code folder> names another, and a missing one stops it), and reads a stale sheet it keeps
  in turn for the stale sheets it names. It does not read translation/ (every item has word rows), the build's sheet
  lists (game_elem/sheets.txt, sheet_id.bin), the players' inventories or the saved scenarios: an item only those name
  is removed. An original sheet a table names (the refugee colours) and a sheet saved without its header are never
  stale

# Craft items
- generate_sitem.py writes the items only. The craft plans that make them are the plans domain of
  ../generate_core4_sheets; ../generate_core4_sheets/plan_items.py is the table both read: the item each plan makes,
  and the plan an item names in CraftPlan (an item no plan makes names none; a leader item names its base item's plan)
- sitem_craft_items.tsv (item, shape male, shape female, tags) holds the craft items the Ring palette has not: range
  weapons, ammunition, jewels, caster armor, staffs, the named advantage items, the kami and karavan faction items and
  shields, the construction pieces of the kami and karavan, the refugee items and tools, the common crafting and
  forage tools, the tool maker ittool (the tool plans need it in hand), Erouk'an's armor, the underwear of the plans,
  the candy cane and the Armlet of Atys. Each is named by its translation id. The plans domain
  reads its first column to know which items exist. Its tags are the words generate_sitem.py reads, as in
  sitem_parsed.tsv; a shape of - is an item no character shows (jewels and ammunition sit in hidden slots, the
  construction pieces have no slot)
- Their parents are in sitem_parents.tsv (the range weapons, ammunition, jewels, crafting and harvest tools,
  construction pieces, and the original staff parent _c_m1bs); an item takes the parent with the most of its tags
- generate_sitem.py fails, naming the item, on: an item of a plan without a sheet after the run, an item whose type is
  not the one its plan is made for, a shape not in shape_list.txt, an icon not in the interface atlas
  (../../../pipeline/install/interfaces/texture_interfaces_*.txt), an advantage or faction item without its fx, a craft
  item that is not in the translation
- The original sheets of the refugee colours (armor\refugee\default) and refugee weapons (icrm1pd, icrm2ms) stay as they
  are; they name the plans plan_items.py gives them

# Generate the plot items of the Ring
- Run generate_sitem.py (sitem_plot_items.tsv: item, icon, icon background; it writes sitem\scroll\r2_*.sitem)
- They are the items the scenario editor offers to make a plot item of: the client lists every item sheet with
  r2_plot_item in its name (200 at most, r2ed_max_num_plot_item_sheets), the scenario service takes r2_plot_item_0 to
  r2_plot_item_184 by name (CRingAccess::init), and a scenario holds the number of the sheet from sheet_id.bin
- So an item keeps its name, its number in sheet_id.bin and its icon for good. A new icon is a new line with the next
  number, which the scenario service must be told of
- The textures are in the interface atlas of the client (texture_interfaces_*.txt in interfaces.bnp). The generator
  does not check them: look a new one up there

# Bricks and phrases
- Every brick and phrase of the actions (fight, magic, forage, craft actions, powers, interface, training,
  characteristics) comes from ../generate_core4_sheets (generate.py, README.md there), which replaces
  generate_craft_actions.py. The craft plans too (the plans domain): generate_sitem.py no longer writes any brick or
  phrase

# Generate the nation leaders
- Run generate_sitem.py for their items (sitem_leaders.tsv: each a variant of a systematic item, on its own shape)
- Run generate_creature_npc_3dset.py for their looks (_parent_3dset/_leader_*.creature)
- Run generate_creature_npc.py leaders for their NPC sheets (npc/leader/leader_*.creature), without rewriting the ring sheets

# Python versions
- The scripts were written for Python 2. generate_creature_npc_3dset.py gives the same sheets with Python 2 and
  Python 3. generate_sitem.py needs Python 3.3 or later (it replaces each sheet in one step, os.replace).
- generate_creature_npc.py does not: Python 3 integer division and float formatting change the ring sheets, so run it in
  full with Python 2 only, and with the argument leaders under Python 3. The leader sheets were written with Python 3; a
  full run with Python 2 rewrites their float values in its own format.

# Fix renamed sbrick
- generate_sitem.py no longer reads sbrick_index.tsv
- Run extract_sbrick.py to update sbrick_index.tsv with the current bricks
- Run fix_rename_sbrick.py to rename sbrick and sphrase in leveldesign if their name changed

# Notes
ring melee hands: blunt pierce slash
ring magic hands: acid cold electricity fire poison rot shockwave
ring magic curser hands: blind fear madness root sleep slow snare stun
ring level: 1 2 3 4
creature levels: a(0-20) b(20-50) c(50-100) d(100-150) e(150-200) f(200-250)
creature levels: b1 b2 b3 b4 (b5 b6 b7) - variants within the level range

