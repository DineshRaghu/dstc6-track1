import numpy as np
import json

if __name__ == '__main__':

    candidates_dict = {}
    files_list = []
    files_list.append("dialog-task1API-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task2REFINE-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task3OPTIONS-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task4INFOS-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task5FULL-kb1_atmosphere-distr0.5-trn10000.json")

    for file in files_list:
        # Declare input file
        inputfile = "../data/" + "train/" + file

        # Get json data
        fd = open(inputfile, 'rb')
        json_data = json.load(fd)
        fd.close()

        for story in json_data:
            for cand in story['candidates']:
                # print(" * " + str(cand['candidate_id']) + " - " + str(cand['utterance']) + "\n")
                candidates_dict[str(cand['utterance'])] = str(cand['candidate_id'])
    

print(len(candidates_dict))
fd_out = open("../data/train/candidates.txt", 'wb')
for candidate in candidates_dict.keys():
    fd_out.write("1 " + candidate+ "\n")
fd_out.close()
