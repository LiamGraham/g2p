"""
Given a word list in a target language for which no specific model exists, find the most suitable adapted model. 
"""

import sh
import sys
import os
from typing import Dict, Set, List


phon = sh.phonetisaurus_apply
carmel = sh.carmel

MODEL_DIR = "/home/liam/university/2020/engg4801/anylang/high_resource/high_resource_openfst/"
MODELS = [MODEL_DIR + model for  model in os.listdir(MODEL_DIR)]

LANG_PATH = "/home/liam/university/2020/engg4801/anylang/lang2lang/lang.dists"
PHON_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.wfst"
DATA_PATH = "/home/liam/university/2020/engg4801/g2p/data"
OUTPUT_PATH = "/home/liam/university/2020/engg4801/g2p/output"
TABLE_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.table"

STATE_NAME = "S"
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


class Transition:
    """
    Single-state transition on 'in_lable' to 'out_label' with the given weight.
    """

    def __init__(self, state, in_label, out_label, weight=1):
        self.state = state
        self.in_label = in_label
        self.out_label = out_label
        self.weight = weight

    def __repr__(self):
        return f'({self.state} ({self.state} "{self.in_label}" "{self.out_label}" {self.weight}))'

    def __str__(self):
        return self.__repr__()


def get_lexicon(word_list, model) -> str:
    """
    Returns the directory of the best model for the given word list file.
    """
    return phon("--word_list", word_list, "--model", model)


def get_inventory(path: str) -> Set[str]:
    """
    Returns the set of phonemes stored in the .phon file at the given path.
    """
    with open(path, "r") as f:
        inventory = set(f.read().split(" "))
    return inventory


def generate_mapping(in_inv: Set[str], out_inv: Set[str], map_path: str) -> None:
    """
    S
    (S (S "I_1" "O_1" 1.0))
    (S (S "I_1" "O_2" 1.0))
    (S (S "I_1" "O_3" 1.0))
    ...
    """
    with open(map_path, "w") as mapping:
        f.write(state + "\n")
        for phon1 in in_inv:
            for phon2 in out_inv:
                trans = Transition(STATE_NAME, phon1, phon2)
                mapping.write(str(trans) + "\n")


def get_mappings(in_inv: Set[str], out_inv: Set[str], table_path: str):
    """
    Yields all mappings in the given table from phonemes in the input inventory to phonemes
    in the output inventory, skipping all others.
    """
    with open(table_path, "r") as table:
        for row in table:
            # Format: "i o 0.001\n"
            in_label, out_label, weight = row.strip().split("\t")
            if in_label not in in_inv:
                continue
            if out_label not in out_inv:
                continue
            yield Transition(STATE_NAME, in_label, out_label, float(weight))


def save_mappings(in_path: str, out_path: str, map_path: str):
    """
    Saves mappings for input and output inventories at the given paths.
    """    
    in_inv = get_inventory(in_path)
    out_inv = get_inventory(out_path)
    mappings = get_mappings(in_inv, out_inv, TABLE_PATH)
    with open(map_path, "w") as f:
        f.write(STATE_NAME + "\n")
        for m in mappings:
            f.write(str(m) + "\n")


def get_closest_phoneme(phoneme, map_path):
    carmel()


if __name__ == "__main__":
    #lang = Lang2Lang(LANG_PATH)
    #print(lang.get_distances("aal", "aap"))
    phon = Phon2Phon(PHON_PATH) 
    phon.get_distances("a")