import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from selenium.common import exceptions
from time import sleep
import os
from selenium import webdriver

comment_data_list = []
unique_tweets = set()

chromedriver_path = r"C:\Users\vansh\Desktop\chromedriver-win64"
print("ChromeDriver path:", chromedriver_path)

# Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("executable_path=" + chromedriver_path)

def get_driver():
    return Chrome(options=chrome_options)

def get_post_url(driver, url):
    driver.get(url)
    return driver

def get_tweet_id(tweet):
    return ''.join(tweet)

def reply_Card_scraper(reply_card):
    username = reply_card.find_element_by_xpath('.//span[contains(text(),"@")]').text
    datetime = reply_card.find_element_by_xpath('.//time').get_attribute('datetime')
    try:
        text = reply_card.find_element_by_xpath('./div[2]/div[2]/div[2]//span').text
        quotes = reply_card.find_element_by_xpath('./div[2]/div[2]/div[4]/div[1]//span').text
        retweets = reply_card.find_element_by_xpath('./div[2]/div[2]/div[4]/div[2]//span').text
        likes = reply_card.find_element_by_xpath('./div[2]/div[2]/div[4]/div[3]//span').text
        print('card_collected :{}'.format(username))
    except NoSuchElementException:
        print('card_exception :{}'.format(username))
        return
    comment = (username, datetime, text, quotes, retweets, likes)
    return comment

def get_scraped_list(reply_cards):
    for reply_card in reply_cards[-10:]:
        data = reply_Card_scraper(reply_card)
        if data:
            data_id = get_tweet_id(data)
            if data_id not in unique_tweets:
                unique_tweets.add(data_id)
                comment_data_list.append(data)

def login_twitter(driver, username, my_password):
    login_url = 'https://twitter.com/login'
    driver.get(login_url)

    try:
        # Wait for the username input field to be present
        username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="session[username_or_email]"]')
        WebDriverWait(driver, 10).until(EC.visibility_of(username_input))
        username_input.send_keys(username)

        # Wait for the password input field to be present
        password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="session[password]"]')
        password_input.send_keys(my_password)

        # Click the login button
        login_button = driver.find_element(By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]')
        login_button.click()

        # Wait for the home screen to load
        WebDriverWait(driver, 10).until(EC.url_to_be("https://twitter.com/home"))

        uid_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="session[username_or_email]"]'))
        )

    except Exception as e:
        print(f"Error during login: {str(e)}")

def scroll_down_page(driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
    """The function will try to scroll down the page and will check the current
    and last positions as an indicator. If the current and last positions are the same after `max_attempts`
    the assumption is that the end of the scroll region has been reached and the `end_of_scroll_region`
    flag will be returned as `True`"""
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region

def collect_all_tweets_from_current_view(driver, lookback_limit=25):
    """The page is continuously loaded, so as you scroll down the number of tweets returned by this function will
    continue to grow. To limit the risk of 're-processing' the same tweet over and over again, you can set the
    `lookback_limit` to only process the last `x` number of tweets extracted from the page in each iteration.
    You may need to play around with this number to get something that works for you. I've set the default
    based on my computer settings and internet speed, etc..."""
    reply_card_xpath = '//div[@data-testid="tweet" and @class="css-1dbjc4n r-18u37iz"]'
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, reply_card_xpath)))
    page_cards = driver.find_elements(By.XPATH, reply_card_xpath)
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]

def save_data(scraped_list, filename):
    comment_data_df = pd.DataFrame(data=scraped_list,
                                    columns=['username', 'datetime', 'comment', 'comment_replies', 'comment_retweets',
                                             'comment_likes'])
    comment_data_df.to_csv(filename)

def main(username, password, filepath, post_url):
    driver = get_driver()  # Use get_driver to create the driver instance

    try:
        login_twitter(driver, username, password)
        get_post_url(driver, post_url)
        last_position = None
        end_of_scroll_region = False

        while not end_of_scroll_region:
            reply_cards = collect_all_tweets_from_current_view(driver)
            get_scraped_list(reply_cards)
            last_position, end_of_scroll_region = scroll_down_page(driver, last_position)

        save_data(comment_data_list, filepath)

    finally:
        driver.quit()

if __name__ == '__main__':
    usr = "VANSHIKASA21372"  # Your Twitter username
    pwd = "f?nQ&aM7e"  # Your Twitter password
    file_path = r'C:\Users\vansh\Desktop\Twitter_customer\collected_data.csv'
    post_url = 'https://twitter.com/narendramodi/status/1389162292022063106'

    main(usr, pwd, file_path, post_url)
