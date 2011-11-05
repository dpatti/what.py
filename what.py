from ID3 import *
import os, sys

# If string lengths (after "The " has been removed) are longer than DIFF_THRESH,
# consider them different without computing
DIFF_THRESH = 6
def longest_subseq(a, b):
	if (len(a) == 0 or 
	    len(b) == 0 or 
	    abs(len(a) - len(b)) >= DIFF_THRESH): return 0
	if (a == b):
		return len(a)

	# Init
	longest = [[0]+[0 for j in b]]+[[0]+[None for j in b] for i in a]
	
	# Recurrence
	def recur(i, j):
		if longest[i][j] == None:
			longest[i][j] = max(
						        recur(i-1, j),
						        recur(i, j-1),
						        recur(i-1, j-1) + (a[i-1] == b[j-1] and 1 or 0)
						       )
		return longest[i][j]

	# Final
	return recur(len(a), len(b))

def stripThe(s):
	if s.find("the ") == 0:
		return s[4:]
	return s

formatCache = {}
def formatArtist(artist):
	if not artist in formatCache:
		formatCache[artist] = stripThe(artist.lower())
	return formatCache[artist]

artists = set()

if len(sys.argv) < 2:
	print "Usage: python what.py <path to music>"
	exit()

for root, _, files in os.walk(sys.argv[1]):
	for f in files:
		if os.path.splitext(f)[1] == ".mp3":
			try:
				id3info = ID3(os.path.join(root, f))
				artists.add(id3info['ARTIST'])
			except:
				pass

# load .ignore file
ignore = set()
try:
	for line in open(".ignore"):
		ignore.add(line[:-1])
except IOError:
	pass

# Sort and begin filtering
artists = sorted(list(artists), cmp=lambda x,y: cmp(x.lower(), y.lower()))

artistMatch = [[None for i in range(len(artists))] for j in range(len(artists))]
final = []
# For each artist found
for i in range(len(artists)):
	a = formatArtist(artists[i])
	# Compare to ignores
	for ign in ignore:
		b = formatArtist(ign)
		lcsPerc = longest_subseq(a, b) * 100 / max(len(a), len(b))
		if lcsPerc > 70:
			sys.stderr.write("\n%-27s'%s'\n" % (("Skipping (%d%%):" % lcsPerc), artists[i]))
			break
	else:
		# Compare to other artists
		for j in range(i+1, len(artists)):
			# We figure out the longest common subsequence between the two
			# artists (i.e., "ASDFJKL" and "A_S_J_L_K" yields "ASJL"). If the
			# found subsequence is more than 70% of the longest artist length,
			# we consider the two equal and do not add it to the final list
			b = formatArtist(artists[j])
			lcsPerc = longest_subseq(a, b) * 100 / max(len(a), len(b))
			if lcsPerc > 70:
				sys.stderr.write("\n%-27s'%s'\n" % (("Detected duplicate (%d%%):" % lcsPerc), artists[i]))
				sys.stderr.write("%-27s'%s'\n" % ("", artists[j]))
				break
		else:
			final.append(artists[i])

# Final output
print ", ".join(final)
