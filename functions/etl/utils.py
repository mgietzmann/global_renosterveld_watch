import ee
import math
import config


def initialize():
    service_account = 'renosterveld-ee@ee-vegetation-gee4geo.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, 'ee-vegetation-gee4geo-6309a79ef209.json')
    ee.Initialize(credentials)


def get_poi():
    return ee.FeatureCollection(config.PREDICT_MASK).geometry().convexHull()


#function to mask renoster pathces
def remclip(mask):
    def remclipInner(image):
        return image.updateMask(mask)
    return remclipInner


#function to remove obs ndvi < 0
def ndclip(image):
    return image.updateMask(image.select(['ndvi']).gt(0))


#to fill nulls with previous non null record
def gap_fill(image, listb):
    previous = ee.Image(ee.List(listb).get(-1))
    new = image.unmask(previous)
    return ee.List(listb).add(new)


#join s2 clouds and s2 data
def joinS2(area_to_join,start,end):
    innerJoin = ee.Join.inner()

    # Specify an equals filter for image timestamps.
    filterIDEq = ee.Filter.equals(
        leftField= 'system:index',
        rightField= 'system:index'
    )

    #level 1 s2 data
    S2_nocloud = ee.ImageCollection('COPERNICUS/S2')\
    .filterBounds(area_to_join)\
    .filterDate(start, end)
    #s2cloudless data
    S2_cloud = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")\
    .filterBounds(area_to_join)\
    .filterDate(start, end)

    innerJoinedS2 = innerJoin.apply(S2_nocloud, S2_cloud, filterIDEq)

    #Map a function to merge the results in the output FeatureCollection
    joinedS2 = innerJoinedS2.map(lambda feature: ee.Image.cat(feature.get('primary'), feature.get('secondary')))
    return ee.ImageCollection(joinedS2)


#S2 shadows and clouds from https://github.com/samsammurphy/cloud-masking-sentinel2/blob/master/cloud-masking-sentinel2.ipynb
def shadowCloudMask(image):
    """
    Finds cloud shadows in images
    
    Originally by Gennadii Donchyts, adapted by Ian Housman
    """
    
    def potentialShadow(cloudHeight):
        """
        Finds potential shadow areas from array of cloud heights
        
        returns an image stack (i.e. list of images) 
        """
        cloudHeight = ee.Number(cloudHeight)
        
        # shadow vector length
        shadowVector = zenith.tan().multiply(cloudHeight)
        
        # x and y components of shadow vector length
        x = azimuth.cos().multiply(shadowVector).divide(nominalScale).round()
        y = azimuth.sin().multiply(shadowVector).divide(nominalScale).round()
        
        # affine translation of clouds
        cloudShift = cloudMask.changeProj(cloudMask.projection(), cloudMask.projection().translate(x, y)) # could incorporate shadow stretch?
        
        return cloudShift

    # select a cloud mask
    cloudMask = image.select(['probability'])

    img = image.select(['B1','B2','B3','B4','B6','B8A','B9','B10', 'B11','B12'],\
                 ['aerosol', 'blue', 'green', 'red', 'red2','red4','h2o', 'cirrus','swir1', 'swir2'])\
                 .divide(10000).addBands(image.select('QA60'))\
                 .set('solar_azimuth',image.get('MEAN_SOLAR_AZIMUTH_ANGLE'))\
                 .set('solar_zenith',image.get('MEAN_SOLAR_ZENITH_ANGLE'))
    
    # make sure it is binary (i.e. apply threshold to cloud score)
    cloudScoreThreshold = config.CLOUD_THRESH
    cloudMask = cloudMask.gt(cloudScoreThreshold)

    # solar geometry (radians)
    azimuth = ee.Number(img.get('solar_azimuth')).multiply(math.pi).divide(180.0).add(ee.Number(0.5).multiply(math.pi))
    zenith  = ee.Number(0.5).multiply(math.pi ).subtract(ee.Number(img.get('solar_zenith')).multiply(math.pi).divide(180.0))

    # find potential shadow areas based on cloud and solar geometry
    nominalScale = cloudMask.projection().nominalScale()
    cloudHeights = ee.List.sequence(500,4000,500)        
    potentialShadowStack = cloudHeights.map(potentialShadow)
    potentialShadow = ee.ImageCollection.fromImages(potentialShadowStack).max()

    # shadows are not clouds
    potentialShadow = potentialShadow.And(cloudMask.Not())

    # (modified) dark pixel detection 
    darkPixels = img.normalizedDifference(['green', 'swir2']).gt(0.25)

    # shadows are dark
    shadows = potentialShadow.And(darkPixels)
    cloudShadowMask = shadows.Or(cloudMask)

    return image.updateMask(cloudShadowMask.Not())


def addBANDS(image):
    img = image.addBands(image.normalizedDifference(['B8', 'B4']).rename(['ndvi']))\
    .addBands(image.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
        'NIR': image.select('B8'),
        'RED': image.select('B4'),
        'BLUE': image.select('B2')
    }).rename(['evi']))\
    .addBands(image.normalizedDifference(['B8', 'B5']).rename(['ndre']))\
    .addBands(image.normalizedDifference(['B8', 'B11']).rename(['ndwi']))\
    .addBands(image.normalizedDifference(['B8', 'B12']).rename(['nbr']))

    return img


#return S2 data in regular time series for prediction
def predS2(renoster,mask_renoster):
    def predS2inner(dlist):
        #extract dates
        #start day
        dat = ee.Date(dlist)
        #end day
        dat2 = dat.advance(-1*config.DSTEP,'day')
        #string
        dat_str = dat.format()

        poi = get_poi()

        #join
        S2_joined = joinS2(poi,dat2,dat)

        #process joined data
        imageCol_gaps = S2_joined\
        .filterBounds(poi)\
        .filterDate(dat2, dat)\
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 70))\
        .map(shadowCloudMask)\
        .map(lambda image: image.divide(10000))\
        .map(remclip(mask_renoster))\
        .map(addBANDS)\
        .select(config.BANDS)

        #need to deal with cases in which we have no image
        imageCol_gaps = ee.Algorithms.If(imageCol_gaps.size(),\
                                        imageCol_gaps.qualityMosaic('ndvi'),\
                                        ee.ImageCollection(ee.List(config.BANDS).map(lambda band: ee.Image())).toBands().rename(config.BANDS))
        imageCol_gaps = ee.Image(imageCol_gaps).updateMask(mask_renoster)

        #remove when ndvi <0
        imageCol_gaps = ndclip(imageCol_gaps)

        #add labels and time
        imageCol_gaps = imageCol_gaps\
        .set('system:time_start', dat)

        return imageCol_gaps
    return predS2inner
