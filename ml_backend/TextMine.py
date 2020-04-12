#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 18:19:49 2020

@author: anibaljt
"""

from elsapy.elsclient import ElsClient
from elsapy.elssearch import ElsSearch
import json
import inspect
import numpy as np
import os
import MLTechniques
from .TextProcess import TEXTPROCESS
import requests
import copy


class TEXTMINE:
    
    
    SUP_TECHNICAL_KEYWORDS = ["supervised","learning","classification" ]
    
    UNS_TECHNICAL_KEYWORDS = ["unsupervised","learning","clustering"]
    
    
    def __init__(self,user_keywords,user_id,analysis_type='supervised'):
        
        self.user_keywords = user_keywords
        self.user_id = user_id
        self.analysis_type = analysis_type

        
    def from_database(self):
        
        if self.analysis_type == 'supervised':
            tech_words = TEXTMINE.SUP_TECHNICAL_KEYWORDS
            
        elif self.analysis_type == 'unsupervised': 
             tech_words = TEXTMINE.UNS_TECHNICAL_KEYWORDS


        con_file = open("config.json")
        config = json.load(con_file)
        con_file.close()
        client = ElsClient(config['apikey'])
        ###TODO: add year back in??
        searchwords = {'general':[],'specific':[],'names':[]}

        for name, obj in inspect.getmembers(MLTechniques):
            if inspect.isclass(obj):
                if obj.TECHNIQUE_TYPE == self.analysis_type:
                        searchwords['names'].append(obj.get_name())
                        searchwords['specific'].append(obj.get_category())

        print(searchwords['specific'])
        textmine_results = {'words':[],'scores':[],'allwords':[]}


        combos = self.generate_combinations(self.user_keywords,tech_words)
        print("-----UNKNOWN DATA DETECTED: INITIATING TEXT MINING-----")
        print()
        allurls = []
        
        for n,combo in enumerate(combos[0:5]):
             print("SEARCH QUERY " + str(n+1) + ":")
             print(combo)
             print()
            
             string = ""
             for word in combo:
                 string += (word + " ") 

             doc_srch = ElsSearch(string, 'sciencedirect')
             results = TEXTMINE.execute_modified(doc_srch.uri,client,get_all=True,set_limit=25)
             
             if results != 0:
               print("SUCCESSFUL QUERY")
               for num,res in enumerate(results):
                 
                 DOI = res['prism:doi']
                 URL = 'https://api.elsevier.com/content/article/DOI/' + str(DOI) + "?APIkey=" + str(config['apikey'])
                 if URL not in allurls:
                     r = requests.get(URL)
                     allurls.append(URL)
                        
                     with open(str(self.user_id),'w') as f:
                        f.write(r.text)
                     f.close()
                 
                     foundwords,allwords,numlines = TEXTPROCESS.findkeywords(str(self.user_id),searchwords,str(self.user_keywords))
                     textmine_results['words'].extend(list(foundwords.keys()))
                     textmine_results['scores'].extend(list(foundwords.values()))
                     textmine_results['allwords'].extend(allwords)
                     os.remove(str(self.user_id))
                 
        print("------MINING COMPLETE: SEARCHING FOR KEYWORDS-----")
        keywords,keyword_scores = self.adjust_output(textmine_results)
        
        return self.two_list_sort(keywords,keyword_scores),keyword_scores,searchwords
        

    def generate_combinations(self,l1,l2):
        
        l3 = []
        for tup in l1:
           for word in l2:
               t = copy.deepcopy(tup)
               t += (word,)
               l3.append(t)
        return l3
    
    
    ### TODO: CITE ELSAPY - I MODIFIED THE SRC FOR MLAI 
    def execute_modified(uri,els_client = None, get_all = False,set_limit=25):

        api_response = els_client.exec_request(uri)
        
        if api_response['search-results']['opensearch:totalResults'] is None:
                return 0
        
        results = api_response['search-results']['entry']
        
        if get_all is True:
           i = 0
           while i<(int(set_limit/25)-1):
            for e in api_response['search-results']['link']:
                    if e['@ref'] == 'next':
                        next_url = e['@href']
            api_response = els_client.exec_request(next_url)
            results += api_response['search-results']['entry']
            i += 1
    
        return results
    
               
                                
    def two_list_sort(self,tosort,basis):
      for i in range(1, len(basis)):
        key = basis[i]
        key2 = tosort[i]
        j = i-1
        while j >=0 and key <basis[j] : 
                basis[j+1] = basis[j] 
                tosort[j+1] = tosort[j]
                j -= 1
                
        basis[j+1] = key 
        tosort[j+1] = key2
        
      return tosort
    
    
     
    def adjust_output(self,words):

      scores = []

      wordkeys = list(set(words['words']))
      
      for word in wordkeys:
          score = np.median(np.asarray(words['scores'])[np.where(np.asarray(words['words']) == word)])
          scores.append(score * (words['allwords'].count(word)/len(words['allwords'])))

      return wordkeys,list(np.asarray(scores)/np.sum(scores))