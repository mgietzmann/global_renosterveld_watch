import os
import tensorflow as tf
import json
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

    
def create_example(data):
    patch_key = data[0]
    patch_data = data[1]
    patch_data = sorted(patch_data, key=lambda pixel: pixel['key'])
    patch = [[], [], []]
    for pixel_data in patch_data:
        patch[0].append(tf.argmax(pixel_data['output_1']))
        patch[1].append(pixel_data['output_1'][0])
        patch[2].append(pixel_data['output_1'][1])
    example = tf.train.Example(
      features=tf.train.Features(
        feature={
          'prediction': tf.train.Feature(
              int64_list=tf.train.Int64List(
                  value=patch[0])),
          'RenoProb': tf.train.Feature(
              float_list=tf.train.FloatList(
                  value=patch[1])),
          'TransProb': tf.train.Feature(
              float_list=tf.train.FloatList(
                  value=patch[2])),
        }
      )
    )
    return (patch_key, example)


def parse_key(data):
    str_key = data['key']
    split_key = data['key'].split(',')
    # need to convert these to integers so sorting works correctly
    # 101 comes before 11 if sorted alphanumerically which we don't 
    # want
    actual_key = (split_key[0], int(split_key[1]), int(split_key[2]))
    data['key'] = actual_key
    return data


class MapWriteToTFRecord(beam.DoFn):
    def process(self, data, output_dir):
        file_key = data[0]
        file_data = data[1]
        file_data = sorted(file_data, key=lambda patch_data: patch_data[0])
        #options = tf.io.TFRecordOptions(compression_type='GZIP')
        writer = tf.io.TFRecordWriter(f'{output_dir}{file_key}.tfrecord')#, options=options)
        for patch_key, patch_example in file_data:
            writer.write(patch_example.SerializeToString())
        writer.close()
        return [f'{output_dir}{file_key}']


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
        | 'Read Predictions' >> beam.io.ReadFromText(path_args.input)
        | 'Parse Data' >> beam.Map(lambda line: json.loads(line))
        | 'Parse Key' >> beam.Map(lambda data: parse_key(data))
        | 'Extract Patch Key' >> beam.Map(lambda data: (data['key'][:2], data))
        | 'Group by Patch Key' >> beam.GroupByKey()
        | 'Create Tensor Flow Examples' >> beam.Map(lambda data: create_example(data))
        # .split('/')[3:] >> we get only the file name within the bucket here
        | 'Extract File Key' >> beam.Map(lambda data: ('/'.join(data[0][0].split('/')[3:]), data))
        | 'Group by File Key' >> beam.GroupByKey()
        | 'Map-Write to TFRecord' >> beam.ParDo(MapWriteToTFRecord(), path_args.output)
        | 'Write File List' >> beam.io.WriteToText(f'{path_args.output}file_list')
    )

    p.run()