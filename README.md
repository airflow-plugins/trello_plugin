# Plugin - Trello to S3

This plugin moves data from the [Trello](https://developers.trello.com/v1.0) API to S3. Implemented for boards, cards, actions, lists, checklists and members.

## Hooks
### TrelloHook
This hook handles the authentication and request to Trello. Inherits from HttpHook.

### S3Hook
[Core Airflow S3Hook](https://pythonhosted.org/airflow/_modules/S3_hook.html) with the standard boto dependency.

## Operators
### TrelloToS3
This operator composes the logic for this plugin. It fetches a specific endpoint and saves the result in a S3 Bucket, under a specified key, in
njson format. The parameters it can accept include the following.

- `trello_conn_id`: The Airflow id used to store the Trello credentials.
- `endpoint`: The endpoint to retrive data from.
- `s3_conn_id`: S3 connection id from Airflow.  
- `s3_bucket`: The output s3 bucket.  
- `s3_key`: The input s3 key.  
- `fields`: *optional* name of the results array from response, acording to pypardot4 documentation
- `since`:  *optional* The starting date parameter
- `before`: *optional* The ending date parameter.
- `fields`: *optional* list of fields that you want to get from the object. If *None*, then this will get all fields for the object

