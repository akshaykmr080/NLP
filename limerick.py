#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')
entries = nltk.corpus.cmudict.entries()
vowels = ['a','A','e','E','i','I','o','O','u','U']

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()

    def checkSub(self, first, second):
        bigger =[]
        smaller = []

        if(len(first) > len(second)):
            bigger = first
            smaller = second
        else :
            bigger = second
            smaller = first

        i = 0
        for smallerData in smaller:
            if bigger[len(bigger) - len(smaller) + i] != smallerData:
                return False
            i = i+1
        return True

    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
        pronounciation = [];
        count = 0
        # TODO: provide an implementation!
        for wordData, pron in entries:
            tempCount = 0
            if(wordData == word):
                for char in pron:
                    for eachChar in char:
                        if(eachChar.isdigit()):
                            tempCount = tempCount +1
                if(count>tempCount or count == 0):
                    count = tempCount

        if(count > 0):
            return count
        else:
            return 1
    def is_Rhyming(self, a,b):


        firstWordSyllables = []
        secondWordSyllables = []
        firstvowelFound = False;
        scondvowelFound = False
        for word, pron in entries:
            if (word == a):
                firstWordSyllables.append(pron)

            if (word == b):
                secondWordSyllables.append(pron)

        for eachPron in firstWordSyllables:
            firstvowelFound = False;
            i = 0;
            for char in eachPron:
                if (char[0] in vowels):
                    firstvowelFound = True
                    break
                i = i+1
            if (firstvowelFound):
                firstStringToMatch = eachPron[i:]
            else:
                firstStringToMatch = ""

            for eachSecond in secondWordSyllables:
                secondvowelFound = False;
                j = 0;
                for charData in eachSecond:
                    if (charData[0] in vowels):
                        secondvowelFound = True
                        break
                    j = j+1
                if (secondvowelFound):
                    secondStringToMatch = eachSecond[j:]
                else:
                    secondconsonentFound = ""

                if (firstvowelFound and secondvowelFound):
                    if (self.checkSub(firstStringToMatch ,secondStringToMatch)):
                        return True
                elif (firstvowelFound and not secondvowelFound) :
                    return True
                elif (secondvowelFound and not firstvowelFound):
                    return True

        return False

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """

        # TODO: provide an implementation!

        if(self.is_Rhyming(a,b)):
            return True
        elif(self.is_Rhyming(b,a)):
            return True

        return False





    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """
        # TODO: provide an implementation!
        text = text.strip('"""').strip('\n').strip()
        lines = text.split("\n")
        Awords = []
        Bwords = []
        if(len(lines) != 5 and len(lines) != 7):
            return False
        i = 1
        for line in lines:
            lineData = re.sub('[^A-Za-z0-9\s]+', '', line)
            if(lineData == ''):
                continue
            if(i == 1 or i == 2 or i == 5):
                wordsArray = word_tokenize(lineData)
                Awords.append(wordsArray[-1])
            elif( i == 3 or i == 4):
                secondWordsArray = word_tokenize(lineData)
                Bwords.append(secondWordsArray[-1])
            i = i+1
        if(len(Awords) >=2):
            if(self.rhymes(Awords[0],Awords[1])):
                if(len(Bwords) >=2):
                    if(self.rhymes(Bwords[0],Bwords[1])):
                        if(len(Awords) == 3):
                            if(self.rhymes(Awords[1], Awords[2])):
                                return True
                            else:
                                return False
                        return True
            return False
        return False


# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()
