import scrapy


class JobTypes(scrapy.Spider):
    name = "job_types"

    def start_requests(self):
        urls = [
            'https://www.careerguide.com/career-options',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for job_group in response.css('.col-md-4'):
            if len(job_group.css('a::text').getall()) < 2:
                continue
            category = job_group.css('a::text').getall()[0]
            if category == "Institutes in India":
                continue
            yield {
                'Category': category,
                'Jobs': job_group.css('a::text').getall()[1:],
            }
