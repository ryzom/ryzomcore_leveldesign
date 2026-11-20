# Generate sitem, sbrick, and sphrase
- Run extract_palette.py to generate sitem_list.txt and creature_list.txt from the R2 palette and merge in the _wk lists
- Run extract_parents.py to generate the parents txt files from the above, and missing sheets
- Run scheme_sitem_parser.py to generate sitem_parsed.tsv from sitem_list.txt minus missing_sheets.txt
- Run extract_shapes.py to list all shapes into shape_list.txt
- Run scheme_shape_parser.py to generate shape_parsed from shape_list.txt excluding _mission_ shapes
- Run sitem_shape_matcher.py to generate match_sitem_shape.tsv from shape_parsed.tsv and sitem_parsed.tsv
- Run extract_sbrick.py to generate the sbrick_index.tsv to ensure indices are correctly reused
- Run generate_sitem.py to generate sitems from the tsv, the nation leader items from sitem_leaders.tsv, and the plot
  items of the Ring from sitem_plot_items.tsv

# Generate the plot items of the Ring
- Run generate_sitem.py (sitem_plot_items.tsv: item, icon, icon background; it writes sitem\scroll\r2_*.sitem)
- They are the items the scenario editor offers to make a plot item of: the client lists every item sheet with
  r2_plot_item in its name (200 at most, r2ed_max_num_plot_item_sheets), the scenario service takes r2_plot_item_0 to
  r2_plot_item_184 by name (CRingAccess::init), and a scenario holds the number of the sheet from sheet_id.bin
- So an item keeps its name, its number in sheet_id.bin and its icon for good. A new icon is a new line with the next
  number, which the scenario service must be told of
- The textures are in the interface atlas of the client (texture_interfaces_*.txt in interfaces.bnp). The generator
  does not check them: look a new one up there

# Generate the craft actions
- Run generate_craft_actions.py (Python 3). It writes the craft actions that the starting roles and missions teach, as
  sphrase\craft\recommended\abc?aca*.sphrase, each the root brick of a civilisation and category
  (sbrick\craft\root\bcpa*.sbrick) and the credit brick of its level (sbrick\craft\credit\recommended\bc?aca*.sbrick)
- The craft window of an action only offers the plans of the families listed in its root brick: the civilisation's own,
  plus the common and refugee ones. A character needs the Tryker armor action to use a Tryker armor plan
- The table holds the armor actions of level 1 for the four civilisations. Other categories and levels get their rows
  once their families and root indices are known
- It writes into R:\leveldesign (leveldesignRoot at the top of the script) and checks everything before the first sheet
  is written: the folders it writes into exist, no other file in game_elem, game_element or world has the name of one of
  its sheets, every sheet has its row in the sbrick or sphrase words of translation\work and of every language in
  translation\translated, and every brick has its row in sbrick_index.tsv (family, index, sheet name). A failed check
  names the file and what to do, and nothing is written
- Each sheet is reported as new, changed or unchanged, and only new and changed ones are written. The sheets come from
  the table: change the table, not the sheets
- A brick with a new index needs its row in sbrick_index.tsv before the run: add it by hand, the error gives the line.
  After the run the generator lists the rows of its bricks that are still marked __missing: remove those marks by hand.
  extract_sbrick.py would clear them too, but it runs on Python 2 only and rewrites every row that no longer matches the
  tree, such as the BIF rows that are marked __missing though their sheets exist, so its output is a change of its own

# Generate the nation leaders
- Run generate_sitem.py for their items (sitem_leaders.tsv: each a variant of a systematic item, on its own shape)
- Run generate_creature_npc_3dset.py for their looks (_parent_3dset/_leader_*.creature)
- Run generate_creature_npc.py leaders for their NPC sheets (npc/leader/leader_*.creature), without rewriting the ring sheets

# Python versions
- The scripts were written for Python 2. generate_sitem.py and generate_creature_npc_3dset.py give the same sheets with
  Python 2 and Python 3.
- generate_creature_npc.py does not: Python 3 integer division and float formatting change the ring sheets, so run it in
  full with Python 2 only, and with the argument leaders under Python 3. The leader sheets were written with Python 3; a
  full run with Python 2 rewrites their float values in its own format.

# Fix renamed sbrick
- Run extract_sbrick.py to update sbrick_index.tsv with the current bricks
- Run fix_rename_sbrick.py to rename sbrick and sphrase in leveldesign if their name changed

# Notes
ring melee hands: blunt pierce slash
ring magic hands: acid cold electricity fire poison rot shockwave
ring magic curser hands: blind fear madness root sleep slow snare stun
ring level: 1 2 3 4
creature levels: a(0-20) b(20-50) c(50-100) d(100-150) e(150-200) f(200-250)
creature levels: b1 b2 b3 b4 (b5 b6 b7) - variants within the level range

