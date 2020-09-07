"""
Given a word list in a target language for which no specific model exists, find the most suitable adapted model (lowest error). 
"""

import sh
import sys
import os
phon = sh.phonetisaurus_apply

MODEL_DIR = "/home/liam/university/2020/engg4801/anylang/high_resource/high_resource_openfst/"
MODELS = [MODEL_DIR + model for  model in os.listdir(MODEL_DIR)]


# phonemic distance between a target language (given the phonemic inventory of that language) and a langauge in the model set

def find_model(word_list, models) -> str:
    """
    Returns the directory of the best model for the given word list file.
    """
    for model in models:
        result = phon("--word_list", word_list, "--model", model)
        print(result)
    return ""


if __name__ == "__main__":
    word_list = sys.argv[1]
    model = find_model(word_list, MODELS)
    print(model)