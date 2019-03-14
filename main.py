#!/usr/bin/env python3
import os
import praw
import requests
import json
import re
import random


DEEPAPI_API_KEY = os.environ["DEEPAPI_API_KEY"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
HISTORY_FILENAME = "history.json"
IMAGE_URL_REGEX = r"(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png)"
ROSS_URLS = [
    "https://i.imgur.com/GSJk3U0.png",
    "https://i.imgur.com/bOCcT0t.png",
    "https://i.imgur.com/rGV6xgj.png",
    "https://i.imgur.com/F8itsh6.png",
    "https://i.imgur.com/Vrbisfu.png",
    "https://i.imgur.com/Hklekjf.png",
    "https://i.imgur.com/SnmHMeM.png",
    "https://i.imgur.com/SjbTZYd.png",
    "https://i.imgur.com/5z0B6mb.png",
    "https://i.imgur.com/pz3LCBr.png",
]


def do_style(style_url, image_url):
    r = requests.post(
        "https://api.deepai.org/api/neural-style",
        data={
            'style': style_url,
            'content': image_url,
        },
        headers={'api-key': DEEPAPI_API_KEY}
    )
    return r.json()


def load_history():
    try:
        with open(HISTORY_FILENAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_history(history):
    with open(HISTORY_FILENAME, "w") as f:
        json.dump(history, f)


def main():
    history = load_history()
    reddit = praw.Reddit(client_id='fEMi2K9P4x4Lcg',
                         client_secret=REDDIT_CLIENT_SECRET,
                         username='imaginary_ross_bot',
                         password='XBLjstJfC999z3hcqDRCHf59UYngRWun',
                         user_agent='linux:botross:v0.1 (by /u/mpfei)')
    print("logged in as", reddit.user.me())
    landscape_subreddit = reddit.subreddit("ImaginaryLandscapes")
    landscape_submissions = landscape_subreddit.hot(limit=10)
    for landscape_submission in landscape_submissions:
        new_url = landscape_submission.url
        if new_url in history or not re.match(IMAGE_URL_REGEX, new_url):
            continue
        print("new image url:", new_url)
        deepapi_output = do_style(random.choice(ROSS_URLS), new_url)
        print(deepapi_output)
        if 'err' in deepapi_output:
            # welp, deepapi probably didn't like the last image
            # blacklist it and try again
            print(deepapi_output['err'])
            history.append(new_url)
        else:
            break
    else:
        print("none of the top 10 hot posts worked out")
        return
    output_url = deepapi_output['output_url']
    image_data = requests.get(output_url).content
    with open("tmp_image", "wb") as f:
        f.write(image_data)
    output_subreddit = reddit.subreddit("testingground4bots")
    submission = output_subreddit.submit_image("happy little test",
                                               "./tmp_image")
    submission.reply("Original submission: [{}]({}) by /u/{}".format(
                     landscape_submission.title,
                     landscape_submission.shortlink,
                     landscape_submission.author.name))
    history.append(new_url)
    save_history(history)


if __name__ == '__main__':
    main()
