# Async REST Server

A simple example of how to implement an asynchronous RESTful API to do NLP tasks with [`transformer`](https://github.com/huggingface/transformers), [`aiohttp`](https://docs.aiohttp.org/en/stable/), and [`asyncio`](https://docs.python.org/3/library/asyncio.html).

### Install Prereqs
```bash
python -m pip install -r requirements.txt
```

### Prepare Data
```bash
# Chunk tale_of_two_cities.txt into chapters
python prepare_data.py
```

### Start server
```bash
python hf_async.py      # For long document summarization
python hf_async.py --qa # For question answering
```

### Test it out
Open an IPython REPL in a new terminal
```python
import requests

def test_summarization():
    '''Can take a minute, depending on length of context.
    Better example than MACAW/T5 with its 512 token limit.
    '''
    url = 'http://0.0.0.0:8080/summarize_text'
    context = # Add your own long document to summarize
    d = {'context': context} # 
    res = requests.post(url, json=d)
    print(res.json(), res.status_code)

def test_qa():
    '''Pretty much immediate response. Bad async example.
    '''
    url = 'http://0.0.0.0:8080/ask_question'
    question = # Add your own question
    context = # Optionally, add some context
    d = {'question': question, 'context': context}
    res = requests.post(url, json=d)
    print(res.json(), res.status_code)

def test_summarize_batch():
    '''Come back and check on tale2cities_cliffnotes.json in 
    about 260 seconds.
    '''
    url = 'http://0.0.0.0:8080/summarize_batch'
    d = {
        'input_filename': 'tale2cities.json',
        'output_filename': 'tale2cities_chapter_summaries.json'
    }
    res = requests.post(url, json=d)
    print(res.json())
```
