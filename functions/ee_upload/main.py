# Copyright 2019 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloudrun_pubsub_server_setup]
# [START run_pubsub_server_setup]
import base64
import os
import json
from google.cloud import storage
import re
import subprocess
from time import sleep

from flask import Flask, request


app = Flask(__name__)
# [END run_pubsub_server_setup]
# [END cloudrun_pubsub_server_setup]


def act(data):
    if data["kind"] == "storage#object":
        file_name = data["name"]
        print(file_name)
        # first we find the total we're expecting
        try:
            final_number = int(file_name.split('-')[-1])
        except:
            return
        pattern = re.compile(f'(\S+)0*{final_number-1}-of-0*{final_number}')
        match = re.match(pattern, file_name)
        if match is not None:
            sleep(5)
            # grab the needed path info for the tfrecords and the mixer
            recombine_prefix = '/'.join(match.groups()[0].split('/')[:-1]) + '/'
            print(recombine_prefix)
            client = storage.Client()
            bucket = client.bucket('grw-recombine')
            for blob in bucket.list_blobs(prefix=recombine_prefix):
                if blob.name.endswith('tfrecord.gz'):
                    download_path = blob.name[len(recombine_prefix):]
                    download_dir = '/'.join(download_path.split('/')[:-1]) + '/'
                    break
            tfrecords_pattern = 'gs://grw-recombine/' + recombine_prefix + download_dir + '*.tfrecord'
            mixer_path = 'gs://grw-ee-download/' + download_dir + 'mixer.json'
            date = download_dir.split('/')[-2]
            asset_id = 'projects/ee-vegetation-gee4geo/assets/Image_reno_predict_' + date
            cmd = f'earthengine --service_account_file ee-vegetation-gee4geo-6309a79ef209.json upload image --asset_id={asset_id} {tfrecords_pattern} {mixer_path}'
            print(cmd)
            output = subprocess.run(cmd, capture_output=True, shell=True)
            print(output.stdout.decode('utf-8'))
            print(output.stderr.decode('utf-8'))

# [START cloudrun_pubsub_handler]
# [START run_pubsub_handler]
@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        data = json.loads(base64.b64decode(pubsub_message["data"]).decode("utf-8").strip())
        print(data)    
        act(data)

    return ("", 204)


# [END run_pubsub_handler]
# [END cloudrun_pubsub_handler]


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)