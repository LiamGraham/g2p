"""
Given a word list in a target language for which no specific model exists, find the most suitable adapted model. 
"""

import sh
import sys
import os
from typing import Dict, List


phon = sh.phonetisaurus_apply
carmel = sh.carmel

MODEL_DIR = "/home/liam/university/2020/engg4801/anylang/high_resource/high_resource_openfst/"
MODELS = [MODEL_DIR + model for  model in os.listdir(MODEL_DIR)]

LANG_PATH = "/home/liam/university/2020/engg4801/anylang/lang2lang/lang.dists"
PHON_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.wfst"

# phonemic distance between a target language (given the phonemic inventory of that language) and a langauge in the model set


class Lang2Lang:
    CONSTS = {"None": None, "+": True, "-": False}
    
    def __init__(self, path):
        self.path = path
        self.distances = {}

    def get_distances(self, lang1, lang2):
        """
        Returns dictionary of distance values between lang1 and lang2
        """
        mappings = self.distances.get(lang1)
        if mappings and mappings.get(lang2):
            return mappings.get(lang2)
        elif not mappings:
            self.distances[lang1] = {}

        values = {}

        with open(self.path, "r") as f:
            column_names = f.readline().strip().split("\t")[2:]
            print(column_names)
            for line in f:
                if line[0:3] != lang1 or line[4:7] != lang2:
                    continue
                columns = line.strip().split("\t")[2:]
                for i, col in enumerate(columns):
                    if col in self.CONSTS:
                        value = self.CONSTS[col]
                    else:
                        value = float(col)
                    values[column_names[i]] = value
                break
        if values:
            self.distances[lang1][lang2] = values
        return values


class Phon2Phon:

    def __init__(self, path):
        self.path = path

    def _parse_transitions(self, transitions):
        pass

    def get_distances(self, phoneme: str):
        """
        Returns distances (weights - higher value means phones are more similar) between 
        given phoneme and all other phonemes.
        """
        print(f"Retrieving distances for '{phoneme}'")
        result = carmel(sh.echo(f"\"{phoneme}\""), "-sli", self.path)
        print(result)

def get_lexicon(word_list, model) -> str:
    """
    Returns the directory of the best model for the given word list file.
    """
    return phon("--word_list", word_list, "--model", model)

if __name__ == "__main__":
    #lang = Lang2Lang(LANG_PATH)
    #print(lang.get_distances("aal", "aap"))
    phon = Phon2Phon(PHON_PATH) 
    phon.get_distances("a")