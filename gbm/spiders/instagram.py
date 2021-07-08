import json
import scrapy
from scrapy.http.response import Response
from gbm.items import InstaPostsItem, InstaAuthorItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/datascience/'

    __api_tag_url = '/graphql/query/'
    __query_hash = '2418469a2b4d9b47ae7bec08e3ec53ad'

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)
        

    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)

            yield scrapy.FormRequest(self.__login_url,
                                     method='POST',
                                     callback=self.parse,
                                     formdata={
                                         'username': self.__login,
                                         'enc_password': self.__password
                                     },
                                     headers={'X-CSRFToken': js_data['config']['csrf_token']}
                                     )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__tag_url, callback=self.tag_page_parse)


    def tag_page_parse(self, response:Response):
        js_data = self.get_js_shared_data(response)
        hashtag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        variables = {"tag_name": hashtag['name'],
                     "first": 50,
                     "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

        """https://www.instagram.com/graphql/query/?query_hash=c769cb6c71b24c8a86590b22402fda50&variables={"tag_name":"datascience","first":7,"after":"QVFCYVRCb0RSVUNFeEE4MUhJWHUwZGNuNUJQQzdrQy1xQkhnd2JoSUY3STZRZC1kaWhMTW9BN0llZXV5eU1wZ3pPUkE0UHY3UEVyWmNmcWtPV3E5d2ZYTg=="}"""

        url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_hastag_posts)

    def get_api_hastag_posts(self, response: Response):
        js_data = self.get_js_shared_data(response)
        hashtag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        variables = {"tag_name": hashtag['name'],
                     "first": 50,
                     "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

        """https://www.instagram.com/graphql/query/?query_hash=c769cb6c71b24c8a86590b22402fda50&variables={"tag_name":"datascience","first":7,"after":"QVFCYVRCb0RSVUNFeEE4MUhJWHUwZGNuNUJQQzdrQy1xQkhnd2JoSUY3STZRZC1kaWhMTW9BN0llZXV5eU1wZ3pPUkE0UHY3UEVyWmNmcWtPV3E5d2ZYTg=="}"""

        url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_hastag_posts)

        post = hashtag['edge_hashtag_to_media']['edges']
        for pst in post:
            if pst['node']['edge_hashtag_to_media']['count'] > 30 or pst['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{pst["node"]["shortcode"]}/', callback=post_parse)
            yield InstaPostsItem(data=post['node'])
    
    def post_parse(self, response):
        user_data = self.get_js_shared_data(response)
        user_data = user_data['entry_data']["PostPage"][0][graphq1]['shortcode_media']['owner']
        yield InstaAuthorItem(data=user_data)

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()'
        ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data) 
