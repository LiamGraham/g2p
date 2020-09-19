from typing import Set, List


DATA_PATH = "/home/liam/university/2020/engg4801/g2p/data"
PHON_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.wfst"
TABLE_PATH = "/home/liam/university/2020/engg4801/anylang/phon2phon/ipa.bitdist.table"

STATE_NAME = "S"

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


def get_inventory(path: str) -> Set[str]:
    """
    Returns the set of phonemes stored in the .phon file at the given path.
    """
    with open(path, "r") as f:
        inventory = set(f.read().split(" "))
    return inventory


def generate_mapping(inv_in: Set[str], inv_out: Set[str], map_path: str) -> None:
    """
    S
    (S (S "I_1" "O_1" 1.0))
    (S (S "I_1" "O_2" 1.0))
    (S (S "I_1" "O_3" 1.0))
    ...
    """
    with open(map_path, "w") as mapping:
        f.write(state + "\n")
        for phon1 in inv_in:
            for phon2 in inv_out:
                trans = Transition(STATE_NAME, phon1, phon2)
                mapping.write(str(trans) + "\n")


def get_pruned_mappings(inv_in: Set[str], inv_out: Set[str], table_path: str):
    """
    Yields all mappings in the given table from phonemes in the input inventory to phonemes
    in the output inventory, skipping all others.
    """
    with open(table_path, "r") as table:
        for row in table:
            # Format: "i o 0.001\n"
            in_label, out_label, weight = row.strip().split("\t")
            if in_label not in inv_in:
                continue
            if out_label not in inv_out:
                continue
            yield Transition(STATE_NAME, in_label, out_label, weight)


if __name__ == "__main__":
    inv_in = get_inventory(DATA_PATH + "/zoh_1021.phon")
    inv_out = get_inventory(DATA_PATH + "/zoc_646.phon")
    #generate_mapping(input_path, output_path, "mapping.wfst")
    mappings = get_pruned_mappings(inv_in, inv_out, TABLE_PATH)
    with open("pruned.carmel", "w") as f:
        f.write(STATE_NAME + "\n")
        for m in mappings:
            f.write(str(m) + "\n")
