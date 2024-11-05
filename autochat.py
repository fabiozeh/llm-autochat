#!/bin/env python

import requests
import backoff
import json
import sys
import argparse
import logging
import os

logging.basicConfig(level=logging.INFO)

def send_messages(args):

    url = args.url
    url = os.getenv('LLM_API_URL', default=None) if url is None else url

    if url is None:
        print("LLM_API_URL variable is not set.")
        return 1

    # Load the text file and split into paragraphs (separated by two empty lines)
    with open(args.input_file, 'r') as file:
        content = file.read()
        messages = content.split('\n\n\n')  # Assuming two empty lines between paragraphs

    session = requests.Session()  # Persist connection
    thread_msgs = []

    output = sys.stdout
    if args.output is not None:
        output = open(args.output, 'a')

    for i, message in enumerate(messages):
        print(f"Sending message {i+1}...\n")
        if (args.raw):
            payload = json.loads(message.strip())
        else:
            payload = {
                    "model": args.model,
                    "stream": False
                    }
            
            new_msg = {
                    "role": "user",
                    "content": message.strip()
                    }

            thread_msgs.append(new_msg)
            payload['messages'] = thread_msgs if args.chat else [new_msg]
            
        # Send POST request
        response = compute_with_backoff(lambda: session.post(url, json=payload, headers={"Content-Type":"application/json"}))

        # Check for successful response
        if response.status_code == 200:
            logging.debug(response.text)
            try:
                response_data = response.json()  # Assuming the response is in JSON format
            except json.decoder.JSONDecodeError as e:
                print(e)
                print(response.text)
                return 1
            thread_msgs.append(response_data['message'])
            print(f"Response {i+1}:\n------------\n")
            if (args.full_response):
                print(f"{json.dumps(response_data, indent=2)}\n", file=output)
            else:
                print(f"{response_data['message']['content']}\n", file=output)

        else:
            print(f"Error with message {i+1}: Status code {response.status_code}")
            print(response.text)
            output.close()
            return 1
    
    output.close()
    return 0


@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def compute_with_backoff(thunk):
    return thunk()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(
        prog='autochat',
        description='Automates the passing of messages to an LLM API.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--url', type=str,
                        help='Endpoint URL')
    parser.add_argument('input_file', metavar='I', type=str,
                        help='Text file containing double-line-break separated messages.')
    parser.add_argument('--raw', action='store_true',
                        help='Send messages as-is. Requires JSON formatted messages.')
    parser.add_argument('--model', type=str, default='llama3.1',
                        help='The model name.')
    parser.add_argument('--chat', action='store_true',
                        help='Send previous messages as chat history.')
    parser.add_argument('--full-response', action='store_true',
                        help='Output the full API response, in JSON.')
    parser.add_argument('-o', '--output', type=str,
                        help='Path to output file.')
    args = parser.parse_args()

    exit_code = send_messages(args)
    sys.exit(exit_code)

