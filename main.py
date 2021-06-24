import yaml
import dotenv
import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram_users_relation.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    with open('credentials.yaml') as stream:
        credentials = yaml.load(stream, Loader=yaml.FullLoader)
        login = credentials['user']
        password = credentials['password']

    #dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("instagram_users_relation.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstagramSpider,
        login=login,
        password=password,
        first_user="pavlova68_life",
        second_user=""
    )
    # crawler_process.crawl(
    #     InstagramSpider,
    #     login=os.getenv("LOGIN"),
    #     password=os.getenv("PASSWORD"),
    #     first_user="pavlova68_life",
    #     second_user=""
    # )
    crawler_process.start()