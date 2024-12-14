from tamil import utf8
import copy
import re
from collections import Counter

with open('data.txt', 'r', encoding='utf-8') as file:
    #text = [next(file) for _ in range(1250000)]
    text = file.readlines()

# Count the number of lines
num_lines = len(text)

# Count the number of words
num_words = sum(len(line.split()) for line in text)

print(f"Number of lines: {num_lines}")
print(f"Number of words: {num_words}")


#text = ['''இராமர் பாலம் ("Rama's Bridge") அல்லது ஆதாமின் பாலம் ("Adam's Bridge") என்பது தமிழ் நாட்டில் உள்ள இராமேஸ்வரத்திற்கும் இலங்கையில் உள்ள மன்னார் தீவுகளுக்கும் இடையே உள்ள சுண்ணாம்புக் கற்களால் ஆன ஆழமற்ற மேடுகளாகும். 30 கி.மீ. நீளம் கொண்ட இந்தப் பாலம், மன்னார் வளைகுடாவையும் (தென்மேற்கு) பாக் ஜலசந்தியையும் (வடகிழக்கு) பிரிக்கின்றது. இந்த பாலத்தில், கடல் ஆழம் சுமார் 3 முதல் 30 அடி வரையே உள்ளது. சில மேடுகள் கடல் மட்டத்திற்கு மேலும் உள்ளன. இது இராம சேது ("Ram Setu") என்றும் அழைக்கப்படுகிறது.''']

def remove_parenthesis_text(lines):
    # Regular expression to match text within parentheses
    pattern = r'\(.*?\)|<\/?doc.*?>|[^ \u0B80-\u0BFF]'
    
    # Process each line and remove the parenthesis text
    cleaned_lines = [re.sub(pattern, '', line).strip() for line in lines]
    
    return cleaned_lines

def clean_line(line):
    # Use regex to substitute anything that's not a letter or space with an empty string
    return re.sub(r'[^஀-௿\s]', '', line)

# Apply the function to each line

text = remove_parenthesis_text(text)
text = [clean_line(line) for line in text]
words=[]
for i in text:
    words.extend(i.split(" "))

words=[word for word in words if word!='']
vocab=set(words)
word_count_dict = {}  
word_count_dict = Counter(words)

probs = {} 
m = sum(word_count_dict.values())
for k, v in word_count_dict.items():
    probs[k] = v / m


def delete_letter(word):
    letters = utf8.get_letters(word)
    
    delete_l = []
    
    
    for i in range(len(letters)):
        # if len(letters[i])>1 and letters[i][1]=='்':
        new_word=''.join(letters[:i])
        if len(letters)>i+1:
            new_word+=''.join(letters[i+1:])
        delete_l.append(new_word)

    

    return delete_l

def insert_letter(word):
    letters = utf8.get_letters(word)
    insert_l=[]
    for i in range(1,len(letters)+1):
        
        for l in ['க', 'ச', 'ட', 'த', 'ப', 'ற', 'ஞ', 'ங', 'ண', 'ந', 
                   'ம','ன', 'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ஜ', 'ஷ', 'ஸ', 'ஹ']:
            x=copy.deepcopy(letters)
            x.insert(i,l+'்')
            insert_l.append(''.join(x))
    
    return insert_l

def transpose_letter(word):
    letters = utf8.get_letters(word)
    transpose_l=[]
    for i in range(1,len(letters)-1):
        x=copy.deepcopy(letters)
        x[i],x[i+1]=x[i+1],x[i]
        transpose_l.append(''.join(x))
    
    return transpose_l    

def substitute_letter(word):
    letters = utf8.get_letters(word)
    target_chars = [['ர','ற'],['ல','ள','ழ'],['ன','ண','ந'],['ங','ஞ']]
    substitute_l=[]
    for i in range(0,len(letters)-1):
        
        for l in target_chars:
            if letters[i][0] in l:
                for char in [char for char in l if char != letters[i][0]]:
                    x=copy.deepcopy(letters)
                    if len(x[i])==2:
                        x[i]=char+x[i][1]
                    else:
                        x[i]=char
                    substitute_l.append(''.join(x))
    
    target_chars = [[ 'ி', 'ீ'],['','ா','ை'],['ு', 'ூ'],['ெ', 'ே'],['ொ', 'ோ']]
    for i in range(0,len(letters)-1):
        
        for l in target_chars:
            if len(letters[i])==1 and letters[i] in ['க', 'ச', 'ட', 'த', 'ப', 'ற', 'ஞ', 'ங', 'ண', 'ந', 
                   'ம','ன', 'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ஜ', 'ஷ', 'ஸ', 'ஹ']:
                for char in ['ா','ை']:
                    x=copy.deepcopy(letters)
                    x[i]+=char
                    substitute_l.append(''.join(x))
            elif len(letters[i])==2 and letters[i][1] in l:
                for char in [char for char in l if char != letters[i][1]]:
                    x=copy.deepcopy(letters)
                    x[i]=x[i][0]+char
                    substitute_l.append(''.join(x))
    
    return substitute_l

def edit_one_letter(word):
    edit_one_set = set()
    
    ### START CODE HERE ###
    edit_one_set.update(delete_letter(word))
    edit_one_set.update(transpose_letter(word))
    edit_one_set.update(substitute_letter(word))
    edit_one_set.update(insert_letter(word))
    ### END CODE HERE ###

    return edit_one_set

def get_corrections(word, probs, vocab, n=2):
    
    suggestions = []
    n_best = []
    #print(edit_one_letter(word).intersection(vocab))
    if word in vocab:
        return 'Nil'
    suggestions = list( edit_one_letter(word).intersection(vocab))
    #print(suggestions)
    n_best = sorted(
    [(word, probs[word]) for word in suggestions if word in probs],
    key=lambda x: x[1],
    reverse=True
)[:n]
    #print(suggestions)
    #print("entered word = ", word, "\nsuggestions = ", n_best)

    return n_best

#a=get_corrections("கன்ணீர்",probs,vocab,3)
#a=get_corrections("கண்ணீர்",probs,vocab,3)

corrected=0
missed=0

with open('index.txt', 'r') as file:
    values = file.read()

values_list = [int(value.strip()) for value in values.split(',')]
index = set(values_list)
#print(index)

with open('noise.txt', 'r', encoding='utf-8') as file:
    test_data = file.readlines()

test_data = remove_parenthesis_text(test_data)
for i in range(len(test_data)):
    test_data[i]=test_data[i].split(" ")
test_data = [[word for word in line if word] for line in test_data]

word_cnt=0
for i in range(len(test_data)):
    for j in range(len(test_data[i])):
        chk = get_corrections(test_data[i][j],probs,vocab)
        if(((word_cnt not in index) and chk=='Nil') or ((word_cnt in index) and (chk!='Nil'))):
            corrected+=1
        else:
            missed+=1
        #print(word_cnt,chk)
        word_cnt+=1
        
print(corrected)
print(missed)
print(corrected*100/(corrected+missed),'%')
