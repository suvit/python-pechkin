
import requests

class PechkinApi(object):

    API_URL = 'api.pechkin-mail.ru'

    def __init__(self, username, password):
        self._client = requests.Session()
        self._client.auth = (username, password)
        self._client.params = {'format': 'json')

    def lists_get(self, list_id):
        kwargs['method'] = 'lists.get'
        response = self._client.get(params=kwargs)
        return response.json()['data']

    def lists_update(self, **kwargs):
        kwargs['method'] = 'lists.update'
        response = self._client.get(params=kwargs)
        return response.json()['data']

    def lists_delete(self, **kwargs):
        kwargs['method'] = 'lists.delete'
        response = self._client.get(params=kwargs)
        return response.json()['data']

    """ TODO another
lists.get_members
lists.upload
lists.add_member
lists.update_member
lists.delete_member
lists.unsubscribe_member
lists.move_member
lists.copy_member
lists.add_merge
lists.update_merge
lists.delete_merge

campaigns.get
campaigns.create
campaigns.update
campaigns.delete

reports.sent
reports.delivered
reports.opened
reports.unsubscribed
reports.bounced
reports.clickstat
reports.bouncestat
reports.summary
reports.clients
reports.geo
    """
