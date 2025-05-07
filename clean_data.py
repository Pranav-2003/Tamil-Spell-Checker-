
import re
from tamil import utf8
def remove_parenthesis_text(lines):
    # Regular expression to match text within parentheses
    # pattern = r'\(.*?\)'
    pattern = r'\(.*?\)|<\/?doc.*?>|[^ \u0B80-\u0BFF.]'

    
    # Process each line and remove the parenthesis text
    cleaned_lines = [re.sub(pattern, '', line).strip() for line in lines]
    
    return cleaned_lines

def clean_line(line):
    # Use regex to substitute anything that's not a letter or space with an empty string
    return re.sub(r'[^஀-௿\s]', '', line)

with open('clean_data.txt', 'r', encoding='utf-8') as file:
    text = file.readlines()

text = remove_parenthesis_text(text)
text = [sentence.strip() for line in text for sentence in line.split('.') if sentence]
text = [clean_line(line) for line in text]

total_lines = len(text)
for i in range(len(text)):
    line=text[i].split(" ")
    line=[word for word in line if word!="" and (len(utf8.get_letters(word))>1 or word in ["பூ", "தீ", "நீ", "தா", "பா", "வா"])]
    text[i]=" ".join(line)
text = [line for line in text if line!=""]
        
with open('new_clean_data.txt','w', encoding='utf-8') as file:
    file.write("\n".join(text))