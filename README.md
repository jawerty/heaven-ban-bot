# Heaven Ban Bot
An Experimental Twitter (X.com) bot that uses Llama 2 to reinforce a user's echo chamber. Essentially a echo chamber bot. 

I coded this in around 5 hours on my [live stream](https://www.youtube.com/watch?v=CIbfStCA_Ho) (August 28th 2023)

Overall, I think it's a fun idea and good to see the process of how to make one considering this will likely be happening on social media platforms in the near future.

# How does it work?
The bot works by first scraping recent tweets from the desired user to "heaven" ban. Using these tweets it will summarize the ideology with an LLM (tested with the LLama 2 chat model). With the ideology summary it will reply to recent tweets from the user with tweets that essentially agree/validates the user and aligns with their worldview.

![Screen Shot 2023-08-29 at 1 48 03 PM](https://github.com/jawerty/heaven-ban-bot/assets/1999719/c6742ceb-0341-4ac7-96c3-0da34fa8e6e6)

# How to use it
As a prerequisite please create a twitter account you want to act as the "Heaven Ban" Bot

### Build from source (best option)
1. Clone the repo
```
$ git clone git@github.com:jawerty/heaven-ban-bot.git
```
2. Install the PyPi Packages (I suggest using a virtualenv)
```
$ cd heaven-ban-bot
$ pip3 install -r requirements.txt
```
3. Add your bot's Twitter credentials to `config.json`
Update the username and password for your bot's twitter user

4. Run the bot 
```
$ python heaven_ban_bot.py [username]
```

see help for optional args
```
$ python heaven_ban_bot.py -h

usage: heaven_ban_bot.py [-h] [-m MODEL_NAME] [-a LLM_API]
                         [-c TWEET_COUNT]
                         username

positional arguments:
  username              The user handle you want to Heaven Ban.
                        Example: AOC

options:
  -h, --help            show this help message and exit
  -m MODEL_NAME, --model-name MODEL_NAME
                        (optional, defaults to llama 2 7b chat)
                        LLM model you want to use (huggingface
                        models). Example: meta-
                        llama/Llama-2-7b-chat-hf
  -a LLM_API, --llm-api LLM_API
                        (optional) use an API to pass up the llm
                        prompts to
  -c TWEET_COUNT, --tweet-count TWEET_COUNT
                        (optional, defaults to 10) amount of
                        recent tweets you want to scrape to
                        sumarize the ideology from
```

### Google Colab
Check out the [Google Colab](https://colab.research.google.com/drive/1eXl0dkcWKycu0B2AfBtcJQIz-2Xbbbbk?usp=sharing) I worked on in the live stream

Beware, building from source (in a local setup) is better since you can run the scraper without headless and less detectable.

# TODO
- Ask llm to shorten replies (character lengthening isn't working well)
