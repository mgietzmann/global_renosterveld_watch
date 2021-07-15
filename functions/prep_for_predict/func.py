from googleapiclient.discovery import build
import google.auth
import os
from time import time

def hello_pubsub(event, context):   

    credentials, _ = google.auth.default()
    service = build('dataflow', 'v1b3', credentials=credentials)
    gcp_project = os.environ["GCLOUD_PROJECT"]

    request = service.projects().locations().flexTemplates().launch(
        projectId=gcp_project,
        location='us-central1',
        body={
            'launch_parameter': {
                'jobName': f"prep-for-predict-{int(time())}",
                'parameters': {
                    "input": "gs://reno-ee-example/NEW_Image_reno_predict__2021-07-0800008.tfrecord.gz",
                    "output": "gs://reno-ee-example/RealBeamOutput2"
                },
                'containerSpecGcsPath': "gs://reno-ee-example/samples/dataflow/templates/streaming-beam.json"
            }
        }
    )
    response = request.execute()

    print(response)