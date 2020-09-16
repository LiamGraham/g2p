"""
Extract phonemic inventories from data/phoible.csv, with one file per inventory.
"""

import csv

PHOIBLE_PATH = "/home/liam/university/2020/engg4801/g2p/data/phoible.csv"
DATA_PATH = "/home/liam/university/2020/engg4801/g2p/data"

def parse_data(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        phonemes = []
        # InventoryID, Allophones
        for row in reader:
            lang_code = row["Glottocode"]
            iso_code = row["ISO6393"]
            allophones = row["Allophones"].replace(" ", "\n")
            with open(f"{DATA_PATH}/{iso_code}_{lang_code}.phon", "a+") as f:
                f.writelines(allophones)
            break

def clear_dir(path):
    files = glob.glob(os.path.join(path, "*"))
    for f in files:
        os.remove(f)

if __name__ == "__main__":
    clear_dir(DATA_PATH)
    parse_data(PHOIBLE_PATH)
