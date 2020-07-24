# -*- coding: utf-8 -*-
"""
Created on Mon July 21 2020
@author: Lisa R
"""

import numpy as np

def rep_quantiles (nombre_classes, array, output) :
    """ En focntion d'un nombre de classes donnée, retourne une matrice séparée en classes selon la méthodes des quantiles"""
    array_ignored_nan = array[array >= array.min()]
    pas = 100/nombre_classes
    for k in range (nombre_classes):
        percentile = np.percentile(array_ignored_nan, k*pas)
        output = np.where((array > percentile), k+1, output) 
    return output
    
    
def intervalles_egaux (nombre_classes, array, output):
    """ En focntion d'un nombre de classes données, retourne une matrice séparée en classes selon la méthodes des quantiles"""
    n_min = array.min()
    number_range=array.max()-n_min
    pas = number_range/nombre_classes
    for k in range (nombre_classes):
        output = np.where((array> (n_min + k*pas)),k+1, output)
    return output
        
     