"""
Given a word list in a target language for which no specific model exists, find the most suitable adapted model. 
"""

import sh
import sys
import os
import re
from typing import Dict, Set, List, Tuple
from uuid import uuid4
import glob
from textdistance import Levenshtein

phon = sh.phonetisaurus_apply
carmel = sh.carmel


LANG_PATH = "/root/uni/anylang/lang2lang/lang.dists"
PHON_PATH = "/root/uni/anylang/phon2phon/ipa.bitdist.wfst"
DATA_PATH = "data"
INV_PATH = "/root/uni/g2p/g2p/inventories"
LEX_PATH = "/root/uni/g2p/g2p/lexicons"
MAPPER_PATH = "/root/uni/g2p/g2p/mappers"

NULL_PRON = "-"

class LexiconError(Exception):
    pass


class PronEntry:

    def __init__(self, word, pron):
        self.word = word
        self.pron = pron

    def compare(self, other: "PronEntry") -> float:
        """
        Returns the normalised Levenshtein distance between the pronunciations
        of this entry and the given entry. 
        """
        longest = max(len(self.pron), len(other.pron))

        distance = Levenshtein().distance(self.pron, other.pron)
        norm = distance / longest
        return norm

    def __repr__(self):
        return f"{self.word} {self.pron}"

    def __str__(self):
        return self.__repr__()


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

    def get_all(self, threshold: float=1.0):
        """
        Returns all pairs of languages (where lang1 != lang2) with distances less than or equal to the given threshold. 
        """
        with open(self.path, "r") as f:
            # Skip initial column names row
            f.readline()
            for line in f:
                columns = line.strip().split("\t")
                lang1 = columns[0]
                lang2 = columns[1]
                dist = float(columns[2])
                if dist <= threshold and lang1 != lang2:
                    yield (lang1, lang2, dist)

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


def get_inventory(path: str) -> Set[str]:
    """
    Returns the set of phonemes stored in the .phon file at the given path.
    """
    with open(path, "r") as f:
        inventory = set(f.read().split(" "))
    return inventory


class Mapper:
    """
    Uses a single-state WFST to map phonemes from an input inventory to those in an output inventory.
    """
    TABLE_PATH = "/root/uni/anylang/phon2phon/ipa.bitdist.table"
    STATE_NAME = "S"

    def __init__(self, in_path: str, out_path: str, map_path: str):
        self.input = get_inventory(in_path)
        self.output = get_inventory(out_path)
        self.map_path = map_path
        self._save_mappings()

    def convert_pronunciation(self, pron: str) -> Tuple[str, float]:
        """
        Returns the pronunciation using phonemes in the output inventory that best
        corresponds to the given pronunciation. 
        """
        if pron == NULL_PRON:
            return NULL_PRON
        formatted = " ".join([f'"{phon}"' for phon in pron.split(" ")])
        result = carmel(sh.echo(formatted), "-silkOQW", 1, self.map_path).strip()
        return result      
    
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


class Converter:
    INV_PATH = "/root/uni/g2p/g2p/inventories"
    LEX_PATH = "/root/uni/g2p/g2p/lexicons"
    MAPPER_PATH = "/root/uni/g2p/g2p/mappers"

    def __init__(self, word_list: str, inventory: str, model: str):
        """
        Creates a new Converter to generate a lexicon for the word list and inventory at the given paths
        """
        self.word_list = word_list
        self.inventory = inventory 
        self.model = model

        self._high_inv_path = os.path.join(self.INV_PATH, uuid4().hex)
        self._base_lex_path = os.path.join(self.LEX_PATH, uuid4().hex)

        self._generate_lexicon()
        self._extract_inventory()

        mapper_path = os.path.join(self.MAPPER_PATH, uuid4().hex)
        self.mapper = Mapper(self._high_inv_path, inventory, mapper_path)
        self.lexicon = Lexicon(self._base_lex_path)

    def _generate_lexicon(self) -> str:
        """
        Generates and saves lexicon using the word list and model at the given paths. 
        """
        command = phon("--word_list", self.word_list, "--model", self.model)
        if command.exit_code != 0:
            raise LexiconError(f"Could not create lexicon for {self.word_list}")
        entries = str(command).split("\n")

        # Phonetisaurus does not include entries for words which have "no
        # pronunciation" (i.e. where model did not return pronunciation for the word)
        # To ensure consistency with the given word list, an "empty" entry (one with a pronunciation of "-") is 
        # included for each of these words.
        i = 0
        with open(self.word_list, "r") as f:
            for word in f:
                word = word.strip()
                entry = entries[i]
                if not entry.startswith(word):
                    entries.insert(i, f"{word}\t{NULL_PRON}")
                i += 1
        with open(self._base_lex_path, "w") as f:
            result = "\n".join(entries)
            f.write(result)

    def _extract_inventory(self):
        """
        Extracts the phonemic inventory from the pronunciation lexicon at the given path and
        saves it at the given out path.
        """
        inventory = set()
        with open(self._base_lex_path, "r") as lexicon:
            for line in lexicon:
                _, pron = re.split("\t", line)
                phonemes = [phon.strip() for phon in pron.split(" ")]
                inventory.update(phonemes)
        with open(self._high_inv_path, "w") as inv:
            inv.write(" ".join(inventory))

    def convert(self):
        self.lexicon.convert(self.mapper)
        return self.lexicon


class Lexicon:

    def __init__(self, path):
        self.entries = {}
        self.path = path
        self._load()

    def _load(self):
        self.entries = {}
        with open(self.path, 'r') as f:
            for line in f:
                word, pron = re.split(r"\s", line.strip(), maxsplit=1)
                entry = PronEntry(word, pron)
                self.entries[word] = entry

    def save(self, path=None):
        """
        Saves this lexicon to a file at the specified path, if one is given.
        Otherwise, saves to the file at the original path. 
        """
        if not path:
            path = self.path
        with open(path, "w") as f:
            for entry in self.entries.values():
                f.write(str(entry) + "\n")

    def convert(self, mapper: Mapper):
        """
        Converts each of the pronunciations in this lexicon using the given mapper.
        """
        for entry in self.entries.values():
            entry.pron = mapper.convert_pronunciation(entry.pron)

    def update(self, prons):
        """
        Updates the pronunciations of each of the entries in this entries to
        the given pronunciations (in the given order).
        """
        if len(prons) != len(self.entries):
            raise LexiconError("Number of pronunciations is not equal to the number of entries")
        for i, pron in enumerate(prons):
            self.entries[i].pron = pron

    def distances(self, other: "Lexicon"):
        """
        Returns the individual distances between each of the entries in this and
        the given lexicon.
        """
        distances = {}
        
        for word in self.entries:
            if word not in other.entries:
                continue
            entry1 = self.entries[word]
            entry2 = other.entries[word]
            distances[word] = entry1.compare(entry2)
        return distances

    def compare(self, other: "Lexicon") -> float:
        """
        Returns normalised distance between this lexicon and the given lexicon.
        Distances are only calculated for words that are shared between the two lexicons.
        """
        distances = self.distances(other)
        norm = sum(distances) / len(distances)
        return norm

    def lookup(self, word):
        """
        Returns the pronunciation corresponding to the given word.
        """
        if word not in self.entries:
            raise LexiconError(f"'{word}' is not in this lexicon")
        return self.entries[word]

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries.values())

    def __repr__(self):
        entries = "" if not self.entries else self.entries.values()[0]
        return f'Lexicon(entries=["{entries}"... ({len(self.entries)} entries)])'

    def __str__(self):
        return self.__repr__()

if __name__ == "__main__":
    pass