import logging
import vk_api
import os
import json
from progress.bar import IncrementalBar


logging.basicConfig(level=logging.ERROR, format='%(asctime)s : %(name)s : [%(levelname)s] : %(message)s')
logger = logging.getLogger(__name__)


def main():
    vk_api_instance = vk_api.VKAPI()

    user_id = vk_api_instance.get_user_id('1682220')
    logger.info(f'UserID={user_id}')

    user_groups = set(vk_api_instance.get_user_groups(user_id))
    logger.info(f'User groups={user_groups}')

    user_friends = vk_api_instance.get_user_friends(user_id)
    logger.info(f'User friends={user_friends}')

    user_friends_groups = set()
    progress_bar = IncrementalBar('No worries. Doing long-term shit...', max=len(user_friends))
    for user_friend in user_friends:
        user_friends_groups.update(vk_api_instance.get_user_groups(user_friend))
        progress_bar.next()
    progress_bar.finish()
    logger.info(f'User friends groups={user_friends_groups}')

    user_groups_without_friends = user_groups - user_friends_groups
    logger.info(f'User groups without friends={user_groups_without_friends}')

    output_json_raw = vk_api_instance.get_group_info(','.join(str(s) for s in user_groups_without_friends))
    output_json_brushed = [{'name': group['name'],
                            'gid': group['id'],
                            'members_count': group['members_count']} for group in output_json_raw]

    with open(f'{os.path.dirname(__file__)}/results.txt', mode='w', encoding='utf-8') as file:
        json.dump(output_json_brushed, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
