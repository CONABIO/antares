'''
Created on 08/09/2015

@author: erickpalacios
'''
from __future__ import unicode_literals

import logging

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as so


LOGGER = logging.getLogger(__name__)
BOUNDARIES = [0.68, 0.95, 0.99] 
USED_COMPONENTS = (0, 1)
DPI = 300
MIN_QUANTILE = 5
MAX_QUANTILE = 95
THRESHOLD_LE = 'le'
THRESHOLD_GE = 'ge'
GLOBAL_MODE = 'global'  # calc global thresholds
LOCAL_MODE = 'local'  # use local thresholds for image classfication

def find_confidence_interval(mu, pdf, confidence_level):
    '''
    FInds a confidence interval around the given point, usign the probability
    desinty function at the given confidence level.
    '''
    return pdf[pdf > mu].sum() - confidence_level
def calc_threshold_grid(image_array, pdf_image, tiles=10, bins=55):
    '''
    Calculate thresholds based on probability density function approach.
    '''
    # TODO: every image needs to have no data "NA" value set to 0 <-----
    # Discuss if 0 is an appropriate value for NA values
    no_data_value = 0 
    bands, rows, columns = image_array.shape
    figure, axarr = plt.subplots(tiles, tiles)
    figure.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.5, hspace=0.9)
    for band_combination in [USED_COMPONENTS]:
        res = list()
        first_band, second_band = band_combination
        LOGGER.info('Calculate thresholds for MAF band combination: %d:%d',
                    first_band,
                    second_band)
        y_step_no = np.floor(rows / tiles).astype(np.int)
        x_step_no = np.floor(columns / tiles).astype(np.int)
        ycount = 0
        for y_idx in range(tiles):
            y_aux = y_idx * y_step_no
            xcount = 0
            for x_idx in range(tiles):
                x = x_idx * x_step_no
                if (y_aux + y_step_no) > rows:
                    y_range = rows
                else:
                    y_range = y_aux + y_step_no
                if (x + x_step_no) > columns:
                    x_range = columns
                else:
                    x_range = x + x_step_no
                data_nan_x = image_array[first_band, y_aux:y_range, x:x_range].flatten()
                data_nan_x = data_nan_x[data_nan_x != no_data_value]
                data_nan_y = image_array[second_band, y_aux:y_range, x:x_range].flatten()
                data_nan_y = data_nan_y[data_nan_y != no_data_value]
                if len(data_nan_x) > 0:
                    contour = density_contour(data_nan_x, data_nan_y, bins, bins, ax=axarr[ycount, xcount], pdf_image=pdf_image)
                    if contour != None:
                        res.append(extract_min_max(contour))
                xcount += 1
            ycount += 1
        if pdf_image != None:
            plt.savefig(pdf_image, dpi=DPI, transparent=True, bbox_inches='tight')
    return res

def density_contour(xdata, ydata, nbins_x, nbins_y, labeltext=None, ax=None, pdf_image=None, **contour_kwargs):
    ''' Create a density contour plot.
 
    Parameters
    ----------
    xdata : numpy.ndarray
    ydata : numpy.ndarray
    nbins_x : int
        Number of bins along x dimension
    nbins_y : int
        Number of bins along y dimension
    ax : matplotlib.Axes (optional)
        If supplied, plot the contour to this axis. Otherwise, open a new figure
    contour_kwargs : dict
        kwargs to be passed to pyplot.contour()
    '''
    axis_font = {'fontname':'Arial', 'size':'10'}
    if len(xdata) == 0:
        return None
    H, xedges, yedges = np.histogram2d(xdata, ydata, bins=(nbins_x, nbins_y), normed=True)
    x_bin_sizes = (xedges[1:] - xedges[:-1]).reshape((1, nbins_x))
    y_bin_sizes = (yedges[1:] - yedges[:-1]).reshape((nbins_y, 1))
 
    pdf = (H * (x_bin_sizes * y_bin_sizes))
    sigma_list = list()
    for b in BOUNDARIES:
        if find_confidence_interval(0, pdf, b) != find_confidence_interval(1, pdf, b) or np.sign(find_confidence_interval(0, pdf, b)) != np.sign(find_confidence_interval(1, pdf, b)):
            sigma_list.append(so.brentq(find_confidence_interval, 0., 1., args=(pdf, b)))
        else:
            LOGGER.warn("PDF unsuitable for finding confidence interval for sigma:%f [0:%f, 1:%f]" % (b, find_confidence_interval(0, pdf, b), find_confidence_interval(1, pdf, b)))
    levels = sigma_list
    X, Y = 0.5 * (xedges[1:] + xedges[:-1]), 0.5 * (yedges[1:] + yedges[:-1])
    Z = pdf.T
    if ax == None:
        ax = plt.subplot() 
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(4)
    ax.get_yaxis().set_tick_params(which='both', direction='out', pad=1)
    ax.get_xaxis().set_tick_params(which='both', direction='out', pad=1)
    if labeltext != None:
        ax.set_title(labeltext)
    if len(levels) > 0:
        contour_f = ax.contourf(X, Y, Z, colors=("#BCBCBC"), levels=levels, origin="lower", **contour_kwargs)
        contour = ax.contour(X, Y, Z, levels=levels, origin="lower", **contour_kwargs)   
        return contour
    else:
        return None  # ignore local PDF because it is unsuitable

def extract_min_max(contour):
    '''
    Extract global min/max limits of countour object
    '''
    limit = dict()
    for i in range (len(contour.collections)):  # for each sigma contour collection
        limit[i] = list()
        x_path = np.array(())
        y_path = np.array(())
        for j in range(len(contour.collections[i].get_paths())):
            p = contour.collections[i].get_paths()[j]
            v = p.vertices
            x_path = np.concatenate((x_path, v[:, 0]))
            y_path = np.concatenate((y_path, v[:, 1]))
        limit[i] = (np.min(x_path), np.max(x_path), np.min(y_path), np.max(y_path))
    return limit

def recode_classes_grid(data, thresholds, tiles=10, NODATA=-999, mode=GLOBAL_MODE):
    '''
    Recode data matrix to class thresholds
    '''
    bands, y_max, x_max = data.shape
    LOGGER.info("PDF classification mode: %s grid" % mode)
 
    result = np.zeros((y_max, x_max)).astype(np.int16) + NODATA

    if mode == GLOBAL_MODE:
        class_list = class_split(thresholds)
        LOGGER.info('Classification list: %s', class_list)
        for class_label in class_list.keys():
            mode, band_no, thres_value = class_list[class_label]
            LOGGER.info("MAF class recode: class #%d - %s" % (class_label, str(class_list[class_label])))
            if mode == THRESHOLD_LE:
                result = np.where(data[band_no, :, :] <= thres_value, class_label, result)
            elif mode == THRESHOLD_GE:
                result = np.where(data[band_no, :, :] >= thres_value, class_label, result)   
    else:
        y_step_no = np.floor(y_max / tiles).astype(np.int)
        x_step_no = np.floor(x_max / tiles).astype(np.int)
        counter = 0
        for y_idx in range(tiles):
            y = y_idx * y_step_no
            for x_idx in range(tiles):
                x = x_idx * x_step_no
                if (y + y_step_no) > y_max:
                    y_range = y_max
                else:
                    y_range = y + y_step_no
                if (x + x_step_no) > x_max:
                    x_range = x_max
                else:
                    x_range = x + x_step_no
                class_list = class_split(thresholds, counter)
                for class_label in class_list.keys():
                    mode, band_no, thres_value = class_list[class_label]
                    # logger.debug("MAF class recode: tile %d, class #%d - %s" % (counter, class_label, str(class_list[class_label])))

                    if mode == "le":
                        result[y:y_range, x:x_range] = np.where(data[band_no, y:y_range, x:x_range] <= thres_value, class_label, result[y:y_range, x:x_range])
                    elif mode == "ge":
                        result[y:y_range, x:x_range] = np.where(data[band_no, y:y_range, x:x_range] >= thres_value, class_label, result[y:y_range, x:x_range])
                counter += 1
    return result

def class_split(thresholds, index=None):
    '''
    Generate class list based on thresholds for further class recoding
    '''
    mode = (THRESHOLD_LE, THRESHOLD_GE)
    bands = tuple(sorted(USED_COMPONENTS * len(mode)))
    class_counter = 0
    class_list = dict()
    if index == None:
        threhold_list = get_global_thres(thresholds)
    else:
        threhold_list = get_local_thres(thresholds, index)
    for thres in threhold_list:
        band_counter = 0
        for c, v in  [(class_counter * len(thres) + item + 1, thres[item]) for item in range(len(thres))]:
            class_list[c] = (mode[(c - 1) % 2], bands[band_counter], v)
            band_counter += 1
        class_counter += 1
    return class_list

def get_local_thres(thresholds, idx):
    '''
    Get local threshold for a given tile specified by index based on probability density function.
    '''
    if idx < len(thresholds) and idx > 0:
        t = thresholds[idx]
        for sigma in range(len(BOUNDARIES)):
            yield t[sigma]

def get_global_thres(thresholds):
    '''
    Get global thresholds based on local probability density function using 5/95 quantiles.
    '''
    for sigma in range(len(BOUNDARIES)):
        glob = list()
        for r in thresholds:
            glob.append(r[sigma])
        if len(glob) > 0:
            glob = np.array(glob).reshape((4, len(thresholds)))
            yield (np.percentile(glob[0, :], MIN_QUANTILE), np.percentile(glob[1, :], MAX_QUANTILE), np.percentile(glob[2, :], MIN_QUANTILE),
                   np.percentile(glob[3, :], MAX_QUANTILE))
