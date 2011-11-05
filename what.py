from ID3 import *
from collections import Counter
import os, sys

DIFF_THRESH = 6

# string distance:
#   - 1 point for deletion
#   - 1 point for addition
#   - 10 point for change
def str_dist(a, b):
	if (abs(len(a) - len(b)) >= DIFF_THRESH): return DIFF_THRESH
	if (len(a) == 0): return len(b)
	if (len(b) == 0): return len(a)

	# Initialize
	edit = [range(len(b)+1)]
	for i in range(len(a)):
		edit.append([i+1] + [-1 for _ in b])

	# Recurrence
	def recur(i, j):
		if edit[i][j] < 0:
			# set cell if not set
			edit[i][j] = min(
							 recur(i, j-1) + 1,
							 recur(i-1, j) + 1,
							 recur(i-1, j-1) + (a[i-1]!=b[j-1] and 10 or 0)
							)
		return edit[i][j]

	# Final
	return recur(len(a), len(b))

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
	print "Usage: python what.py <path-to-music>"
	exit()

for root, _, files in os.walk(sys.argv[1]):
	for f in files:
		if os.path.splitext(f)[1] == ".mp3":
			try:
				id3info = ID3(os.path.join(root, f))
				artists.add(id3info['ARTIST'])
			except:
				pass

# Sample output for testing
# artists = set(['Sambassadeur', 'The New Pornographers', 'Panda Bear', 'Beirut', 'The Shins', 'Max\xefmo Park',
# 	'Apostle Of Hustle', 'Beulah', 'Kings Of Leon', 'Frog Eyes', 'The Seatbelts', 'Have A Nice Life', 
#     'Sunset Rubdown', 'MGMT', 'Explosions in the Sky', 'The Strokes', 'The Unicorns', 'Band Of Horses', 
#     'Radiohead', 'Broken Social Scene', 'Flying Lotus', 'Portishead', 'Anberlin', 'Portugal The Man', 
#     'Discovery', 'Rise Against', 'Modest Mouse', 'of Montreal', 'Muse', 'Fanfarlo', 'Mew', 'Portugal. The Man', 
#     'Led Zeppelin', 'Swan Lake', 'Mountain Goats', 'Moonface', 'Arctic Monkeys', 'Death Cab For Cutie', 
#     'Islands', 'Explosions In The Sky', 'The Smashing Pumpkins', 'Metric', 'Aphex Twin', 'Rogue Wave', 
#     'Beach House', 'Goo Goo Dolls', 'James Blake', 'Minus The Bear', 'Destroyer', "Carissa's Wierd",
#     'The Pillows', 'The Snake The Cross The Crown', 'Third Eye Blind', 'Passion Pit', 'Kings of Leon',
#     'Vampire Weekend', 'Wintersleep', 'The Flashbulb', 'Atlas Strategic', 'The Mars Volta', 'The Tallest Man On Earth', 
#     'Ra Ra Riot', 'Spoon', 'Portal', 'Death Cab for Cutie', 'Man Man', 'Of Montreal', 'Voxtrot', 
#     'Wolf Parade', 'Cursive', 'Kevin Drew', 'Bright Eyes', 'Gorillaz', 'The Delgados', 'Florence And The Machine', 
#     'Iron & Wine', 'Foals', 'Archive', 'Smashing Pumpkins', 'A.C. Newman', 'Coheed And Cambria', 'Arcade Fire', 
#     'Brendan Canning', 'R\xf6yksopp', 'Thom Yorke', 'Coldplay', 'Band of Horses', 'Karkwa', 'M83', 
#     'The Naked and Famous', 'Two Door Cinema Club', 'Neutral Milk Hotel', 'Ladyhawk', 'Animal Collective', 
#     'Chevelle', 'Peter Bjorn & John', 'Queens Of The Stone Age', 'Handsome Furs', 'Saltillo', 'Moving Mountains', 
#     'Starfucker', 'Sigur R\xf3s', 'Yoko Kanno', 'Weezer', 'The Antlers', 'Clap Your Hands Say Yeah'])
		

# load .ignore file
ignore = set()
try:
	for line in open(".ignore"):
		ignore.add(line[:-1])
except IOError:
	pass


artists = sorted(list(artists), cmp=lambda x,y: cmp(x.lower(), y.lower()))

artistMatch = [[None for i in range(len(artists))] for j in range(len(artists))]
final = []
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
		# Compare to artist
		for j in range(i+1, len(artists)):
			# Method 1: String editing score ---------------------------------------------
			# artistMatch[i][j] = str_dist(artists[i].lower(), artists[j].lower())
			# if artistMatch[i][j] < DIFF_THRESH and artists[i].lower() != artists[j].lower():
			# 	print artistMatch[i][j], artists[i], artists[j]
			# Method 2: Common characters % ----------------------------------------------
			# a, b = artists[i].lower(), artists[j].lower()
			# if len(a) - len(b) <= 6:
			# 	similars = sum([k for k in (Counter(a) & Counter(b)).values()])
			# 	if similars * 100 / max(len(a), len(b)) > 70:
			# 		print similars * 100 / max(len(a), len(b)), a, b
			# Method 3: Longest common subsequence as a % --------------------------------
			b = formatArtist(artists[j])
			lcsPerc = longest_subseq(a, b) * 100 / max(len(a), len(b))
			if lcsPerc > 70:
				sys.stderr.write("\n%-27s'%s'\n" % (("Detected duplicate (%d%%):" % lcsPerc), artists[i]))
				sys.stderr.write("%-27s'%s'\n" % ("", artists[j]))
				break
		else:
			final.append(artists[i])

print ", ".join(final)
