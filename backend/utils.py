
import base64
import json
import os
import pprint
import random
import re
import time
from mimetypes import guess_type

from agentlego import list_tools, load_tool
from openai import OpenAI


def tool_list():
    print(list_tools())
    return list_tools()


def gpt4o_history_call_stream(model, history, json=False):
    start = time.time()
    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    messages = history if history else []
    if json:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            stream=True
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
    # return response


def gpt4o_history_call(model, history, json=False):
    start = time.time()
    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    messages = history if history else []
    if json:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            stream=False
        )
    else:
        response = client.chat.completions.create(
            # max_tokens=300,
            model=model,
            messages=messages,
            stream=False
        )
    print(response.choices[0].message.content)
    print("Response Time:", time.time()-start)
    return response.choices[0].message.content


def gpt4o_call(model, prompt, system_prompt, json=False):
    start = time.time()
    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    if json:
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'system', 'content': system_prompt},
                      {'role': 'user', 'content': prompt}],
            # max_tokens=300,
            # temperature=0.7,
            # top_p=1,
            response_format={"type": "json_object"},
            stream=False
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'system', 'content': system_prompt},
                      {'role': 'user', 'content': prompt}],
            # max_tokens=300,
            # temperature=0.7,
            # top_p=1,
            # response_format={ "type": "json_object" },
            stream=False
        )
    # stream=True
    # for chunk in stream:
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")
    # print(response)
    print(response.choices[0].message.content)
    print("Response Time:", time.time()-start)
    return response.choices[0].message.content


def encode_image(image_path):
    # Function to encode the image
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def local_image_to_data_url(image_path):
    # Function to encode a local image into data URL
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    print(mime_type)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(
            image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"


def gpt4o_image_call(model, prompt, system_prompt, image_path):
    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    img_url = local_image_to_data_url(image_path)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url,
                        },
                    },
                ],
            }
        ],
        # max_tokens=300,
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content
