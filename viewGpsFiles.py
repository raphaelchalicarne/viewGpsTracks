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
from fastkml import kml
import xml.etree.ElementTree as ET

dir = os.path.join('Vélo','OruxMaps_2019-11-20 1801-Centrale-Maison')
kml_file = os.path.join(dir,'20-11-19-Centrale-maison.kml')

# %% Functions
def llaf2array(llaf):
    """Input : long_lat_alt_filtered
    Output : numpy array with [long, lat, alt] at each line"""
    splitted_array = [line.split(',') for line in llaf]
    splitted_array = np.array(splitted_array, dtype=str)
    array2float = splitted_array.astype(np.float)
    return array2float

# %% Fast kml

#Read file into string and convert to UTF-8 (Python3 style)
with open(kml_file, 'rt') as myfile:
    doc = myfile.read().encode('utf-8')
    

# Create the KML object to store the parsed result
k = kml.KML()

# Read in the KML string
k.from_string(doc)

# Check that the number of features is correct
# This corresponds to the single ``Document``
features = list(k.features())

f2 = list(features[0].features())
f3_0 = list(f2[0].features())

# %% Using ElementTree

tree = ET.parse(kml_file)

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


