from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class scrape:
    driver: Chrome = None
    WAIT_TIMEOUT = 2
    