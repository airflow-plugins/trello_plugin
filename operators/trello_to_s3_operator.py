from airflow.hooks.S3_hook import S3Hook
from airflow.models import BaseOperator

from trello_plugin.hooks.trello_hook import TrelloHook

from tempfile import NamedTemporaryFile
import json


class EndpointNotSupported(Exception):

    def __init__(self) -> None:
        super().__init__("Specified endpoint not currently supported.")


class TrelloToS3Operator(BaseOperator):
    """
    Trello to S3 Operator
    :param trello_conn_id:          The Airflow id used to store the Trello
                                    credentials.
    :type trello_conn_id:           string
    :param endpoint:                The endpoint to retrive data from.
                                    Implemented for: 
                                        - boards
                                        - cards
                                        - actions 
                                        - lists
                                        - checklists
                                        - members
    :type endpoint:                 string
    :param s3_conn_id:              The Airflow connection id used to store
                                    the S3 credentials.
    :type s3_conn_id:               string
    :param s3_bucket:               The S3 bucket to be used to store
                                    the Marketo data.
    :type s3_bucket:                string
    :param s3_key:                  The S3 key to be used to store
                                    the Marketo data.
    :type s3_bucket:                string
    :param fields:                  List of fields to retrive for each object
                                    from that endpoint
    :type fields:                   list
    :param since:                   The starting date parameter.
    :type since: 
    :param: before:                 The ending date parameter.
    :type before:                   
    """

    def __init__(self,
                 trello_conn_id,
                 endpoint,
                 s3_conn_id,
                 s3_bucket,
                 s3_key,
                 fields=None,
                 since=None,
                 before=None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.trello_conn_id = trello_conn_id
        self.endpoint = endpoint

        self.since = since
        self.before = before
        self.fields = fields

        self.s3_conn_id = s3_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key

        self.hook = TrelloHook(http_conn_id=self.trello_conn_id)

        if self.endpoint not in (
            'boards',
            'actions',
            'cards',
            'checklists',
            'lists',
                'members'):
            raise EndpointNotSupported()


    def get_me(self, nested_object, extra_args):
        """
        Get specific nested object from 'members/me' endpoint.
        """
        return self.hook.run('members/me/{nested_object}', extra_args=extra_args).json()

    def get_all(self, endpoints, extra_args={}):
        """
        Fetch results from multiple endpoints and
        return an array with all the results.
        """
        results = []

        for endpoint in endpoints:
            result = self.hook.run(
                endpoint, fields=self.fields, extra_args=extra_args).json()
            results += result

        return results

    def execute(self, context):
        boards_endpoint = 'members/me/boards'
        extra_args = {
            'fields': self.fields,
            'since': self.since,
            'before': self.before
        }

        if self.endpoint is 'members':
            organizations = self.get_me('organizations', extra_args=extra_args)
            results = []

            if organizations:
                for org in organizations:
                    org_members = self.hook.run(
                        'organizations/{}/members'.format(org['id']), extra_args=extra_args).json()
                    results += org_members
        elif self.endpoint is 'boards':
            results = self.hook.run(
                boards_endpoint, extra_args=extra_args).json()
        else:
            boards = self.hook.run(
                boards_endpoint,
                extra_args={
                    'fields': 'id',
                    'since': self.since,
                    'before': self.before
                }).json()
            endpoints = [
                "boards/{}/{}".format(board['id'],
                                      self.endpoint,
                                      extra_args=extra_args) for board in boards]
            results = self.get_all(endpoints, extra_args=extra_args)

        with NamedTemporaryFile("w") as tmp:
            for result in results:
                tmp.write(json.dumps(result) + '\n')

            tmp.flush()

            dest_s3 = S3Hook(s3_conn_id=self.s3_conn_id)
            dest_s3.load_file(
                filename=tmp.name,
                key=self.s3_key,
                bucket_name=self.s3_bucket,
                replace=True

            )
            dest_s3.connection.close()
            tmp.close()
