# `grw_recombine`

## Building the Template
Make the build script executable with `chmod +x build.sh` and then run:
```bash
./build.sh
```

## Running the Template
Make the template run script executable with `chmod +x run_template.sh` and then run:
```bash
export GRW_RECOMBINE_INPUT="gs://grw-predict/1626879681/-00198-of-00610"
export GRW_RECOMBINE_OUTPUT="gs://grw-recombine/TestBeamRecombine/"
./run_template.sh
```

Obviously you may need to change the environment variables `GRW_INPUT` and `GRW_OUTPUT` to match example data for yourself.

## Running Locally
First start by install grw_preprocess:
```bash
python setup.py develop
```

Next set your `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your JSON credentials config,

Finally run:
```bash
export GRW_RECOMBINE_PROJECT="ee-vegetation-gee4geo"
export GRW_RECOMBINE_TEMP_LOCATION="gs://reno-ee-example/tmp/"
export GRW_RECOMBINE_STAGING_LOCATION="gs://reno-ee-example/staging/"
export GRW_RECOMBINE_INPUT="gs://grw-predict/1627302676/-00000-of-00609"
export GRW_RECOMBINE_OUTPUT="gs://reno-ee-example/TestBeamRecombine2/"
./run_local.sh
```

Obviously you may need to change the environment variables to match your situation.
