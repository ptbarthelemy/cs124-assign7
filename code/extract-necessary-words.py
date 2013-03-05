import re

"""
This code simply extracts the words which we will need to define. Unfortunately
we cannot just use a text dictionary, as I cannot find one.
"""

if __name__ == "__main__":
	# read all words
	f = open("../data/source.txt")
	text = f.read().lower()
	f.close()
	words = re.findall(r"[^\., '\n]+'?", text)
	words = set(words)

	# save all words to be defined
	f = open("../data/source-words.txt", "w+")
	for word in sorted(list(words)):
		f.write(word + "\n")
	f.close()