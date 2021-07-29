# `predict`

## Components
This stage consists of nothing more than a *cloud function*, a *bucket*, and a *dataflow template*.

## Setup Instructions
1. First you'll need to create the bucket `grw-predict` where artifacts will be stored.
2. Next build the dataflow template by running:
```bash
chmod +x build.sh
./build.sh
```
3. Create a cloud function that uses a "finalize" storage trigger for the `grw-preprocess` bucket and choose a `python3` execution environment. 
4. Copy the code from the `cloud_func` folder into the cloud function.
5. Deploy!

## Testing
There are three ways you can test the pipeline code. 
1. Run it with the local apache beam runner:
```bash
export GRW_PREDICT_INPUT=<input location>
export GRW_PREDICT_OUTPUT=<output location>
chmod +x run_local.sh
./run_local.sh
```
2. Run it on dataflow without the template:
```bash
export GRW_PREDICT_PROJECT="ee-vegetation-gee4geo"
export GRW_PREDICT_TEMP_LOCATION="gs://reno-ee-example/tmp/"
export GRW_PREDICT_STAGING_LOCATION="gs://reno-ee-example/staging/"
export GRW_PREDICT_INPUT=<input location>
export GRW_PREDICT_OUTPUT=<output location>
chmod +x run_dataflow.sh
./run_dataflow.sh
```
3. Run the template:
```bash
export GRW_PREDICT_INPUT=<input location>
export GRW_PREDICT_OUTPUT=<output location>
chmod +x build.sh
./build.sh
chmod +x run_template.sh
./run_template.sh
```

## Notes on the Code
1. You'll notice that the beam pipeline code is packaged as a python package rather than just being a simple script. This is because using custom built functions directly in the python callable can result in strange import loops and errors. Within the `run` function of the pipeline we specify a `setup_file` argument to ensure our package gets picked up and used by the beam pipeline. 
2. In order to include the model we've added a `MANIFEST.in` file and included it in the `setup.py` code.
3. For whatever reason when the template is being build, it tries to install the `requirements.txt` dependencies with the `--no-binary` flag. This simply does not work for `tensorflow` so we install `tensorflow` separately in the Dockerfile and leave it out of `requirements.txt`.
4. The model has been stored with a special signature that allows us to pass a key along with our datapoint and have the key come through unscathed. This is in keeping with how the google cloud batch prediction service would work - it would also require you to submit a model with a specialized signature so you can pass through keys and thus reconstitute your data after the fact. For more information on how to build a different model signature see how we did it:
```python
import tensorflow as tf

MODEL_EXPORT_PATH = 'models/save_test'
KEYED_EXPORT_PATH = 'models/keyed_model/'

loaded_model = tf.keras.models.load_model(MODEL_EXPORT_PATH, compile=False)

@tf.function(input_signature=[tf.TensorSpec([None], dtype=tf.string),tf.TensorSpec([None, 18, 18], dtype=tf.float32)])
def keyed_prediction(key, input_1):
    pred = loaded_model(input_1, training=False)
    return {
        'output_1': pred,
        'key': key
    }

# Resave model, but specify new serving signature
loaded_model.save(KEYED_EXPORT_PATH, 
                  signatures={'serving_default': keyed_prediction})
```
