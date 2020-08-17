# -*- coding: utf-8 -*-

"""
/***************************************************************************
 AgriculturePrecision
                                 A QGIS plugin
 Chaines de traitement
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-07-21
        copyright            : (C) 2020 by ASPEXIT
        email                : cleroux@aspexit.com
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

__author__ = 'ASPEXIT'
__date__ = '2020-07-21'
__copyright__ = '(C) 2020 by ASPEXIT'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

#import QColor

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsVectorLayer,
                       QgsDataProvider,
                       QgsVectorDataProvider,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingUtils,
                       NULL,
                       QgsMessageLog)

from qgis import processing 

import numpy as np
import pandas as pd

class IndiceZonage(QgsProcessingAlgorithm):
    """
    
    """

    OUTPUT= 'OUTPUT'
    INPUT_POINTS = 'INPUT_POINTS'
    INPUT_ZONES = 'INPUT_ZONES'
    FIELD_ID = 'FIELD_ID'
    FIELD = 'FIELD'
    BOOLEAN = 'BOOLEAN'
  

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_POINTS,
                self.tr('Vecteur points'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_ZONES,
                self.tr('Vecteur zones'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        self.addParameter( 
            QgsProcessingParameterField( 
                self.FIELD_ID,
                self.tr( "Champ identifiant des zones" ), 
                QVariant(),
                self.INPUT_ZONES
            ) 
        )
        
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.BOOLEAN,
                self.tr('Calculer sur tous les champs numériques')
            )
        )
        
        self.addParameter( 
            QgsProcessingParameterField( 
                self.FIELD, 
                self.tr( "Champ dont on veut l'indice" ), 
                QVariant(),
                self.INPUT_POINTS,
                type=QgsProcessingParameterField.Numeric
            ) 
        )
        
        
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Fichier contenant les indices'),
                '.csv',
            )
        )
        
        

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        
        layer_points=self.parameterAsVectorLayer(parameters,self.INPUT_POINTS,context) 
        csv = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        zone_id = self.parameterAsString(parameters, self.FIELD_ID, context)
        choosed_field = self.parameterAsString(parameters, self.FIELD, context)
      
         # Joindre les attributs par localisation
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['INPUT_POINTS'],
            'JOIN': parameters['INPUT_ZONES'],
            'JOIN_FIELDS': 'DN',
            'METHOD': 1,
            'PREDICATE': [5],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_result = processing.run('qgis:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        points_et_zones = QgsProcessingUtils.mapLayerFromString(alg_result['OUTPUT'],context)
       
        features = points_et_zones.getFeatures()
              
        if parameters[self.BOOLEAN] :
            #liste contenant les noms des champs (uniquement numériques)
            field_list=[field.name() for field in points_et_zones.fields() if field.type() in [4,6] or field.name() == zone_id] 
            # 4 integer64, 6 Real
        else :
            field_list =[choosed_field, zone_id]
      
        #on créé une matrice ou 1 ligne = 1 feature
        data = np.array([[feat[field_name] for field_name in field_list] for feat in features])
                
        #on créer le dataframe avec les données et les noms des colonnes
        df = pd.DataFrame(data, columns = field_list)
        
        #Remplacer les valeur NULL (Qvariant) en Nan de panda dataframe
        df = df.where(df!=NULL)
        
        #Mettre toutes les valeurs du dataframe en réel
        df = df.astype(float)# !!! ne va pas marcher si l'identifiant de parcelle n'est pas un chiffre 
        
        #compte du nombre de points (non NaN) dans chaque zone
        nb_points_zones = df.groupby([zone_id]).count()
        nb_points_list = nb_points_zones.values.tolist()
        #avoir la variance pour chaque zone 
        df = df.groupby([zone_id]).var()
        df_list = df.values.tolist()
        
        nb_points = len(df)
        nb_columns=len(df_list[0])
        
        area_weighted_variance = [0 for k in range(nb_columns)]
        #calcul de la variance pour chaque zone et pour chaque champ
        k = 0
        for variance in df_list :
            for i in range(nb_columns):
                prop_variance = variance[i]*(nb_points_list[k][i]/nb_points)
                area_weighted_variance[i] += prop_variance
            k+=1
        #calcul de la variance totale
        var_df = df.var()
        var_df_list = var_df.values.tolist()
        
        #calcul de l'indice RV pour chaque champ 
        RV = []
        for k in range(len(var_df_list)):
            if var_df_list[k] !=0 :
                RV.append(1- (area_weighted_variance[k]/var_df_list[k]))
            else :
                RV.append(NULL)
            
        
        #création du fichier csv qui va contenir les données de RV
        with open(csv, 'w') as output_file:
          # write header
          line = ','.join(name for name in field_list if name != zone_id) + '\n'
          output_file.write(line)
          line = ','.join(str(rv) for rv in RV) + '\n'
          output_file.write(line)
         
        
        
        return{self.OUTPUT : csv} 

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Indice de Zonage'

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
        return self.tr('Action sur Vecteurs')

    def shortHelpString(self):
        short_help = self.tr(
            'Permet de détecter les données aberrantes (outliers) pour un champ donné (une colonne) d’une '
            'couche vecteur à l’aide de plusieurs méthodes de filtrage. Les données aberrantes peuvent être '
            'soit supprimées, soit identifiées dans une nouvelle colonne dans la couche vecteur. '
            ' 3 sigmas : Sous l’hypothèse d’une distribution normale des données, la fonction identifie '
            'les données dans les intervalles (moyenne +/- 1 écart type ; moyenne +/- 2 écarts type ; '
            'moyenne +/- 3 écarts type ; '
            ' Interquartile : aussi connue sous le nom de la règle de Tukey. '
        ) 
        return short_help


    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'action_sur_vecteur'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return IndiceZonage()
