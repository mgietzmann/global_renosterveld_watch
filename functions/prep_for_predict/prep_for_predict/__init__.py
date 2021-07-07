import tensorflow as tf
import json
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions


# KEYED IO
from apache_beam import coders
from apache_beam.io.filebasedsource import FileBasedSource
from apache_beam.io.filesystem import CompressionTypes
from apache_beam.io.iobase import Read
from apache_beam.transforms import PTransform
from apache_beam.io.tfrecordio import _TFRecordUtil

from apache_beam.io.tfrecordio import _TFRecordSource

"""
class KeyedTFRecordSource(FileBasedSource):
    def __init__(self, file_pattern, coder, compression_type, validate):
        super(KeyedTFRecordSource, self).__init__(
        # super not allowed https://stackoverflow.com/questions/58410406/gcp-dataflow-with-python-attributeerror-cant-get-attribute-jsonsink-on-mo
        #FileBasedSource.__init__(self,
            file_pattern=file_pattern,
            compression_type=compression_type,
            splittable=False,
            validate=validate)
        
        self._coder = coder

    def read_records(self, file_name, offset_range_tracker):
        if offset_range_tracker.start_position():
            raise ValueError(
                'Start position not 0:%s' % offset_range_tracker.start_position())

        current_offset = offset_range_tracker.start_position()
        with self.open_file(file_name) as file_handle:
            while True:
                if not offset_range_tracker.try_claim(current_offset):
                    raise RuntimeError('Unable to claim position: %s' % current_offset)
                record = _TFRecordUtil.read_record(file_handle)
                if record is None:
                    return  # Reached EOF
                else:
                    current_offset += _TFRecordUtil.encoded_num_bytes(record)
                    yield (file_name, current_offset, self._coder.decode(record))
                    """


class KeyedTFRecordSource(_TFRecordSource):
    def __init__(self, file_pattern, coder, compression_type, validate):
        super(KeyedTFRecordSource, self).__init__(file_pattern, coder, compression_type, validate)
    
    def read_records(self, file_name, offset_range_tracker):
        if offset_range_tracker.start_position():
            raise ValueError(
                'Start position not 0:%s' % offset_range_tracker.start_position())

        current_offset = offset_range_tracker.start_position()
        with self.open_file(file_name) as file_handle:
            while True:
                if not offset_range_tracker.try_claim(current_offset):
                    raise RuntimeError('Unable to claim position: %s' % current_offset)
                record = _TFRecordUtil.read_record(file_handle)
                if record is None:
                    return  # Reached EOF
                else:
                    current_offset += _TFRecordUtil.encoded_num_bytes(record)
                    yield (file_name, current_offset, self._coder.decode(record))
                
                
class KeyedReadFromTFRecord(PTransform):
    """Transform for reading TFRecord sources."""
    def __init__(
        self,
        file_pattern,
        coder=coders.BytesCoder(),
        compression_type=CompressionTypes.AUTO,
        validate=True):
        """Initialize a ReadFromTFRecord transform.

        Args:
          file_pattern: A file glob pattern to read TFRecords from.
          coder: Coder used to decode each record.
          compression_type: Used to handle compressed input files. Default value
              is CompressionTypes.AUTO, in which case the file_path's extension will
              be used to detect the compression.
          validate: Boolean flag to verify that the files exist during the pipeline
              creation time.

        Returns:
          A ReadFromTFRecord transform object.
        """
        #super(KeyedReadFromTFRecord, self).__init__()
        # super not allowed https://stackoverflow.com/questions/58410406/gcp-dataflow-with-python-attributeerror-cant-get-attribute-jsonsink-on-mo
        PTransform.__init__(self)
        self._source = KeyedTFRecordSource(
            file_pattern, coder, compression_type, validate)

    def expand(self, pvalue):
        return pvalue.pipeline | Read(self._source)
    
# CONFIG
MAXES = {
    "B1": 0.2646461444046211, 
    "B10": 0.02135643009876302, 
    "B11": 0.45914211598880617, 
    "B12": 0.3551247273442366, 
    "B2": 0.24704067457677212, 
    "B3": 0.24506566228579266, 
    "B4": 0.28417120654254574, 
    "B5": 0.29591222742379286, 
    "B6": 0.3339981156929012, 
    "B7": 0.37680363932814853, 
    "B8": 0.3651257736365482, 
    "B8A": 0.4042514650642024, 
    "B9": 0.1630839023154672, 
    "evi": 0.6329985345270633, 
    "label": 1, 
    "nbr": 0.59955735854801,
    "ndre": 0.48651306834284724,
    "ndvi": 0.6543590629869743, 
    "ndwi": 0.3260883093801998
}
MINS = {
    "B1": 0.1071878310266745, 
    "B10": 9.99999974737875e-05, 
    "B11": 0.04055041829261718, 
    "B12": 0.021972806848443917,
    "B2": 0.07788308777803843, 
    "B3": 0.05443219895090026, 
    "B4": 0.03686619734897828, 
    "B5": 0.0402839230566983, 
    "B6": 0.04838389392726, 
    "B7": 0.051249101310881714, 
    "B8": 0.046352828801548, 
    "B8A": 0.05127381553341451, 
    "B9": 0.015004677379421008, 
    "evi": 0.005874500824244935, 
    "label": 0, 
    "nbr": -0.214462275311423, 
    "ndre": -0.029295845476347133, 
    "ndvi": 0.008852780316880287, 
    "ndwi": -0.339603199531223
}  
BANDS = [
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6','B7', 
    'B8', 'B8A', 'B9', 'B10', 'B11', 'B12', 
    'ndvi', 'evi', 'ndre', 'ndwi', 'nbr'
]
PATCH_DIMENSIONS_FLAT = [2,64 * 64]
FEATURES = {
    band: tf.io.FixedLenFeature(PATCH_DIMENSIONS_FLAT, dtype=tf.float32)
    for band in BANDS
}
    
# UTILS
def pass_key(func):
    return lambda x: (x[0], func(x[1]))
    
def file_path_key(file_path):
    return file_path.split('_')[-1].split('.')[0]
    
def transpose_per_key(data_dict):
    for key, value in data_dict.items():
        data_dict[key] = tf.transpose(value)
    return data_dict
    
def break_up_patch(x):
    key, data_dict = x
    return [(f'{key},{i}', pixel_dict) 
            for i, pixel_dict 
            in enumerate(tf.data.Dataset.from_tensor_slices(data_dict))
           ]
    
def standardize(x):
    for k in x:
        x[k] = (x[k]-MINS[k])/(MAXES[k]-MINS[k])
    return x
    
def jsonify_data(x):
    key, data = x
    data = [
        [float(element) for element in array]
        for array in data.numpy()
    ]
    return json.dumps({'key': key, 'input_1': data})

def run():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    path_args, pipeline_args = parser.parse_known_args()

    options = PipelineOptions(pipeline_args)
    options.view_as(SetupOptions).save_main_session = True
    p = beam.Pipeline(options=options)
    filtered_keys = ['2021-07-04,590216', '2021-07-04,1180432', '2021-07-04,1770648', '2021-07-04,2360864', '2021-07-04,2951080']
    fk2 = ['2021-07-04,590216,0', '2021-07-04,590216,1', '2021-07-04,590216,2', '2021-07-04,590216,3', '2021-07-04,590216,4']

    data = (
        p
        | 'Read Earth Engine Output' >> KeyedReadFromTFRecord(path_args.input)
        | 'Create Keys from Position Information' >> beam.Map(lambda x: (f'{file_path_key(x[0])},{x[1]}', x[2]))
        | 'Filter Keys' >> beam.Filter(lambda x: x[0] in filtered_keys)
        | 'Parse Features' >> beam.Map(pass_key(lambda record: tf.io.parse_single_example(record, FEATURES)))
        | 'Tranpose to Timeline per Pixel' >> beam.Map(pass_key(transpose_per_key))
        | 'Break Into Data per Pixel' >> beam.FlatMap(break_up_patch)
        | 'Filter Keys 2' >> beam.Filter(lambda x: x[0] in fk2)
        | 'Standardize Data' >> beam.Map(pass_key(standardize))
        | 'Transform Data Dict Into a Timeline of Tuples' \
            >> beam.Map(pass_key(lambda data_dict: tf.transpose(list(data_dict.values()))))
        | 'JSONify Data' >> beam.Map(jsonify_data)
        | 'Write Data' >> beam.io.WriteToText(path_args.output)
    )

    p.run()