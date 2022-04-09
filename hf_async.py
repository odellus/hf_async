from aiohttp import web
import asyncio
import json
import time
import torch
import argparse

from typing import Tuple
from transformers import (
    T5TokenizerFast, 
    T5ForConditionalGeneration,
    LEDTokenizerFast,
    LEDForConditionalGeneration,
)

def parse_args():
    '''LED is a better example for async because processing long documents
    is compute intensive.
    '''
    parser = argparse.ArgumentParser(description='An async NLP server.')
    parser.add_argument('--qa', action='store_true')
    return parser.parse_args()

args = parse_args()

def load_macaw() -> Tuple[T5TokenizerFast, T5ForConditionalGeneration]:
    print('Loading MACAW tokenizer and model...')
    fpath = '/home/thomas/src/hf_models/macaw-large'
    tokenizer = T5TokenizerFast.from_pretrained(fpath)
    model = T5ForConditionalGeneration.from_pretrained(fpath)
    model = model.to('cuda')
    return tokenizer, model

def load_led() -> Tuple[LEDTokenizerFast, LEDForConditionalGeneration]:
    print('Loading LED tokenizer and model...')
    fpath = '/home/thomas/src/hf_models/led-large-16384-arxiv'
    tokenizer = LEDTokenizerFast.from_pretrained(fpath)
    model = LEDForConditionalGeneration.from_pretrained(fpath)
    model = model.to('cuda')
    return tokenizer, model

if args.qa:
    tokenizer, model = load_macaw()
else:
    tokenizer, model = load_led()

async def summarize_text(
    input_str: str, 
    tokenizer: LEDTokenizerFast, 
    model: LEDForConditionalGeneration,
    ) -> str:
    input_ids = tokenizer(input_str, return_tensors='pt').input_ids.to('cuda')
    global_attention_mask = torch.zeros_like(input_ids).to('cuda')
    global_attention_mask[:,0] = 1
    output = model.generate(input_ids, global_attention_mask=global_attention_mask)
    output_str = tokenizer.decode(output[0], skip_special_tokens=True)
    print(output_str)
    return output_str

async def summarize_request(request):
    try:
        inputs = await request.json()
        print(json.dumps(inputs))
        context = inputs.get('context')
        loop = asyncio.get_event_loop()
        loop.create_task(
            answer_question(context, tokenizer, model)
        )
        resp_obj = {'status': 'success', 'inputs': inputs}
        return web.Response(text=json.dumps(resp_obj), status=200)
    except Exception as e:
        resp_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(resp_obj), status=500)

async def answer_question(
    input_str: str, 
    tokenizer: T5TokenizerFast, 
    model: T5ForConditionalGeneration,
    ) -> str:
    input_ids = tokenizer(input_str, return_tensors='pt').input_ids.to('cuda')
    output = model.generate(input_ids, max_length=300)
    output_str = tokenizer.decode(output[0], skip_special_tokens=True)
    print(output_str)
    return output_str

async def ask_question(request) -> web.Response:
    '''
    Another asynchronous function that handles requests, taking the
    nap_length parameter as input from the body of a post request
    and launching a waiter task with the corresponding nap_length.
    Returns response immediately while `waiter` runs asynchronously.
    '''
    try:
        if args.qa:
            resp_obj = {'status': 'failed', 'reason': 'Not in QA mode'}
            return web.Response(text=json.dumps(resp_obj), status=500)
        inputs = await request.json()
        print(json.dumps(inputs))
        question = inputs.get('question')
        context = inputs.get('context')
        input_str = f"$answer$; $question$ = {question}"
        if context is not None:
            input_str += f"; $context$ = {context}"
        loop = asyncio.get_event_loop()
        loop.create_task(
            answer_question(input_str, tokenizer, model)
        )
        resp_obj = {'status': 'success', 'inputs': inputs}
        return web.Response(text=json.dumps(resp_obj), status=200)
    except Exception as e:
        resp_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(resp_obj), status=500)

async def waiter(t: int) -> None:
    '''An asynchronous dummy function that simulates a generic, 
    long running batch job. Takes as input an integer number of seconds.
    '''
    time.sleep(t)
    print('That was a refreshing nap')

async def take_nap(request) -> web.Response:
    '''
    Another asynchronous function that handles requests, taking the
    nap_length parameter as input from the body of a post request
    and launching a waiter task with the corresponding nap_length.
    Returns response immediately while `waiter` runs asynchronously.
    '''
    try:
        inputs = await request.json()
        print(json.dumps(inputs))
        nap_length = inputs.get('nap_length')
        loop = asyncio.get_event_loop()
        loop.create_task(waiter(int(nap_length)))
        resp_obj = {'status': 'success', 'inputs': inputs}
        return web.Response(text=json.dumps(resp_obj), status=200)
    except Exception as e:
        resp_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(resp_obj), status=500)



if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/ask_question', ask_question)
    app.router.add_post('/summarize_text', summarize_request)
    web.run_app(app)