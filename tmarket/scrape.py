import os
import re
from selenium import webdriver
from selenium.webdriver import Chrome
from .logger_config import get_logger

class scrape:
    logger = get_logger(__name__)
    driver: Chrome = None
    WAIT_TIMEOUT = 1
    _chrome_options = webdriver.ChromeOptions()
    _quit = False
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
        print("The default user_agent is: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\n" +
              "Changing to another user_agent could probably make the website rejects the requests.\n" +
              "Create a new player object will still use the default user_agent\n")
        self.logger.info(f"Changed user agent to {user_agent}")
        self.user_agent = user_agent

    def get_current_user_agent(self):
        return self.user_agent
    
    def setup_parent_domain(self, parent_domain):
        pattern = r'^https://www\.transfermarkt\.[a-z]+$'
        if bool(re.match(pattern, parent_domain)):
            print("The default parent domain is: https://www.transfermarkt.com/\n" +
                "Changing to another parent domain could probably navigate to another website.\n" +
                "Create a new player object will still use the default parent domain\n")
            self.logger.info(f"Changed parent domain to {parent_domain}")
            self.parent_domain = parent_domain
        else:
            self.logger.warning(f"Failed to changed parent domain to {parent_domain} due to the invalid url")
            raise error.URLNavigationError("Invalid parent domain")
            

    def get_current_parent_domain(self):
        return self.parent_domain

    def _clear_log_file(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs/tmarket.log'),'w') as log_file:
            pass
    def _save_log_copy(self,save_path):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs/tmarket.log'), 'r') as original:
            content = original.read()
        with open(save_path, 'w') as save:
            save.write(content)


class error:
    
    class URLNavigationError(Exception):
        pass

    class UnknownDriverError(Exception):
        pass