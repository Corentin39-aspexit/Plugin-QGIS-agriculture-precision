# -*- coding: utf-8 -*-
"""
Created on Mon July 21 2020
@author: Lisa Rollier - ASPEXIT
"""
   
def pixel_resolution(layer, pixel):
    """ permet d'obtenir la résolution en pixels du raster 
    que l'on veut en sortie à partir de la taille du 
    pixel que l'on veut"""
    ex = layer.extent()
    xlength = ex.xMaximum() - ex.xMinimum()
    ylength = ex.yMaximum() - ex.yMinimum()
    resolution_x=abs(xlength/pixel)
    resolution_y=abs(ylength/pixel)
    return resolution_x,resolution_y