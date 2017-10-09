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
								if 'api_call' in utt_json[j+1]:
									api_call_count+=1
								if 'here it is' in utt_json[j+1]:
									here_it_is_count+=1
								last_line = utt_json[j+1]
								dialog_str = dialog_str + utt_json[j+1] + '\n'
							else:
								dialog_str = dialog_str + "i am sorry, i don't have an answer to that question\n"
							j += 1
						lineNo=lineNo+1
						j += 1
					
					dialog_str = dialog_str + '\n'
					
					if subfolder_idx == 0:
						if (task_id == 1 and api_call_count == 1) or (task_id == 2 and api_call_count == 2) or (task_id == 3 and 'great let me do the reservation' in last_line):
							dialogList.append(dialog_str)
						if task_id == 5 and here_it_is_count > 0:
							dialogList.append(dialog_str)
						if task_id == 4:
							dialogList.append(dialog_str)
					else:
						dialogList.append(dialog_str)
					
				if subfolder_idx == 0:
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
					