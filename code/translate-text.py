from re import findall
from nltk import pos_tag
import pickle
import os.path

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
			wf, we = findall("[^\n,]+", line)
			self.dictionary[wf] = we
		f.close()

	def readSource(self, filename):
		self.source = []
		f = open(filename)
		for lineF in f.readlines():
			self.source.append(findall(r"[^\., '\n]+'?", lineF.lower()))
		f.close()

	def translateText(self):
		self.target = []
		for lineF in self.source:
			lineE = []
			for word in lineF:
				lineE.extend(self.dictionary[word].split())
			self.target.append(lineE)

	def posTagging(self):
		self.targetPosTags = []
		for line in self.target:
			posLine = []
			for word in line:
				posLine.extend(pos_tag([word]))
			self.targetPosTags.append(posLine)
			print posLine

	def rearrangeWords(self):
		for source, target in zip(self.source, self.targetPosTags):
			print "SOURCE  :", ' '.join(source)
			print "TARGET1 :", ' '.join(list(a for a,b in target))
			for i in range(len(target)):

				# RULE 1: NN JJ ->> JJ NN
				if i < len(target) - 1:
					if target[i][1] == 'NN' and target[i+1][1] == 'JJ':
						print "  switching", target[i][0], target[i+1][0]
						temp = target[i]
						target[i] = target[i+1]
						target[i+1] = temp

#				# RULE 2: NN1 NN2 ->> NN2 NN1   ### THIS COMMENT WILL BE CLEANED UP(french probably got it wrong)
#				if i < len(target) - 1:
#					if target[i][1] == 'NN' and target[i+1][1] == 'NN':
#						print "  switching", target[i][0], target[i+1][0]
#						temp = target[i]
#						target[i] = target[i+1]
#						target[i+1] = temp

				# RULE 3: NN VBG ->> VBG NN  ### THIS COMMENT WILL BE CLEANED UP(french probably got it wrong)
				if i < len(target) - 1:
					if target[i][1] == 'NN' and target[i+1][1] == 'VBG':
						print "  switching", target[i][0], target[i+1][0]
						temp = target[i]
						target[i] = target[i+1]
						target[i+1] = temp

				# RULE 4: NN1 of NN2 -> NN2 NN1; from the French "NN1 d'/de NN2", which describes compound nouns in French
				if i < len(target) - 2:
					if target[i][1] == 'NN' and target[i+1][0] == 'of' and target[i+2][1] == 'NN':
						print "  fixing", target[i][0], target[i+1][0], target[i+2][0]
						target.pop(i+1)
						temp = target.pop(i+1)
						target.insert(i, temp)


			print "TARGET2 :", ' '.join(list(a for a,b in target)), "\n"

if __name__ == "__main__":
	modelname = "model.tmp"
	if os.path.isfile(modelname):
		print "Loading preexisting model..."
		model = pickle.load(open(modelname, "rb"))
	else:
		print "Creating new model..."
		model = DirectTranslation("../data/dictionary.txt")
		model.readSource("../data/source.txt")
		model.translateText()
		model.posTagging()
		pickle.dump(model, open(modelname, "wb"))

	model.rearrangeWords()
