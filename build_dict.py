import csv
import json
import logging
import os
import re

import util

logging.basicConfig(level="INFO")

input_dir = "./data/elkmovie_hsk30/"
output_file = "./assets/hsk30_words.json"
wubi_file = "./data/wubi86_stripped.txt"

info = []

wubi_dictionary = None
with open(wubi_file, "r", encoding="utf-8-sig") as wf:
    wubi_dictionary = wf.read()

input_files = os.listdir(input_dir)
for input_file in input_files:
    hsk_level = re.search(r"[1-7]", input_file).group()    # use 7 for 7 through 9
    with open("{}{}".format(input_dir, input_file), "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
        for line in  lines:
            match = re.match(r"(\d+) ([^（｜\s]+)", line)
            index = match.group(1)
            word = match.group(2)

            logging.info("Getting info for '{}'.".format(word))
            word_info = util.get_info(word)
            word_info["hsk_level"] = hsk_level

            # find the wubi strokes for each character
            wubi = []
            for char in word:
                # this pops up a couple times, ignore it (for now)
                try:
                    keys = re.search(r"^{}\t([a-z]+)$".format(char), wubi_dictionary, re.MULTILINE).group(1)
                except:
                    logging.warning("Unable to find wubi strokes for '{}', skipping.".format(char))
                    next

                wubi.append(keys)

            word_info["wubi"] = " ".join(wubi)

            info.append(word_info)

with open(output_file, "w") as f:
    f.write(json.dumps(info, ensure_ascii=False))
