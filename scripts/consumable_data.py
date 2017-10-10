import json
import os
from collections import Counter

if __name__ == '__main__':
	
	basedir = '/Users/dineshraghu/IIT/proj-wksp/dstc6-track1/data/'
	subfolders = ['train/', 'test/tst1/','test/tst2/','test/tst3/','test/tst4/']
	subfolderPrefixes = ['train-', 'tst_1-','tst_2-','tst_3-','tst_4-']
	outputFolder = basedir + 'dstc6-consumable/'
	
	for subfolder_idx in range(len(subfolders)):
		subfolder = subfolders[subfolder_idx]
		data_dir = basedir+subfolder+'anon/'
		files = os.listdir(data_dir)
		for f in files:
			if '.json' in f:
				
				print(subfolderPrefixes[subfolder_idx][:-1] + ' : ' + f[:-5])
				
				infilePath = os.path.join(data_dir, f)
				outfilePath = os.path.join(outputFolder, subfolderPrefixes[subfolder_idx] + f[:-4] + 'txt')
				
				dialogList = []
				devfilePath = ''
				task_id = -1
				if subfolder_idx == 0:
					for task_idx in range(1,6):
						if ('dialog-task' + str(task_idx)) in f:
							devfilePath = os.path.join(outputFolder,'dev-dialog-task' + str(task_idx) + '.txt')
							task_id = task_idx
				
				infileJson = json.load(open(infilePath))
				if subfolder_idx == 0:
					devfile = open(devfilePath,'w')
				
				outfile = open(outfilePath,'w')
				utt_count_arr = []

				for i in range(len(infileJson)):
					#print(str(i))
					utt_json = infileJson[i]['utterances']

					utt_count = 0
					j = 0
					
					while j < len(utt_json):
						utt = utt_json[j]
						if not(utt.startswith('rest_name_')):
							utt_count+=1
							j += 1
						j += 1
					utt_count_arr.append(utt_count)
				count_map = dict((x,utt_count_arr.count(x)) for x in set(utt_count_arr))
				total = 0
				length_to_consider = 0
				#for key, value in count_map.iteritems():
				#	print(str(key) + "\t" + str(value))
				for key, value in count_map.iteritems():
					total+=value
					if total > 8000:
						length_to_consider = key
						break
					

				for i in range(len(infileJson)):
					utt_json = infileJson[i]['utterances']

					utt_count = 0
					lineNo = 1
					j = 0
					
					dialog_str = ''
					last_line = ''
					api_call_count = 0
					here_it_is_count = 0
					while j < len(utt_json):
						utt = utt_json[j]
						if utt.startswith('rest_name_'):
							dialog_str = dialog_str + str(lineNo) + ' ' + utt + '\n'
						else:
							utt_count+=1
							dialog_str = dialog_str + str(lineNo) + ' ' + utt + '\t'
							if j+1 < len(utt_json):
								dialog_str = dialog_str + utt_json[j+1] + '\n'
							else:
								dialog_str = dialog_str + "foo bar\n"
							j += 1
						lineNo=lineNo+1
						j += 1
					
					dialog_str = dialog_str + '\n'
					if subfolder_idx == 0:
						if utt_count >= length_to_consider:
							dialogList.append(dialog_str)
					else:
						dialogList.append(dialog_str)
					
				if subfolder_idx == 0:
					print(str(len(dialogList)))
					for i in range(len(dialogList)):
						if i < int(len(dialogList)*0.9):
							outfile.write(dialogList[i])
						else:
							devfile.write(dialogList[i])
					devfile.close()
				else:
					for i in range(len(dialogList)):
						outfile.write(dialogList[i])
				
				outfile.close()
					