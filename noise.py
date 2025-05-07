from tamil import utf8
import random
import re

num_transpose=0
num_insertion=0
num_deletion=0
num_substitution=0
num_substitution2=0
total_lines=0
total_words=0

def remove_parenthesis_text(lines):
    # Regular expression to match text within parentheses
    # pattern = r'\(.*?\)'
    pattern = r'\(.*?\)|<\/?doc.*?>|[^. \u0B80-\u0BFF]'
    
    # Process each line and remove the parenthesis text
    cleaned_lines = [re.sub(pattern, '', line).strip() for line in lines]
    
    return cleaned_lines

def clean_line(line):
    # Use regex to substitute anything that's not a letter or space with an empty string
    return re.sub(r'[^஀-௿\s]', '', line)

with open('clean_test_data.txt', 'r', encoding='utf-8') as file:
    text = file.readlines()

text = remove_parenthesis_text(text)
text = [clean_line(line) for line in text]
text = [sentence.strip() for line in text for sentence in line.split('.') if sentence]
total_lines = len(text)



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
        if len(letters[index])==1 and letters[index] in ['க', 'ச', 'ட', 'த', 'ப', 'ற', 'ஞ', 'ங', 'ண', 'ந', 
                   'ம','ன', 'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ஜ', 'ஷ', 'ஸ', 'ஹ']:
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
#index_arr = []

total_single_errors=0
total_double_errors=0
word_cnt=0
def introduce_errors(text,error_prob):
    punctuations = {'.',',','"',"'",''}
    global word_cnt
    word_index=0
    global total_single_errors,total_double_errors
    single_error=[]
    double_error=[]
    no_error=[]

    

    for i in range(len(text)):
        for j in range(len(text[i])):
            original_word=text[i][j]
            no_of_errors=0
            if text[i][j] in punctuations:
                continue
            if random.random()<error_prob:
                
                punctuation=''
                if text[i][j][-1] in punctuations:
                    punctuation=text[i][j][-1]
                    text[i][j]=text[i][j][:-1]
                word = text[i][j]
                if j==len(text[i])-1 or text[i][j][-1] != '்':
                    chosen_function = random.choices(functions[:4], weights=[7,7,20,10], k=1)[0]
                    
                    text[i][j]=chosen_function(text[i][j])
                    # if(text[i][j]!=word):
                    #     index_arr.append(word_cnt)
                else:
                    chosen_function = random.choices(functions, weights=[7,7,20,10,50], k=1)[0]
                    
                    text[i][j]=chosen_function(text[i][j],text[i][j+1])
                    # if(text[i][j]!=word):
                    #     index_arr.append(word_cnt)
                if(text[i][j]!=word):
                    no_of_errors+=1
                text[i][j]+=punctuation
            if text[i][j] and random.random()<0.7:
                punctuation=""
                if text[i][j][-1] in punctuations:
                    
                    punctuation=text[i][j][-1]
                    text[i][j]=text[i][j][:-1]
                word = text[i][j]
                if j==len(text[i])-1 or text[i][j][-1] != '்':
                    chosen_function = random.choices(functions[:4], weights=[10,7,20,7], k=1)[0]
                    
                    text[i][j]=chosen_function(text[i][j])
                    # if(text[i][j]!=word):
                    #     index_arr.append(word_cnt)
                else:
                    chosen_function = random.choices(functions, weights=[10,7,20,7,50], k=1)[0]
                    
                    text[i][j]=chosen_function(text[i][j],text[i][j+1])
                    # if(text[i][j]!=word):
                    #     index_arr.append(word_cnt)
                if(text[i][j]!=word):
                    no_of_errors+=1
                if(text[i][j]==original_word):
                    no_of_errors=0
                text[i][j]+=punctuation
            
            if no_of_errors==0:
                no_error.append(word_index)
                
            elif no_of_errors==1:
                single_error.append(word_index)
                total_single_errors+=1
            elif no_of_errors==2:
                double_error.append(word_index)
                total_double_errors+=1

            word_cnt+=1
            word_index+=1
        chunk_size=300
        if i%chunk_size == chunk_size-1 or i==len(text)-1:
            file_name = f"Error_Files/error_details_{i // chunk_size + 1}.txt"
        
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(",".join(map(str,no_error)))
                file.write("\n")
                file.write(",".join(map(str,single_error)))
                file.write("\n")
                file.write(",".join(map(str,double_error)))
            no_error.clear()
            single_error.clear()
            double_error.clear()
            word_index=0
    for i in range(len(text)):
        text[i]=' '.join(text[i])
    
    # text='\n'.join(text)
    #print("total words=",word_cnt)
    chunk_size = 300

# Write chunks to files
    
    # with open("test_data_noise.txt", 'w', encoding='utf-8') as file:
    #     file.write("\n".join(text))

    for i in range(0, len(text), chunk_size):
        chunk=[]
        if i+chunk_size<len(text):
            chunk = text[i:i + chunk_size]
        else:
            chunk = text[i:]
        #print(chunk)
        file_name = f"Error_Files/error_file_{i // chunk_size + 1}.txt"
        
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write("\n".join(chunk))
    
    # with open('index.txt', 'w') as file:
    #     file.write(','.join(map(str, index_arr)))
    
    # with open('index.txt', 'r+', encoding='utf-8') as file:
    #     content = file.read().strip()
    #     if content:
    #         updated_content = content + ',' + ','.join(map(str, index_arr))
    #     else:
    #         updated_content = ','.join(map(str, index_arr))
    #     file.seek(0)
    #     file.write(updated_content)

introduce_errors(text,0.4)
total_errors=(num_substitution2+num_deletion+num_insertion+num_substitution+num_transpose)
print("total words=",word_cnt)
print("total lines=", total_lines)
print("insertions=",num_insertion,num_insertion/total_errors*100,"%")
print("deletions=",num_deletion,num_deletion/total_errors*100,"%")
print("transpose=",num_transpose,num_transpose/total_errors*100,"%")
print("substitutions=",num_substitution,num_substitution/total_errors*100,"%")
print("substitutions2=",num_substitution2,num_substitution2/total_errors*100,"%")
print("percentage=",(total_single_errors+total_double_errors)/total_words*100,"%")
print("total_single_errors=",total_single_errors,total_single_errors*100/word_cnt)
print("total_double_errors=",total_double_errors,total_double_errors*100/word_cnt)
