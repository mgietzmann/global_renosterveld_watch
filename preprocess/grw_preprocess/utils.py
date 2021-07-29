import json
import tensorflow as tf

from .config import MINS, MAXES


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