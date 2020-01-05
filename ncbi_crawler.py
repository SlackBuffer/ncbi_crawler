from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd

from urllib.parse import urlparse
import math
import time
import random


"""
configuration
"""
# scrawl target url
search_term = 'ctrp'
target_url = 'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + search_term
# scrawl page numbers
total_pages_wanted = 10
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

def bootstrap_chrome_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # not supported
    chrome_options.add_argument('--load-extension=./pubmedy')
    return webdriver.Chrome(chrome_options=chrome_options)
        
def calc_pages(driver):
    total_items = int(driver.find_element_by_id('resultcount').get_property('value'))
    # print(total_items)
    actual_total_pages = math.ceil(int(total_items) / DEFAULT_PAGE_SIZE)
    if actual_total_pages < total_pages_wanted:
        return actual_total_pages
    return total_pages_wanted

def handle_scrawl(driver, page_num):
    parse_static_content(driver)
    WebDriverWait(driver, ajax_timeout).until(
        element_has_gone(".cited-num > img")
    )
    parse_cited_number(driver, page_num)
    driver.get_screenshot_as_file(gen_screenshot_name(page_num+1))

def parse_static_content(driver):
    soup = BeautifulSoup(driver.page_source, features='lxml')
    target_div_list = soup.find_all('div', {'class': 'rprt'})
    # prepare cited element list ahead; the list might shrink after some click is executed 
    cited_element_list = driver.find_elements_by_css_selector('.cited-num > img')
    for i in range(len(target_div_list)):
        anchor = target_div_list[i].find('p', {'class': 'title'}).find('a')
        # article title
        title = anchor.get_text()
        # article link
        href = complete_url(anchor['href'])

        """
        extra elements that the chrome extention pubmedy provides
        """
        dl = target_div_list[i].select('.novopro-impactfactor-container > dl')[0]
        # article impact factor
        impact_factor = dl.select('*:nth-child(3)')[0].get_text()
        # article download link
        science_hub_link = get_science_hub_link(dl.select('*:nth-child(6)')[0].select('a'))
        result_list.append([title, href, impact_factor, science_hub_link])
        # print(title, '\n', href, '\n', impact_factor, '\n', science_hub_link)

        # click the img to trigger the ajax for cited number
        cited_element_list[i].click()

def parse_cited_number(driver, page_num):
    soup = BeautifulSoup(driver.page_source, features='lxml')
    eles = soup.find_all('dd', {'class': 'cited-num'})
    for i in range(len(eles)):
        # print(eles[i].get_text(), '\n') 
        offset = page_num * DEFAULT_PAGE_SIZE
        # article cited number
        result_list[i + offset].append(eles[i].get_text())

def parse_sub_pages():
    for r in result_list:
        driver.get(r[1])
        sub_soup = BeautifulSoup(driver.page_source, features='lxml')

        abstract_div_content = "no abstract provided"
        sub_target_div = sub_soup.find('div', {'class': 'abstr'})
        if not (sub_target_div is None):
            abstract_div = sub_target_div.find('div')
            # article abstract
            abstract_div_content = abstract_div.get_text()

        journal_name = sub_soup.select('.cit > span > a')[0]['title']
        publish_info = sub_soup.select('.cit')[0].contents[1]
        r.append(journal_name)
        r.append(publish_info)
        r.append(abstract_div_content)
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


DEFAULT_PAGE_SIZE = 20
base_url = get_base_url(target_url)
result_list = []

driver = bootstrap_chrome_driver()
driver.get(target_url)

pages_to_crawl = calc_pages(driver)
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
result_list.insert(0, ["title", "page link", "impact factor", "science hub download link", "cited number", "journal", "publication", "abstract"])
df = pd.DataFrame()
df = df.append(result_list)

df.to_excel(search_term + '.xlsx')
