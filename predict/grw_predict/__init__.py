import os
import tensorflow as tf
import json
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
KEYED_EXPORT_PATH = os.path.join(DIR_PATH, 'keyed_model')


class Predict(beam.DoFn):
    def __init__(self):
        self.model = None
        
    def process(self, data):
        if self.model is None:
            self.model = tf.keras.models.load_model(KEYED_EXPORT_PATH, compile=False).signatures['serving_default']
        # convert to tensors
        data = {
            'key': tf.constant(data['key']),
            'input_1': tf.convert_to_tensor([data['input_1']], dtype=tf.float32)
        }
        # predict
        prediction = self.model(**data)
        # back to jsonable form
        prediction = {
            'key': prediction['key'].numpy().decode('utf-8'),
            'output_1': [
                [float(element) for element in array]
                for array in  prediction['output_1'].numpy()
            ][0]
        }
        return [prediction]


def run():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--setup_file', required=False, default='./setup.py')

    path_args, pipeline_args = parser.parse_known_args()

    options = PipelineOptions(pipeline_args, setup_file=path_args.setup_file)
    options.view_as(SetupOptions).save_main_session = True
    p = beam.Pipeline(options=options)

    data = (
        p
        | 'Read Transformed Data' >> beam.io.ReadFromText(path_args.input)
        | 'Parse Data' >> beam.Map(lambda line: json.loads(line))
        | 'Predict' >> beam.ParDo(Predict())
        | 'JSONify Data' >> beam.Map(lambda data: json.dumps(data))
        | 'Write Data' >> beam.io.WriteToText(path_args.output)
    )

    p.run()