"""scan_rewards.py PRIMITIVES_DIR : missions whose failure-protected reward run holds two or more item grants.

A 'failure' block followed by several recv_item/recv_named_item actions (before the next jump_point, failure
block or objective) re-grants the earlier items when a later one fails for room and the handler jumps back."""
import sys, os, re, html

ITEM = re.compile(r'^(recv_item|recv_named_item)\s*:')
STOP = re.compile(r'^(jump_point|failure|talk_to|kill_|target_|give_item|give_money|loot_|craft|forage|visit|cast|buy|sell|wait|escort|skill|ring_scenario|dyn_chat|queue_start|ooo|any|/ooo|/any|teleport|encyclo|day_period|season|player_reconnect|crash|end)\b')
root = sys.argv[1]
out = []
for dp, dn, fn in os.walk(root):
	if '_unpublished_' in dp:
		continue
	for f in fn:
		if not f.endswith('.primitive'):
			continue
		path = os.path.join(dp, f)
		s = open(path, 'rb').read().decode('utf-8', 'replace')
		for m in re.finditer(r'<NAME>script</NAME>(.*?)</PROPERTY>', s, re.S):
			start_line = s.count('\n', 0, m.start()) + 1
			lines = re.findall(r'<STRING>(.*?)</STRING>', m.group(1), re.S)
			lines = [html.unescape(l).strip() for l in lines]
			name = None
			hdr = s.rfind('<NAME>name</NAME>', 0, m.start())
			mm = re.search(r'<NAME>name</NAME>\s*<STRING>(.*?)</STRING>', s[hdr:m.start()], re.S)
			if mm:
				name = mm.group(1)
			full = any(l.startswith('fail_if_inventory_is_full') for l in lines)
			i = 0
			while i < len(lines):
				if lines[i] == 'failure':
					j = i + 1
					while j < len(lines) and lines[j] != '/failure':
						j += 1
					handler = lines[i + 1:j]
					k = j + 1
					items = []
					while k < len(lines) and not STOP.match(lines[k]):
						if ITEM.match(lines[k]):
							items.append(lines[k])
						k += 1
					if len(items) >= 2 and handler:
						out.append((os.path.relpath(path, root).replace(os.sep, '/'), start_line, name, full, handler, items))
					i = j
				i += 1
for p, ln, name, full, handler, items in out:
	print('%s:%d\t%s\tfull=%s\t%s\t%s' % (p, ln, name, full, ' | '.join(handler), ' ; '.join(items)))
print('total', len(out))
