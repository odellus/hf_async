import asyncio
import json
import time
import torch
import argparse
import os

from aiohttp import web
from typing import Tuple, List
from pydrive.drive import GoogleDrive

from transformers import (
    T5TokenizerFast, 
    T5ForConditionalGeneration,
    LEDTokenizerFast,
    LEDForConditionalGeneration,
)

from utils import (
    get_cfg,
    get_drive,
    get_file,
    put_file,
)

def parse_args() -> argparse.Namespace:
    '''LED is a better example for async because processing long documents
    is compute intensive.
    '''
    parser = argparse.ArgumentParser(description='An async NLP server.')
    parser.add_argument('--qa', action='store_true')
    return parser.parse_args()

args = parse_args()
cfg = get_cfg()
drive = get_drive()

def load_macaw(cfg: dict) -> Tuple[T5TokenizerFast, T5ForConditionalGeneration]:
    print('Loading MACAW tokenizer and model...')
    hf_model_dir = cfg['hf_model_dir']
    macaw_model_name = cfg['macaw_model_name']
    fpath = os.path.join(hf_model_dir, macaw_model_name)
    tokenizer = T5TokenizerFast.from_pretrained(fpath)
    model = T5ForConditionalGeneration.from_pretrained(fpath)
    model = model.to('cuda')
    return tokenizer, model

def load_led(cfg: dict) -> Tuple[LEDTokenizerFast, LEDForConditionalGeneration]:
    print('Loading LED tokenizer and model...')
    hf_model_dir = cfg['hf_model_dir']
    led_model_name = cfg['led_model_name']
    fpath = os.path.join(hf_model_dir, led_model_name)
    tokenizer = LEDTokenizerFast.from_pretrained(fpath)
    model = LEDForConditionalGeneration.from_pretrained(fpath)
    model = model.to('cuda')
    return tokenizer, model

if args.qa:
    tokenizer, model = load_macaw(cfg)
else:
    tokenizer, model = load_led(cfg)


def load_book(filename: str, drive: GoogleDrive) -> dict:
    if not get_file(filename, drive): return None
    with open(filename, 'r') as f:
        return json.load(f)

def save_book(book: dict, filename: str, drive: GoogleDrive) -> None:
    with open(filename, 'w') as f:
        json.dump(book, f)
    put_file(filename, drive)

async def summarize_texts(
    input_filename: str,
    output_filename: str,
    drive: GoogleDrive,
    tokenizer: LEDTokenizerFast, 
    model: LEDForConditionalGeneration,
    ) -> List[str]:
    t = time.time()
    book = load_book(input_filename, drive)
    input_strs = [x['text'] for x in book]
    outputs = []
    for input_str in input_strs:
        output = await summarize_text(input_str, tokenizer, model)
        outputs.append(output)
    output_book = [{'summary': x} for x in outputs]
    save_book(output_book, output_filename, drive)
    print(f'Took {time.time()-t} seconds to summarize Tale of Two Cities.')
    return outputs

async def summarize_batch_request(request: web.Request) -> web.Response:
    try:
        if args.qa:
            resp_obj = {'status': 'failed', 'reason': 'Not in Summarize mode'}
            return web.Response(text=json.dumps(resp_obj), status=500)
        inputs = await request.json()
        input_filename = inputs.get('input_filename')
        output_filename = inputs.get('output_filename')
        loop = asyncio.get_event_loop()
        loop.create_task(
            summarize_texts(
                input_filename, 
                output_filename, 
                drive, 
                tokenizer, 
                model
            )
        )
        resp_obj = {'status': 'success'}
        return web.Response(text=json.dumps(resp_obj), status=200)
    except Exception as e:
        resp_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(resp_obj), status=500)


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
    print(input_str)
    print(output_str)
    return output_str

async def summarize_request(request: web.Request) -> web.Response:
    try:
        if args.qa:
            resp_obj = {'status': 'failed', 'reason': 'Not in Summarize mode'}
            return web.Response(text=json.dumps(resp_obj), status=500)
        inputs = await request.json()
        print(json.dumps(inputs))
        context = inputs.get('context')
        loop = asyncio.get_event_loop()
        loop.create_task(
            summarize_text(context, tokenizer, model)
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

async def ask_question(request: web.Request) -> web.Response:
    '''
    Another asynchronous function that handles requests, taking the
    nap_length parameter as input from the body of a post request
    and launching a waiter task with the corresponding nap_length.
    Returns response immediately while `waiter` runs asynchronously.
    '''
    try:
        if not args.qa:
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

async def take_nap(request: web.Request) -> web.Response:
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
    app.router.add_post('/summarize_batch', summarize_batch_request)

    web.run_app(app)
