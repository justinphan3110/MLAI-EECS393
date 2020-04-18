#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:40:12 2020

@author: anibaljt
"""


from .Technique import Technique
from sklearn.naive_bayes import GaussianNB as GNB 
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler


class NaiveBayes(Technique):
    
    GENERAL_USE = True
    
    TECHNIQUE_TYPE = "supervised"
    
    
    def get_class_name():
        return 'NaiveBayes'
    
    def get_name():
        return 'naive bayes'

    def get_category():
        return 'bayes'
        
    
    def preprocess(data):
        
        if data.data_type == 'image':
            features = StandardScaler().fit_transform(data.data)
            return features
        
        if data.data_type == 'numeric':
            features = StandardScaler().fit_transform(data.data)
            return features

        
        if data.data_type == 'text':
            pass
        
        return -1 
        
    
    def train(data):
 
        X = NaiveBayes.preprocess(data)
        y = np.asarray(data.labels)
        test_labels = []
        test_data = []
        time_constraint = data.time_constraint
        
        if time_constraint == 1:
            
            model = GNB()
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            model.fit(X_train,y_train)
            results = model.predict(X_test)
            test_data = X_test
            test_labels = y_test

        if time_constraint == 2:
            
            for i in range(2):
                model = GNB()
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                model.fit(X_train,y_train)
                results = model.predict(X_test)
                test_data.extend(X_test)
                test_labels.extend(y_test)
                
        if time_constraint > 2:
            
            model = GNB()
            results = []
            cv = StratifiedKFold(n_splits=5,shuffle=True)
            for train, test in cv.split(X,y):
                 model.fit(X[train],y[train])
                 results.extend(model.predict(X[test]))
                 test_data.extend(X[test])
                 test_labels.extend(y[test])
                 
        return test_data,test_labels,results,None
    
    
