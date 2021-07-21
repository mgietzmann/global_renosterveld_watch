from googleapiclient.discovery import build
import google.auth
import os
import re
from time import time, sleep

def main(event, context):
    file_name = event['name']
    print(file_name)
    # first we find the total we're expecting
    try:
        final_number = int(file_name.split('/')[-1].split('-')[-1])
    except:
        return
    pattern = re.compile(f'(\S+)0*{final_number-1}-0*{final_number}')
    match = re.match(pattern, file_name)
    if match is not None:
        sleep(5) # just let any last files settle
        input_pattern = f'gs://grw-preprocess/{match.groups()[0]}*'
        credentials, _ = google.auth.default()
        service = build('dataflow', 'v1b3', credentials=credentials)
        gcp_project = os.environ["GCLOUD_PROJECT"]

        request = service.projects().locations().flexTemplates().launch(
            projectId=gcp_project,
            location='us-central1',
            body={
                'launch_parameter': {
                    'jobName': f"grw-predict-{int(time())}",
                    'parameters': {
                        "input": input_pattern,
                        "output": f"gs://grw-predict/{int(time())}/",
                        "max_num_workers": "50",
                        "worker_machine_type": "n1-standard-2"
                    },
                    'containerSpecGcsPath': "gs://grw-predict/dataflow/templates/grw_predict.json"
                }
            }
        )
        response = request.execute()

        print(response)
