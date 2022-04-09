import re
import json

def load_book():
    with open('tale_of_two_cities.txt', 'r') as f:
        return f.read()

def chapterize(book):
    pattern = r'CHAPTER'
    chapters = re.split(pattern, book, flags=re.DOTALL|re.MULTILINE)
    chapter_start = 46 # Determined by manual investigation
    # Just get the chapters that have text
    chapters = [chapters[k].strip() for k in range(chapter_start, len(chapters))]
    return [{'text': x} for x in chapters]

def save_book(book):
    with open('tale2cities.json','w') as f:
        json.dump(book, f)

def prepare_data():
    book = load_book()
    chapters = chapterize(book)
    save_book(chapters)

if __name__ == '__main__':
    prepare_data()