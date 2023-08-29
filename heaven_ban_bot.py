import argparse
import json

from llm import LLM
from bot import HeavenBanBot

parser = argparse.ArgumentParser()
parser.add_argument("username", help="The user handle you want to Heaven Ban. Example: AOC")
parser.add_argument("-m", "--model-name", help="(optional, defaults to llama 2 7b chat) LLM model you want to use (huggingface models). Example: meta-llama/Llama-2-7b-chat-hf")
parser.add_argument("-a", "--llm-api", help="(optional) use an API to pass up the llm prompts to")
parser.add_argument("-c", "--tweet-count", help="(optional, defaults to 10) amount of recent tweets you want to scrape to sumarize the ideology from")

args = parser.parse_args()

with open('config.json') as f:
    config = json.load(f)

if args.llm_api:
  llm = LLM(llm_api=args.llm_api)
else:
  llm = LLM()

bot = HeavenBanBot(args.username, config, llm)
bot.login()

# scrape user for tweets and summarize ideology
if args.tweet_count:
  bot.get_ideology(n=args.tweet_count)
else:
  bot.get_ideology()

# generate a reply
bot.reply_to_recent_thread()
