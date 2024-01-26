# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 14:37:12 2023

@author: brusseevwd1
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import numpy as np
from functools import partial
from multiprocessing import Pool, Process

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, WebDriverException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, InvalidArgumentException, StaleElementReferenceException, SessionNotCreatedException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.service import Service

import os

from get_gecko_driver import GetGeckoDriver
from get_chrome_driver import GetChromeDriver

class Check():
    def __init__(self, data_to_check, i, round_):
        results = []

        def check_availability(url):
            user_agt = "'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'"
            headers = {'User-Agent': user_agt}
            try:
                page = requests.get(url, headers = headers, timeout=30)
                if page.status_code == 404:
                    print(404)
                    print(url)
                    return page.status_code
                elif page.status_code == 200:
                    soup = BeautifulSoup(page.content, "html.parser", from_encoding="utf-8")
                    if (("访问" in soup.text or "页面" in soup.text) and 
                        ("不存在" in soup.text or "删除" in soup.text or "找不到" in soup.text)):
                        print(404)
                        print(url)
                        return 404
                    else:
                        return 200
                else:
                    return page.status_code
                
            except requests.exceptions.RequestException as e:
                return "webpage unavailable"
        
        def check_availability_selenium(url, driver):
            try:
                driver.get(url)
            except:
                return "webpage unavailable"
            time.sleep(5)
            html = driver.find_element(By.XPATH, "/html").text
            if (("访问" in html or "页面" in html) and 
                ("不存在" in html or "删除" in html or "找不到" in html)):
                return 404
            else:
                return None
            
        
        if round_ == 1:
            
            for url in data_to_check["Link"]:
                results.append(check_availability(url))
            data_to_check["result"] = results
            data_to_check.to_excel(f".//data_{str(i)}.xlsx")
        
        if round_ == 2:
            
            def start_webdriver():
                
                """
                TODO: changing user agents
                """

                    
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
                #options.add_argument("--headless")
                options.page_load_strategy = 'eager'
                try:
                    driver = webdriver.Chrome(options=options)
                    
                except (WebDriverException, SessionNotCreatedException):
                    
                    get_driver = GetChromeDriver()
                    get_driver.install()
                    driver = webdriver.Chrome(options=options)
                    
                except PermissionError: 
                    os.rmdir("chromedriver")
                    get_driver = GetChromeDriver()
                    get_driver.install()
                    driver = webdriver.Chrome(options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
                
                return driver
            
            driver = start_webdriver()
            print("webdriver started")
            
            for j in range(len(data_to_check)):
            
                if str(data_to_check["result"][j]) in ["403", "408", "412", "420", "502", "521"]:
                    result = check_availability_selenium(data_to_check["Link"][j], driver)
                    if result:
                        results.append(result)
                    else:
                        results.append(200)
                else:
                    results.append(data_to_check["result"][j])

            data_to_check["result"] = results
            data_to_check.to_excel(f".//data_{str(i)}.xlsx")

if __name__ == "__main__":
    
    """
    This code uses two rounds: one using BS4/requests and one using selenium for the websites that blocked the requests in the first round. 
    """
    
    #ROUND 1 CODE
    
    data = pd.read_excel("data.xlsx")
    
    checked = pd.DataFrame()
    for database in data["Database"].unique():
        results = [] 
        try:
            df = data.loc[data["Database"] == database].sample(50).reset_index(drop=True)
        except ValueError:
            df = data.loc[data["Database"] == database].reset_index(drop=True)
        df = df[["Database", "Link"]]
        checked = checked.append(df)
    
    num_processes = 5
    dataframes = np.array_split(checked, num_processes)
    checked_data = pd.DataFrame()
    func = partial(Check)
    processes = []
    
    for i in range(num_processes):
        print(f"process {str(i)} starting")
        process_data = dataframes[i].reset_index(drop=True)
        process = Process(target=func, args=(process_data, i, 1))
        processes.append(process)
        process.start()    
    for process in processes:
        process.join() 
    
    cross_referenced = pd.DataFrame()
    for i in range(num_processes):
        df = pd.read_excel(f".//data_{str(i)}.xlsx")
        cross_referenced = pd.concat([cross_referenced, df])
    cross_referenced.to_excel(".//checked_round_1.xlsx")
    
    #ROUND 2 CODE
    checked = pd.read_excel("checked_round_1.xlsx")
       
    num_processes = 5
    dataframes = np.array_split(checked, num_processes)
    checked_data = pd.DataFrame()
    func = partial(Check)
    processes = []
    
    for i in range(num_processes):
        print(f"process {str(i)} starting")
        process_data = dataframes[i].reset_index(drop=True)
        process = Process(target=func, args=(process_data, i, 2))
        processes.append(process)
        process.start()    
    for process in processes:
        process.join() 
    
    cross_referenced = pd.DataFrame()
    for i in range(num_processes):
        df = pd.read_excel(f".//data_{str(i)}.xlsx")
        cross_referenced = pd.concat([cross_referenced, df])
    cross_referenced.to_excel(".//checked_round_2.xlsx")
    
    
    
    
    
    