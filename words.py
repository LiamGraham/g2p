
def trim_word_list(wlist_path, out_path, skip):
    """
    Trims the given word list by selecting each 'skip' line and writes it to a new file.

    e.g. skip = 3
   
    Original    Trimmed
    
    the         the
    quick       fox
    brown   =>
    fox
    jumped
    """
    with open(wlist_path, "r") as original:
        with open(out_path, "w") as new:
            for i, line in enumerate(original):
                if i % skip == 0:
                    new.write(line)


def remove_duplicates(wlist_path):
    with open(wlist_path, "r") as f:
        words = f.readlines()
    unique = set(words)
    print(f"{len(words) - len(unique)} words removed")
    with open(wlist_path, "w") as f:
        f.writelines(unique)

if __name__ == "__main__":
    remove_duplicates("/root/uni/g2p/g2p/lists/ces.wlist")