import json
import time
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import scrapy


class LinkedinScrape(scrapy.Spider):
    name = "linkedin_scrape"
    handle_httpstatus_list = [999]


    def __init__(self):
        self.driver = webdriver.Chrome()

    """
    Sample full url :

    https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?
    keywords=Real%2BEstate&
    location=India&
    geoId=&
    trk=public_jobs_jobs-search-bar_search-submit&
    start=25"""

    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
    url_feed = "https://www.linkedin.com/feed/"
    url_directory = "https://www.linkedin.com/directory/companies"
    LOCATIONS = [
        "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
        "Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir",
        "Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra",
        "Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
        "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura",
        "Uttar Pradesh","Uttarakhand","West Bengal"]
    SOURCE_FILE = "data/jobCategories.json"

    def buid_query_params(self, keyword, location, start):
        return {
            "keywords": keyword,
            "location": location,
            "geoId": "",
            "trk": "public_jobs_jobs-search-bar_search-submit",
            "start": start
        }

    def start_requests(self):
        with open(self.SOURCE_FILE, 'r') as f:
            data = json.load(f)
        for row in data:
            jobs = row["Jobs"]
            if len(jobs) < 1:
                continue
            for job in jobs:
                for location in self.LOCATIONS:
                    url = self.url + urlencode(self.buid_query_params(job, location, 0))
                    yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(q_location=location))

    def parse(self, response, q_location):
        for job in response.css('li'):
            position = job.css("a span::text").get().replace("\n","").strip()
            position_link = job.css("a::attr(href)").getall()[0]
            company = job.css(".base-search-card__subtitle a::text").get().replace("\n","").strip()
            company_link = job.css(".base-search-card__subtitle a::attr(href)").get()
            location = job.css(".job-search-card__location::text").get().replace("\n","").strip()

            if q_location not in location:
                continue

            print("Q Location : ", q_location)
            print("Location : ", location)

            self.driver.get(company_link)
            while("authwall" in self.driver.current_url):
                time.sleep(2)
                self.driver.get(self.url_feed)
                print("%"*80)
                print("Diff url encountered")
                print("Driver url : ", self.driver.current_url)
                print("Company url : ", company_link)
                self.driver.delete_all_cookies()
                time.sleep(2)
                self.driver.get(company_link)
                print("%"*80)
            self.driver.delete_all_cookies()
            selenium_response_text = self.driver.page_source
            new_selector = scrapy.Selector(text=selenium_response_text)
            description = new_selector.css(".break-words.whitespace-pre-wrap.text-color-text::text").get()
            employees_count = new_selector.css(".core-section-container__content.break-words dd::text").getall()[3].strip()
            headquarters = new_selector.css(".core-section-container__content.break-words dd::text").getall()[4].strip()
            print("Description : ", description)
            print("Employees count : ", employees_count)
            print("Location : ", headquarters)

            yield {
                'query_location': q_location,
                'position': position,
                'position_link': position_link,
                'company': company,
                'company_link': company_link,
                'location': location,
                'company_description': description,
                'employees_count': employees_count,
                'company_location': headquarters
            }