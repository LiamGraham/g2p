"""
Given a word list in a target language for which no specific model exists, find the most suitable adapted model. 
"""

import sh
import sys
import os
from typing import Dict, Set, List, Tuple


phon = sh.phonetisaurus_apply
carmel = sh.carmel

MODEL_DIR = "/home/liam/university/2020/engg4801/anylang/high_resource/high_resource_openfst/"
MODELS = [MODEL_DIR + model for  model in os.listdir(MODEL_DIR)]

LANG_PATH = "/home/liam/university/2020/engg4801/anylang/lang2lang/lang.dists"
PHON_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.wfst"
DATA_PATH = "/home/liam/university/2020/engg4801/g2p/data"
OUTPUT_PATH = "/home/liam/university/2020/engg4801/g2p/output"

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
    Single-state transition on 'in_label' to 'out_label' with the given weight.
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


class Mapping:
    """
    Uses a single-state WFST to map phonemes from an input inventory to those in an output inventory.
    """
    TABLE_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.table"
    STATE_NAME = "S"

    def __init__(self, in_path: str, out_path: str, map_path: str):
        self.input = get_inventory(in_path)
        self.output = get_inventory(out_path)
        self.map_path = map_path
        self._save_mappings()

    def get_closest(self, phoneme: str) -> Tuple[str, float]:
        """
        Returns the phoneme in the output inventory, as well as the corresponding distance, that is most similar to the given phoneme
        in the input inventory.
        """
        if phoneme not in self.input:
            raise ValueError(f"'{phoneme}' is not in the input inventory")
        result = carmel(sh.echo(f'"{phoneme}"'), "-silkOQ", 1, self.map_path).split(" ")
        closest = result[0]
        distance = float(result[1])
        return closest, distance        

    def _save_mappings(self) -> None:
        """
        Saves mappings for input and output inventories to .wfst file
        """    
        mappings = self._get_mappings()
        with open(self.map_path, "w") as f:
            f.write(self.STATE_NAME + "\n")
            for m in mappings:
                f.write(str(m) + "\n")
    
    def _get_mappings(self) -> Transition:
        """
        Yields all mappings in the phon2phon table from phonemes in the input inventory to phonemes
        in the output inventory, skipping all others.
        """
        with open(self.TABLE_PATH, "r") as table:
            for row in table:
                in_label, out_label, weight = row.strip().split("\t")
                if in_label not in self.input:
                    continue
                if out_label not in self.output:
                    continue
                yield Transition(self.STATE_NAME, in_label, out_label, float(weight))


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


if __name__ == "__main__":
    #mapping = Mapping(DATA_PATH + "/eng_2176.phon", DATA_PATH + "/deu_2184.phon", OUTPUT_PATH + "/eng_deu.wfst")
    #phonemes = ["θ", "ɪ", "ŋ", "kʰ"]
    
    mapping = Mapping(DATA_PATH + "/ben_2162.phon", DATA_PATH + "/eng_2176.phon", OUTPUT_PATH + "/eng_deu.wfst")
    phonemes = ["d̪ʱ", "a", "k", "a"]
    for phon in phonemes:
        closest, _ = mapping.get_closest(phon)
        print(closest)
