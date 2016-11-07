'''
Created on 31/10/2016

@author: erickpalacios
'''
import logging
import numpy
import pandas
from sklearn.decomposition import PCA
from scipy import stats
from madmex.mapper.data import vector
from madmex.mapper.data.vector import create_empty_layer
import ogr
LOGGER = logging.getLogger(__name__)

def reduce_dimensionality(dataframe, maxvariance, columns_to_drop):
    '''
    Performs PCA on feature pandas dataframe and reduces number of
    principal components to those which explain a defined variance
    '''
    dataframe_without_columns = dataframe.drop(columns_to_drop, axis = 1)
    LOGGER.info('Columns to be used by pca:')
    print dataframe_without_columns.columns
    LOGGER.info('Adding noise to dataframe')
    dataframe_without_columns = dataframe_without_columns + numpy.random.normal(size = dataframe_without_columns.shape)*1.e-19 
    pca = PCA(n_components = 'mle')
    pca.fit(dataframe_without_columns)
    # transform
    samples = pca.transform(dataframe_without_columns)
    # aggregated sum of variances
    sum_variance = sum(pca.explained_variance_)
    #print sum_variance, pca.explained_variance_
    # get those having aggregated variance below threshold
    scomp = 0
    ncomp = 0
    while scomp < maxvariance:
        c = pca.explained_variance_[ncomp]
        scomp = scomp + c/sum_variance
        ncomp = ncomp+1
    # reduce dimensionality
    samples = samples[:,:ncomp]  
    LOGGER.info("Number of features after PCA transformation %s" % samples.shape[1])    
    return samples
def outlier_elimination_for_dataframe(dataframe, column_name_of_ids,  column_name_of_classes, columns_to_drop, max_number_of_features, list_of_classes, probability):
    object_ids_and_given = dataframe[[column_name_of_ids, column_name_of_classes]]
    dataframe_without_columns = dataframe.drop(columns_to_drop, axis = 1)
    number_of_columns = len(dataframe_without_columns.columns)
    LOGGER.info('Number of columns of dataframe without columns :%s', number_of_columns)
    dataframe = None
    dataframe_new_indexing = dataframe_without_columns.set_index(column_name_of_classes)
    #dataframe_new_indexing = dataframe.set_index(column_name_of_classes)   
    number_of_columns_new_indexing = len(dataframe_new_indexing.columns) 
    LOGGER.info('Number of columns of dataframe new indexing :%s', number_of_columns_new_indexing)
    print 'columns new indexing'
    print dataframe_new_indexing.columns
    if number_of_columns_new_indexing < max_number_of_features:
        dataframe_subset = dataframe_new_indexing.iloc[:, 0:0+number_of_columns_new_indexing]
    else:
        dataframe_subset = dataframe_new_indexing.iloc[:, 0:0+max_number_of_features]
    dataframe_new_indexing = None
    object_ids_new_indexing = object_ids_and_given.set_index(column_name_of_classes)
    number_of_columns_new_indexing_and_subset = len(dataframe_subset.columns)
    LOGGER.info('Number of columns of dataframe new indexing and subset :%s', number_of_columns_new_indexing_and_subset)
    print 'columns new indexing and subset'
    print dataframe_subset.columns
    max_number_of_objects = 5.e4
    list_ids_kept = []
    LOGGER.info('Classes to be processed: %s' % list_of_classes)
    for i in range(len(list_of_classes)):
        df = dataframe_subset.loc[list_of_classes[i]]
        object_ids_per_class = object_ids_new_indexing.loc[list_of_classes[i]][column_name_of_ids]
        LOGGER.info('Number of objects: %s in class %s' % (len(df.index), list_of_classes[i]))
        y = len(df.index)
        if y > max_number_of_objects:
            LOGGER.info('Class %s have more than %s objects' %(list_of_classes[i], max_number_of_objects))
            LOGGER.info('Class %s will be processed by chunks' % list_of_classes[i])
            number_of_bins = y / max_number_of_objects
            if y % max_number_of_objects == 0:
                maxcounter = number_of_bins+1
            else:
                maxcounter = number_of_bins+2
            for j in range(1,maxcounter):
                if j*max_number_of_objects > y:
                    LOGGER.info('Chunk: %s' % j)
                    ind_ids = (j-1)*max_number_of_objects+j-2
                    ids_kept = histogram_trimming(df.iloc[ind_ids:], object_ids_per_class.iloc[ind_ids:], probability, list_of_classes[i])
                    ids_kept.columns = [column_name_of_ids]
                    list_ids_kept.append(ids_kept)
                else:
                    LOGGER.info('Chunk: %s' % j)
                    ind_ids_1 = max_number_of_objects*(j-1)
                    ind_ids_2 = max_number_of_objects*(j-1)+max_number_of_objects
                    ids_kept = histogram_trimming(df.iloc[ind_ids_1:ind_ids_2], object_ids_per_class.iloc[ind_ids_1:ind_ids_2], probability, list_of_classes[i])       
                    ids_kept.columns = [column_name_of_ids]
                    list_ids_kept.append(ids_kept)
        else:
            
            ids_kept = histogram_trimming(df, object_ids_per_class, probability, list_of_classes[i])
            ids_kept.columns = [column_name_of_ids]
            list_ids_kept.append(ids_kept) 
    return pandas.concat(list_ids_kept)
def histogram_trimming(dataframe, object_ids, threshold, name_of_class):
    '''
    Performs classwise an iterative histogram trimming over all features,
    thereby calculate probability density function and remove samples below a given probability,
    iteratively it does that until all remaining samples have a probability higher the given threshold.
    The outlier elimination is based on Radoux, J. and Defourney, P. (2010) 
    '''
    LOGGER.info('Class to be processed by outlier elimination iterative histogram trimming: %s' % name_of_class)
    data = dataframe.convert_objects(convert_numeric=True)
    data = data.astype(numpy.int16)
    data = (data.values).T
    crit = 1
    iteration = 1
    thisfeatureinliers = object_ids
    prev_obj = 1.e6
    if data.shape[1] > 30: # preserve at least 30 samples
        LOGGER.info('Reducing number of objects of class: %s' % name_of_class)
        LOGGER.info('Class %s found %s objects, continue with outlier elimination' %(name_of_class, data.shape[1]))
        while crit > 0 and data.shape[1] > 30:
            my_pdf = stats.kde.gaussian_kde(data[:,:])
            ddev = my_pdf.evaluate(my_pdf.dataset)
            p1 = stats.scoreatpercentile(ddev,25)
            adjust = False      
            if (p1 < threshold) and (adjust == False):
                thisthreshold = p1    
                adjust = True      
            idx = ddev > thisthreshold
            data = data[:,idx]
            thisfeatureinliers = thisfeatureinliers[idx] 
            crit = ddev.shape[0] > sum(idx)
            n_obj_changed = prev_obj - data.shape[1]
            prev_obj = data.shape[1]
            if n_obj_changed < 5:
                crit = 0
            if iter == 20:
                crit = 0
            LOGGER.info('Class: %s , iteration: %s, objects: %s, current threshold: %s, current minimum probability %s' %(name_of_class, iteration, data.shape[1], threshold, min(ddev)))
            iteration = iteration + 1
        LOGGER.info('Class: %s conserved: %s objects' %(name_of_class, data.shape[1]))
    else:
        LOGGER.info('Class: %s have less than 30 objects, so this are preserved' % name_of_class)
        LOGGER.info('Number of objects: %s' % len(object_ids.index))
    #get indices of inlier ids
    thisclassinliers = numpy.unique(thisfeatureinliers)
    ix = numpy.in1d(numpy.array(object_ids),thisclassinliers)
    ix = object_ids[ix]
    return pandas.DataFrame(ix)
def generate_namesfile(columns, unique_classes, name_namesfile, column_name_of_ids, column_name_of_classes):
    f = open(name_namesfile, 'w+')
    f.write(column_name_of_classes + '.\n\n')
    for c in columns:
        if c == column_name_of_ids:
            f.write(c+ ':label.\n')
        elif c == column_name_of_classes:
            f.write(c + ': ' + ','.join(map(str,unique_classes)) + '.\n')
        else:
            f.write(c + ': continuous.\n')
    f.close()
    return name_namesfile
def join_dataframes_by_column_name(list_of_dataframes, column_name):
    dataframe = list_of_dataframes[0]
    for i in range(1, len(list_of_dataframes)):
        dataframe = pandas.merge(dataframe, list_of_dataframes[i], on = column_name, how = 'inner')
    return dataframe
def join_C5_dataframe_and_shape(shape_class, shape_column, dataframe, dataframe_column):
    feature = shape_class.layer.GetNextFeature()
    feature_list = []
    while feature is not None:
        object_id = feature.GetField(shape_column)
        feature_list.append([feature.GetGeometryRef().ExportToWkt(), object_id])
        feature = shape_class.layer.GetNextFeature()
    shape_dataframe = pandas.DataFrame(feature_list)
    shape_dataframe.columns = ['geom', shape_column]
    LOGGER.info('Joining segmentation shape and C5 data frame')
    return join_dataframes_by_column_name([shape_dataframe, dataframe], dataframe_column)
def write_C5_dataframe_to_shape(dataframe, shape_class, out_file):
    data_layer, ds_layer = create_empty_layer(out_file, 'export', shape_class.srid)
    fid = ogr.FieldDefn('gid', ogr.OFTInteger)
    data_layer.CreateField(fid) 
    table_types = dataframe.dtypes
    table_columns = dataframe.columns   
    geomcolumn = 'geom'     
    for c in range(table_columns.shape[0]):
        dt = table_types[c]
        n = table_columns[c]
        if "float" in str(dt) :
            FieldType = ogr.OFTReal
        elif "int" in str(dt)  :
            FieldType = ogr.OFTInteger 
        elif "object" in str(dt)  :
            FieldType = ogr.OFTString 
        else:
            FieldType = ogr.OFTString 
        fd = ogr.FieldDefn(n, FieldType) 
        if not n ==  geomcolumn: 
            data_layer.CreateField(fd) 
    for i in range(dataframe.shape[0]):
        data = dataframe.iloc[i].values
        feature = ogr.Feature(data_layer.GetLayerDefn())
        gfi = feature.GetFieldIndex('gid')
        feature.SetField(gfi, i+1)
        for c in range(table_columns.shape[0]):
            d = data[c]
            n = table_columns[c]
            if n ==  geomcolumn:
                feature.SetGeometry(ogr.CreateGeometryFromWkt(d))
            else:
                gfi = feature.GetFieldIndex(n)
                feature.SetField(gfi, str(d))
            data_layer.CreateFeature(feature)  
        feature.Destroy()      
        data_source = None

