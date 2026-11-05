# Translation tools

Python 3 helpers for editing `translation/` without the NeL translation tools, keeping every byte of the
files outside the edited entries (UTF-8, BOM kept as found, line endings untouched). The editors check their
result before they write the file.

## Hashes

Every translated entry carries the `HASH_VALUE` of the work text it was translated from, in all languages.
The work texts are `translation/work/wk.uxt`, `work/phrase_wk.txt` with the files it `#include`s from
`work/phrases/`, and `work/*_words_wk.txt`. The translation tools compare the stored hashes with the hashes
of the work texts to find entries to retranslate, so:

- a change to a translation alone keeps the hash;
- a change to a work text (and to its copy in `translation/translated/*_wk.*`) needs the new hash in every
  language whose translation already matches the new text. Leave a translation that does not match with the
  old hash, so it shows up for retranslation.

The hashes are ports of the NeL code:

- `CI18N::makeHash` for uxt entries: the hash of the work text, with its escapes resolved (a `\n` hashes as a
  line break);
- `STRING_MANAGER::makePhraseHash` for phrases: parameters, then each clause's conditions, identifier and text;
- `makeHashCode` for the words sheets: all columns whose header starts with neither `*` nor `DIFF `, the id
  included, stored with a `_` prefix.

`clause_<lang>.txt` holds the named clauses of `phrase_<lang>.txt`. Edit both, or a later clause injection
reverts the phrase.

## Scripts

| Script | Use |
|---|---|
| `ryi18n.py` | Library: `make_hash`, `parse_phrases`, `phrase_hash`, `words_rows`, `words_hash`. `read_with_includes` reads a file with `#include` lines. |
| `uxt.py` | Library: `parse_uxt` and `parse_uxt_string` for `.uxt` and `clause_*.txt`. |
| `uxt_set.py FILE VALUES.tsv` | Sets the texts of existing keys from `key<TAB>text` rows (a literal `\n` is the newline escape). Hashes and indexes are kept. |
| `uxt_rehash.py KEY OLD NEW FILE...` | Replaces the `HASH_VALUE` of one key. |
| `uxt_tokens.py TRANSLATEDDIR LANG KEYS.tsv [--fix-trailing OUT.tsv]` | Compares placeholders, colour codes, newlines and trailing spaces of the listed keys with en; `--fix-trailing` writes OUT.tsv with the trailing spaces of en, for `uxt_set.py`. |
| `phrase_edit.py text FILE ID INDEX OLD NEW` | Replaces the text of one clause of a phrase. |
| `phrase_edit.py texts FILE EDITS.tsv` | The same for many clauses at once, from `ID<TAB>CLAUSE_IDENTIFIER<TAB>OLD<TAB>NEW` rows; with `uxt_set.py` on `clause_<lang>.txt` for the clause copies. |
| `phrase_edit.py hash FILE ID` | Prints the computed hash of a phrase (meaningful in work files) and the one stored before it. |
| `phrase_edit.py rehash ID OLD NEW FILE...` | Replaces the `HASH_VALUE` of one phrase. |
| `words_edit.py set/setcell/renameid/hash/rehash ...` | The same for the `*_words_*.txt` sheets. |
| `check_hashes.py TRANSLATIONDIR [-v]` | Per translated file, the entries whose hash matches the work text, the ones whose work text changed since, and the ones missing; `-v` lists them. |

Example, changing a work phrase and the languages that already say the right thing:

```
python phrase_edit.py text work/phrases/phrase_exchange_wk.txt SOME_PHRASE 0 "old text" "new text"
python phrase_edit.py text translated/phrase_wk.txt SOME_PHRASE 0 "old text" "new text"
python phrase_edit.py hash work/phrases/phrase_exchange_wk.txt SOME_PHRASE
python phrase_edit.py rehash SOME_PHRASE OLDHASH NEWHASH translated/phrase_wk.txt translated/phrase_en.txt ...
python check_hashes.py ../../translation
```
