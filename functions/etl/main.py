import ee
import config
import utils

def main(**args):
    utils.initialize()

    # load area to predict
    predict = ee.FeatureCollection(config.PREDICT_MASK)

    # mask to our study area
    mask_predict = predict \
    .map(lambda feature: feature.set('flag', ee.Number(1))) \
    .reduceToImage(['flag'],ee.Reducer.first())

    # get the dates of interest
    pDateEnd = ee.Date(config.PDATESTR).advance(-1,'day')
    pDateStart = pDateEnd.advance(-1*config.DWINDOW,'day')
    PDate_Start = ee.Date(pDateStart)
    PDate_End = ee.Date(pDateEnd)
    n_day_pred = config.DWINDOW-config.DSTEP
    pdates = ee.List.sequence(0, n_day_pred, config.DSTEP)

    # map to dates and create imagecol from results
    # produces stack of images from yesterday to 6 months ago
    ilist = pdates.map(utils.predS2(predict,mask_predict))
    imageCol_gaps = ee.ImageCollection(ilist)
    imageCol_gaps = imageCol_gaps.select(config.BANDS)
    names = imageCol_gaps.first().bandNames()

    #find first non-null value in timeseries
    first_im = imageCol_gaps\
    .reduce(ee.Reducer.firstNonNull())\
    .rename(names)\
    .set({'system:index': 'first'})
    first = ee.List([first_im])

    #fill nulls
    #then drop first image
    imageCol = ee.ImageCollection(ee.List(imageCol_gaps.iterate(utils.gap_fill, first)))\
    .filter(ee.Filter.neq('system:index', 'first'))

    #timeseries length
    tsLengthPred = imageCol.size().getInfo()
    #18

    #flatten to array bands
    imageCol = imageCol.map(remclip(mask_predict))
    imageCol_all = imageCol.toArrayPerBand()

    #define bands to export and dim
    export_options = {
        'tensorDepths': dict(zip(list(config.BANDS), np.repeat(tsLengthPred,len(config.BANDS)).tolist()))
    }
    export_options.update(config.EXPORT_FORMAT_OPTIONS)

    # Setup the task
    imageTask = ee.batch.Export.image.toCloudStorage(
        image=imageCol_all,
        description='Image Export',
        fileNamePrefix=config.IMAGE_FILE_PREFIX,
        bucket=config.BUCKET,
        maxPixels=config.MAX_PIXELS,
        scale=config.SCALE,
        fileFormat='TFRecord',
        region=utils.get_poi(),
        formatOptions=export_options,
    )

    # Start the task
    imageTask.start()
    # this whole process can take 6-24 hours