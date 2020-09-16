"""
Extract phonemic inventories from data/phoible.csv, with one file per inventory.
"""
import csv
import os
import glob

PHOIBLE_PATH = "/home/liam/university/2020/engg4801/g2p/phoible.csv"
DATA_PATH = "/home/liam/university/2020/engg4801/g2p/data"

def parse_data(path):
    """
    Extracts phonemic inventories of langauges in phoible.csv. Each inventory is stored in a file with name
    <iso_code>_<inventory_id>.phon. Inclusion of inventory ID ensures that different inventories with the
    same ISO code are stored in separate files.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        phonemes = []
        for num, row in enumerate(reader):
            inv_id = row["InventoryID"]
            iso_code = row["ISO6393"]
            phones = row["Allophones"]
            if phones == "NA":
                # When no allphones are given, revert to phoneme
                phones = row["Phoneme"]
            # Eliminate alternation character (i.e. "|") and place all phones on separate lines
            phones = phones.replace("|", " ").replace(" ", "\n") + "\n"
            with open(f"{DATA_PATH}/{iso_code}_{inv_id}.phon", "a+") as f:
                f.write(phones)

def clear_dir(path):
    files = glob.glob(os.path.join(path, "*"))
    for f in files:
        os.remove(f)


if __name__ == "__main__":
    clear_dir(DATA_PATH)
    parse_data(PHOIBLE_PATH)
