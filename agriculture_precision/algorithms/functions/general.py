# -*- coding: utf-8 -*-
"""
Created on Mon July 21 2020
@author: Lisa R
"""

def pixel_size(layer, resolution) :
    """ permet d'obtenir la taille des pixels du raster 
    que l'on veut en sortie à partir de la taille du 
    vecteur de départ et de la résolution que l'on veut"""
    ex = layer.extent()
    xlength = ex.xMaximum() - ex.xMinimum()
    ylength = ex.yMaximum() - ex.yMinimum()
    if ylength>xlength :
        pixel_size = ylength/resolution
    else :
        pixel_size = xlength/resolution
        
    return pixel_size