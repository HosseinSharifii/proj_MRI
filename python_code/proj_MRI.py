# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 21:34:31 2021

@author: Hossein Sharifi
"""
import os 
import json
import sys 
import calendar as cal
from datetime import datetime, timedelta

import pandas as pd
import numpy as np 


def project_MRI_scanning(instruction_str=""):
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
        from redcap import Project
        
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
        if not 'sheet_name' in local_data_info:
            local_data_info['sheet_name'] = 'Sheet 1'

        data_file_str = local_data_info['data_file_str']
        print(f'local data is reading from {data_file_str}')
        if data_file_str.split('.')[-1]=='csv':
            df = pd.read_csv(data_file_str)
        elif data_file_str.split('.')[-1]=='xlsx':
            df = pd.read_excel(data_file_str,sheet_name=local_data_info['sheet_name'])
   
    if 'keywords' in instruction and 'animals_col_name' in instruction['keywords']:
        df=df.reset_index()
        index_name = instruction['keywords']['animals_col_name']
        df = df.set_index(index_name)

    if not 'animals_to_pick' in instruction:
        instruction['animals_to_pick'] = ['all']

    # slice data according to the selected animals
    sliced_data=\
        df.loc[((df['redcap_repeat_instrument'].isnull())|(df['redcap_repeat_instrument']=='mri'))]
    for c in ['mouse_date_of_birth', 'mri_date']:
        sliced_data[c] = pd.to_datetime(sliced_data[c]).dt.date

    if instruction['animals_to_pick'][0] != 'all':
        sliced_data = sliced_data.loc[instruction['animals_to_pick']]
    
    print(sliced_data.head())
    
    #build the counter for calander

    # first build up arrays for months, name of weekdays, and determine
    # the indicies of scan days starting from 0 for Monday
    months = np.array(cal.month_name)
    weekdays = np.array(cal.day_abbr)
    if not 'scan_days' in instruction:
        instruction['scan_days'] = weekdays[0:4]

    sd_index = np.zeros(len(instruction['scan_days']))
    for i,sd in enumerate(instruction['scan_days']):
        index, = np.where(weekdays == sd)[0]
        sd_index[i] = index
  
    # now generate counters for scan days in the calendar
    cal_count_dict = dict()
    for i,m in enumerate(months[1:13]):
        #print((i,m))
        n_of_weeks = len(cal.monthcalendar(2021,i+1))
        cal_count_dict[m]=np.zeros((n_of_weeks,7))
        
        for w in np.arange(len(cal_count_dict[m])):
            for d in np.arange(len(cal_count_dict[m][w])):
                if d in sd_index and cal.monthcalendar(2021,i+1)[w][d]!=0:
                    cal_count_dict[m][w][d] = instruction['max_animals_per_day']

    # generate output dataframe 
    output_df = sliced_data.loc[sliced_data['redcap_repeat_instrument'].isna()]
    output_df = output_df[['mouse_date_of_birth']]
    output_df['ref_date'] = pd.Series()
    
    """for k in cal_count_dict.keys():
        m = np.where(months==k)[-1][-1]
        print(cal.prmonth(2021,m))
        print('')
        print(cal_count_dict[k])"""
    # start working with the projection
    # determine the existing data frame cols for scan dates
    scan_cols = np.zeros(instruction['max_scan_reps'])
    for sr in range(instruction['max_scan_reps']):
        scan_date_name = f'Scan {sr+1}'
        if scan_date_name in sliced_data.columns:
            scan_cols[sr] = 1
    # determine last time of scanning otherwise pick dob as the reference date 
    # for calculating the projection
    
    for id in sliced_data.index.unique():
        print('id is',id)
        if 'mri' in np.array(sliced_data['redcap_repeat_instrument'].loc[id]):

            last_scan_rep = sliced_data['redcap_repeat_instance'].loc[id].max()
            output_df['ref_date'].loc[id] = \
                sliced_data['mri_date'].loc[(sliced_data['redcap_repeat_instance']==last_scan_rep)&\
                    (sliced_data.index==id)].to_list()[0]
            remained_scans = instruction['max_scan_reps'] - last_scan_rep
        else:
            output_df['ref_date'].loc[id] = sliced_data['mouse_date_of_birth'].loc[id]
            remained_scans = instruction['max_scan_reps']

        
        while remained_scans>0:
            proj_number = str(int(instruction['max_scan_reps']-remained_scans+1))
            if output_df['ref_date'].loc[id] == output_df['mouse_date_of_birth'].loc[id]:
                next_scan_date = output_df['ref_date'].loc[id]+\
                    timedelta(days = instruction['initial_scan_age_weeks']*7)
                next_scan_date_col = 'projection_1'
                
            
            else:
                next_scan_date = output_df['ref_date'].loc[id]+\
                    timedelta(days = instruction['frequency_in_days'])
                next_scan_date_col = 'projection_' + proj_number
                    

            if not next_scan_date_col in output_df.columns:
                #print(f'col {next_scan_date_col} is added to dataframe')
                output_df[next_scan_date_col] = pd.Series()

            remained_scans -= 1

            selected_date = -1
            while selected_date < 0:
                
                y = next_scan_date.year
                m = next_scan_date.month
                d = next_scan_date.day
                w = get_week_of_month(y,m,d)

                d_index = cal.weekday(y,m,d)
                month = months[m]
                
                if cal_count_dict[month][w][d_index]>0:
                    output_df[next_scan_date_col].loc[id] = next_scan_date
                    selected_date += 1
                    cal_count_dict[month][w][d_index] -= 1
                    output_df['ref_date'].loc[id] = next_scan_date
                    print(f'Projection {proj_number}: {next_scan_date}', flush=True)
                    
                
                else:
                    next_scan_date += timedelta(days=1)
    # now remove the ref_date col from the output data frame 
    output_df = output_df.drop(columns='ref_date')
    if 'projected_data_str' in instruction:
        output_file_str = instruction['projected_data_str']
        format = output_file_str.split('/')[-1].split('.')[-1]
        if format == 'xlsx':
            output_df.to_excel(output_file_str)
        elif format == 'csv':
            output_df.to_csv(output_file_str)
        print(f'Projection spread sheet is saved to {output_file_str}')
    #out_df = sliced_data[['record_id','mouse_date_of_birth','redcap_repeat_instrument','ref_date']]

    



    

    #start checking when was the last time 
    
def get_week_of_month(year, month, day):
    x = np.array(cal.monthcalendar(year, month))
    week_of_month = np.where(x==day)[0][0] 

    return week_of_month

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
    
  