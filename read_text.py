with open('ta.txt', 'r', encoding='utf-8') as file:
    lines = [next(file) for _ in range(1250000)]
    

#Open the file in write mode
with open("sample_500mb.txt", "w", encoding='utf-8') as file:
    # Write the content to the file
    for line in lines:
        file.write(line)