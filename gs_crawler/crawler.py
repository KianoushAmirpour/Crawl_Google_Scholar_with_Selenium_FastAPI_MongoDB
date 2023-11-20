import time
import utils
import httpx
from collections import namedtuple

import selenium.common as SC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebDriver:

    options = Options()
    options.add_argument("-headless")

    def __init__(self, url: str, logger) -> None:
        self.webdriver = webdriver.Firefox(options=self.options)
        self.url = url
        self.logger = logger

    def open_url(self) -> None:
        try:
            self.webdriver.get(self.url)
            self.webdriver.maximize_window()
        except Exception as e:
            self.logger.exception(F"An unexpected error occurred: {str(e)}")

    def click_on_show_more_button(self) -> None:
        show_more_button = self.webdriver.find_element(
            By.XPATH, '//*[@id="gsc_bpf_more"]/span/span[2]')
        for i in range(4):
            show_more_button.click()
            time.sleep(0.1)
            self.scroll_down()

    def sort_main_page_by_year(self) -> None:
        WebDriverWait(self.webdriver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="gsc_a_ha"]'))).click()

    def scroll_down(self) -> None:
        current_height = self.webdriver.execute_script(
            "return document.body.scrollHeight")
        while True:
            self.webdriver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.2)
            iter_height = self.webdriver.execute_script(
                "return document.body.scrollHeight")
            if current_height == iter_height:
                break
            current_height = iter_height


class ScrapeMainPage(WebDriver):
    def __init__(self, url: str, logger) -> None:
        super().__init__(url, logger)

    def extract_name(self) -> str:
        name = ""
        try:
            name = self.webdriver.find_element(By.ID, 'gsc_prf_in').text
        except SC.TimeoutException:
            name = WebDriverWait(self.webdriver, 10).until(
                EC.presence_of_element_located((By.ID, 'gsc_prf_in'))).text
        except SC.NoSuchElementException:
            self.logger.exception(
                f"Empty string sent. Unable to locate element (name) for {self.url}")
        except Exception as e:
            self.logger.exception(
                f'Empty string sent. Sth unexpected happened while locating the element (name) for {self.url}')
        return name.replace(" ", "_")

    def extract_university(self) -> str:
        university = ""
        try:
            university = self.webdriver.find_element(
                By.CLASS_NAME, "gsc_prf_ila").text
        except SC.NoSuchElementException:
            try:
                university = self.webdriver.find_element(
                    By.CLASS_NAME, 'gsc_prf_il').text
            except SC.NoSuchElementException:
                self.logger.exception(
                    f"Empty string sent. Unable to locate element (university) for {self.url}")
        except Exception as e:
            self.logger.exception(
                f'Empty string sent. Sth unexpected happened while locating element (university) for {self.url}')
        return university.replace(" ", "_")

    def extract_citations_data(self) -> tuple:
        citations = namedtuple(
            "citations", ["all_citations", "h_index", "i_10_index"])
        scholar_citation = citations("", "", "")
        try:
            all_citations = self.webdriver.find_element(
                By.XPATH, '//*[@id="gsc_rsb_st"]/tbody/tr[1]/td[2]').text
            h_index = self.webdriver.find_element(
                By.XPATH, '//*[@id="gsc_rsb_st"]/tbody/tr[2]/td[2]').text
            i_10_index = self.webdriver.find_element(
                By.XPATH, '//*[@id="gsc_rsb_st"]/tbody/tr[3]/td[2]').text
            scholar_citation = citations(all_citations, h_index, i_10_index)
        except SC.NoSuchElementException:
            self.logger.exception(
                f"Empty string sent. Unable to locate elements (citations) for {self.url}")
        except Exception as e:
            self.logger.exception(
                f'Empty string sent. Sth unexpected happened while locating elements (citations) for {self.url}')
        return scholar_citation

    def extract_papers_info(self) -> list:
        self.sort_main_page_by_year()
        time.sleep(1)
        self.click_on_show_more_button()
        time.sleep(1)
        paper_info = []
        papers = WebDriverWait(self.webdriver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'gsc_a_tr')))
        for paper in papers:
            paper_dict = {}
            article_info, citation, year = "", "", ""
            try:
                article_info = WebDriverWait(paper, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'gsc_a_t'))).text
            except SC.NoSuchElementException:
                self.logger.exception(
                    f"Empty string sent. Unable to locate elements (article_info) for {self.url}")
            try:
                citation = WebDriverWait(paper, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'gsc_a_c'))).text.replace("\n*", "").strip()
            except SC.NoSuchElementException:
                self.logger.exception(
                    f"Empty string sent. Unable to locate elements (citation) for {self.url}")
            try:
                year = WebDriverWait(paper, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'gsc_a_y'))).text.strip()
            except SC.NoSuchElementException:
                self.logger.exception(
                    f"Empty string sent. Unable to locate elements (year) for {self.url}")

            paper_dict["article_info"] = article_info.splitlines()

            paper_dict["citation"] = int(citation) if citation else 0

            paper_dict["year"] = int(year) if year else 0

            paper_info.append(paper_dict)
        return paper_info


def main():
    utils.check_for_dirs()
    logger = utils.logger(__name__)
    with open(utils.URLS_PATH / 'urls.txt') as urls_file:
        URLS = [url for url in urls_file]
    for url in URLS:
        scholars_profile = {}
        scholars_papers = {}
        logger.info(f'Crawling started for: {url}')
        try:
            scholar_page = ScrapeMainPage(url, logger)
            scholar_page.open_url()

            name = scholar_page.extract_name()
            university = scholar_page.extract_university()
            scholar_citation = scholar_page.extract_citations_data()
            scholar_papers = scholar_page.extract_papers_info()

            scholars_profile['name'] = name
            scholars_profile['university'] = university
            scholars_profile['all_citations'] = int(
                scholar_citation.all_citations)
            scholars_profile['h_index'] = int(scholar_citation.h_index)
            scholars_profile['i_10_index'] = int(scholar_citation.i_10_index)

            scholars_papers["name"] = name
            scholars_papers['papers'] = scholar_papers

            try:
                scholars_info_response = httpx.post(
                    'http://127.0.0.1:8000/profilescollection/add_profiles', json=scholars_profile)
                scholars_info_response.raise_for_status()
                logger.info(
                    f'Scholars profile was successfully stored in the database for: {name}.')
            except httpx.HTTPError as e:
                logger.error(
                    f'Failed to store scholars profile for {name}. Status code: {e.response.status_code}.')

            try:
                papers_list_response = httpx.post(
                    'http://127.0.0.1:8000/paperscollection/add_papers', json=scholars_papers)
                papers_list_response.raise_for_status()
                logger.info(
                    f'Scholars papers was successfully stored in the database for: {name}.')
            except httpx.HTTPError as e:
                logger.error(
                    f'Failed to store Scholars papers for {name}. Status code: {e.response.status_code}.')

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)} for {url}.")


if __name__ == "__main__":
    main()
