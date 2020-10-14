import os

from g2p import Lang2Lang, LANG_PATH

MODEL_DIR = "/root/uni/anylang/high_resource/high_resource_openfst/"
MODELS = [MODEL_DIR + model for  model in os.listdir(MODEL_DIR)]

ISO_PATH = "/root/uni/iso_639/iso-639-3_20200515.tab"


def get_lang_name(code):
    with open(ISO_PATH, "r") as f:
        f.readline()
        for line in f:
            values = line.split("\t")
            if values[0] == code:
                return values[6]


def get_candidates(threshold):
    models = []
    candidates = []
    for path in MODELS:
        models.append(os.path.basename(path).split(".")[0])
    
    lang2lang = Lang2Lang(LANG_PATH)
    lowest = lang2lang.get_all(threshold)
    for values in lowest:
        lang1, lang2, dist = values
        if lang1 in models and lang2 in models:
            name1 = get_lang_name(lang1)
            name2 = get_lang_name(lang2)
            print(f"{name1} ({lang1}) -> {name2} ({lang2}): {dist}")
            candidates.append(values)
    return candidates


if __name__ == "__main__":
    get_candidates(0.25)