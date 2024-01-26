from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
from selenium.webdriver.chrome.service import Service
import time 
import pandas as pd
import os
from get_chrome_driver import GetChromeDriver


from multiprocessing import Process

num_processes = 1

class Scraper():
    def __init__(self, df, range_start, range_end, range_interval):
        """
        Uses tool.chinaz.com to check availability of websites per geographic location

        Parameters
        ----------
        df : Pandas DataFrame
            Contains all the localities to iterate through and find availability for.
        range_start : Int
            Start number for the range (for multiprocessing).
        range_end : TYPE
            Final number for the range (for multiprocessing).
        range_interval : TYPE
            Interval number for the range (for multiprocessing).

        Returns
        -------
        None. Instead, saves results as Excel format to be stiched together later.

        """
        
        
        # manually-specified countries to get results from
        countries = ["台湾", "香港", "日本", "韩国", "美国", "荷兰", "泰国", "新加坡", "俄罗斯"]
        cols = countries + ["url"]
        checked_data = pd.DataFrame(columns=cols)
        self.start_driver()
        print("driver started")
        
        for i in range(range_start, range_end, range_interval):
            location = df["Url"][i].replace("http://","").replace("https://","")
                
            url = f"https://tool.chinaz.com/speedworld/{location}"
            self.driver.get(url)
            time.sleep(10)
            
            row = self.check_status(countries)
            to_save = row + [df["Url"][i]]
            checked_data.loc[i] = to_save
        
            checked_data.to_excel(f".//main__{str(range_start)}.xlsx")
        
    def check_status(self, countries):
        """

        Parameters
        ----------
        countries : List
            List of countries (in Chinese) that have servers on the website to check.

        Returns
        -------
        Results: List
            List with availability of each website per server (in order as countries).

        """
        # finds box
        try:
            speedlist = self.driver.find_element(By.ID, "speedlist")
            rows = speedlist.find_elements(By.CLASS_NAME, "row.listw.clearfix")
        except:
            time.sleep(15)
            try:
                speedlist = self.driver.find_element(By.ID, "speedlist")
                rows = speedlist.find_elements(By.CLASS_NAME, "row.listw.clearfix")
            except:
                # if box not found after two attempts, assume no result found
                return [None, None, None, None, None, None, None, None, None]
            
        def check_available_status(country, rows):
            
            def wait(row):
                """
                Waits up to 60 seconds for a result to load

                """
                wait = True
                timer = 0
                while wait and timer < 60:
                    if "正在加载..." in row.text:
                        time.sleep(1)
                    else:
                        wait = False
                        timer += 1
                        break
                    
            for row in rows:
                # wait until result has been loaded
                wait(row)
                # check whether result matches locality we are interested in
                place = row.find_element(By.NAME, "city").text
                if country in place:
                    http_state = row.find_element(By.NAME, "httpstate").text
                    # if status == 200, website loads, return 200
                    if http_state == "200":
                        return "200"
            # if it did not find a 200 status for the locality, 
            # find the first result that has a non-200 status code
            for row in rows:
                wait(row)
                place = row.find_element(By.NAME, "city").text
                if country in place:
                    http_state = row.find_element(By.NAME, "httpstate").text
                    for status_code in range(200, 599):
                        if http_state == (str(status_code)):
                            return str(status_code)
            # if no results found, indicate 'unavailable' for failure to reach server
            return "unavailable"

        results = []
        for country in countries:
            results.append(check_available_status(country, rows))
        return results
            
        
    def start_driver(self):
        """
        Starts Chrome webdriver, installs via GetChromeDriver if not working first time
        """
        # settings to minimize chance of scraper detection
        options = webdriver.ChromeOptions() 
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('prefs',  {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
            }
        )
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")
        options.page_load_strategy = 'eager'
        
        # execute webdriver
        try:
            self.driver = webdriver.Chrome(options=options)
        except (WebDriverException, SessionNotCreatedException):
            if "chromedriver" in os.listdir():
                chrome_version = os.listdir("chromedriver")[0]
                chrome_path = os.path.join("chromedriver", chrome_version, "bin", "chromedriver.exe")
                service = Service(chrome_path)
                try:
                    self.driver = webdriver.Chrome(service=service, options=options)
                except (WebDriverException, SessionNotCreatedException):
                    get_driver = GetChromeDriver()
                    get_driver.install()
                    self.driver = webdriver.Chrome(options=options)
            else: 
                get_driver = GetChromeDriver()
                get_driver.install()
                self.driver = webdriver.Chrome(options=options)
        except PermissionError: 
            os.rmdir("chromedriver")
            get_driver = GetChromeDriver()
            get_driver.install()
            self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})

if __name__ == "__main__":
    
    national_websites = pd.read_excel("./national_websites.xlsx")
    local_websites = pd.read_excel("./national_websites.xlsx")
    df = pd.concat([national_websites, local_websites])

    processes = []
    for i in range(num_processes):
        print(f"Process {str(i)} starting")
        process = Process(target=Scraper, args=(df, i, len(df), num_processes))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join() 

    cross_referenced = pd.DataFrame()
    for i in range(num_processes):
        df = pd.read_excel(f".//main__{str(i)}.xlsx")
        cross_referenced = pd.concat([cross_referenced, df])
    cross_referenced.to_excel(".//geoblocking_tested_local.xlsx")
