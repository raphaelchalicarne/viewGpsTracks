#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 19:08:42 2019

@author: Raphaël Chalicarne
"""
# %% IMPORTS

import matplotlib.pyplot as plt
import mplleaflet
import os
from fastkml import kml
import xml.etree.ElementTree as ET

dir = os.path.join('Vélo','OruxMaps_2019-11-20 1801-Centrale-Maison')
kml_file = os.path.join(dir,'20-11-19-Centrale-maison.kml')

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
#root = tree.getroot()
#tag_link = root.tag
lineStrings = tree.findall('.//{http://earth.google.com/kml/2.2}LineString')

for attributes in lineStrings:
    for subAttribute in attributes:
        if subAttribute.tag == '{http://earth.google.com/kml/2.2}coordinates':
            print(subAttribute.tag, subAttribute.text)




