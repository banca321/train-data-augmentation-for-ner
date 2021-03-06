import spacy
import pandas as pd
nlp = spacy.load('en')

##################################################
### Description
# File save and load by using pickle
import pickle
def save(data, name):
    filehandler = open(name,"wb")
    pickle.dump(data, filehandler)
    filehandler.close()
def load(name):
    filehandler = open(name, "rb")
    return pickle.load(filehandler)
### Example
# save(some_list, 'voca1')
# voca = load('voca1')
##################################################



def store_new_sent(path_write, new_sent_raw_list, new_sent_label_list):
    with open(path_write, 'w', encoding='UTF-8') as txt:
        for i, _ in enumerate(new_sent_raw_list):
            splited_sent = new_sent_raw_list[i].split()
            splited_label = new_sent_label_list[i].split()
            for j, token in enumerate(splited_sent):
                txt.write(splited_sent[j]+' '+'NNP'+' '+'B-NP'+' '+splited_label[j])
                txt.write('\n')
            txt.write('\n')


def filtering_clauses(raw_data, label_data):
    sent_clauses = ['because', 'before', 'until', 'after', 'while', 'if', 'since', 'when', 'as', 'Because', 'Before', 'Until', 'After', 'While', 'If', 'Since', 'When', 'As']
    new_data = []
    new_label = []
    
    for i, _ in enumerate(raw_data):
        if type(raw_data[i])!=type([]):
            raw_data[i] = raw_data[i].split()
        if any((True for x in raw_data[i] if x in sent_clauses))==True:
            raw_data[i] = ' '.join(raw_data[i])
            #label_data[i] = ' '.join(label_data[i])
            new_data.append(raw_data[i])
            new_label.append(label_data[i])
        else:
            raw_data[i] = ' '.join(raw_data[i])
            #label_data[i] = ' '.join(label_data[i])
            
    return new_data, new_label

def filtering_noENT_sentFORM(raw_data, label_data):
    sent_raw = []
    sent_label = []
    cnt = 0
    for i, row in enumerate(raw_data):
        row_nlp = nlp(row)
        if raw_data[i][-1] == '.' or raw_data[i][-1] == '"': # ???????????? ????????? ?????? ???????????? ????????????.
            if len(raw_data[i].split()) >= 2: # ????????? ?????? 2????????? ??????????????? ????????????. (ex. .??? ?????? ????????? ??????)
                temp = []
                for token in row_nlp:
                    temp.append(token.pos_) # ??? token??? pos ??????
                if 'VERB' in temp: # ????????? ?????? 1???????????? verb??? ????????? ??????.
                    if len([x for x in label_data[i].split() if x != 'O']) != 0: # ???????????? ????????? ????????? ?????????.
                        sent_raw.append(raw_data[i])
                        sent_label.append(label_data[i])
    print('>>> [filtering_noENT_sentFORM]: before = {} and after = {}'.format(len(raw_data), len(sent_raw)))
    return sent_raw, sent_label

def preprocessing_for_spacy(sent_raw):
    ### ?????? string ?????? ??????
    sent_raw = sent_raw.replace("'ve", 'have')
    ### ?????? ?????? ?????? token ??????
    # nlp output??? sent_raw??? ????????? ????????? ?????? ?????? ????????? ??????
    # ex. nlp()??? ?????????, EU-wide??? ?????? ????????? EU, -, wide??? 3?????? ????????????. 
    splited_sent_raw = sent_raw.split()
    for i, token in enumerate(splited_sent_raw):
        splited_token = token.split('-')
        if not splited_token == 1: # ?????? ???????????? ????????????, result. 'EU-wide', '--'
            if not (splited_token[0] == '' or splited_token[-1] =='km'): # '-'????????? ????????? ????????? ????????????, result.'EU-wide'
                filtered_token = [x for x in splited_token if x != '-'] # '-'??? list?????? ?????? result.['EU', 'wide']
                merged_token = ''.join(filtered_token)
                splited_sent_raw[i] = merged_token
    
    for i, token in enumerate(splited_sent_raw):
        if not len(token) == 1: # . ????????? ?????? token??? ??????
            splited_sent_raw[i] = splited_sent_raw[i].replace('.', '')
            splited_sent_raw[i] = splited_sent_raw[i].replace('$', '')
        if token == 'cannot':
            splited_sent_raw[i] = "can"
        if token == 'dont':
            splited_sent_raw[i] = "do"
        if token == "'re":
            splited_sent_raw[i] = "are"
        if token == "**":
            splited_sent_raw[i] = "*"        
        if token == "..." or token == ".." or token == "....":
            splited_sent_raw[i] = "."         
        if token == "'m":
            splited_sent_raw[i] = "am"         
        if token == "'ll":
            splited_sent_raw[i] = "will" 
        if token == "'d":
            splited_sent_raw[i] = "would"
            
        # very specific problem of this task    
        if token == "*Note":
            splited_sent_raw[i] = "Note"   
        if token == "*Name":
            splited_sent_raw[i] = "Name" 
        if token == 'km':
            splited_sent_raw[i] = "miles"             
        if token == '237km':
            splited_sent_raw[i] = "237-km"             
    return ' '.join(splited_sent_raw)


def filtering_none_entity(sent_raw, sent_label):
    filtered_raw = []
    filtered_label = []
    for i, _ in enumerate(sent_raw):
        if len([x for x in sent_label[i].split() if x != 'O']) != 0: # ???????????? ???????????? ?????????
            filtered_raw.append(sent_raw[i])
            filtered_label.append(sent_label[i])
    print('>>> [filtering_none_entity]: before =',len(sent_raw),'and after =',len(filtered_raw))      
    return filtered_raw, filtered_label



def load_conll2003(read_path):

	#read_path = 'data/conll2003/eng.train'
	#read_path = 'train.txt'
	
	with open(read_path, "r") as ins:
		raw_data = []
		label_data = []
		
		temp_sent = ''
		temp_label = ''
		tkn = False
		
		for line in ins:
			#array.append(line)

			if len(line) == 1:
				raw_data.append(temp_sent)
				label_data.append(temp_label)
				temp_sent = ''
				temp_label = ''
				tkn = False
			else:
				if tkn == True:
					temp_sent += ' '
					temp_label += ' '
					
				temp_sent += line.split()[0] # ??????
				temp_label += line.split()[-1] # NER ??????
				tkn = True

	return raw_data, label_data



def load_csv(DATASET):

    if DATASET == 'agnews':
        # data load
        train = pd.read_csv('ag_news_csv/train.csv', header=None)
        test = pd.read_csv('ag_news_csv/test.csv', header=None) # test set??? is only for statistical analysis
        #^^; since ag-news dataset does not have NA data, we do not need to have 'keep_default_na=False'

        ## column rename
        train.columns = ['y', 'title', 'description']
        test.columns = ['y', 'title', 'description']
        # merge (merge with '.' to recognize different sentence)
        train['X'] = train['title'] + '. ' + train['description']
        test['X'] = test['title'] + '. ' + test['description']
        
    elif DATASET == 'sst':
        # data load
        train = pd.read_csv('sst_csv/sst_train_sentences.csv', header=None, keep_default_na=False)
        dev = pd.read_csv('sst_csv/sst_dev.csv', header=None, keep_default_na=False)
        test = pd.read_csv('sst_csv/sst_test.csv', header=None, keep_default_na=False)

        ## column rename
        train.columns = ['y', 'X']
        dev.columns = ['y', 'X']
        test.columns = ['y', 'X']

        train['y'] = pd.cut(train['y'], [0, 0.2, 0.4, 0.6, 0.8, 1.0], include_lowest=True, labels=[1, 2, 3, 4, 5])
        dev['y'] = pd.cut(dev['y'], [0, 0.2, 0.4, 0.6, 0.8, 1.0], include_lowest=True, labels=[1, 2, 3, 4, 5])
        test['y'] = pd.cut(test['y'], [0, 0.2, 0.4, 0.6, 0.8, 1.0], include_lowest=True, labels=[1, 2, 3, 4, 5])
        
    return dev['X'], dev['y']



	
def remove_duplicate(list):
    pure_list = []
    for x in list:
        if not x in pure_list:
            pure_list.append(x)
    return pure_list
