# -*- coding: utf-8 -*-

"""
/***************************************************************************
 CentroideLisa
                                 A QGIS plugin
 test plugin centroide
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-07-07
        copyright            : (C) 2020 by Lisa R
        email                : dolisaob@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Lisa R'
__date__ = '2020-07-07'
__copyright__ = '(C) 2020 by Lisa R'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

#import QColor

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsRasterLayer,
                       #QgsColorRampShader,
                       #QgsRasterShader,
                       #QgsSingleBandPseudoColorRenderer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

from .functions.fonctions_repartition import *

from qgis import processing 

from osgeo import gdal
import numpy as np
#from PyQt5.QtGui import QColor

class ClassifyRaster(QgsProcessingAlgorithm):
    """
    
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    
    

    OUTPUT= 'OUTPUT'
    INPUT = 'INPUT'
    INPUT_METHOD = 'INPUT_METHOD'
    INPUT_N_CLASS='INPUT_N_CLASS'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # We add the input vector features source. It can have any kind of
        # geometry.
       
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Couche raster a traiter')
            )
        )

       
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_METHOD,
                self.tr('Choix de la méthode de classification'),
                ['Quantiles', 'Intervalles Egaux']#, 'Jenks']                
            )
        )
       
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_N_CLASS, 
                self.tr('Nombre de classes'),
                QgsProcessingParameterNumber.Integer,
                4,
                False,
                2,
                10
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Couche raster classee')
            )
        )
        
        
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        
        layer_temp=self.parameterAsRasterLayer(parameters,self.INPUT,context) #type : QgsRasterLayer
        fn = self.parameterAsOutputLayer(parameters,self.OUTPUT,context)
        method = self.parameterAsEnum(parameters,self.INPUT_METHOD,context)
        nombre_classes=self.parameterAsInt(parameters,self.INPUT_N_CLASS,context)
        
        #self.INPUT c'est le nom de la couche
        ##parameters c'est la liste des paramètres
        #donc parameters[self.INPUT] c'est le paramètre dont le nom est self.INPUT
        #fn contient le str du path du fichier source
        fn_temp = layer_temp.source()
        
        ds_temp = gdal.Open(fn_temp)

        #permet de lire la bande du raster en tant que matrice de numpy. 
        band_temp = ds_temp.GetRasterBand(1)
        array = band_temp.ReadAsArray()

        #extraction de la valeur artificielle des points sans valeur
        nodata_val = band_temp.GetNoDataValue()
        #on va masquer les valeurs de "sans valeur", ce qui va permettre le traitement ensuite
        if nodata_val is not None:
            array = np.ma.masked_equal(array, nodata_val)
            
        
        #on créé la couche raster en calque sur la couche source
        driver_tiff = gdal.GetDriverByName("GTiff")
        ds = driver_tiff.Create(fn, xsize=ds_temp.RasterXSize, \
        ysize = ds_temp.RasterYSize, bands = 1, eType = gdal.GDT_Float32)

        ds.SetGeoTransform(ds_temp.GetGeoTransform())
        ds.SetProjection(ds_temp.GetProjection())
        
        #on récupère la bande en matrice
        output = ds.GetRasterBand(1).ReadAsArray()
        # on rempli cette couche de NaN
        output[:].fill(np.nan)
        
        
        #QUANTILES
        if method == 0:             
            output = rep_quantiles(nombre_classes,array,output)
        #INTERVALLES EGAUX
        elif method == 1 :
            output = intervalles_egaux(nombre_classes,array,output)
       
        #elif method == 2 :'''

        #ajouter les modifications effectuées sur la matrice dans la couche raster
        ds.GetRasterBand(1).WriteArray(output)
        
        
        ## definir les couleurs du raster
        '''#create the color ramp shader
        fnc = QgsColorRampShader()
        fnc.setColorRampType(QgsColorRampShader.Exact)
        min=0.25
        max=1
        

        #define the color palette (here yellow to green)
        lst = [QgsColorRampShader.ColorRampItem(min, QColor(255,255,102)),QgsColorRampShader.ColorRampItem(0.5, QColor (255,204,51)),QgsColorRampShader.ColorRampItem(0.75, QColor(255,153,51)),QgsColorRampShader.ColorRampItem(max, QColor(255,102,0))]
        fnc.setColorRampItemList(lst)

        #assign the color ramp to a QgsRasterShader so it can be used to symbolize a raster layer.
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(fnc)

        #Apply symbology to raster

        rlayer = QgsRasterLayer(fn)
        renderer = QgsSingleBandPseudoColorRenderer(rlayer.dataProvider(), 1, shader)
        rlayer.setRenderer(renderer)
        '''


        return{self.OUTPUT : fn} #donc c'est bien l'adresse ou se trouve l'objet qu'on veut mettre en sortie qu'on doit mettre
   
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "Classification d'un raster"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Action sur Raster')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'action_sur_raster'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ClassifyRaster()
