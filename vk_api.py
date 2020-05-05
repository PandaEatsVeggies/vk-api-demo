import logging
import configparser
import errors
from vk_connector import VKConnector


logger = logging.getLogger(__name__)


class VKAPI:

    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read('.config')
            self.api_retry_attempts = int(config['VK_API']['API_RETRY_ATTEMPTS'])
            self.user_id = ''
            self.vk_connector_instance = VKConnector()
        except Exception as e:
            logger.exception('Something bad happened.')
            raise

    def get_user_id(self, user_ids):
        if self.user_id:
            return self.user_id
        else:
            response = self.vk_connector_instance.get_vk_api_response(method='users.get',
                                                                      params={'user_ids': user_ids},
                                                                      retry_attempts=self.api_retry_attempts)
            logger.debug(f'{__class__}.get_user_id response={response}')
            self.user_id = response[0]['id']
            return self.user_id

    def get_user_friends(self, user_id):
        try:
            response = self.vk_connector_instance.get_vk_api_response(method='friends.get',
                                                                      params={'user_id': user_id},
                                                                      retry_attempts=self.api_retry_attempts)
        except (errors.UserWasDeletedOrBanned, errors.ThisProfileIsPrivate):
            return list()
        else:
            logger.debug(f'{__class__}.get_user_friends response={response}')
            return response['items']

    def get_user_groups(self, user_id):
        try:
            response = self.vk_connector_instance.get_vk_api_response(method='groups.get',
                                                                      params={'user_id': user_id},
                                                                      retry_attempts=self.api_retry_attempts)
        except (errors.UserWasDeletedOrBanned, errors.ThisProfileIsPrivate):
            return list()
        else:
            logger.debug(f'{__class__}.get_user_groups response={response}')
            return response['items']

    def get_group_info(self, group_ids):
        try:
            response = self.vk_connector_instance.get_vk_api_response(method='groups.getById',
                                                                      params={'group_ids': group_ids,
                                                                              'fields': 'members_count'},
                                                                      retry_attempts=self.api_retry_attempts)
        except Exception:
            logger.exception('Something bad happened.')
            raise
        else:
            logger.debug(f'{__class__}.get_group_info response={response}')
            return response
