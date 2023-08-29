import pickle
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

class HeavenBanBot:
  def __init__(self, user_to_ban, bot_credentials, llm, chrome_driver_path="./chromedriver"):
    driver_path = chrome_driver_path
    chrome_options = Options()

    # add these arguments for a headless browser with a proxy url
    # proxy_server_url = "50.170.90.34"
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--remote-debugging-port=9222")
    # chrome_options.add_argument(f"--proxy-server={proxy_server_url}")

    service = Service(executable_path=driver_path)

    self.driver = webdriver.Chrome(service=service, options=chrome_options)
    self.logged_in = False
    self.bot_credentials = bot_credentials
    self.user_to_ban = user_to_ban
    self.user_ideology = "" # string that is related to their recent tweets that we summarize using the llm
    self.llm = llm
  
  def login(self):
    self.driver.get("https://twitter.com/i/flow/login");
    print("Logging in as", self.bot_credentials["username"])
    wait = WebDriverWait(self.driver, 100)

    try:
      print("Trying log in w/ saved cookies")
      cookies = pickle.load(open("cookies.pkl", 'rb'))
      for cookie in cookies:
        print(cookie)
        self.driver.add_cookie(cookie)
      print("Loaded Cookies!")
      return True
    except Exception as e: 
      print("Failed Getting Cookies:", str(e))
      pass

    # print(self.driver.text)

    # print(self.driver.page_source)
    # print(self.driver.find_element(By.XPATH, "/html/body").text)
    input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[autocomplete=\"username\"]")))
    # input = self.driver.find_element(By.CSS_SELECTOR, 'input[autocomplete=\"username\"]')
    input.click()
    input.send_keys(self.bot_credentials["username"])
    
    # find the next button
    all_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[role="button"]')

    found_button = None
    for button in all_buttons:
      if "Next" in button.text:
        # print("Found the next button")
        found_button = button;
        break
    
    found_button.click()

    password = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[autocomplete=\"current-password\"]")))
    # password = self.driver.find_element(By.CSS_SELECTOR, 'input[autocomplete=\"current-password\"]')
    password.click()
    password.send_keys(self.bot_credentials["password"])

    login = self.driver.find_element(By.CSS_SELECTOR, "[data-testid=\"LoginForm_Login_Button\"]")
    login.click()
    print("Successfully logged in")
    time.sleep(10)

    self.logged_in = True

  def scrape_recent_user_tweets(self, n=10):
    print(f"Scraping {n} tweets from {self.user_to_ban}")
    wait = WebDriverWait(self.driver, 100)

    self.driver.get(f"https://twitter.com/{self.user_to_ban}");

    cookies = self.driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))

    tweet_selector = "article[data-testid=\"tweet\"]"
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, tweet_selector)))

    # loop
    found_tweets = [] # array of strings

    def map_tweet(tweet_element):
      try:
        tweet_text_element = tweet_element.find_element(By.CSS_SELECTOR, "[data-testid=\"tweetText\"]").text
      except:
        tweet_text_element = None
      return tweet_text_element
      # get the text again

    def filter_tweet(tweet_element):
      # must have tweet text greater than 3 words
      try:
        tweet_text_element = tweet_element.find_element(By.CSS_SELECTOR, "[data-testid=\"tweetText\"]").text
        word_count_condition = len(tweet_text_element.split(" ")) > 3
      except:
        word_count_condition = False
      # must not be a repost
      
      try:
        social_context_text = tweet_element.find_element(By.CSS_SELECTOR, "[data-testid=\"socialContext\"]").text
        not_a_repost_condition = "reposted" not in social_context_text 
      except:
        # it is not a repost 
        not_a_repost_condition = True

      return word_count_condition and not_a_repost_condition

    while len(found_tweets) < n:
      tweets = self.driver.find_elements(By.CSS_SELECTOR, tweet_selector)
      tweets = map(map_tweet, filter(filter_tweet, tweets))
      
      # merge the newly found tweets ith the current tweets
      for tweet in tweets:
        if tweet is None:
          continue
        elif tweet in found_tweets:
          continue

        print("Found a new tweet:", tweet)
        found_tweets.append(tweet.strip())

      self.driver.execute_script("window.scrollBy(0, 2000)")
      time.sleep(1)
    
    return found_tweets

  def reply_to_recent_thread(self):
    print(f"Replying to recent thread")
    wait = WebDriverWait(self.driver, 100)

    self.driver.get(f"https://twitter.com/{self.user_to_ban}");
    time.sleep(1)

    # needs to scroll to trigger new tweet
    self.driver.execute_script("window.scrollBy(0, 2000)")
    tweet_selector = "article[data-testid=\"tweet\"]"
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, tweet_selector)))
    

    found_tweets = self.driver.find_elements(By.CSS_SELECTOR, tweet_selector)
    tweet_with_text = None
    for tweet in found_tweets:
      try:
        tweet.find_elements(By.CSS_SELECTOR, "[data-testid=\"tweetText\"]")
        tweet_with_text = tweet
        break
      except:
        continue

    if tweet_with_text is None:
      print("Could not find a tweet to reply to :(. Try another user?")
      return False

    tweet_text = tweet_with_text.text
    # use llama to generate reply
    reply_prompt = self.llm.prompt_for_generating_reply(tweet_text, self.user_ideology)
    res = self.llm.request(reply_prompt)
    reply = res["output"]
    print("The reply:", reply)

    # actually reply!
    reply_element = tweet_with_text.find_element(By.CSS_SELECTOR, "[data-testid=\"reply\"]")
    reply_element.click()

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid=\"tweetTextarea_0\"]")))
    time.sleep(1)

    actions = ActionChains(self.driver)
    actions.send_keys(reply[:240])
    actions.perform()

    buttons = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid=\"tweetButton\"]")
    found_reply_button = None
    for button in buttons:
      print("Reply check:", button.text)
      if "Reply" in button.text:
        found_reply_button = button
        break

    self.driver.execute_script("arguments[0].scrollIntoView();", found_reply_button)
    found_reply_button.click()
    time.sleep(3)
    print(f"\nYou have replied to a tweet!\nThe Tweet: {tweet_text}\nYour Bot's Reply: {reply}\n")


  def get_ideology(self, n=6):
    recent_tweets = self.scrape_recent_user_tweets(n=n)
    print("Getting ideology")

    prompt = self.llm.prompt_for_guessing_ideology(recent_tweets)
    res = self.llm.request(prompt)
    output = res["output"]
    # parse output
    
    self.user_ideology = output
    print('Ideology:', self.user_ideology)
    return self.user_ideology

