# `recombine`

## Components
This stage consists of nothing more than a *cloud function*, a *bucket*, and a *dataflow template*.

## Setup Instructions
1. First you'll need to create the bucket `grw-recombine` where artifacts will be stored.
2. Next build the dataflow template by running:
```bash
chmod +x build.sh
./build.sh
```
3. Create a cloud function that uses a "finalize" storage trigger for the `grw-predict` bucket and choose a `python3` execution environment. 
4. Copy the code from the `cloud_func` folder into the cloud function.
5. Deploy!

## Testing
There are three ways you can test the pipeline code. 
1. Run it with the local apache beam runner:
```bash
export GRW_RECOMBINE_INPUT=<input location>
export GRW_RECOMBINE_OUTPUT=<output location>
chmod +x run_local.sh
./run_local.sh
```
2. Run it on dataflow without the template:
```bash
export GRW_RECOMBINE_PROJECT="ee-vegetation-gee4geo"
export GRW_RECOMBINE_TEMP_LOCATION="gs://reno-ee-example/tmp/"
export GRW_RECOMBINE_STAGING_LOCATION="gs://reno-ee-example/staging/"
export GRW_RECOMBINE_INPUT=<input location>
export GRW_RECOMBINE_OUTPUT=<output location>
chmod +x run_dataflow.sh
./run_dataflow.sh
```
3. Run the template:
```bash
export GRW_RECOMBINE_INPUT=<input location>
export GRW_RECOMBINE_OUTPUT=<output location>
chmod +x build.sh
./build.sh
chmod +x run_template.sh
./run_template.sh
```

## Notes on the Code
1. You'll notice that the beam pipeline code is packaged as a python package rather than just being a simple script. This is because using custom built functions directly in the python callable can result in strange import loops and errors. Within the `run` function of the pipeline we specify a `setup_file` argument to ensure our package gets picked up and used by the beam pipeline. 
2. For whatever reason when the template is being build, it tries to install the `requirements.txt` dependencies with the `--no-binary` flag. This simply does not work for `tensorflow` so we install `tensorflow` separately in the Dockerfile and leave it out of `requirements.txt`.
3. Because we need to write out tensorflow records in a specific order, the records are written during a map function rather than using the standard TFRecord writer given by apache beam. In addition we write out a set of file lists so that we can determine when the pipeline is complete from the upload stage of the pipeline. It is also important that we write out the TFRecords with the same directory structure as the files in `grw-ee-download` so that the upload stage knows where to go looking for the `mixer.json` file. 
