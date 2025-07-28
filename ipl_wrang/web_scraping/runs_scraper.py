from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import pandas as pd
# Initialize WebDriver
def details(year):
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode (no GUI)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f'https://www.iplt20.com/stats/{year}'
    driver.get(url)

    # Wait for the page to load dynamically
    driver.implicitly_wait(15)  # Adjust wait time as needed

    # Get the page source
    page_content = driver.page_source

    # Now, parse the page using BeautifulSoup
    soup = BeautifulSoup(page_content, "html.parser")
    table = soup.find("table")  # Try again after the page is fully loaded

    title = table.find_all("th")
    print(title)

    header = []
    for i in title:
        name = i.text
        header.append(name)
    print(header)

    df = pd.DataFrame(columns=header)

    rows = table.find_all("tr")

    for i in rows[1:]:  # Skip header row
        data = i.find_all("td")
        row = [tr.text.strip() for tr in data]  # Remove unnecessary spaces

        # Append row to DataFrame
        if len(row) == len(df.columns):  # Ensure row matches number of columns
            df.loc[len(df)] = row

    # Reset index to remove any unintended extra columns
    df.reset_index(drop=True, inplace=True)
    df['year'] = year
    return df

def save_dataframe(df, filename, file_path):
    """
    This function takes a dataframe and save it as a csv file.
    
    df: dataframe to save
    filename: Name to use for the csv file eg: 'my_file.csv'
    file_path = where to save the file
    """
    path = os.path.join(file_path, filename)
    df.to_csv(path, index=False)


df_empty = []
# years = [2008,2009,2010,2011,2012,2013,2014,2015,2016,2018,2019,2020,2021,2023,2024]
years = [2017,2022]
for i in years:
    df = details(i)
    df_empty.append(df)

final_df = pd.concat(df_empty, ignore_index=True)

save_dataframe(final_df,'IPL_runs_2008_2024_temp.csv','/Users/Manan/Desktop/data_wrang_proj/ipl/data')