from tamil import utf8
import random
import re

num_transpose=0
num_insertion=0
num_deletion=0
num_substitution=0
num_substitution2=0

total_words=0

def remove_parenthesis_text(lines):
    # Regular expression to match text within parentheses
    pattern = r'\(.*?\)'
    
    # Process each line and remove the parenthesis text
    cleaned_lines = [re.sub(pattern, '', line).strip() for line in lines]
    
    return cleaned_lines

with open('sample_500mb.txt', 'r', encoding='utf-8') as file:
    text = file.readlines()

text = remove_parenthesis_text(text)



for i in range(len(text)):
    text[i]=text[i].split(" ")
    total_words+=len(text[i])
text = [[word for word in line if word] for line in text]

def insertion(word,next_word=""):
    letters = utf8.get_letters(word)
    if len(letters)<3:
        return word
#    index = 1 if len(letters)==2 else random.randint(1,len(letters)-1)  
    index=random.randint(1,len(letters)-1)
    new_word=''.join(letters[:index])
    if (len(letters[index])==1 or letters[index][1] != '்') and (len(letters[index-1])==1 or letters[index-1][1] != '்'):
        new_word+=letters[index][0]+ '்'
        new_word+=''.join(letters[index:])
        global num_insertion
        num_insertion+=1
        return new_word
    return word

def deletion(word,next_word):
    letters = utf8.get_letters(word)
    if letters[-1] == next_word[0] + '்':
        new_word=''.join(letters[:-1])
        global num_deletion
        num_deletion+=1
        return new_word
    return word

def substitution1(word,next_word=""):
    target_chars = [['ர','ற'],['ல','ள','ழ'],['ன','ண','ந'],['ங','ஞ']]
            #    { 'ி', 'ீ'},{'','ா','ை'},{'ு', 'ூ'},{'ெ', 'ே'},{'ொ', 'ோ'}
                
    letters = utf8.get_letters(word)
    index = 0 if len(letters)==1 else random.randint(0,len(letters)-1)  
    for l in target_chars:
        if letters[index][0] in l:
            sub_char=random.choice([char for char in l if char != letters[index][0]])
            new_word=''.join(letters[:index])+sub_char
            if len(letters[index])==2:
                new_word+=letters[index][1]
            if len(letters)>index+1:
                new_word+=''.join(letters[index+1:])
            global num_substitution
            num_substitution+=1
            
            return new_word
    return word

def substitution2(word,next_word=""):
    target_chars = [[ 'ி', 'ீ'],['','ா','ை'],['ு', 'ூ'],['ெ', 'ே'],['ொ', 'ோ']]
            #    
                
    letters = utf8.get_letters(word)
    index = 0 if len(letters)==1 else random.randint(0,len(letters)-1)  
    for l in target_chars:
        if len(letters[index])==1:
            sub_char=random.choice(['ா','ை'])
            new_word=''.join(letters[:index])+letters[index]+sub_char
            if len(letters)>index+1:
                new_word+=''.join(letters[index+1:])
            global num_substitution2
            num_substitution2+=1
            
            return new_word
            
        
        if len(letters[index])==2 and letters[index][1] in l:
            sub_char=random.choice([char for char in l if char != letters[index][1]])
            new_word=''.join(letters[:index])+letters[index][0]+sub_char
            
            if len(letters)>index+1:
                new_word+=''.join(letters[index+1:])
            
            num_substitution2+=1
            
            return new_word
        
    return word

def transpose(word,next_word=""):
    letters = utf8.get_letters(word)
    if len(letters) < 3:
        return word
    index = 1 if len(letters)==3 else random.randint(1,len(letters)-2)  
    # index=random.randint(1,len(letters)-2)
    new_word=''.join(letters[:index])+letters[index+1]+letters[index]
    global num_transpose
    num_transpose+=1
    if len(letters)>index+2:
        new_word+=''.join(letters[index+2:])
    return new_word

# Create a list of functions
functions = [insertion, transpose ,substitution1,substitution2, deletion]


def introduce_errors(text,error_prob):
    punctuations = {'.',',','"',"'"}
    for i in range(len(text)):
        for j in range(len(text[i])):
            if text[i][j] in punctuations:
                continue
            if random.random()<error_prob:
                punctuation=''
                if text[i][j][-1] in punctuations:
                    punctuation=text[i][j][-1]
                    text[i][j]=text[i][j][:-1]
                if j==len(text[i])-1:
                    chosen_function = random.choices(functions[:4], weights=[10,7,20,7], k=1)[0]
                    text[i][j]=chosen_function(text[i][j])
                else:
                    chosen_function = random.choices(functions, weights=[10,7,20,7,15], k=1)[0]
                    text[i][j]=chosen_function(text[i][j],text[i][j+1])
                text[i][j]+=punctuation
    for i in range(len(text)):
        text[i]=' '.join(text[i])
    text='\n'.join(text)

    with open('noise_500mb.txt', 'w', encoding='utf-8') as file:
        file.write(text)

introduce_errors(text,0.5)
total_errors=(num_substitution2+num_deletion+num_insertion+num_substitution+num_transpose)
print("total words=",total_words)
print("insertions=",num_insertion,num_insertion/total_errors*100,"%")
print("deletions=",num_deletion,num_deletion/total_errors*100,"%")
print("transpose=",num_transpose,num_transpose/total_errors*100,"%")
print("substitutions=",num_substitution,num_substitution/total_errors*100,"%")
print("substitutions2=",num_substitution2,num_substitution2/total_errors*100,"%")

print("percentage=",total_errors/total_words*100,"%")