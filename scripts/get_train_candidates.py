import numpy as np
import json

if __name__ == '__main__':

    files_list = []
    files_list.append("dialog-task1API-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task2REFINE-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task3OPTIONS-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task4INFOS-kb1_atmosphere-distr0.5-trn10000.json")
    files_list.append("dialog-task5FULL-kb1_atmosphere-distr0.5-trn10000.json")

    for i, file in enumerate(files_list):
        candidates_dict = {}

        # Declare input file
        inputfile = "../data/" + "train/" + file

        # Get json data
        fd = open(inputfile, 'rb')
        json_data = json.load(fd)
        fd.close()

        for story in json_data:
            #for cand in story['candidates']:
                # print(" * " + str(cand['candidate_id']) + " - " + str(cand['utterance']) + "\n")
            candidates_dict[str(story['answer']['utterance'])] = str(story['answer']['candidate_id'])
            lineNo=0
            for utt_index in range(len(story['utterances'])):
                # print(" * " + str(cand['candidate_id']) + " - " + str(cand['utterance']) + "\n")
                if ' r_location ' in story['utterances'][utt_index] or ' r_price ' in story['utterances'][utt_index] or ' r_rating ' in story['utterances'][utt_index] or ' r_phone ' in story['utterances'][utt_index] or ' r_cuisine ' in story['utterances'][utt_index] or ' r_atmosphere ' in story['utterances'][utt_index] or ' r_restrictions ' in story['utterances'][utt_index] or ' r_number ' in story['utterances'][utt_index] or ' r_address ' in story['utterances'][utt_index]:
                    continue
                if lineNo%2 == 1:
                    #if 'is there a movie theater close by' in story['utterances'][utt_index]:
                    #    print(story['utterances'][utt_index])
                    candidates_dict[str(story['utterances'][utt_index])] = str(story['utterances'][utt_index])
                    #print(story['utterances'][utt_index])
                lineNo=lineNo+1
        print( "Task" + str(i+1), len(candidates_dict))
        outfileall = "../data/train/candidates.txt"
        outfile = "../data/train/candidates" + str(i+1) + ".txt"
        fd_out = open(outfile, 'wb')
        if i == 0:
            fd_out_all = open(outfileall, 'wb')
        else:
            fd_out_all = open(outfileall, 'ab')
        for candidate in candidates_dict.keys():
            fd_out_all.write("1 " + candidate+ "\n")
            fd_out.write("1 " + candidate+ "\n")
        fd_out_all.close()
        fd_out.close()


