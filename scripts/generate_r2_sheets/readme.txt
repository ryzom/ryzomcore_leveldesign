# Generate sitem, sbrick, and sphrase
- Run extract_palette.py to generate sitem_list.txt and creature_list.txt from the R2 palette and merge in the _wk lists
- Run extract_parents.py to generate the parents txt files from the above, and missing sheets
- Run scheme_sitem_parser.py to generate sitem_parsed.tsv from sitem_list.txt minus missing_sheets.txt
- Run extract_shapes.py to list all shapes into shape_list.txt
- Run scheme_shape_parser.py to generate shape_parsed from shape_list.txt excluding _mission_ shapes
- Run sitem_shape_matcher.py to generate match_sitem_shape.tsv from shape_parsed.tsv and sitem_parsed.tsv
- Run extract_sbrick.py to generate the sbrick_index.tsv to ensure indices are correctly reused
- Run generate_sitem.py to generate sitems from the tsv, and the nation leader items from sitem_leaders.tsv

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

