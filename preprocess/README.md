# `preprocess`

## Components
This stage consists of nothing more than a *cloud function*, a *bucket*, and a *dataflow template*.

## Setup Instructions
1. First you'll need to create the bucket `grw-preprocess` where artifacts will be stored.
2. Next build the dataflow template by running:
```bash
chmod +x build.sh
./build.sh
```
3. Create a cloud function that uses a "finalize" storage trigger for the `grw-ee-download` bucket and choose a `python3` execution environment. 
4. Copy the code from the `cloud_func` folder into the cloud function.
5. Deploy!

## Testing
There are three ways you can test the pipeline code. 
1. Run it with the local apache beam runner:
```bash
export GRW_PREPROCESS_INPUT=<input location>
export GRW_PREPROCESS_OUTPUT=<output location>
chmod +x run_local.sh
./run_local.sh
```
2. Run it on dataflow without the template:
```bash
export GRW_PREPROCESS_PROJECT="ee-vegetation-gee4geo"
export GRW_PREPROCESS_TEMP_LOCATION="gs://reno-ee-example/tmp/"
export GRW_PREPROCESS_STAGING_LOCATION="gs://reno-ee-example/staging/"
export GRW_PREPROCESS_INPUT=<input location>
export GRW_PREPROCESS_OUTPUT=<output location>
chmod +x run_dataflow.sh
./run_dataflow.sh
```
3. Run the template:
```bash
export GRW_PREPROCESS_INPUT=<input location>
export GRW_PREPROCESS_OUTPUT=<output location>
chmod +x build.sh
./build.sh
chmod +x run_template.sh
./run_template.sh
```

## Notes on the Code
1. You'll notice that the beam pipeline code is packaged as a python package rather than just being a simple script. This is because using custom built functions directly in the python callable can result in strange import loops and errors. Within the `run` function of the pipeline we specify a `setup_file` argument to ensure our package gets picked up and used by the beam pipeline. 
2. The preprocess stage of our pipeline has to make the keys that will allow us to reconstitute ordering during the recombine stage of our pipeline. To create these keys we had to subclass the traditional tensor flow reader to return information on the file name and offset which are then used to create those keys.
