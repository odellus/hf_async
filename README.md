# Async REST Server

A simple example of how to implement an asynchronous RESTful API to do NLP tasks with [Hugging Face Transformers](https://github.com/huggingface/transformers), [`aiohttp`](https://docs.aiohttp.org/en/stable/), and [`asyncio`](https://docs.python.org/3/library/asyncio.html).

### Install Prereqs
```bash
python -m pip install -r requirements.txt
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
    url = 'http://0.0.0.0:8080/summarize_text'
    context = # Add your own long document to summarize
    d = {'context': context} # 
    res = requests.post(url, json=d)
    print(res.json(), res.status_code)

def test_qa():
    url = 'http://0.0.0.0:8080/ask_question'
    question = # Add your own question
    context = # Optionally, add some context
    d = {'question': question, 'context': context}
    res = requests.post(url, json=d)
    print(res.json(), res.status_code)
```