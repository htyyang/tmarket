# Standard library imports
import re
import time
# Third-party library imports
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, TimeoutException
from bs4 import BeautifulSoup

# Relative imports
from .scrape import scrape
from .error import error
from .logger_config import get_logger, clear_log_file


class Player(scrape):
    logger = get_logger(__name__)
    transfer_history = []
    all_seasons_stats_compact = []
    def __init__(self, **kwargs):
            # Inherit
            self.logger.info("Create player object")
            super().__init__()
            # Core info
            self.core_info = {
                'name': kwargs.get('name', None),
                'id': kwargs.get('id', None),
                'url': kwargs.get('url', None),
            }
            # Basic data
            self.basic_data = _basic_data(**self.core_info)
            # Set up the chrome settings
            self._chrome_options.add_argument(f"user-agent={self.user_agent}")
            self._chrome_options.add_argument("--headless") # Do not pop up
            image_block = {"profile.managed_default_content_settings.images": 2}
            js_block = {"profile.managed_default_content_settings.javascript": 2}
            self._chrome_options.add_experimental_option("prefs", image_block)
            self._chrome_options.add_experimental_option("prefs", js_block)
            del js_block, image_block
            # Set up the driver
            self._start_driver()
            # Feed the url
            if self.core_info['url']: # Directly by the url
                self.driver.get(self.core_info['url'])
            elif self.core_info['id']: # By ID
                if "www.transfermarkt" in self.parent_domain:
                    self.driver.get(self.parent_domain + "any/profil/spieler/" + str(self.core_info['id']))
                else:
                    self.driver.get("https://www.transfermarkt.com/any/profil/spieler/" + str(self.core_info['id']))
            elif self.core_info['name']:
                try:
                    self.driver.get(self.parent_domain + "schnellsuche/ergebnis/schnellsuche?query=" + re.sub(r'\s+', '+', str(self.core_info['name'])))
                    if "Search results for players" in self._safe_find_element(driver = self.driver, path = "content-box-headline", attr="textContent", type=By.CLASS_NAME):
                        self.driver.get(self._safe_find_element(driver=self.driver, path="hauptlink", attr="href", type=By.CLASS_NAME, path_2="a",type_2=By.TAG_NAME))
                    else:
                        self.logger.error(f"Cannot find player's profile: {error.URLNavigationError(e)}")
                        self.logger.critical("The process failed to continue")
                        exit("1")
                except Exception as e:
                    self.logger.error(f"Cannot find player's profile: {error.URLNavigationError(e)}")
                    self.logger.critical("The process failed to continue")
                    exit("1")
            self.logger.info("Get player's profile url")
            try:
                self._check_url()
            except error.URLNavigationError as e:
                self.logger.critical(f"The process failed to continue: {e}")
                exit(1)
            #default scraping
            self._scrape_core_info()
            
            self._scrape_basic_data()
            
            # Quit the driver
            self.driver.quit()
            self.logger.info("Quit player object's initial driver ")
            self.driver = None
            
    # Start the driver
    def _start_driver(self):
        if self.driver is None:
            try:
                self.driver = webdriver.Chrome(options=self._chrome_options)
                self.logger.info("Start driver")
            except Exception as e:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self._chrome_options)
                self.logger.info(f"Install chrome driver and then start due to: {e}")
                # Fallback logic in case the above fails for any reason
                
    # Check url
    def _check_url(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "data-header")))
            self.logger.info("Correct profile url")
            return
        except Exception as e:
            if self.driver.current_url == ("https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"):
                self.driver.quit()
                self.logger.exception(f"Error navigating by wrong URL: {e}")
                raise error.URLNavigationError(f"Error navigating by wrong URL: {e}")
            elif not self.driver.current_url.startswith("https://www.transfermarkt.com/"):
                self.driver.quit()
                self.logger.exception(f"Error navigating by wrong URL: {e}")
                raise error.URLNavigationError(f"Error navigating by wrong URL: {e}")
            else: 
                self.driver.implicitly_wait(1)
                try:
                    WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "data-header")))
                    self.logger.info("Correct profile url")
                    return
                except:
                    pass
            self.driver.quit()
            self.logger.exception(f"Error navigating by wrong URL: {e}")
            raise error.URLNavigationError(f"Error navigating by wrong URL: {e}")

    # Scrape core info   
    def _scrape_core_info(self):
        self.core_info['name'] = self.basic_data.name = self._safe_find_element(driver = self.driver, path = ".data-header__headline-wrapper strong", type = By.CSS_SELECTOR)
        self.core_info['id'] = self.basic_data.id = self._safe_find_element(driver = self.driver, path = "div#subnavi[data-id]", attr = "data-id", type = By.CSS_SELECTOR)
        self.core_info['url'] = self.basic_data.url = self._safe_find_element(driver = self.driver, path = "//a[@class='tm-subnav-item megamenu']", attr = "href")
        self.logger.info("Scraped core info")
    # SCrape basic data
    def _scrape_basic_data(self):

        self.basic_data.status = self._safe_find_element(self.driver, path = "data-header__club", attr="textContent", type = By.CLASS_NAME)
        if self.basic_data.status != "Retired":
            self.basic_data.status = "Active"

        self.basic_data.image_url = self._safe_find_element(self.driver, "//div[@id='fotoauswahlOeffnen']//img", "src")
        self.basic_data.current_club_joined = self._safe_find_element(self.driver, "//span[text()='Joined: ']//span", "textContent")
        if self.basic_data.status == "Retired":
            self.basic_data.last_club_name = self._safe_find_element(self.driver, "//span[contains(text(),'Last club:')]//span//a", "title")
            self.basic_data.last_club_url = self._safe_find_element(self.driver, "//span[contains(text(),'Last club:')]//span//a", "href")
            self.basic_data.most_games_for_club_name = self._safe_find_element(self.driver, "//span[contains(text(),'Most games for:')]//span//a")
            self.basic_data.retired_since_date = self._safe_find_element(self.driver, "//span[contains(text(),'Retired since:')]//span", "textContent")
        else:
            self.basic_data.jersey_number = self._safe_find_element(driver = self.driver, path = "data-header__shirt-number", type = By.CLASS_NAME)
            if self.basic_data.jersey_number:
                try:
                    self.basic_data.jersey_number = self.basic_data.jersey_number.strip("#")
                except: 
                    pass
            self.basic_data.current_club_name = self._safe_find_element(self.driver, "//span[@class='data-header__club']//a", "title")
            self.basic_data.current_club_url = self._safe_find_element(self.driver, "//span[@class='data-header__club']//a", "href")
            self.basic_data.market_value_current = self._safe_find_element(driver = self.driver, path = "tm-player-market-value-development__current-value", attr = "textContent", type = By.CLASS_NAME)
            self.basic_data.current_club_contract_expires = self._safe_find_element(self.driver, "//span[text()='Contract expires: ']//span")
       
        #self.basic_data.current_club_contract_option = self._safe_find_element(self.driver, "//span[contains(text(),'Contract option:')]//following::span[1]", "textContent")
        #self.basic_data.name_in_home_country = self._safe_find_element(self.driver, "//span[text()='Name in home country:']//following::span[1]", "textContent")

        self.basic_data.full_name = self._safe_find_element(self.driver, "//span[text()='Full name:']//following::span[1]", "textContent")
        self.basic_data.DOB = self._safe_find_element(self.driver, "//span[text()='Date of birth:']//following::span[1]//a", "textContent")

        self.basic_data.place_of_birth_city = self._safe_find_element(self.driver, "//span[text()='Place of birth:']//following::span[1]//span", "textContent")
        self.basic_data.place_of_birth_country = self._safe_find_element(self.driver, "//span[text()='Place of birth:']//following::span[1]//span//img", "title")
        
        
        self.basic_data.age = self._safe_find_element(self.driver, "//span[text()='Age:']//following::span[1]", "textContent")
        
        
        self.basic_data.height = self._safe_find_element(self.driver, "//span[text()='Height:']//following::span[1]", "textContent")
      
        citizenship_element_content = self._safe_find_element(self.driver, "//span[contains(text(), 'Citizenship:')]/following-sibling::span[1]", "textContent")
        split_data = [] if citizenship_element_content is None else citizenship_element_content.split()
        self.basic_data.citizenship = tuple(filter(None, split_data))
        del split_data, citizenship_element_content
        
           

        self.basic_data.position = self._safe_find_element(self.driver, "//span[text()='Position:']//following::span[1]", "textContent")

        self.basic_data.position_main = self._safe_find_element(driver = self.driver, path = "detail-position__position", attr = "textContent", type = By.CLASS_NAME)
        self.basic_data.position_other = self._safe_find_element(driver = self.driver, path = "//dt[contains(text(),'Other position:')]//following::dd", attr = "textContent")
        another_position_other = self._safe_find_element(driver = self.driver, path = "//dt[contains(text(),'Other position:')]//following::dd[2]", attr = "textContent")

        if (self.basic_data.position_other and another_position_other) :
            self.basic_data.position_other = tuple((self.basic_data.position_other, another_position_other))
        del another_position_other

        self.basic_data.dominant_foot = self._safe_find_element(self.driver, "//span[text()='Foot:']//following::span[1]", "textContent")

        
        self.basic_data.market_value_max = self._safe_find_element(driver = self.driver, path = 'tm-player-market-value-development__max-value', attr = "textContent", type = By.CLASS_NAME)

        #self.basic_data.agent_name = self._safe_find_element(self.driver, "//span[text()='Player agent:']//following::span[1]//a", "textContent")
        #self.basic_data.agent_url = self._safe_find_element(self.driver, "//span[text()='Player agent:']//following::span[1]//a", "href")

        

     
        self.basic_data.outfitter = self._safe_find_element(self.driver, "//span[contains(text(),'Outfitter:')]//following::span[1]", "textContent")

        try:
            social_media_elements = WebDriverWait(self.driver, 0.1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='socialmedia-icons']")))
            self.basic_data.social_media_links = tuple(href.get_attribute('href') for href in social_media_elements.find_elements(By.XPATH, ".//a[@href]"))
        except: 
            self.basic_data.social_media_links = None
        # For 'social_media', assuming it might return multiple links
        self.logger.info("Scraped basic data")  
    # Get the info 
    def _safe_find_element(self, driver, path, attr=None, type=By.XPATH, path_2 = None, type_2=By.XPATH):
        """Returns the element's attribute or text safely. If element isn't found, return None."""
        try:
            element = WebDriverWait(driver, 0.1).until(EC.presence_of_element_located((type, path)))
            if path_2:
                element = element.find_element(type_2,path_2)
            if attr == "textContent":
                try:
                    text = element.get_attribute("textContent").strip()
                    if text in ["N/a", "N/A", "n/a"]:
                        return None
                    return text
                except AttributeError:
                    return None
            text_value = element.get_attribute(attr) if attr else element.text
            if text_value in ["N/a", "N/A", "n/a"]:
                return None
            return text_value
        except TimeoutException:
            return None
        except NoSuchElementException:
            return None
        except InvalidSelectorException:
            return None

    def get_core_info(self, df=False):
        if df:
            return pd.DataFrame([self.core_info])
        return self.core_info
  
    def get_basic_data(self, df=False, drop_na=False):
         if df:
            if drop_na:
                return pd.DataFrame([self.basic_data._to_dict()]).dropna(axis=1, how='all')
            return pd.DataFrame([self.basic_data._to_dict()])
         return self.basic_data._to_dict()
    
    def _scrape_transfer_history(self):
        self._start_driver()
        self.driver.get(self.core_info['url'])
        try:
            all_history = WebDriverWait(self.driver, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tm-player-transfer-history-grid')))
            all_history = all_history[1:-1]
            self.logger.info("Get all elments of transfer histories")
        except Exception as e:
            self.logger.exception(f"Can not find transfer history{e}")
            return None
        
        for one_history in all_history:
            history = _transfer_history()
            history.season = _transfer_history._extract_history_data(one_history, 'tm-player-transfer-history-grid__season')
            history.transfer_date = _transfer_history._extract_history_data(one_history, 'tm-player-transfer-history-grid__date')
            history.left = _transfer_history._extract_history_data(one_history, 'tm-player-transfer-history-grid__old-club', 'tm-player-transfer-history-grid__club-link')
            history.joined = _transfer_history._extract_history_data(one_history, 'tm-player-transfer-history-grid__new-club', 'tm-player-transfer-history-grid__club-link')
            history.market_value = _transfer_history._extract_history_data(one_history, 'tm-player-transfer-history-grid__market-value')
            history.fee = _transfer_history._extract_history_data(one_history, 'tm-player-transfer-history-grid__fee')
            self.transfer_history.append(history)
        self.logger.info("Scraped transfer histories")
        self.driver.quit()
        self.logger.info("Quit driver")
        self.driver = None

    def get_transfer_history(self, to_dict=False):
        if not self.transfer_history:
            self._scrape_transfer_history()
            self.logger.info("Scraped transfer history")
        if to_dict:
            history_dict_list = []
            for history in self.transfer_history:
                history_dict_list.append(history._to_dict())
            self.logger.info("Return transfer history in dictionary form")
            return history_dict_list
        self.logger.info("Return transfer history")
        return self.transfer_history

    def get_all_seasons_stats_compact(self, to_dict=False):
        if not self.all_seasons_stats_compact:
            self._scrape_all_seasons_stats_compact()
            self.logger.info("Scraped all seasons stats compact")
        if to_dict:
            stats_dict_list = []
            for stats in self.all_seasons_stats_compact:
                stats_dict_list.append(stats._to_dict())
            self.logger.info("Return all seasons stats compact in dictionary form")
            return stats_dict_list
        self.logger.info("Return all seasons stats compact")
        return self.all_seasons_stats_compact
    
    def _scrape_all_seasons_stats_compact(self):
        self._start_driver()
        self.driver.get(_all_seasons_stats_compact._provide_url_by_main_url(self.core_info['url']))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='items')
        # Ensure that the table was found before proceeding.
        if table:
            # Extract the tbody from the table
            tbody = table.find('tbody')
            if tbody:
            # Loop through each tr within the tbody
                for tr in tbody.find_all('tr'):
                    # Do whatever you want with each 'tr'
                    single_season_stats_compact = _all_seasons_stats_compact._get_single_season_stats_compact(tr)
                    self.all_seasons_stats_compact.append(single_season_stats_compact)
        else:
            self.all_seasons_stats_compact.append(None)
        self.driver.quit()
class _basic_data:
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
    social_media_links = None
    status = None

    def __init__(self, **kwargs):
            self.name = kwargs.get('name', None)
            self.id = kwargs.get('id', None)
            self.url = kwargs.get('url', None)

    def _to_dict(self):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}

class _transfer_history:
    season = None
    transfer_date = None
    left = None
    joined = None
    market_value = None
    fee = None

    def __str__(self):
        return f"season:{self.season}\ntransfer date:{self.transfer_date}\nleft from:{self.left}\njoined:{self.joined}\nmarket value:{self.market_value}\nfee:{self.fee}"
        
    def _to_dict(self):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}
    
    def _extract_history_data(element, class_name1, class_name2 = None):
        try:
            if class_name2:
                return element.find_element(By.CLASS_NAME, class_name1)\
                            .find_element(By.CLASS_NAME, class_name2)\
                            .get_attribute('textContent').strip()
            else:
                return element.find_element(By.CLASS_NAME, class_name1).get_attribute('textContent').strip()
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

class _all_seasons_stats_compact:
    season = None
    competetion = None
    team = None
    game_num = None
    goal = None
    assists = None
    cards = None
    minutes = None

    def __str__(self):
        return (f"season: {self.season}\n"
                f"competetion: {self.competetion}\n"
                f"team: {self.team}\n"
                f"game_num: {self.game_num}\n"
                f"goal: {self.goal}\n"
                f"assists: {self.assists}\n"
                f"cards: {self.cards}\n"
                f"minutes: {self.minutes}")
    
    def _to_dict(self):
        return {attr: getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}
    
    @staticmethod
    def _provide_url_by_main_url(url):
        parts = url.split('/')
        # Check if the URL is in the expected format
        if len(parts) < 5 or parts[-3] != "profil":
            raise ValueError("URL not in the expected format!")
        parts[-3] = "leistungsdatendetails"
        # Join the parts back together
        return '/'.join(parts)
    
    @staticmethod
    def _get_single_season_stats_compact(tr):
        single_season = _all_seasons_stats_compact()
        single_season.season = tr.find('td', class_='zentriert').text
        competition_img = tr.find('td', class_='hauptlink no-border-rechts').find('img')
        single_season.competetion = competition_img['title'] if competition_img else None
        team_img = tr.find('td', class_='hauptlink no-border-rechts zentriert').find('img')
        single_season.team = team_img['title'] if team_img else None
        single_season.game_num = tr.find_all('td', class_='zentriert')[2].text
        single_season.game_num = _all_seasons_stats_compact._replace_with_num(single_season.game_num)
        single_season.goal = tr.find_all('td', class_='zentriert')[3].text
        single_season.goal = _all_seasons_stats_compact._replace_with_num(single_season.goal)
        single_season.assists = tr.find_all('td', class_='zentriert')[4].text
        single_season.assists = _all_seasons_stats_compact._replace_with_num(single_season.assists)
        data_string = tr.find_all('td', class_='zentriert')[5].text
        data_values = [int(x.strip()) if x.strip().isdigit() else 0 for x in data_string.split('/')]
        single_season.cards = {'yellow cards': data_values[0], 'second yellow cards': data_values[1], 'red cards': data_values[2]}
        # Ensure there are 3 values by padding with Nones if necessary
        single_season.minutes = tr.find('td', class_='rechts').text
        single_season.minutes=_all_seasons_stats_compact._replace_with_minutes(single_season.minutes)
        return single_season

    @staticmethod
    def _replace_with_num(string):
        if string:
            if string == "-":
                return "0"
            return int(string)
        return None
    
    @staticmethod
    def _replace_with_minutes(string):
        if string:
            if string == "-":
                return 0
            else:
                string = string.replace("'", "")
                string = string.replace(".", "")
            return int(string)
        return None

if __name__ == '__main__':
    try:
            start_time = time.time()
            clear_log_file()
            messi = Player(url = "https://www.transfermarkt.com/lionel-messi/profil/spieler/28003")
            print("--- %s seconds ---" % (time.time() - start_time))
            print(messi.get_core_info())
            print(messi.get_basic_data(True,True))
            start_time = time.time()
            a = messi.get_all_seasons_stats_compact(True)
            
            for data_compact in a:
                print(data_compact)
            print("--- %s seconds ---" % (time.time() - start_time))
    except Exception as e:
                print(f"Error: {e}")
    finally:
            try:
                messi._save_log_copy("/Users/haotianyang/desktop")
                messi.driver.quit()
            except: pass