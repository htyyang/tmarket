import os
from selenium import webdriver
from selenium.webdriver import Chrome
from .logger_config import get_logger

class scrape:
    logger = get_logger(__name__)
    driver: Chrome = None
    WAIT_TIMEOUT = 1
    _chrome_options = webdriver.ChromeOptions()
    _quit = False
    current_directory = os.path.dirname(os.path.abspath(__file__))
    #file_path = os.path.join(current_directory, 'docs/url.txt')
    #with open(file_path, 'r') as file:  # Get the parent domain
        #parent_domain = file.readline().strip()
    #file_path = os.path.join(current_directory, 'docs/USER_AGENT.txt')
    #with open(file_path, 'r') as file:
        #user_agent = file.readline().strip()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    parent_domain = "https://www.transfermarkt.com/"
    logger.info("create scrape object")
    def setup_user_agent(self, user_agent):
        self.user_agent = user_agent

    def get_current_user_agent(self):
        return self.user_agent
    
    def setup_parent_domain(self, parent_domain):
        self.parent_domain = parent_domain

    def get_current_parent_domain(self):
        return self.parent_domain



class error:
    
    class URLNavigationError(Exception):
        pass

    class UnknownDriverError(Exception):
        pass