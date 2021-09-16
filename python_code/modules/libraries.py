# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 21:34:31 2021

@author: Hossein Sharifi
"""
import os
import pandas as pd
import numpy as np 
import calendar as cal

from datetime import date, timedelta


def pull_data(pull_data_dict):

    """
    Pull data to start make the scanning projection.

    Parameters
    ----------
    pull_data_dict : dict, 
        A dictionary of inputs that are required to pull data.

    Returns
    -------
    sliced_data : data spread sheet 
        A format of data that is ready to be used for scanning projection.
  
    """

# handle data
    if not 'data_source' in pull_data_dict:
        pull_data_dict['data_source']='redcap'

    if pull_data_dict['data_source']=='redcap':
        if not 'redcap' in pull_data_dict:
            print('"redcap" information is not defined.')
            return

        redcap_info = pull_data_dict['redcap']
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

        
    elif pull_data_dict['data_source']=='local_data':
        if not 'local_data' in pull_data_dict:
            print('"local_data" information is not defined.')
            return
        local_data_info = pull_data_dict['local_data']
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
   
    if 'animals_col_name' in pull_data_dict:
        df=df.reset_index()
        index_name = pull_data_dict['animals_col_name']
        df = df.set_index(index_name)

    if not 'animals_to_pick' in pull_data_dict:
        pull_data_dict['animals_to_pick'] = ['all']

    if 'export_redcap_raw_data' in pull_data_dict:
        save_output_file(df,pull_data_dict['export_redcap_raw_data'])
    # slice data according to the selected animals
    sliced_data=\
        df.loc[((df['redcap_repeat_instrument'].isnull())|(df['redcap_repeat_instrument']=='mri'))]
    for c in ['mouse_date_of_birth', 'mri_date']:
        sliced_data[c] = pd.to_datetime(sliced_data[c]).dt.date

    if pull_data_dict['animals_to_pick'][0] != 'all':
        sliced_data = sliced_data.loc[pull_data_dict['animals_to_pick']]

    return sliced_data

def generate_counter_calendar(scan_days, animal_rep_per_session):
     """
    Generate a calendar of counters based on 
    scanning days and number of animals per session.

    Parameters
    ----------
    scan_days : list 
        An array of weekdays that scanning can be obtained.
    animal_rep_per_session : int
        Maximum number of animals to scan at each session of scanning. 
    Returns
    -------
    count_cal_dict : dict
        A dictionary yof counters that based on calendar.
  
    """
    months = np.array(cal.month_name)
    weekdays = np.array(cal.day_abbr)
    sd_index = np.zeros(len(scan_days))
    for i,sd in enumerate(scan_days):
        index, = np.where(weekdays == sd)[0]
        sd_index[i] = index
  
    # now generate counters for scan days in the calendar
    count_cal_dict = dict()
    # first get the current date and start generating the calendar for  
    # this year + 2 years later
    today = date.today()
    start_year = today.year 
    for y in range(start_year,start_year+3):
        count_cal_dict[y]=dict()
        print(f'year:{y} and type is {type(y)}')
    
        for i,m in enumerate(months[1:13]):
            #print((i,m))
            n_of_weeks = len(cal.monthcalendar(y,i+1))
            count_cal_dict[y][m]=np.zeros((n_of_weeks,7))
            
            for w in np.arange(len(count_cal_dict[y][m])):
                for d in np.arange(len(count_cal_dict[y][m][w])):
                    if d in sd_index and cal.monthcalendar(y,i+1)[w][d]!=0:
                        count_cal_dict[y][m][w][d] = animal_rep_per_session
    
    return count_cal_dict

def save_output_file(data_frame,output_file_str):

    # Make sure the path exists
    output_dir = os.path.dirname(output_file_str)
    print('output_dir %s' % output_dir)
    if not os.path.isdir(output_dir):
        print('Making output dir')
        os.makedirs(output_dir)

    format = output_file_str.split('/')[-1].split('.')[-1]
    if format == 'xlsx':
        data_frame.to_excel(output_file_str)
    elif format == 'csv':
        data_frame.to_csv(output_file_str)

    print(f'Writing data to: {output_file_str}')