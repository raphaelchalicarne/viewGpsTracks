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

dir = os.path.join('Centrale Lyon','Vélo','OruxMaps_2019-11-20 1801-Centrale-Maison')
filename = os.path.join(dir,'20-11-19-Centrale-maison.kml')
