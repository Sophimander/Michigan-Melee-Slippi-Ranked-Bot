from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

import selenium.common.exceptions
import re

username = None
password = None

slippi_url_prefix = "https://slippi.gg/user/"

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)


def login():
    if username and password:
        driver.get('https://slippi.gg')
        element = driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/header/div/header/div/div[3]/button')
        element.click()
        element = driver.find_element(by=By.XPATH, value='//*[@id="menu-appbar"]/div[3]/ul/li')
        element.click()
        element = driver.find_element(by=By.XPATH, value='//*[@id="email"]')
        element.send_keys(username)
        element = driver.find_element(by=By.XPATH, value='//*[@id="password"]')
        element.send_keys(password)
        element.submit()


def elo_sort(elem):
    return elem[4]


def is_valid_connect_code(connect_code):
    return re.match(r"^[a-zA-Z]{1,7}#[0-9]{1,7}$", connect_code) and len(connect_code) < 9


def connect_code_to_html(connect_code):
    return connect_code.replace("#", "-")


def format_elo_rating(elo_rating_string):
    if elo_rating_string == "PLAY RANKED MODE":
        return 0.0
    return float(elo_rating_string.split(" ")[0])


def does_user_exist(connect_code):
    driver.implicitly_wait(.5)

    driver.get(f"{slippi_url_prefix}{connect_code_to_html(connect_code)}")
    driver.implicitly_wait(.5)

    player_not_found = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div/div/p")
    if player_not_found.text == "Player not found":
        return False
    return True


def get_player_ranked_data_fast(connect_code):

    driver.implicitly_wait(.5)
    # Check if valid connect_code
    if not is_valid_connect_code(connect_code):
        return False

    # Get slipppi profile page, replace hashtag with - to go to correct link
    driver.get(f"{slippi_url_prefix}{connect_code_to_html(connect_code)}")
    driver.implicitly_wait(.5)
    try:
        rank_text = driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/p[3]").text
    except selenium.common.WebDriverException as e:
        print(e)
        return False
    if rank_text == "NONE":
        return [connect_code, "NONE", 0.0, 0, 0]
    elo_rating = driver.find_element(by=By.XPATH,
                                     value="/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/p[4]").text
    wins = int(driver.find_element(by=By.XPATH,
                               value="/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/div[2]/div/p[1]").text)
    loses = int(driver.find_element(by=By.XPATH,
                                value="/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/div[2]/div/p[3]").text)

    print(f"{connect_code}: {rank_text} | {elo_rating} | {wins}/{loses}")

    return [connect_code, rank_text, 0.0 if wins+loses < 5 else format_elo_rating(elo_rating), wins, loses]


def get_player_ranked_data(user):

    uid = user[0]
    name = user[1]
    connect_code = user[2]

    driver.implicitly_wait(.5)
    # Check if valid connect_code
    if not is_valid_connect_code(connect_code):
        return False

    # Get slipppi profile page, replace hashtag with - to go to correct link
    driver.get(f"{slippi_url_prefix}{connect_code_to_html(connect_code)}")
    driver.implicitly_wait(.5)
    try:
        rank_text = driver.find_element(by=By.XPATH,
                                        value="/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/p[3]").text
    except selenium.common.WebDriverException as e:
        print(e)
        return False
    if rank_text == "NONE":
        return [uid, name, connect_code, "NONE", 0.0, 0, 0]
    elo_rating = driver.find_element(by=By.XPATH,
                                     value="/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/p[4]").text
    wins = int(driver.find_element(by=By.XPATH,
                               value="/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/div[2]/div/p[1]").text)
    loses = int(driver.find_element(by=By.XPATH,
                                value="/html/body/div[1]/div/div/div/div/div[2]/div/div[2]/div[2]/div/p[3]").text)

    print(f"{connect_code}: {rank_text} | {elo_rating} | {wins}/{loses}")

    return [uid, name, connect_code, rank_text, 0.0 if wins+loses < 5 else format_elo_rating(elo_rating), wins, loses]


