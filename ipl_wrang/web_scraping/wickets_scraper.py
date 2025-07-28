from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os 
# Chrome Browser class
class ChromeBrowser:
    def __init__(self):
        pass  # No need to specify chromedriver path manually

    def Chrome(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")  # Run in headless mode (optional)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Automatically download and use the correct ChromeDriver
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def save_dataframe(df, filename, file_path):
    """
    This function takes a dataframe and save it as a csv file.
    
    df: dataframe to save
    filename: Name to use for the csv file eg: 'my_file.csv'
    file_path = where to save the file
    """
    path = os.path.join(file_path, filename)
    df.to_csv(path, index=False)
class IPL_Data:
    def __init__(self, url_id, years):
        self.url_id = url_id
        self.years = years

    def ExtractDetails(self, n):
        Chrome1 = ChromeBrowser().Chrome()
        Chrome2 = ChromeBrowser().Chrome()
        
        year = self.years[n]
        id = self.url_id[n]
        url = f'https://www.cricbuzz.com/cricket-series/{id}/indian-premier-league-{year}/stats'
        #id - 7607
        Chrome1.get(url)
        time.sleep(3)  # Wait for page to load
        #seriesStats
        # Player Matches Inns Runs Avg Sr 4s 6s

        try:
            wickets_tab = Chrome1.find_element("xpath", "//a[@ng-click=\"setTab('mostWickets')\"]")
            wickets_tab.click()
            time.sleep(3)

            players = []
            info = []
            no =[]
            matches = []
            inns = []
            runs = []
            avg = []
            Sr = []
            fours = []
            sixes = []
            fifers = []

            table = Chrome1.find_element("xpath", '//*[@id="seriesStats"]/div[2]')
            player =  table.find_elements("class name", 'cb-text-link')
            for p in player:
                p = p.text
                players.append(p)

            
            match_elements = table.find_elements("xpath", ".//td[contains(@class, 'cb-srs-stats-td') and contains(@class, 'text-right')]")
            for m in match_elements:
                info.append(m.text)


            for i in range(0,len(info),9):
                no.append(info[i])
                matches.append(info[i+1])
                inns.append(info[i+2])
                runs.append(info[i+3])
                avg.append(info[i+4])
                Sr.append(info[i+5])
                fours.append(info[i+6])
                sixes.append(info[i+7])
                fifers.append(info[i+8])
            return {
            'No': no, 'Player':players,'Matches': matches, 'Overs': inns, 'Balls': runs, 
            'Wickets': avg, 'Average': Sr, 'Runs': fours, '4-fers': sixes, '5-fers': fifers
        }
            
        except Exception as e:
            print(f"Error extracting table for year {year}: {e}")
        finally:
            Chrome1.quit()

# Parameters
url_id = [7607]
years = [2024]

# Initialize scraper
Code = IPL_Data(url_id, years)
df_list = []  # Store each year's DataFrame

for i in range(len(url_id)):  
    print(f"Extracting data for year {years[i]}...")
    data_dict = Code.ExtractDetails(i)
    
    if data_dict:  # If data was successfully extracted
        df = pd.DataFrame(data_dict)
        df_list.append(df)

# Combine all data into a single DataFrame
final_df = pd.concat(df_list, ignore_index=True)


save_dataframe(final_df,'IPL_wickets_2024_wickets.csv','ipl/data/')

