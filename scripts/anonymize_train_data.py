import json
import ast

def anonymize_data_task1(inputfile, outputfile, mapfile):
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
        restaurants = set()
        data = {}
        data["dialog_id"] = i
        dialog_id_map[i] = story["dialog_id"]
        data["utterances"] = []
        data["candidates"] = []
        candidate_id_map[i] = {}
        for utt in story['utterances'] + [story["answer"]["utterance"]]:
            if '_' in utt:
                line = utt.split()
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
                    trans_candidate = ' '.join([str(x) for x in line])
            else:
                trans_candidate = candidate['utterance']
            data["candidates"].append(trans_candidate)
            candidate_id_map[i][trans_candidate] = candidate["candidate_id"] 
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

def anonymize_candidates():
    fd_in = open("../data/test/candidates.txt", 'rb')
    fd_out = open("../data/test/anon/candidates.txt", 'wb')
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
        else :
            fd_out.write(line.strip() + '\n')
    fd_out.close()
    print(alreadyAdded)

def anonymize_data():
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
        anonymize_data_task1(inputfile,outputfile,mapfile)

if __name__ == '__main__':
	anonymize_data()
	anonymize_candidates()