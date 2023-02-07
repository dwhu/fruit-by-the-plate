import requests

SCOPES = 'user_profile,user_media,instagram_content_publish'
INSTAGRAM_APP_ID = '720851756220898'


class Instagram:

    def __init__(self, logger):
        self.logger = logger

    # Get the Instagram Account ID by getting the FB ID then using that to retrieve the IG id
    # https://developers.facebook.com/docs/instagram-api/getting-started#4--get-the-user-s-pages
    # https://developers.facebook.com/docs/instagram-api/getting-started#5--get-the-page-s-instagram-business-account
    def get_instgram_account_id(self, access_token):
        # Get FB Id from the acces token
        url = f'https://graph.facebook.com/v16.0/me/accounts?access_token={access_token}'
        resp = requests.get(url)
        body = resp.json()
        if 'data' not in body:
            self.logger.info(body)
            raise Exception("Invalid response when getting FB account info: " + str(body))
        fb_account_data = body["data"][0]
        fb_id = fb_account_data["id"]

        # Get the instagram account id
        url = f'https://graph.facebook.com/v16.0/{fb_id}?fields=instagram_business_account&access_token={access_token}'
        resp = requests.get(url)
        body = resp.json()
        if "instagram_business_account" not in body:
            self.logger.info(body)
            raise Exception("Invalid response when getting Instagram account info: " + str(body))
        return body["instagram_business_account"]["id"]

    # Create an IG Post
    # https://developers.facebook.com/docs/instagram-api/guides/content-publishing#single-media-posts
    def post_image(self, ig_id, access_token, img_url, caption):
        # 1. Create the container
        url = f'https://graph.facebook.com/v16.0/{ig_id}/media?' + \
              f'image_url={img_url}&caption={caption}&access_token={access_token}'
        resp = requests.post(url)
        body = resp.json()
        if 'id' not in body:
            self.logger.info(body)
            raise Exception("Error creating Instagram container: " + str(body))
        container_id = body["id"]

        # 2. Publish the container
        url = f'https://graph.facebook.com/v16.0/{ig_id}/media_publish?' + \
              f'creation_id={container_id}&access_token={access_token} '
        requests.post(url)
