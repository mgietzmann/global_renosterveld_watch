from apache_beam import coders
from apache_beam.io.filebasedsource import FileBasedSource
from apache_beam.io.filesystem import CompressionTypes
from apache_beam.io.iobase import Read
from apache_beam.transforms import PTransform
from apache_beam.io.tfrecordio import _TFRecordUtil
from apache_beam.io.tfrecordio import _TFRecordSource


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
    def __init__(
        self,
        file_pattern,
        coder=coders.BytesCoder(),
        compression_type=CompressionTypes.AUTO,
        validate=True):
        super(KeyedReadFromTFRecord, self).__init__()
        self._source = KeyedTFRecordSource(
            file_pattern, coder, compression_type, validate)

    def expand(self, pvalue):
        return pvalue.pipeline | Read(self._source)