# Standard library imports
import os

# Third-party library imports
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException

# Relative imports
from .scrape import scrape
from .scrape import error


class Player(scrape):
    
    def __init__(self, **kwargs):
            
            # Inherit
            super().__init__()

            # Core info
            self.core_info = {
                'name': kwargs.get('name', None),
                'id': kwargs.get('id', None),
                'url': kwargs.get('url', None),
            }
            # Basic data
            self.basic_data = basic_data(**self.core_info)

            # Set up the chrome settings
            self._chrome_options.add_argument(f"user-agent={self.user_agent}")
            self._chrome_options.add_argument("--headless") # Do not pop up

            # Set up the driver
            if self.driver is None:
                self._start_driver()
  
            # Feed the url
            if self.core_info['url']: # Directly by the url
                self.driver.get(self.core_info['url'])
            elif self.core_info['id']: # By ID
                if "www.transfermarkt" in self.parent_domain:
                    self.driver.get(self.parent_domain + "any/profil/spieler/" + str(self.core_info['id']))
                else:
                    self.driver.get("https://www.transfermarkt.com/any/profil/spieler/" + str(self.core_info['id']))

            # Check url
            try:
                self._check_url()
            except error.URLNavigationError as e:
                print(e)
                exit(1)

            # Default scraping content
            self._scrape_core_info()
            self._scrape_basic_data()

            # Quit the driver
            self.driver.quit()
            self.driver = None
            
    # Start the driver
    def _start_driver(self):
        try:
            if os.getenv("CHROMEDRIVER") is None:
                expected_cache_path = os.path.join(os.path.dirname(__file__), "drivers")
                    # Ensure the 'drivers' directory exists
                if not os.path.exists(expected_cache_path):
                    os.makedirs(expected_cache_path)
                    # Automatically download the necessary version of ChromeDriver to the specified cache path
                driver_path = ChromeDriverManager(cache_path=expected_cache_path).install()
            else:
                driver_path = os.getenv("CHROMEDRIVER")
            self.driver = webdriver.Chrome(executable_path=driver_path, options=self._chrome_options)
        except:
            # Fallback logic in case the above fails for any reason
            self.driver = webdriver.Chrome(options=self._chrome_options)

    # Check url
    def _check_url(self):
        self.driver.implicitly_wait(self.WAIT_TIMEOUT)
        if self.driver.current_url == ("https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"):
            self.driver.quit()
            raise error.URLNavigationError("Error navigating by wrong URL")
        elif not self.driver.current_url.startswith("https://www.transfermarkt.com/"):
            self.driver.quit()
            raise error.URLNavigationError("Error navigating by wrong URL")
        try:
            WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, "data-header")))
        except:
            self.driver.quit()
            raise error.URLNavigationError("Error navigating by wrong URL")

    # Scrape core info   
    def _scrape_core_info(self):
        self.core_info['name'] = self.basic_data.name = self._safe_find_element(self.driver, "//h1[@class='data-header__headline-wrapper']//strong")
        self.core_info['id'] = self.basic_data.id = self._safe_find_element(self.driver, "//div[@data-action='profil']", "data-id")
        self.core_info['url'] = self.basic_data.url = self._safe_find_element(self.driver, "//a[@class='tm-subnav-item megamenu']", "href")

    # SCrape basic data
    def _scrape_basic_data(self):
        self.basic_data.image_url = self._safe_find_element(self.driver, "//div[@id='fotoauswahlOeffnen']//img", "src")
        self.basic_data.jersey_number = self._safe_find_element(self.driver, "//span[@class='data-header__shirt-number']")
        self.basic_data.current_club_name = self._safe_find_element(self.driver, "//span[contains(text(), 'Current club:')]/following-sibling::span[1]//a[2]", "textContent")
        self.basic_data.current_club_url = self._safe_find_element(self.driver, "//span[@class='data-header__club']//a", "href")
        self.basic_data.current_club_joined = self._safe_find_element(self.driver, "//span[text()='Joined: ']//span", "textContent")
        self.basic_data.last_club_name = self._safe_find_element(self.driver, "//span[contains(text(),'Last club:')]//span//a", "title")
        self.basic_data.last_club_url = self._safe_find_element(self.driver, "//span[contains(text(),'Last club:')]//span//a", "href")
        self.basic_data.most_games_for_club_name = self._safe_find_element(self.driver, "//span[contains(text(),'Most games for:')]//span//a")
        self.basic_data.retired_since_date = self._safe_find_element(self.driver, "//span[contains(text(),'Retired since:')]//span", "textContent")
        self.basic_data.current_club_contract_expires = self._safe_find_element(self.driver, "//span[text()='Contract expires: ']//span")

        try:
            self.basic_data.current_club_contract_option = self._safe_find_element(self.driver, "//span[contains(text(),'Contract option:')]//following::span[1]", "textContent")
        except AttributeError:
            self.basic_data.current_club_contract_option = None

        self.basic_data.name_in_home_country = self._safe_find_element(self.driver, "//span[text()='Name in home country:']//following::span[1]", "textContent")

        self.basic_data.full_name = self._safe_find_element(self.driver, "//span[text()='Full name:']//following::span[1]", "textContent")
        self.basic_data.DOB = self._safe_find_element(self.driver, "//span[text()='Date of birth:']//following::span[1]//a", "textContent")
        self.basic_data.place_of_birth_city = self._safe_find_element(self.driver, "//span[text()='Place of birth:']//following::span[1]//span", "textContent")
        self.basic_data.place_of_birth_country = self._safe_find_element(self.driver, "//span[text()='Place of birth:']//following::span[1]//span//img", "title")

        
        self.basic_data.age = self._safe_find_element(self.driver, "//span[text()='Age:']//following::span[1]", "textContent")
        
        
        
        self.basic_data.height = self._safe_find_element(self.driver, "//span[text()='Height:']//following::span[1]", "textContent")

        citizenship_element_content = self._safe_find_element(self.driver, "//span[contains(text(), 'Citizenship:')]/following-sibling::span[1]", "textContent")
        split_data = [] if citizenship_element_content is None else citizenship_element_content.split()
        self.basic_data.citizenship = tuple(filter(None, split_data))
        
           

        self.basic_data.position = self._safe_find_element(self.driver, "//span[text()='Position:']//following::span[1]", "textContent")
        self.basic_data.position_main = self._safe_find_element(self.driver, "//dt[contains(text(),'Main position:')]//following::dd[1]", "textContent")
        self.basic_data.position_other = self._safe_find_element(self.driver, "//dt[contains(text(),'Other position:')]//following::dd", "textContent")
        self.basic_data.dominant_foot = self._safe_find_element(self.driver, "//span[text()='Foot:']//following::span[1]", "textContent")
        self.basic_data.market_value_current = self._safe_find_element(self.driver, "//div[@class='tm-player-market-value-development__current-value']", "textContent")
        self.basic_data.market_value_max = self._safe_find_element(self.driver, "//div[@class='tm-player-market-value-development__max-value']", "textContent")
        self.basic_data.agent_name = self._safe_find_element(self.driver, "//span[text()='Player agent:']//following::span[1]//a", "textContent")
        self.basic_data.agent_url = self._safe_find_element(self.driver, "//span[text()='Player agent:']//following::span[1]//a", "href")

        

     
        self.basic_data.outfitter = self._safe_find_element(self.driver, "//span[contains(text(),'Outfitter:')]//following::span[1]", "textContent")

        
        # For 'social_media', assuming it might return multiple links
        self.social_media_links = self._safe_find_element(self.driver, "//div[@class='socialmedia-icons']", "href")

        if self.basic_data.jersey_number:
            self.basic_data.jersey_number = self.basic_data.jersey_number.strip("#")

    # Get the info by xpath
    def _safe_find_element(self, driver, xpath, attr=None):
        """Returns the element's attribute or text safely. If element isn't found, return None."""
        try:
            element = driver.find_element(By.XPATH, xpath)
            if attr == "textContent":
                try:
                    text = element.get_attribute("textContent").strip().capitalize()
                    if text in ["N/a", "N/A", "n/a"]:
                        return None
                    return text
                except AttributeError:
                    return None
            text_value = element.get_attribute(attr) if attr else element.text
            if text_value in ["N/a", "N/A", "n/a"]:
                return None
            return text_value

        except NoSuchElementException:
            return None
        except InvalidSelectorException:
            return None

    def get_core_info_dict(self):
            return self.core_info

    def get_core_info_df(self):
        return pd.DataFrame([self.core_info])
        
    def get_basic_data_dict(self):
         return self.basic_data.to_dict()
    
    def get_basic_data_df(self):
        return pd.DataFrame([self.basic_data.to_dict()])
        
    def get_basic_data_df_available(self):
        return pd.DataFrame([self.basic_data.to_dict()]).dropna(axis=1, how='all')
            
# Class of basic data
class basic_data:
    age = None
    agent_name = None
    agent_url = None
    citizenship = None
    current_club_contract_expires = None
    current_club_contract_option = None
    current_club_joined = None
    current_club_name = None
    current_club_url = None
    DOB = None
    dominant_foot = None
    full_name = None
    height = None
    image_url = None
    last_club_name = None
    last_club_url = None
    market_value_current = None
    market_value_max = None
    most_games_for_club_name = None
    name_in_home_country = None
    outfitter = None
    place_of_birth_city = None
    place_of_birth_country = None
    position = None
    position_main = None
    position_other = None
    retired_since_date = None
    jersey_number = None
    social_media = None

    def __init__(self, **kwargs):
            self.name = kwargs.get('name', None)
            self.id = kwargs.get('id', None)
            self.url = kwargs.get('url', None)

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}

# Temp test entrance    
if __name__ == '__main__':
    try:
        messi = Player(id = 201)
        print(messi.get_core_info_df())
        print(messi.get_core_info_dict())
        print(messi.get_basic_data_df_available())
        print(messi.basic_data.citizenship)
        print(messi.basic_data.height)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        csv_file = os.path.join(desktop_path, "tmarket_output.csv")
        messi.get_basic_data_df_available().to_csv(csv_file, index=False)
        
    except Exception as e:
            print(f"Error: {e}")
    