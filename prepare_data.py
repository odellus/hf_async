import re
import json

from util import get_cfg
from typing import List

def load_book(cfg: dict) -> str:
    book_text_filename = cfg['book_text_filename']
    with open(book_text_filename, 'r') as f:
        return f.read()

def chapterize(book: str) -> List(dict):
    pattern = r'CHAPTER'
    chapters = re.split(pattern, book, flags=re.DOTALL|re.MULTILINE)
    chapter_start = 46 # Determined by manual investigation
    # Just get the chapters that have text
    chapters = [chapters[k].strip() for k in range(chapter_start, len(chapters))]
    return [{'text': x} for x in chapters]

def save_book(book: List(dict), cfg: dict) -> None:
    book_json_filename = cfg['book_json_filename']
    with open(book_json_filename,'w') as f:
        json.dump(book, f)

def prepare_data(cfg: dict) -> None:
    book = load_book(cfg)
    chapters = chapterize(book)
    save_book(chapters, cfg)

if __name__ == '__main__':
    cfg = get_cfg()
    prepare_data()