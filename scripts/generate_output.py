import numpy as np
import json
from os import listdir
from os.path import isfile, join

def get_mappings(mapfile):
    in_file = open(mapfile, 'rb')
    dialog_id_map = ast.literal_eval(in_file[0])
    candidate_id_map = ast.literal_eval(in_file[1])
    candidate_dialog_map = ast.literal_eval(in_file[2])
    return dialog_id_map, candidate_id_map, candidate_dialog_map

if __name__ == '__main__':

    file_folder = "../data/test/Results"
    resultFiles = [f for f in listdir(file_folder) if isfile(join(file_folder, f))]

    files_list = []
    files_list.append("dialog-task1API-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task2REFINE-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task3OPTIONS-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task4INFOS-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task5FULL-kb1_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task1API-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task2REFINE-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task3OPTIONS-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task4INFOS-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task5FULL-kb2_atmosphere-distr0.5-tst1000.json")
    files_list.append("dialog-task1API-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task2REFINE-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task3OPTIONS-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task4INFOS-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task5FULL-kb1_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task1API-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task2REFINE-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task3OPTIONS-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task4INFOS-kb2_atmosphere_restrictions-distr0.5-tst1000.json")
    files_list.append("dialog-task5FULL-kb2_atmosphere_restrictions-distr0.5-tst1000.json")

    for test in range(1,5)
        for task in range(1,6):
            # Populate FileList
            fileList = [f for f in resultFiles if ("tst" + str(test)) in f and ("task" + str(task)) in f]
            
            for file in fileList:
                fd = open(file, 'rb')
                json_data = json.load(fd)
                fd.close()

                prob_list = {}
                for story in json_data:
                    dialog_id = story['dialog_id']
                    if dialog_id not in prob_list:
                        prob_list[dialog_id] = {}
                        for cand in story['rank_candidates']:
                            prob_list[dialog_id][cand['utterance']] = cand['prob']
                    else:
                        for cand in story['rank_candidates']:
                            prob_list[dialog_id][cand['utterance']] += cand['prob']
                rank_list = {}
                for dialog in prob_list:
                    rank_list[dialog] = []
                    for cand in prob_list[dialog]:
                        rank_list[dialog].append((cand, prob_list[dialog][cand]))
                    rank_list[dialog] = sorted(rank_list[dialog], key=lambda x: x[1], reversed=True)
                    for i, cand in enumerate(rank_list[dialog]):
                        prob_list[dialog][cand[0]] = i

            # Open Anonymised File
            file_index = (task-1) + (test-1)*5
            infile = "../data/test/tst" + str(test) + "/anon/" + files_list[file_index]
            mapfile = "../data/test/tst" + str(test) + "/anon/" + files_list[file_index]
            outfile = "../data/test/tst" + str(test) + "/out/" + files_list[file_index]
            
            fd = open(infile, 'rb')
            json_data = json.load(fd)
            fd.close()
            dialog_id_map, candidate_id_map, candidate_dialog_map = get_mappings(mapfile)

            out_file = open(outfile, 'w')
            all_data = []
            for story in json_data:
                data = {}
                dialog_id = story['dialog_id']
                data['dialog_id'] = dialog_id_map[dialog_id]
                data['lst_candidate_id'] = []
                for cand in story['candidates']:
                    rank = prob_list[dialog_id][cand]
                    data['lst_candidate_id'].append({"candidate_id":candidate_id_map[dialog_id][cand], "rank":rank})
                all_data.append(data)
            out_file.write(json.dumps(all_data, ensure_ascii=False))
            out_file.close()

