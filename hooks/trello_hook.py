from airflow.hooks.http_hook import HttpHook
import json
import logging


class TrelloHook(HttpHook):
    def __init__(
            self,
            method='GET',
            http_conn_id='http_default',
            *args,
            **kwargs):
        self._args = args
        self._kwargs = kwargs

        self.connection = self.get_connection(http_conn_id)
        self.extras = self.connection.extra_dejson

        self.api_key = self.extras['api_key']
        self.token = self.extras['token']
        self.authorization_params = "key={0}&token={1}".format(
            self.api_key, self.token)
        self.endpoint = None

        super().__init__(method, http_conn_id)

    def run(self, endpoint, data=None, headers=None, extra_options=None, extra_args={}):
        print (endpoint, extra_args)
        if '?' not in endpoint:
            endpoint += '/?'
        else:
            endpoint += '&'

        endpoint += self.authorization_params

        if 'fields' in extra_args and extra_args['fields']:
            fields = extra_args['fields']

            if isinstance(fields, list):
                fields = ",".join(fields)
            endpoint += '&fields={}'.format(fields)

        if 'since' in extra_args and extra_args['since']:
            endpoint += '&since={}'.format(str(extra_args['since']))
        if 'before' in extra_args and extra_args['before']:
            endpoint += '&before={}'.format(str(extra_args['before']))

        self.endpoint = endpoint
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return super().run(endpoint, data, headers, extra_options)

    def get_records(self, sql):
        pass

    def get_pandas_df(self, sql):
        pass
