import json
import ast

cuisines = set()
locations = set()

def build_sets():
    files_list = []
    files_list.append("../data/train/extendedkb1.txt")
    files_list.append("../data/test/extendedkb1.txt")
    files_list.append("../data/test/extendedkb2.txt")
    for file in files_list:
        in_file = open(file)
        for line in in_file:
            line_split = line.split()
            if 'location' in line_split[2]:
                locations.add(line_split[3])
            if 'cuisine' in line_split[2]:
                cuisines.add(line_split[3])   
        in_file.close()

def anonymize_data_task(inputfile, outputfile, mapfile, train):
    in_file = open(inputfile)
    out_file = open(outputfile, 'w')

    all_data = []
    dialog_id_map = {} # Dialog No to Dialog Id
    candidate_id_map = {} # Dialog No and dialog to candidate id
    candidate_dialog_map = {} # Candidate id to dialog

    json_data = json.load(in_file)

    for i, story in enumerate(json_data):
        rest_dict={}
        phone_dict={}
        addr_dict={}
        cuisine_dict={}
        location_dict={}
        restaurants = set()
        data = {}
        data["dialog_id"] = i
        dialog_id_map[i] = story["dialog_id"]
        data["utterances"] = []
        data["candidates"] = []
        candidate_id_map[i] = {}
        if train:
            utterances_list = story['utterances'] + [story["answer"]["utterance"]]
        else:
            utterances_list = story['utterances']
        for utt in utterances_list:
            line = utt.split()
            if '_' in utt:
                if '_' in line[0]:
                    rest = line[0]
                    if rest in rest_dict:
                        line[0] = "rest_name_" + str(rest_dict[rest])
                    else:
                        rest_dict[rest] = len(rest_dict)
                        line[0] = "rest_name_" + str(rest_dict[rest])
                    if "_phone" in line[1]:
                        line[2] = "phone_" + str(rest_dict[rest])
                    elif "_address" in line[1]:
                        line[2] = "address_" + str(rest_dict[rest])
                else:
                    rest = line[-1]
                    if rest in rest_dict:
                        line[-1] = "rest_name_" + str(rest_dict[rest])
                    else:
                        rest_dict[rest] = len(rest_dict)
                        line[-1] = "rest_name_" + str(rest_dict[rest])
            for i, word in enumerate(line):
                word = word.replace(',','')
                if word in cuisines:
                    if word in cuisine_dict:
                        line[i] = "cuisine_" + str(cuisine_dict[word])
                    else:
                        cuisine_dict[word] = len(cuisine_dict)
                        line[i] = "cuisine_" + str(cuisine_dict[word])
                elif word in locations:
                    if word in location_dict:
                        line[i] = "location_" + str(location_dict[word])
                    else:
                        location_dict[word] = len(location_dict)
                        line[i] = "location_" + str(location_dict[word])
            utt = ' '.join([str(x) for x in line])
            data["utterances"].append(utt) 
        for candidate in story['candidates']:
            line = candidate['utterance'].split()
            if '_' in line[-1]:
                rest = line[-1]
                if rest in rest_dict:
                    line[-1] = "rest_name_" + str(rest_dict[rest])
                else:
                    rest_dict[rest] = len(rest_dict)
                    line[-1] = "rest_name_" + str(rest_dict[rest])
            for i, word in enumerate(line):
                if word in cuisines:
                    if word in cuisine_dict:
                        line[i] = "cuisine_" + str(cuisine_dict[word])
                    else:
                        cuisine_dict[word] = len(cuisine_dict)
                        line[i] = "cuisine_" + str(cuisine_dict[word])
                elif word in locations:
                    if word in location_dict:
                        line[i] = "location_" + str(location_dict[word])
                    else:
                        location_dict[word] = len(location_dict)
                        line[i] = "location_" + str(location_dict[word])
            trans_candidate = ' '.join([str(x) for x in line])
            data["candidates"].append(trans_candidate)
            # candidate_id_map[i][trans_candidate] = candidate["candidate_id"] 
            if candidate["candidate_id"] not in candidate_dialog_map:
                candidate_dialog_map[candidate["candidate_id"]] = candidate["utterance"]
        all_data.append(data)
    out_file.write(json.dumps(all_data, ensure_ascii=False))
    out_file.close()

    map_file = open(mapfile, 'w')
    map_file.write(json.dumps(dialog_id_map) + "\n")
    map_file.write(json.dumps(candidate_id_map) + "\n")
    map_file.write(json.dumps(candidate_dialog_map) + "\n")
    map_file.close()

def anonymize_candidates(inputfile, outputfile):
    fd_in = open(inputfile, 'rb')
    fd_out = open(outputfile, 'wb')
    alreadyAdded = set()
    for line in fd_in:
        line_split = line.split()
        if '_' in line_split[-1] and line_split[-1].endswith('_phone'):
            key = ' '.join([str(x) for x in line_split[:-1]])
            if key + '_phone' not in alreadyAdded:
                alreadyAdded.add(key + '_phone')
                for i in range(0,10):
                    fd_out.write(key + ' phone_' + str(i) + '\n')
        elif '_' in line_split[-1] and line_split[-1].endswith('_address'):
            key = ' '.join([str(x) for x in line_split[:-1]])
            if key + '_address' not in alreadyAdded:
                alreadyAdded.add(key + '_address')
                for i in range(0,10):
                    fd_out.write(key + ' address_' + str(i) + '\n')
        elif '_' in line_split[-1]:
            key = ' '.join([str(x) for x in line_split[:-1]])
            if key not in alreadyAdded:
                alreadyAdded.add(key)
                for i in range(0,10):
                    fd_out.write(key + ' rest_name_' + str(i) + '\n')
        elif '_' in line_split[1]:
            key = ' '.join([str(x) for x in line_split[4:]])
            if key not in alreadyAdded:
                alreadyAdded.add(key)
                for i in range(0,5):
                    for j in range(0,5):
                        fd_out.write("1 api_call" + ' cuisine_' + str(i) + ' location_' + str(j) + ' ' + key + '\n')
        else :
            fd_out.write(line.strip() + '\n')
    fd_out.close()

def anonymize_train_data():
    candidate_in = "../data/train/candidates.txt"
    candidate_out = "../data/train/anon/candidates.txt"
    anonymize_candidates(candidate_in, candidate_out)
    files_list = []
    files_list.append("dialog-task1API-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task2REFINE-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task3OPTIONS-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task4INFOS-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task5FULL-kb1_atmosphere-distr0.5-trn10000.json")
    for file in files_list:
        inputfile = "../data/train/" + file
        outputfile = "../data/train/anon/" + file
        mapfile = "../data/train/maps/" + file
        anonymize_data_task(inputfile,outputfile,mapfile,train = True)

def anonymize_test_data():
    files_list = []
    base = ""
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
    for i, file in enumerate(files_list):
        if i % 5 == 0:
            base = "tst" + str((i+5)/5) + "/"
            candidate_in = "../data/test/" + base + "candidates.txt"
            candidate_out = "../data/test/" + base + "anon/candidates.txt"
            anonymize_candidates(candidate_in, candidate_out)
        inputfile = "../data/test/" + base + file
        outputfile = "../data/test/" + base + "anon/" + file
        mapfile = "../data/test/" + base + "maps/" + file
        anonymize_data_task(inputfile,outputfile,mapfile,train = False)

if __name__ == '__main__':
    build_sets()
    anonymize_train_data()
    anonymize_test_data()