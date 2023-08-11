import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from scrape import scrape

class Player(scrape):
    def __init__(self, **kwargs):
            #core info
            self.core_info = {
                'name': kwargs.get('name', None),
                'id': kwargs.get('id', None),
                'url': kwargs.get('url', None),
            }
            #basic data
            self.basic_data = basic_data(**self.core_info)
            #set up the driver
            if self.driver is None:
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

                    self.driver = webdriver.Chrome(executable_path=driver_path)
                except:
                    # Fallback logic in case the above fails for any reason
                    self.driver = webdriver.Chrome()
            
            # Set up the driver
            if self.basic_data.url: #Directly by the url
                self.driver.get(self.basic_data.url)
            elif self.basic_data.id: #By ID
                with open('../docs/URL.txt', 'r') as file:  # Get the parent domain
                    parent_domain = file.readline().strip()
                if "www.transfermarkt" in parent_domain:
                    self.driver.get(parent_domain + f"any/profil/spieler/{self.basic_data.id}")
                else:
                     self.driver.get(f"https://www.transfermarkt.com/any/profil/spieler/{self.basic_data.id}")

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
    date_of_birth = None
    foot = None
    full_name = None
    height = None
    image_url = None
    last_club_name = None
    last_club_url = None
    market_value_current = None
    market_value_highest = None
    most_games_for_club_name = None
    name_in_home_country = None
    outfitter = None
    place_of_birth_city = None
    place_of_birth_country = None
    position = None
    position_main = None
    position_other = None
    retired_since_date = None
    shirt_number = None
    social_media = None

    def __init__(self, **kwargs):
            #core info
            self.name = kwargs.get('name', None)
            self.id = kwargs.get('id', None)
            self.url = kwargs.get('url', None)


if __name__ == '__main__':
     messi = Player(url = "https://www.transfermarkt.com/lionel-messi/profil/spieler/28003")
     print(messi.driver.current_url)