from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd

from urllib.parse import urlparse
from datetime import datetime
import math
import time
import random


"""
configuration
"""
# scrawl target url
search_term = 'c1q like protein'
start_page = 1
# scrawl page numbers
total_pages_wanted = 1
# timeout for ajax request
ajax_timeout = 60


class element_has_gone(object):
  def __init__(self, css_class):
    self.css_class = css_class
  def __call__(self, driver):
    elements = driver.find_elements_by_css_selector(self.css_class)
    if len(elements) == 0:
        # return a 
        return driver.find_element_by_css_selector('.cited-num')
    else:
        return False

def go_to_start_page(driver, page):
    if page != 1:
        page_input = driver.find_element_by_id("pageno")
        page_input.clear()
        page_input.send_keys(page)
        # print(page_input.get_attribute('value'))
        page_input.send_keys(Keys.RETURN)

def gen_target_url(term):
    t = term.split(' ')
    return 'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + '+'.join(t)

def bootstrap_chrome_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # not supported
    chrome_options.add_argument('--load-extension=./pubmedy')
    return webdriver.Chrome(chrome_options=chrome_options)
        
def calc_pages(driver, start_page):
    total_items = int(driver.find_element_by_id('resultcount').get_property('value'))
    # print(total_items)
    if total_items < DEFAULT_PAGE_SIZE * start_page:
        raise ValueError("Starting page number is too large!")
    actual_total_pages = math.ceil((int(total_items) - (start_page - 1) * DEFAULT_PAGE_SIZE) / DEFAULT_PAGE_SIZE)
    if actual_total_pages < total_pages_wanted:
        return actual_total_pages
    return total_pages_wanted

def handle_scrawl(driver, page_num):
    print("current page: ", page_num+1)
    driver.get_screenshot_as_file(gen_screenshot_name(page_num+1))
    extention_ok = parse_static_content(driver)
    if extention_ok:
        WebDriverWait(driver, ajax_timeout).until(
            element_has_gone(".cited-num > img")
        )
    parse_cited_number(driver, page_num)

def parse_static_content(driver):
    soup = BeautifulSoup(driver.page_source, features='lxml')
    target_div_list = soup.find_all('div', {'class': 'rprt'})
    extention_ok = True
    # prepare cited element list ahead; the list might shrink after some click is executed 
    cited_element_list = driver.find_elements_by_css_selector('.cited-num > img')
    if len(cited_element_list) == 0:
        extention_ok = False
    for i in range(len(target_div_list)):
        anchor = target_div_list[i].find('p', {'class': 'title'}).find('a')
        # article title
        title = anchor.get_text()
        # article link
        href = complete_url(anchor['href'])

        """
        extra elements that the chrome extention pubmedy provides
        """
        if extention_ok:
            dl = target_div_list[i].select('.novopro-impactfactor-container > dl')[0]
            # article impact factor
            impact_factor = dl.select('*:nth-child(3)')[0].get_text()
            # article download link
            science_hub_link = get_science_hub_link(dl.select('*:nth-child(6)')[0].select('a'))
            result_list.append([title, href, to_float(impact_factor), science_hub_link])
            # print(title, '\n', href, '\n', impact_factor, '\n', science_hub_link)

            # click the img to trigger the ajax for cited number
            cited_element_list[i].click()
        else:
            result_list.append([title, href, "", "", ""])
    return extention_ok

def parse_cited_number(driver, page_num):
    soup = BeautifulSoup(driver.page_source, features='lxml')
    eles = soup.find_all('dd', {'class': 'cited-num'})
    for i in range(len(eles)):
        # print(eles[i].get_text(), '\n') 
        offset = page_num * DEFAULT_PAGE_SIZE
        # article cited number
        result_list[i + offset].append(to_float(eles[i].get_text()))

def parse_sub_pages():
    for i in range(len(result_list)):
        if (i + 1) % 10 == 0:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ": collected " + str(i + 1) + " abstracts and counting...")
        driver.get(result_list[i][1])
        sub_soup = BeautifulSoup(driver.page_source, features='lxml')

        abstract_div_content = "no abstract provided"
        sub_target_div = sub_soup.find('div', {'class': 'abstr'})
        if not (sub_target_div is None):
            abstract_div = sub_target_div.find('div')
            # article abstract
            abstract_div_content = abstract_div.get_text()

        journal_name = sub_soup.select('.cit > span > a')[0]['title']
        publish_info = sub_soup.select('.cit')[0].contents[1]
        result_list[i].append(journal_name)
        result_list[i].append(publish_info)
        result_list[i].append(abstract_div_content)
        # print(journal_name, publish_info)

        time.sleep(random.randint(1, 3))

def complete_url(url):
    if not 'http' in url:
        url = base_url + url
    return url

def get_base_url(url):
    o = urlparse(target_url)
    return o.scheme + '://' + o.netloc

def get_science_hub_link(link_list):
    science_hub_link = "no link provided"
    if len(link_list) > 0:
        science_hub_link = link_list[0]['href']
    return science_hub_link

def gen_screenshot_name(index):
    return "sreenshot_page" + str(index) + ".png"

# [title, href, impact_factor, science_hub_link, cited number, journal_name, publish_info, abstract_div_content]
# order: title, impact factor, publication date, journal name, abstract, download link, page link
def arrange():
    i = 'do nothing for now'

def to_float(s):
    try:
        return float(s)
    except ValueError:
        return s

target_url = gen_target_url(search_term)
# print(target_url)
DEFAULT_PAGE_SIZE = 20
base_url = get_base_url(target_url)
result_list = []

driver = bootstrap_chrome_driver()
driver.get(target_url)

pages_to_crawl = calc_pages(driver, start_page)
go_to_start_page(driver, start_page)

for i in range(pages_to_crawl):
    if i == 0:
        handle_scrawl(driver, i)
    else:
        # driver is updated after the following click()
        driver.find_element_by_link_text("Next >").click()
        handle_scrawl(driver, i)
    if i < pages_to_crawl - 1:
        time.sleep(random.randint(1, 3))

parse_sub_pages()
driver.close()

arrange()
result_list.insert(0, ["Title", "Page Link", "Impact Factor", "Sci-Hub Download Link", "Cited Number", "Journal", "Publication", "Abstract"])
df = pd.DataFrame()
df = df.append(result_list)

df.to_excel(search_term + datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + '.xlsx')
