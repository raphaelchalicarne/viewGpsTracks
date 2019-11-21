#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 19:08:42 2019

@author: Raphaël Chalicarne
"""
# %% IMPORTS

import matplotlib.pyplot as plt
import numpy as np
import mplleaflet
import os
import re
import gpxpy
import gpxpy.gpx
import xml.etree.ElementTree as ET

#dir = os.path.join('Vélo','OruxMaps_2019-11-18 1906-livraison-Stuart')
#filename = '18-11-19-livraison-Stuart.kml'
#dir = os.path.join('Vélo','OruxMaps_2019-11-20 1801-Centrale-Maison')
#filename = '20-11-19-Centrale-maison.kml'
dir = os.path.join('Vélo','RaidECL_2018_J1')
filename = 'EnsembleJ1.gpx'

file = os.path.join(dir,filename)

# %% Functions

def path_show_ext(fullpath):
    """
    splits a full file path into path, basename and extension
    :param fullpath: str
    :return: the path, the basename and the extension
    """
    tmp = os.path.splitext(fullpath)
    ext = tmp[1]
    p = tmp[0]
    while tmp[1] != '':
        tmp = os.path.splitext(p)
        ext = tmp[1] + ext
        p = tmp[0]

    path = os.path.dirname(p)
    if path == '':
        path = '.'
    base = os.path.basename(p)
    return path, base, ext

def llaf2array(llaf):
    """Input : long_lat_alt_filtered
    Output : numpy array with [long, lat, alt] at each line"""
    splitted_array = [line.split(',') for line in llaf]
    splitted_array = np.array(splitted_array, dtype=str)
    array2float = splitted_array.astype(np.float)
    return array2float

# %% Using ElementTree (kml files)
if path_show_ext(file)[2] == '.kml':
    tree = ET.parse(file)
    
    root = tree.getroot()
    tag_link = root.tag
    # We delete every character that comes after '{' in the tag link.
    link = re.sub(r'}.*$', "", tag_link)
    
    lineStrings = tree.findall('.//' + link + '}LineString')
    
    for attributes in lineStrings:
        for subAttribute in attributes:
            if subAttribute.tag == link + '}coordinates':
                raw_long_lat_alt = subAttribute.text
    
    # We split the string into an array of lines
    long_lat_alt = raw_long_lat_alt.splitlines()
    # We remove the empty lines (containing no digits)
    long_lat_alt_filtered = [line for line in long_lat_alt if re.search(r'\d+',line)]
    # We convert it into an array where each line is [long, lat, alt].
    coordinates = llaf2array(long_lat_alt_filtered)

# %% Using gpxpy (gpx files)
if path_show_ext(file)[2] == '.gpx':
    
    gpx_file = open(file, 'r')
    gpx = gpxpy.parse(gpx_file)
    
    coordinates = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append([point.longitude, point.latitude, point.elevation])
    
    coordinates = np.array(coordinates)

# %% Showing track on OSM with leaflet

longitude = coordinates[:,0]
latitude = coordinates[:,1]
altitude = coordinates[:,2]

plt.plot(longitude, latitude, color = 'r', linewidth=4)
mplleaflet.show()
