# `ee_download`

## components
This stage is comprised of nothing more than a *bucket*, a *cloud function*, and a *service account* that has access to Earth Engine's API. 

## setup instructions

### step 1
First you'll need to create a bucket `grw-ee-download` where the artifacts from the download can be stored.

### step 2 
Next you'll need a service account that has access to Earth Engine's API. Specifically you'll need the credentials file (a json file). 

### step 3
In the `utils.py` file update the `initialize` function with your service account's info.

### step 4
Create a cloud function that is triggered by the `start-reno-v1` pub sub topic. Choose a `python3` execution environment and then copy the code in this repository as well as your credentials file into the cloud function. 

### step 5
Deploy!

## testing
Testing this code is really easy. Just as the code can be run in a cloud function, so you can run it locally. `main.py:main` is your entry point and you don't need to specify any arguments. The function will return a task id which you can use to query the status of your job by running:
```bash
earthengine task info <TASKID>
```
