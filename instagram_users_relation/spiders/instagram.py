import scrapy
import json
from instagram_users_relation.settings import USER_AGENT


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_path = '/accounts/login/ajax/'
    _api_base_url = 'https://i.instagram.com/'
    _api_followers_url = 'api/v1/friendships/{user_id}/followers/?count={count}'
    _base_url = start_urls[0]
    _ttt = '{username}/?__a=1'

    def __init__(self, login, password, first_user, second_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password

        self.first_user = first_user
        self.second_user = second_user

    def csrf_token_extract(self, response) -> dict:
        js = response.xpath("//script[contains(text(), 'window._sharedData =')]/text()").extract_first()
        return json.loads(js[js.index("{"):-1])

    def parse(self, response):
        try:
            #d = self.csrf_token_extract(response)
            csrf_token = self.csrf_token_extract(response)['config']['csrf_token']
            yield scrapy.FormRequest(
                response.urljoin(self._login_path),
                method='POST',
                formdata={
                    'username': self.login,
                    'enc_password': self.password
                },
                headers={
                    'X-CSRFToken': csrf_token
                },
                callback=self.parse
            )
        except AttributeError:
            r_data = response.json()
            if r_data.get("authenticated"):
                response = response.replace(url=self._base_url)
                yield response.follow(
                    response.urljoin(self._ttt.format(username=self.first_user)),
                    callback=self.users_parse
                )
            #response = response.replace(url=self._api_base_url)
            print(1)
            # yield response.follow(
            #     response.urljoin("users/{username}/usernameinfo/".format(username=self.first_user)),
            #     headers={'user-agent': USER_AGENT},
            #     callback=self.get_user_info_parse
            # )
            # yield response.follow(
            #     response.urljoin(self._api_followers_url),
            #     callback=self.get_user_info_parse
            # )

    def users_parse(self, response):
        print(response.url)
        user_data = json.loads(response.text)
        first_user_id = user_data['graphql']['user']['id']
        response = response.replace(url=self._api_base_url)

        yield response.follow(
            response.urljoin(self._api_followers_url.format(user_id=first_user_id, count=1)),
            headers={
                'Connection': 'keep-alive',
                'Host': 'i.instagram.com',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': 'https://www.instagram.com',
                'Alt-Used': 'i.instagram.com',
                'Referer': "https://www.instagram.com/",
            },
            #cookies=response.request.cookies,
            callback=self.get_user_info_parse
        )


    def get_user_info_parse(self, response):
        print(1)