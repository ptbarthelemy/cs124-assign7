import re

"""
Read the document and translate the text word-by-word.
"""

class DirectTranslation:
	def __init__(self, dictionary):
		self.loadDictionary(dictionary)

	def loadDictionary(self, filename):
		self.dictionary = {}
		f = open(filename)
		for line in f.readlines():
			wf, we = re.findall("[^\n,]+", line)
			self.dictionary[wf] = we
		f.close()

	def translateText(self, filename):
		f = open(filename)
		for lineF in f.readlines():
			lineE = []
			for word in re.findall(r"[^\., '\n]+'?", lineF.lower()):
				lineE.append(self.dictionary[word])
			print "ORIGINAL   :", lineF.strip().lower()
			print "TRANSLATION:", ' '.join(lineE)
		f.close()

if __name__ == "__main__":
	model = DirectTranslation("../data/dictionary.txt")
	model.translateText("../data/source.txt")