from airflow.plugins_manager import AirflowPlugin

from trello_plugin.operators.trello_to_s3_operator import TrelloToS3Operator
from trello_plugin.hooks.trello_hook import TrelloHook


class trello_plugin(AirflowPlugin):
    name = "trello_plugin"
    operators = [TrelloToS3Operator]
    hooks = [TrelloHook]
    # Leave in for explicitness
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
