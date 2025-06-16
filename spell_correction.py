from transformers import MT5Tokenizer,MT5ForConditionalGeneration, AutoTokenizer, AutoModelForTokenClassification
import torch
import math
import re, Levenshtein
from collections import Counter
import copy
from tamil import utf8


model_name = "google/mt5-base"  # You can replace this with the appropriate model for Tamil
qa_model = MT5ForConditionalGeneration.from_pretrained(model_name)
qa_tokenizer = MT5Tokenizer.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
qa_model.to(device)


with open('sampledata.txt', 'r', encoding='utf-8') as file:
    text = file.readlines()

def remove_parenthesis_text(lines):
    # Regular expression to match text within parentheses
    # pattern = r'\(.*?\)'
    pattern = r'\(.?\)|<\/?doc.?>|[^ \u0B80-\u0BFF]'

    # Process each line and remove the parenthesis text
    cleaned_lines = [re.sub(pattern, '', line).strip() for line in lines]

    return cleaned_lines

def clean_line(line):
    # Use regex to substitute anything that's not a letter or space with an empty string
    return re.sub(r'[^஀-௿\s]', '', line)

text = remove_parenthesis_text(text)

text = [clean_line(line) for line in text]

def generate_ngrams(words, n):
    """Generate n-grams from a list of words."""
    return [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]

words=[]
unigrams = Counter()
bigrams = Counter()
trigrams = Counter()

for line in text:
    words_in_line = line.strip().split()
    unigrams.update(words_in_line)  # Unigrams
    bigrams.update(generate_ngrams(words_in_line, 2))  # Bigrams
    trigrams.update(generate_ngrams(words_in_line, 3))  # Trigrams
    words.extend(line.split(" "))

words=[word for word in words if word!='']

vocab=set(words)

model_path = "pytorch/"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path,torch_dtype=torch.float16)
model.eval()

# Label mapping
id_to_label = {0: "O", 1: "B-ERR"}

def predict(sentence):
    words = sentence.strip().split()
    encoding = tokenizer(words, is_split_into_words=True, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model(**encoding)
        predictions = torch.argmax(outputs.logits, dim=2)

    word_ids = encoding.word_ids()
    pred_labels = [id_to_label[pred.item()] for pred in predictions[0]]

    result = []
    for idx, word_idx in enumerate(word_ids):
        if word_idx is None:
            continue
        word = words[word_idx]
        if word_idx >= len(result):  # avoid duplicates
            result.append((word, pred_labels[idx]))
    return result

word_count_dict = {}
word_count_dict = Counter(words)
probs = {}
m = sum(word_count_dict.values())

for k, v in word_count_dict.items():
    probs[k] = v / m

def delete_letter(word):
    letters = utf8.get_letters(word)

    delete_l = []
    if len(letters)<3:
        return word

    for i in range(1,len(letters)):
        new_word=''.join(letters[:i])
        if len(letters)>i+1:
            new_word+=''.join(letters[i+1:])
        delete_l.append(new_word)

    return delete_l

def insert_letter(word):
    letters = utf8.get_letters(word)
    insert_l=[]

    for l in ['க', 'ச', 'ட', 'த', 'ப', 'ற',
                'ம', 'ய', 'ர', 'வ', 'ஜ', 'ஸ']:
        x=copy.deepcopy(letters)
        x.append(l+'்')
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
    target_chars = [['ர','ற'],['ல','ள','ழ'],['ன','ண','ந'],['ங','ஞ'], ['ன','ள'], ['ர','கள']]
    substitute_l=[]
    for i in range(0,len(letters)):

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
    for i in range(0,len(letters)):

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
    edit_one_set.update(delete_letter(word))
    edit_one_set.update(transpose_letter(word))
    edit_one_set.update(substitute_letter(word))
    edit_one_set.update(insert_letter(word))

    return edit_one_set

words_outof_context=0

# Compute Context Probability
def ngram_probability(word, prev_word, prev_prev_word):
    
    unigram_prob = unigrams.get(word, 0) / sum(unigrams.values())
    bigram_prob = bigrams.get((prev_word, word), 0) / unigrams.get(prev_word, 1)
    trigram_prob = trigrams.get((prev_prev_word, prev_word, word), 0) / bigrams.get((prev_prev_word, prev_word), 1)

    return 0.5 * trigram_prob + 0.4 * bigram_prob + 0.1 * unigram_prob

def normalize_scores(scores):
    min_score = min(scores.values())
    max_score = max(scores.values())

    if min_score == max_score:
        return {key: 1.0 for key in scores}  # Return all normalized to 1 if all scores are the same

    return {key: (value - min_score) / (max_score - min_score) for key, value in scores.items()}

def log_transform_scores(scores):
    return {key: math.log(value + 1e-8) for key, value in scores.items()}


def get_mt5_ranking(sentence, word, suggestions):
    mt5suggestions = copy.deepcopy(suggestions)
    qa_scores = {}

    cleaned_suggestions = set()
    for suggestion in mt5suggestions:
        suggestion = re.sub(r"[a-zA-Z0-9]", "", suggestion)
        suggestion = re.sub(r"[^\u0B80-\u0BFF\s]", "", suggestion).strip()
        if suggestion and len(suggestion) > 2:
            cleaned_suggestions.add(suggestion)

    for suggestion in cleaned_suggestions:
        input_text = f"Is '{suggestion}' the correct spelling for '{word}' in this sentence: {sentence}?"
        inputs = tokenizer(input_text, return_tensors="pt")

        with torch.no_grad():
            outputs = qa_model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss.item()

        qa_scores[suggestion] = 1 / (1 + loss)  # Convert loss to score
        
        if(len(cleaned_suggestions)>5):
            distance_penalty = math.exp(-1 * Levenshtein.distance(word, suggestion))
            qa_scores[suggestion] *= distance_penalty

    total_score = sum(qa_scores.values())
    if total_score > 0:
        qa_scores = {w: score / total_score for w, score in qa_scores.items()}

    return qa_scores



def get_corrections(word, sentence, prev_word, prev_prev_word):

    #ngram = {}
    mt5 = {}
    final_scores = {}
    suggestions = []
    index = len(sentence.split(' '))-1
    
    if predict(" ".join(sentence))[index][1] == "O" and ngram_probability(word, prev_word, prev_prev_word) > 0.00001:
        return []

    one_error_set = edit_one_letter(word)
    suggestions = one_error_set.intersection(vocab)
    one_error = list(one_error_set)
    two_error_set = set()
    for i in one_error:
        two_error_set = two_error_set.union(edit_one_letter(i))
        
        suggestions = suggestions.union(two_error_set.intersection(vocab))
    
    suggestions = list(suggestions)
    
    suggestions.append(word)
    n_best_list_tuple = sorted(
        [(word, probs[word]) if word in probs else (word, 0) for word in suggestions]
,
        key=lambda x: x[1],
        reverse=True
    )

    n_best_list = [word for word, _ in n_best_list_tuple]
    n_best_list = list(dict.fromkeys(n_best_list))
    # l = n_best_list[6:10]
    n_best_list = n_best_list[:12]
    # for wrd in n_best_list:
    #     ngram[wrd] = ngram_probability(wrd, prev_word, prev_prev_word)

    sentence_text = " ".join(sentence)      
    # ngram = log_transform_scores(ngram)
    # ngram = normalize_scores(ngram)
    
    mt5 = get_mt5_ranking(sentence_text, word, n_best_list)
    sorted_mt5 = sorted(mt5.items(), key=lambda x: x[1], reverse=True)
    for i, (suggestion, score) in enumerate(sorted_mt5):
        final_scores[suggestion] = score
          
    n_best_list = [suggestion for suggestion, _ in sorted_mt5]
    n_best_list =sorted(n_best_list, key=lambda w: final_scores[w], reverse=True)
    # n_best_list.extend(l)
    n_best_list = n_best_list[:5] # Comment this line to get maximum accuracy of statistical model else this will give top 3 accuracy
    return n_best_list

