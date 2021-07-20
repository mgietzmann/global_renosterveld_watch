import tensorflow as tf
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

from .config import FEATURES
from .keyed_io import KeyedReadFromTFRecord
from .utils import (
    pass_key, file_path_key, transpose_per_key,
    break_up_patch, standardize, jsonify_data
)


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
        | 'Read Earth Engine Output' >> KeyedReadFromTFRecord(path_args.input)
        | 'Create Keys from Position Information' >> beam.Map(lambda x: (f'{file_path_key(x[0])},{x[1]}', x[2]))
        | 'Parse Features' >> beam.Map(pass_key(lambda record: tf.io.parse_single_example(record, FEATURES)))
        | 'Tranpose to Timeline per Pixel' >> beam.Map(pass_key(transpose_per_key))
        | 'Break Into Data per Pixel' >> beam.FlatMap(break_up_patch)
        | 'Standardize Data' >> beam.Map(pass_key(standardize))
        | 'Transform Data Dict Into a Timeline of Tuples' \
            >> beam.Map(pass_key(lambda data_dict: tf.transpose(list(data_dict.values()))))
        | 'JSONify Data' >> beam.Map(jsonify_data)
        | 'Write Data' >> beam.io.WriteToText(path_args.output)
    )

    p.run()