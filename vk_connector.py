import logging
import configparser
import requests
import time
import errors


logger = logging.getLogger(__name__)


class VKConnector:

    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read('.config')
            self.api_endpoint = config['VK_API']['API_ENDPOINT']
            self.session = requests.Session()
            self.session.params = {
                'access_token': config['VK_API']['API_TOKEN'],
                'v': config['VK_API']['API_VERSION']
            }

        except Exception as e:
            logger.exception('Something bad happened.')
            raise

    def get_vk_api_response(self, method, params, retry_attempts):
        try:
            if not retry_attempts:
                raise errors.TooManyRetries

            response = self.session.get(f'{self.api_endpoint}{method}', params=params, timeout=5)

            response.raise_for_status()
            logger.debug(f'Response payload: {response.json()}')

            if response.json().get('error'):
                raise errors.RequestError(code=response.json()['error']['error_code'],
                                          message=response.json()['error']['error_msg'])

        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(f'Connection error or timeout. Retries left {retry_attempts-1}. Retrying...')
            time.sleep(5)
            return self.get_vk_api_response(method, params, retry_attempts=retry_attempts-1)

        except requests.HTTPError as e:
            logger.exception(e)
            raise

        except errors.RequestError as e:
            if e.code == 5:
                logger.error(f'User authorization failed: no access_token passed. Check config file for API_TOKEN')
                raise
            elif e.code == 6:
                logger.warning(f'Too many requests per second. Retries left {retry_attempts-1}. Retrying...')
                time.sleep(0.2)
                return self.get_vk_api_response(method, params, retry_attempts=retry_attempts-1)
            elif e.code == 18:
                logger.warning(f'User was deleted or banned. Skipping...')
                raise errors.UserWasDeletedOrBanned(code=response.json()['error']['error_code'],
                                                    message=response.json()['error']['error_msg'])
            elif e.code == 30:
                logger.warning(f'This profile is private. Skipping...')
                raise errors.UserWasDeletedOrBanned(code=response.json()['error']['error_code'],
                                                    message=response.json()['error']['error_msg'])
            else:
                logger.exception(f'Unknown error in VK API response.')
                raise
        else:
            return response.json().get('response')
