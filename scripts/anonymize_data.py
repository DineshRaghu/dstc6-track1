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

def rank_restaurants(rank_list, rest_dict):
    rank_map = {}
    restaurants = set()
    for item in rank_list:
        restaurants.add(item[0])
    for rest in rest_dict:
        if "rest_name_" + str(rest_dict[rest]) not in restaurants:
            rank_list.append(("rest_name_" + str(rest_dict[rest]), 0))
    rank_list = sorted(rank_list, key=lambda x: x[1], reverse = True)
    for i, item in enumerate(rank_list):
        rank_map[item[0]] = "rest_name_" + str(i)
        rank_map['phone_' + item[0].split('_')[-1]] = "phone_" + str(i)
        rank_map['address_' + item[0].split('_')[-1]] = "address_" + str(i)
    return rank_map

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
        rank_list = []
        rank_map = {}
        if train:
            utterances_list = story['utterances'] + [story["answer"]["utterance"]]
        else:
            utterances_list = story['utterances']
        for utt in utterances_list:
            line = [str(x) for x in utt.split()]
            if '_' in utt and line[0] != "api_call":
                if '_' in line[0]:
                    rest = line[0]
                    if rest in rest_dict:
                        line[0] = "rest_name_" + str(rest_dict[rest])
                    else:
                        rest_dict[rest] = len(rest_dict)
                        line[0] = "rest_name_" + str(rest_dict[rest])
                    if "_phone" in line[1]:
                        phone_dict[line[2]] = len(phone_dict)
                        line[2] = "phone_" + str(phone_dict[line[2]])
                    elif "_address" in line[1]:
                        addr_dict[line[2]] = len(addr_dict)
                        line[2] = "address_" + str(addr_dict[line[2]])
                    elif "_rating" in line[1]:
                        rank_list.append((line[0], line[2]))
                    #   continue
                else:
                    rest = line[-1]
                    if '_phone' in rest:
                        if rest in phone_dict:
                            line[-1] = "phone_" + str(phone_dict[rest])
                        else:
                            phone_dict[rest] = len(phone_dict)
                            line[-1] = "phone_" + str(phone_dict[rest])
                    elif '_address' in rest:
                        if rest in addr_dict:
                            line[-1] = "address_" + str(addr_dict[rest])
                        else:
                            addr_dict[rest] = len(addr_dict)
                            line[-1] = "address_" + str(addr_dict[rest])
                    else:
                        if rest in rest_dict:
                            line[-1] = "rest_name_" + str(rest_dict[rest])
                        else:
                            rest_dict[rest] = len(rest_dict)
                            line[-1] = "rest_name_" + str(rest_dict[rest])
            for j, word in enumerate(line):
                word = word.replace(',','')
                if word in cuisines:
                    if word in cuisine_dict:
                        line[j] = "cuisine_" + str(cuisine_dict[word])
                    else:
                        cuisine_dict[word] = len(cuisine_dict)
                        line[j] = "cuisine_" + str(cuisine_dict[word])
                elif word in locations:
                    if word in location_dict:
                        line[j] = "location_" + str(location_dict[word])
                    else:
                        location_dict[word] = len(location_dict)
                        line[j] = "location_" + str(location_dict[word])
            utt = ' '.join([str(x) for x in line])
            data["utterances"].append(utt) 
        for candidate in story['candidates']:
            line = [str(x) for x in candidate['utterance'].split()]
            if '_' in line[-1]:
                rest = line[-1]
                if '_phone' in rest:
                    if rest in phone_dict:
                        line[-1] = "phone_" + str(phone_dict[rest])
                    else:
                        phone_dict[rest] = len(phone_dict)
                        line[-1] = "phone_" + str(phone_dict[rest])
                elif '_address' in rest:
                    if rest in addr_dict:
                        line[-1] = "address_" + str(addr_dict[rest])
                    else:
                        addr_dict[rest] = len(addr_dict)
                        line[-1] = "address_" + str(addr_dict[rest])
                else:
                    if rest in rest_dict:
                        line[-1] = "rest_name_" + str(rest_dict[rest])
                    else:
                        rest_dict[rest] = len(rest_dict)
                        line[-1] = "rest_name_" + str(rest_dict[rest])
            for j, word in enumerate(line):
                if word in cuisines:
                    if word in cuisine_dict:
                        line[j] = "cuisine_" + str(cuisine_dict[word])
                    else:
                        cuisine_dict[word] = len(cuisine_dict)
                        line[j] = "cuisine_" + str(cuisine_dict[word])
                elif word in locations:
                    if word in location_dict:
                        line[j] = "location_" + str(location_dict[word])
                    else:
                        location_dict[word] = len(location_dict)
                        line[j] = "location_" + str(location_dict[word])
            trans_candidate = ' '.join([str(x) for x in line])
            data["candidates"].append(trans_candidate)
            if candidate["candidate_id"] not in candidate_dialog_map:
                candidate_dialog_map[candidate["candidate_id"]] = candidate["utterance"]
        #rank_map = rank_restaurants(rank_list, rest_dict)
        for j, utt in enumerate(data["utterances"]):
            line = [str(x) for x in utt.split()]
            for k, word in enumerate(line):
                if word in rank_map:
                    line[k] = rank_map[word]
            val = ' '.join([str(x) for x in line])
            data["utterances"][j] = val 
        for j, cand in enumerate(data["candidates"]):
            line = [str(x) for x in cand.split()]
            for k, word in enumerate(line):
                if word in rank_map:
                    line[k] = rank_map[word]
            val = ' '.join([str(x) for x in line])
            data["candidates"][j] = val 
            candidate_id_map[i][val] = story['candidates'][j]["candidate_id"] 
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
        cuisine_list = []
        location_list = []
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
            for i, word in enumerate(line_split):
                if word in cuisines:
                    cuisine_list.append(i)
                if word in locations:
                    location_list.append(i)
            if len(cuisine_list) == 0 and len(location_list) == 0:
                fd_out.write(line.strip() + '\n')
            else:
                key = ' '.join([str(x) for i, x in enumerate(line_split) if i not in cuisine_list and i not in location_list])
                if key not in alreadyAdded:
                    alreadyAdded.add(key)
                    if len(cuisine_list) == 0:
                        for i in range(0,5):
                            line_split[location_list[0]] = 'location_' + str(i)
                            fd_out.write(' '.join([str(x) for x in line_split]) + '\n')
                    elif len(location_list) == 0:
                        for i in range(0,5):
                            line_split[cuisine_list[0]] = 'cuisine_' + str(i)
                            fd_out.write(' '.join([str(x) for x in line_split]) + '\n')
                    else:
                        for i in range(0,5):
                            for j in range(0,5):
                                line_split[cuisine_list[0]] = 'cuisine_' + str(i)
                                line_split[location_list[0]] = 'location_' + str(j)
                                fd_out.write(' '.join([str(x) for x in line_split]) + '\n')
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