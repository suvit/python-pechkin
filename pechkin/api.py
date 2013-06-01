# -*- coding: utf-8 -*-
import logging
from functools import partial

import requests

logger = logging.getLogger(__name__)


class PechkinFixApi(object):

    API_URL = 'http://pechkinfix.ru/check.php'

    def __init__(self, username, password):
        self._client = requests.Session()

    def check(self, email):
        return self._client.get(self.API_URL,
                                params={'email': email}).json()


class PechkinApi(object):

    # TODO ssl from pechkin bad
    API_URL = 'http://api.pechkin-mail.ru'

    def __init__(self, username, password):
        self._client = requests.Session()
        #self._client.auth = (username, password)
        self._client.params = {'format': 'json',
                               'username': username,
                               'password': password}

    def log_errors(self, response):
        json = response.json()['response']
        if 'msg' in json:
            message = json['msg']

            if message['type'] == 'message':
                log = logger.info
            elif message['type'] == 'notice':
                log = logger.warning
            elif message['type'] == 'error':
                log = logger.error
            else:
                log = logger.debug

            log(u'%(err_code)s: %(text)s' % message)

    def _api_request(self, **kwargs):
        response = self._client.get(self.API_URL, params=kwargs)
        self.log_errors(response)
        return response.json()['response']

    def _get_params(self, params):
        return dict(item for item in params.items()
                    if item[1] is not None and item[0] != 'self')

    def lists_get(self, list_id=None, raw=False):
        params = self._get_params(locals())
        params['method'] = 'lists.get'
        lists = self._api_request(**params)['data']

        if not raw:
            lists = [PechkinList(self, list['id'], list) for list in lists]

        return lists[0] if list_id else lists

    def lists_add(self, name, abuse_email=None, abuse_name=None,
                  company=None,
                  address=None, city=None, zip=None, country=None,
                  url=None, phone=None):
        params = self._get_params(locals())
        params['method'] = 'lists.add'
        return self._api_request(**params)['data']['list_id']

    def lists_update(self, list_id, abuse_email=None, abuse_name=None,
                     company=None,
                     address=None, city=None, zip=None, country=None,
                     url=None, phone=None):
        params = self._get_params(locals())
        params['method'] = 'lists.update'
        return self._api_request(**params)['msg'][0]['err_code'] == 0

    def lists_delete(self, list_id):
        params = self._get_params(locals())
        params['method'] = 'lists.delete'
        return self._api_request(**params)['data']['deleted_members']

    def lists_get_members(self, list_id, state=None, start=0, limit=None,
                          order='id desc', member_id=None, email=None):

        assert state in [None, 'active', 'unsubscribed', 'bounced']
        params = self._get_params(locals())
        params['method'] = 'lists.get_members'
        return self._api_request(**params)['data']

    def lists_upload(self, list_id, file, email, type,
                     merge_1=None, merge_2=None, merge_3=None,
                     merge_4=None, merge_5=None,
                     update=None, sheet_index=None, sheet_name=None):
        params = self._get_params(locals())
        params['method'] = 'lists.upload'
        return self._api_request(**params)['data']

    def lists_add_member(self, list_id, email,
                         merge_1=None, merge_2=None, merge_3=None,
                         merge_4=None, merge_5=None,
                         update=None):
        params = self._get_params(locals())
        params['method'] = 'lists.add_member'
        return self._api_request(**params)['data']['member_id']

    def lists_update_member(self, member_id,
                            merge_1=None, merge_2=None, merge_3=None,
                            merge_4=None, merge_5=None):
        params = self._get_params(locals())
        params['method'] = 'lists.update_member'
        return self._api_request(**params)['msg']['err_code'] == 0

    def lists_delete_member(self, member_id):
        params = self._get_params(locals())
        params['method'] = 'lists.delete_member'
        return self._api_request(**params)['msg']['err_code'] == 0

    def lists_unsubscribe_member(self, member_id, reason, email=None,
                                 list_id=None):
        params = self._get_params(locals())
        params['method'] = 'lists.unsubscribe_member'
        return self._api_request(**params)

    def lists_move_member(self, member_id, list_id):
        params = self._get_params(locals())
        params['method'] = 'lists.move_member'
        return self._api_request(**params)['data']

    def lists_copy_member(self, member_id, list_id):
        params = self._get_params(locals())
        params['method'] = 'lists.copy_member'
        return self._api_request(**params)['data']

    def lists_add_merge(self, list_id, type, choices=None,
                        title=None, req=None, var=None):
        assert type in ['text', 'date', 'choice']
        params = self._get_params(locals())
        params['method'] = 'lists.add_merge'
        return self._api_request(**params)['msg']['err_code'] == 0

    def lists_update_merge(self, list_id, merge_id, choices=None,
                           title=None, req=None, var=None):
        params = self._get_params(locals())
        params['method'] = 'lists.update_merge'
        return self._api_request(**params)['data']

    def lists_delete_merge(self, list_id, merge_id):
        params = self._get_params(locals())
        params['method'] = 'lists.delete_merge'
        return self._api_request(**params)['data']

    """ TODO another
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


class PechkinList(object):
    def __init__(self, api, id, data=None):
        self.id = id

        for method in ['get', 'update', 'delete',
                       'get_members', 'add_member',
                       'add_merge', 'update_merge', 'delete_merge']:
            api_method = getattr(api, 'lists_%s' % method)
            setattr(self, method, partial(api_method, list_id=self.id))

        if data is None:
            data = self.get(raw=True)
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError(name)


class PechkinMember(object):
    def __init__(self, api, id):
        self.id = id

        for method in 'add', 'update', 'delete', 'unsubscribe':
            api_method = getattr(api, 'lists_%s_member' % method)
            setattr(self, method, partial(api_method, member_id=self.id))



class PechkinCampaign(object):
    def __init__(self, api, id):
        self.id = id

        for method in 'get', 'create', 'update', 'delete':
            api_method = getattr(api, 'campaigns_%s' % method)
            setattr(self, method, api_method)


class PechkinReport(object):
    def __init__(self, api, id):
        self.id = id

        for method in ['send', 'delivered', 'opened', 'unsubscribed', 'bounced',
                       'clickstat', 'bouncestat', 'summary',
                       'clients', 'geo']:
            api_method = getattr(api, 'reports_%s' % method)
            setattr(self, method, api_method)
