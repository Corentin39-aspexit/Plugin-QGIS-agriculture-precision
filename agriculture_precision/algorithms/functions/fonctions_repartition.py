# -*- coding: utf-8 -*-
"""
Created on Mon July 21 2020
@author: Lisa R
"""

import numpy as np

def rep_quantiles (nombre_classes, array, output) :
    """ En fonction d'un nombre de classes donnée, retourne une matrice 
    séparée en classes selon la méthodes des quantiles"""
    array_ignored_nan = array[array >= array.min()]
    pas = 100/nombre_classes
    for k in range (nombre_classes):
        percentile = np.percentile(array_ignored_nan, k*pas)
        output = np.where((array >= percentile), k+1, output) 
    return output
    
    
def intervalles_egaux (nombre_classes, array, output):
    """ En fonction d'un nombre de classes données, retourne une matrice 
    séparée en classes selon la méthodes des intervalles égaux"""
    n_min = array.min()
    number_range=array.max()-n_min
    pas = number_range/nombre_classes
    for k in range (nombre_classes):
        output = np.where((array>= (n_min + k*pas)),k+1, output)
    return output
 
''' 
def jenks_breaks (nombre_classes,array,output):
    """ En fonction d'un nombre de classes données, retourne une matrice 
    séparée en classes selon la méthodes des intervalles égaux"""
    #trouver les jenks breaks
    mat = array[:]
    mat.np.sort()
    list_sorted_values = mat.tolist()
    
    #définition temporaires des breaks (intervalles égaux)
    n_min = array.min()
    number_range=array.max()-n_min
    pas = number_range/nombre_classes
    breaks = []
    for k in range (nombre_classes):
        breaks.append(n_min+k*pas)
    
    
    #trouver à quelle place sont les éléments "breaks" dans la 
    #matrice triée 
    breaks_places=[]
    k=0
    while k < nombre_classes :
        for i in range (len(list_sorted_values)-1):
            if list_sorted_values[i+1]>breaks[k]:
                breaks_places.append(i)
                k+=1
    breaks_places.append(len(list_sorted_values)-1)    
    
    #calcul des SDCM
    SDCM = []
    for i in breaks_places:
        for k in range(i+1):
            
    
    #On va ensuite comparer chaque groupe et regarder si en décalant un element
    #vers "le groupe de droite" ou celui de gauche c'est plus petit (recursivité)
    
    for k in range (nombre_classes) :
        
'''  
    

        
        
        
        
        