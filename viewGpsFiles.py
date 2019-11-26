#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 19:08:42 2019

@author: Raphaël Chalicarne
"""
# %% IMPORTS

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import mplleaflet
import os
import re
import gpxpy
import gpxpy.gpx
import xml.etree.ElementTree as ET
from geopy import distance
from datetime import datetime

import plotly 
import plotly.graph_objs as go 
import plotly.io as pio
pio.renderers.default = "browser"

#dir = os.path.join('Vélo','OruxMaps_2019-11-18 1906-livraison-Stuart')
#filename = '18-11-19-livraison-Stuart.kml'
dir = os.path.join('Vélo','OruxMaps_2019-11-20 1801-Centrale-Maison')
filename = '20-11-19-Centrale-maison.kml'
#dir = os.path.join('Vélo','RaidECL_2018_J1')
#filename = 'EnsembleJ1.gpx'

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

def calculateSpeed(coordinates, timestamp):
    n = len(timestamp)
    speed_ms = np.zeros(n-1)
    
    for i in range(1,n):
        point0 = (coordinates[i-1,0], coordinates[i-1,1])
        point1 = (coordinates[i,0], coordinates[i,1])
        time0 = datetime.strptime(timestamp[i-1], '%Y-%m-%dT%H:%M:%S%z')
        time1 = datetime.strptime(timestamp[i], '%Y-%m-%dT%H:%M:%S%z')
        delta_t = (time1 - time0).total_seconds()
        dist = distance.distance(point0, point1).m
        speed_delta = dist/delta_t
        speed_ms[i-1] = speed_delta
        
    return speed_ms

# %% Using ElementTree (kml files)
if path_show_ext(file)[2] == '.kml':
    tree = ET.parse(file)
    
    root = tree.getroot()
    tag_link = root.tag
    # We delete every character that comes after '{' in the tag link.
    link = re.sub(r'}.*$', "", tag_link)
    
    Folders = tree.findall('.//' + link + '}Folder')
    
    lastName = ''
    timestamp = []
    long_lat_alt = []
    
    for attributes in Folders:
        #print('Attributes : ', attributes.tag)
        for subAttributes in attributes:
            #print(subAttributes.tag, subAttributes.text)
            if (subAttributes.tag == link + '}name'):
                lastName = subAttributes.text
            if (subAttributes.tag == link + '}Placemark') and (lastName == 'Tracks'):
                #On est dans le Placemark correspondant à 'Tracks'
                for subSubAttributes in subAttributes:
                    #print(subSubAttributes.tag)
                    if (subSubAttributes.tag == '{http://www.google.com/kml/ext/2.2}Track'):
                        for sssubAttributes in subSubAttributes:
                            if sssubAttributes.tag == '{http://earth.google.com/kml/2.2}when':
                                timestamp.append(sssubAttributes.text)
                            elif sssubAttributes.tag == '{http://www.google.com/kml/ext/2.2}coord':
                                long_lat_alt.append(sssubAttributes.text)
    long_lat_alt = [line.split(' ') for line in long_lat_alt]
    splitted_array = np.array(long_lat_alt, dtype=str)
    coordinates = splitted_array.astype(np.float)

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

plt.plot(longitude, latitude, color='r', linewidth=4)
mplleaflet.show()

# %% Showing track with plotly
longitude = coordinates[:,0]
latitude = coordinates[:,1]
altitude = coordinates[:,2]

track = go.Scattermapbox(
                  mode = "markers+lines",
                  lon = longitude,
                  lat = latitude,
                  marker = {'size': 10})

layout_track = go.Layout(title='Mon trajet à vélo', 
                              xaxis=dict(title='Longitude',), 
                              yaxis=dict(title='Latitude',)) 
#plotly.offline.plot(go.Figure(data=track , layout=layout_track), 
#                   filename="temp.html", auto_open=True)
go.Figure(data=track , layout=layout_track).show(renderer="browser")

# %%
fig = go.Figure(go.Scattermapbox(
    mode = "markers+lines",
    lon = [10, 20, 30],
    lat = [10, 20,30],
    marker = {'size': 10}))

fig.add_trace(go.Scattermapbox(
    mode = "markers+lines",
    lon = [-50, -60,40],
    lat = [30, 10, -20],
    marker = {'size': 10}))

fig.update_layout(
    margin ={'l':0,'t':0,'b':0,'r':0},
    mapbox = {
        'center': {'lon': 10, 'lat': 10},
        'style': "stamen-terrain",
        'center': {'lon': -20, 'lat': -20},
        'zoom': 1})

fig.show()


# %% Show speed if it exists

if len(timestamp) > 0:
    speed_kmh = 3.6*np.array(calculateSpeed(coordinates, timestamp))

# Create a set of line segments so that we can color them individually
# This creates the points as a N x 1 x 2 array so that we can stack points
# together easily to get the segments. The segments array for line collection
# needs to be (numlines) x (points per line) x 2 (for x and y)
points = np.array([longitude, latitude]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)

# Create a continuous norm to map from data points to colors
norm = plt.Normalize(0, speed_kmh.max())
lc = LineCollection(segments, cmap='rainbow', norm=norm)
# Set the values used for colormapping
lc.set_array(speed_kmh)
lc.set_linewidth(2)
line = axs[0].add_collection(lc)
fig.colorbar(line, ax=axs[0])

#plt.plot(longitude, latitude, color='rainbow', linewidth=4)
#plt.show()










