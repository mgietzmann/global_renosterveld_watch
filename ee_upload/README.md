# `upload`

## Components
This stage consists of a *service account*, a dockerized *application*, a pub sub *topic*, a *notification* publisher, and a *cloud run* service.

## Setup Instructions
1. First create a service account that is both an Editor of your project and has access to Earth Engine's API. Add the credentials file to this folder (locally as we don't want to upload to `git`).
2. Update the `earthengine` cli call in `main.py:act` to point to your credentials file. 
3. Build the docker image and upload it to gcp with:
```bash
chmod +x build.sh
./build.sh
```
4. Create a cloud run service that listens to a new pub sub topic called `grw-ee-upload`. Select our newly built `grw-ee-upload` docker image for the service.
5. Setup a cloud storage notification publisher by running:
```bash
chmod +x notification.sh
./notification.sh
```

## Testing
You can of course run the cli call made by `main.py:act` yourself locally. Regardless of whether you run it locally or trigger the cloud run service you've just built, you'll get a task id that you can query the status of with:
```bash
earthengine task info <TASKID>
```
Note that if you triggered the job with a service account you'll need to specify the `--service-account-file` option for the `earthengine` cli.
