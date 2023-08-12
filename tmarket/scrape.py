from selenium import webdriver
from selenium.webdriver import Chrome

class scrape:
    driver: Chrome = None
    WAIT_TIMEOUT = 1
    _chrome_options = webdriver.ChromeOptions()
    _quit = False
    with open('tmarket/docs/URL.txt', 'r') as file:  # Get the parent domain
        parent_domain = file.readline().strip()
    with open('tmarket/docs/USER_AGENT.txt', 'r') as file:
        user_agent = file.readline().strip()

class error:
    
    class URLNavigationError(Exception):
        pass

    class UnknownDriverError(Exception):
        pass
    