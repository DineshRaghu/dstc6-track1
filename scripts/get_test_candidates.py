import numpy as np
import json

if __name__ == '__main__':
    candidates_dict = {}
    base = ""
    files_list = []
    files_list.append("tst1/dialog-task1API-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst1/dialog-task2REFINE-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst1/dialog-task3OPTIONS-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst1/dialog-task4INFOS-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst1/dialog-task5FULL-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst2/dialog-task1API-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst2/dialog-task2REFINE-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst2/dialog-task3OPTIONS-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst2/dialog-task4INFOS-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst2/dialog-task5FULL-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("tst3/dialog-task1API-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst3/dialog-task2REFINE-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst3/dialog-task3OPTIONS-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst3/dialog-task4INFOS-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst3/dialog-task5FULL-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst4/dialog-task1API-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst4/dialog-task2REFINE-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst4/dialog-task3OPTIONS-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst4/dialog-task4INFOS-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("tst4/dialog-task5FULL-kb2_atmosphere_restrictions-distr0.5-tst1000.json")

    for i, file in enumerate(files_list):
        if i % 5 == 0:
            candidates_set = set()
            base = "tst" + str((i+5)/5) + "/"

        # Declare input file
        inputfile = "../data/" + "test/" + file

        # Get json data
        fd = open(inputfile, 'rb')
        json_data = json.load(fd)
        fd.close()

        for story in json_data:
            for cand in story['candidates']:
                candidates_set.add(str(cand['utterance']))

        if i % 5 == 4:
            fd_out = open("../data/test/" + base + "candidates.txt", 'wb')
            for candidate in candidates_set:
                fd_out.write("1 " + candidate + "\n")
            fd_out.close()