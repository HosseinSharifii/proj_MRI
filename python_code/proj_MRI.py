# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 21:34:31 2021

@author: Hossein Sharifi
"""
import os 
import json
import sys 

import pandas as pd
import numpy as np 


def project_MRI_scanning(data_str = "",
                            instruction_str="",
                            projection_out_str=""):
    """
    Project a time-table for MRI scanning of mice.

    Parameters
    ----------
    data_file_string : str, optional
        Path to the data file. The default is "".
    instruction_str : str, optional
        Path to the .json instruction file. The default is "".
    projection_out_str : str, optional
        Path where the output projection is saved. The default is "".
    

    Returns
    -------
    proj_data : data spread sheet 
        Data file containing the MRI scanning projection.
  
    """
   
    if not instruction_str:
        instruction = dict()
    else:
        with open (instruction_str,'r') as f:
            instruction = json.load(f)
            
     # handle data
    if not 'data_source' in instruction:
        instruction['data_source']='redcap'

    if instruction['data_source']=='redcap':
        if not 'redcap' in instruction:
            print('"redcap" information is not defined.')
            return

        redcap_info = instruction['redcap']
        if not 'api_key' in redcap_info:
            print('No "api_key" is assigned, exiting...')
            return 
        else:
            api = redcap_info['api_key']

        if not 'url_address' in redcap_info:
            print('No  "url_address" is assigned, exiting...')
            return 
        else: 
            url = redcap_info['url_address']
        
        # call the project from redcap 
        from redcap import Project, RedcapError
        
        project = Project(url, api)
        print('Project is read from RedCap')
        df = project.export_records(format = 'df')
        print('Data is exported from RedCap')

    elif instruction['data_source']=='local_data':
        if not 'local_data' in instruction:
            print('"local_data" information is not defined.')
            return
        local_data_info = instruction['local_data']
        if not 'data_file_str' in local_data_info:
            print('Path to local data is not defined.')
            print('Try to define the path to "data_file_str" key.')
            return
        data_file_str = local_data_info['data_file_str']
        print(f'local data is reading from {data_file_str}')
        if data_file_str.split('.')[-1]=='csv':
            df = pd.read_csv(data_file_str)
        elif data_file_str.split('.')[-1]=='xlsx':
            df = pd.read_excel(data_file_str)
   


    if not 'animals_to_pick' in instruction:
        instruction['animals_to_pick'] = ['all']

    # slice data according to the selected animals
    sliced_data=pd.DataFrame()
  
    if instruction['animals_to_pick'][0] != 'all':
        for ad in instruction['animals_to_pick']:
            sliced_data = \
                sliced_data.append(df.loc[df['animals_ID'] == ad])
    else:
        sliced_data = df
        
    #start checking when was the last time 
    
    print(sliced_data)
if __name__=="__main__":

    no_of_arguments = len(sys.argv)
    print(no_of_arguments)
    print(sys.argv[1])

    if no_of_arguments == 1:
        print('No instruction file has been called!')
        print('Exiting...')
    elif no_of_arguments == 2:
        print('Using the following instruction file to project the MRI scanning...')
        print(sys.argv[1])
        project_MRI_scanning(instruction_str=sys.argv[1])
    
  