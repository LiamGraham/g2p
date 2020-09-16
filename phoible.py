"""
Extract phonemic inventories from data/phoible.csv, with one file per inventory.
"""
import csv
import os
import glob

PHOIBLE_PATH = "/home/liam/university/2020/engg4801/g2p/phoible.csv"
DATA_PATH = "/home/liam/university/2020/engg4801/g2p/data"

def parse_data(phoible_path, data_path):
    """
    Extracts phonemic inventories of langauges in phoible.csv. Each inventory is stored in a file with name
    <iso_code>_<inventory_id>.phon. Inclusion of inventory ID ensures that different inventories with the
    same ISO code are stored in separate files.
    """
    clear_dir(data_path)
    with open(phoible_path, newline="", encoding="utf-8") as f:
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
            with open(f"{data_path}/{iso_code}_{inv_id}.phon", "a+") as f:
                f.write(phones)

def clean_data(path):
    print("Cleaning", path)
    with open(path, "r") as f:
        lines = f.readlines()
    cleaned = set(lines)
    diff = len(lines) - len(cleaned)
    if diff > 0:
        print(diff, " phones removed")
    with open(path, "w") as f:
        f.writelines(cleaned)

def clean_all(data_path):
    data_files = glob.glob(os.path.join(data_path, "*"))
    for data_file in data_files:
        clean_data(data_file)


def clear_dir(path):
    files = glob.glob(os.path.join(path, "*"))
    for f in files:
        os.remove(f)


if __name__ == "__main__":
    #parse_data(PHOIBLE_PATH, DATA_PATH)
    clean_all(DATA_PATH)
