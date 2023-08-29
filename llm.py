import torch
import requests
from transformers import pipeline, AutoTokenizer
from accelerate import Accelerator

class LLM:
  def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf", llm_api=None):
    self.llm_api = llm_api
    
    if self.llm_api is None:
      tokenizer = AutoTokenizer.from_pretrained(model_name)
      pipeline = pipeline(
          "text-generation",
          model=model_name,
          torch_dtype=torch.float16,
          device_map="auto",
          trust_remote_code=True
      )
      self.pipeline = pipeline
      self.tokenizer = tokenizer

  def generate(self, prompt):
    if self.llm_api:
      return self.request(prompt)
    else:
      sequences = self.pipeline(
          prompt,
          do_sample=True,
          top_k=40,
          num_return_sequences=1,
          eos_token_id=self.tokenizer.eos_token_id,
          max_length=10000,
      )
      return sequences[0]['generated_text']
 
  def request(self, prompt):
    response = requests.post(self.llm_api, json={
      "prompt": prompt
    })

    return response.json()["output"]

  def prompt_for_generating_reply(self, tweet, ideology):
    return """
      [INST]
      <<SYS>>
      You are an intelligent bot that replies to twitter users as user requested persona. You will be given an ideology to pretend to be. You must reply to the given tween acting with your persona's ideology
      You must reply to the given tweet as if you completely agree with the user as well as utilize your persona.
      You must keep your reply within 140 characters (including spaces). Do not go over 140 characters in your response!
      You must not use more than 3 emojis in your response.

      The user will give you the tweet to the reply to in the following format.
      TWEET: the tweet to reply to

      The user will give you the ideology you must pretend to be in the following format.
      IDEOLOGY: the ideology you will pretend to have

      Do not reply with anything other than the reply and do not start with any explanation or feedback ONLY respond with the reply to the tweet.
      <</SYS>>
      TWEET: %s
      IDEOLOGY: %s
      [/INST]
    """ % (tweet, ideology)

  def prompt_for_guessing_ideology(self, tweets):
    tweets_string = ""
    for tweet in tweets:
      tweets_string += ". ".join(tweet.split('\n')) + "\n"

    return """
      [INST]
      <<SYS>>
      You are a intelligent bot knowledgable in world politics and culture.

      You will be given a series of "tweets" from a twitter account each separated by a newline character. 

      With these tweets you must guess the twitter user's political ideology and/or their cultural identity. You must reply in no more than 2 sentences a summary of what this twitter user's ideology is.

      The user will give you tweet in the format below
      TWEETS:
      the first tweet
      the second tweet
      the third tweet
      
      Do not reply with anything other than the twitter user's ideology summary
      <</SYS>>
      
      Tweets:
      %s
      [/INST]
    """ % tweets_string

