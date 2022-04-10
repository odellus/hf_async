# Async REST Server

A simple example of how to implement an asynchronous RESTful API to do NLP tasks with [`transformer`](https://github.com/huggingface/transformers), [`aiohttp`](https://docs.aiohttp.org/en/stable/), and [`asyncio`](https://docs.python.org/3/library/asyncio.html).

### Install Prereqs
Setting up an oauth token for Google Drive inside of the Google Cloud API can be intimidating, but it's worth the $36/year to be able to experiment with hybrid cloud computing. Follow the instructions in [PyDrive's Quickstart](https://pythonhosted.org/PyDrive/quickstart.html) to set up your oauth tokens
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

## Why
 - Why not set up batch jobs with crontab or airflow or any other of a plethora of methods?  
 - Why set up an asynchronous RESTful API to launch batch jobs? The benefits of putting a service behind an API as opposed to making users install their own version are demonstrated innumerable times, so the real question is why asynchronous batch? 
 - Why not just hand the data in the body of the request and wait for a complete version to come back from the synchronous, real time server? 
 
 In the given example, it takes roughly __six seconds__ to summarize a chapter of A Tale of Two Cities. In terms of event driven / serverless cloud computing, six seconds is an eternity. So we use cloud storage to tell it where to get the input and where to put the output. Doing it this way, we turn our local laptop/desktop into a hybrid cloud node as easily as setting up OAuth for Google Drive.

I was doing this with microk8s Jobs, but I wanted to be able to run a audio denoising API that uses the Nvidia Audio Effects SDK at the same time as training a model or doing inference, all inside kubernetes services, BUT Nvidia wants $20-30k for a GPU that is MIG-enabled and will allow more than one pod access to the resource at a time. That's too much. So I'm looking at solutions than PUT IT IN A CONTAINER. Might try to solve the dependency hell by putting all my services inside a single asynchronous server. I do all the inference one at a time. Packing them together in there in a giant batch doesn't speed things up and all it does is block the GPU off by occupying all the memory, so I can get away with doing inference for NLP and denoising audio at the same time. The denoising models aren't very large. I love Docker but I love saving money too. Hate being put in a place where I have to choose between the two, because I'm sorry Docker, but you're not that special.

But yeah back to the whole async batch thing, the idea is that you can specify some sort of alert when the message lands in storage, whether it's notifications from Google about your Drive or if it's an SNS set up to monitor an S3 bucket, you can get alerts when things get uploaded. There's the response from the async API. You're welcome. This is a quick and easy way to expose local computing resources that cost an arm and a leg to requisition from a cloud provider (**like GPUs**) to your primarily cloud based computing infrastructure that, since it is 2022, might be heavily geared towards serverless, asynchronous solutions that aren't going to want to sit around and wait for `LEDForConditionalGeneration` to grind through a long document for thousands upon thousands of milliseconds.
