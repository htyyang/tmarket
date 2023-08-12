import os
from selenium import webdriver
from selenium.webdriver import Chrome

class scrape:
    driver: Chrome = None
    WAIT_TIMEOUT = 1
    _chrome_options = webdriver.ChromeOptions()
    _quit = False
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'docs/url.txt')
    with open(file_path, 'r') as file:  # Get the parent domain
        parent_domain = file.readline().strip()
    file_path = os.path.join(current_directory, 'docs/USER_AGENT.txt')
    with open('tmarket/docs/USER_AGENT.txt', 'r') as file:
        user_agent = file.readline().strip()

class error:
    
    class URLNavigationError(Exception):
        pass

    class UnknownDriverError(Exception):
        pass