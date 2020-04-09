#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author: anibaljt

"""


from .Technique import Technique

class MeanShift(Technique):
    
    
    GENERAL_USE = False
    
    TECHNIQUE_TYPE = "unsupervised"
    
    def __init__(self):
        self.model = None
 
    def get_class_name():
        return 'MeanShift'
    
    def get_name():
        return 'mean shift'

    def get_category():
        return 'density'

    def preprocess(self,data):
        pass
        
    def train(self,data,time_constraint):
        pass

    def predict(self,data,labels,model):
        pass
    
    def set_model(self,model):
        self.model = model
    
    
    def get_model(self):
        return self.model