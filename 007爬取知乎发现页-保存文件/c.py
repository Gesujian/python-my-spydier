import csv

filename = 'info.csv'
with open(filename, 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['question', 'author', 'answer'])