from googleapiclient.discovery import build
import google.auth
import os
import re
from time import time

def main(event, context):
    file_name = event['name']
    pattern = re.compile('gs://grw-ee-download/(\S+)mixer.json')
    match = re.match(pattern, file_name)
    if match is not None:
        input_pattern = f'gs://grw-ee-download/{match.groups()[0]}*.tfrecord.gz'
        credentials, _ = google.auth.default()
        service = build('dataflow', 'v1b3', credentials=credentials)
        gcp_project = os.environ["GCLOUD_PROJECT"]

        request = service.projects().locations().flexTemplates().launch(
            projectId=gcp_project,
            location='us-central1',
            body={
                'launch_parameter': {
                    'jobName': f"grw-preprocess-{int(time())}",
                    'parameters': {
                        "input": input_pattern,
                        "output": f"gs://grw-preprocess/{int(time())}/",
                        "max_num_workers": "50",
                        "worker_machine_type": "n1-standard-2"
                    },
                    'containerSpecGcsPath': "gs://grw-preprocess/dataflow/templates/grw_preprocess.json"
                }
            }
        )
        response = request.execute()

        print(response)