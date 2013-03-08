from re import findall
from nltk import pos_tag
import pickle
import os.path

"""
Read the document and translate the text word-by-word.
"""

MONTHS = ['january','february','march','april','may','june','july','august','september','october','november','december']

def isDate(day, month):
	try:
		day = int(day) # if day is not an integer value, this will fail
		assert day <= 31 and day > 0 and month in MONTHS
		return True
	except:
		return False


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
			self.source.append(findall(r"([^\., '\n]+'?|[,.])", lineF.lower()))
		f.close()

	def translateText(self):
		self.target = []
		for lineF in self.source:
			lineE = []
			for word in lineF:
				if word in ".,":
					lineE.append(word)
				else:
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
			# print "TARGET1 :", target
			for i in range(len(target)):

				# RULE 1: NN JJ --> JJ NN
				if i < len(target) - 1:
					if target[i][1][:2] == 'NN' and target[i+1][1] == 'JJ':
						print "  switching", target[i][0], target[i+1][0]
						target.insert(i,target.pop(i+1))

				# RULE 2: NN VBG --> VBG NN  
				if i < len(target) - 1:
					if target[i][1][:2] == 'NN' and target[i+1][1] == 'VBG':
						print "  switching", target[i][0], target[i+1][0]
						target.insert(i,target.pop(i+1))

				# RULE 3: NN1 of NN2 --> NN2 NN1; from the French "NN1 d'/de NN2", which describes compound nouns in French
				# NOTE: This screws up on "passports of states of members of
				# the european union", which is a very difficult case due to
				# the many "of"s. This is probably worth discussing!
				# NOTE: ignore if this looks like a list
				if i < len(target) - 2:
					if target[i][1][:2] == "NN" and target[i+1][0] == 'of' and target[i+2][1][:2] == "NN":
						print "  fixing", target[i][0], target[i+1][0], target[i+2][0]
						target.insert(i, target.pop(i+2))
						target.pop(i+2)

				# RULE 4: "HOPE FOR" --> "PLEASE"
				if i < len(target) - 1:
					if target[i][0] == 'hope' and target[i+1][0] == 'for':
						print "  replacing", target[i][0], target[i+1][0]
						target.pop(i+1)
						target[i] = ("please", "NN") # according to NLTK

				# RULE 5: "THE" (cardinal number) (month) --> (cardinal number) (month) 
				# SO SOMETHING LIKE "THE 30TH DECEMBER" SHOULD BECOME "30TH DECEMBER ONLY"
				if i < len(target) - 2:
					if target[i][0] == 'the' and isDate(target[i+1][0], target[i+2][0]):
						print "  removing", target[i][0]
						target.pop(i)
						print "  switching", target[i][0], target[i+1][0]
						target.insert(i,target.pop(i+1))

				# RULE 6: DELETE TWO WORDS IN A ROW THAT ARE THE SAME
				# SO "MAIL MAIL" --> "MAIL" OR "BYE BYE" --> "BYE"
				if i < len(target) - 1:
					if target[i][0] == target[i+1][0]:
						print "  removing", target[i+1][0]
						target.pop(i+1)

				# RULE 7: "NOT" VERB "NO" --> VERB "NO" [DELETE THE "NOT"]
				# TRANSLATED FROM THE FRENCH "NE" VERBE "AUCUNE"
				# ONLY NEED TO RETAIN THE LAST NO.
				# SO "NOT HAS NO" --> "HAS NO"
				if i < len(target) - 2:
					if target[i][0] == 'not' and target[i+1][1][:2] == 'VB' and target[i+2][0] == "no":
						print "  removing", target[i][0]
						target.pop(i)

				# RULE 8: "NOT" VERB "MORE" --> VERB "NO LONGER" 
				# TRANSLATED FROM THE FRENCH "NE" VERBE "PLUS"
				# THIS TRANSLATES AS "NO LONGER"
				if i < len(target) - 2:
					if target[i][0] == 'not' and target[i+1][1][:2] == 'VB' and target[i+2][0] == "more":
						print "  removing", target[i][0]
						target.pop(i)
						print "  replacing", target[i+1][0]
						target[i+1] = ("no", "DT")
						target.insert(i+2, ("longer", "JJR"))

				# RULE 9: "OF TO" --> "TO" [DELETE "OF"]
				# FRENCH OFTEN REQUIRES PREPS + INFINITIF, NOT NECESSARY
				# IN ENGLISH
				if i < len(target) - 1:
					if target[i][0] == "of" and target[i+1][0] == "to":
						print "  removing", target[i][0]
						target.pop(i)

				# RULE 10: "AT TO LEAVE OF" --> "FROM"
				# "A PARTIR DE" --> MORE LIKE "FROM"
				if i < len(target) - 3:
					if target[i][0] == "at" and target[i+1][0] == "to" and target[i+2][0] == "leave" \
					and target[i+3][0] == "of":
						for j in range(3):
							print "  removing", target[i+1][0]
							target.pop(i+1)
						print "  replacing", target[i][0]
						target[i] = ("from", "IN")


				###############################################################
				# More harm then good

				# # RULE X: IN IN --> IN
				# # "for of more loose news" --> "for more loose news"
				# if i < len(target) - 1:
				# 	if target[i][1] == "IN" and target[i+1][1] == "IN":
				# 		print "  removing", target[i+1][0]
				# 		target.pop(i+1)


			print "TARGET2 :", ' '.join(list(a for a,b in target)), "\n"

if __name__ == "__main__":
	modelname = "model.tmp"
	if os.path.isfile(modelname) and False:
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
