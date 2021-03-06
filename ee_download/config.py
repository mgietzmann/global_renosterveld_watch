import datetime

BANDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6','B7', 'B8', 'B8A', 'B9', 'B10', 'B11','B12','ndvi','evi','ndre','ndwi','nbr']
BUCKET = 'grw-ee-download'
CLOUD_THRESH = 40
DWINDOW = 180
DSTEP = 10
EXPORT_FORMAT_OPTIONS = {
        'patchDimensions': [64, 64],
        'maxFileSize': 1000000000,
        'compressed': True
    }
MAX_PIXELS = 200000000
PDATESTR = datetime.datetime.today().strftime('%Y-%m-%d')
PREDICT_IMG_BASE = 'downloads'
PREDICT_MASK = 'users/glennwithtwons/remnos'
SCALE = 10

IMAGE_FILE_PREFIX = PREDICT_IMG_BASE + "/" + PDATESTR + "/"