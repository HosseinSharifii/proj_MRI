# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 21:34:31 2021

@author: Hossein Sharifi
"""

import json
import sys 

import numpy as np 
import calendar as cal

from modules.libraries import pull_data, generate_counter_calendar
from modules.project_timetable import project_timetable as pt
from modules.project_timetable import find_animals_to_scan as fas

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
    
    if 'projection_data' not in instruction:
        print('Projection info is not provided, \
            hence default values will be used.')
        instruction['projection_data']= dict()
     # handle data
    if 'pull_data' not in instruction:
        print('Informtion for pulling data is not provided.')
        return
    df = pull_data(instruction['pull_data'])
    
    
    # generate counters for calendar
    weekdays = np.array(cal.day_abbr)
    if not 'scan_days' in instruction['projection_data']:
        instruction['projection_data']['scan_days'] = weekdays[0:4]
    
    if not 'max_animals_per_day' in instruction['projection_data']:
        instruction['projection_data']['max_animals_per_day'] = 1

    count_cal_dict = generate_counter_calendar(
            instruction['projection_data']['scan_days'], 
            instruction['projection_data']['max_animals_per_day'])

    # project scan dates
    output_df = pt(df, instruction['projection_data'],
                    count_cal_dict)
    

    if 'animals_to_scan' in instruction: 
        fas(output_df, instruction)

        


if __name__=="__main__":

    no_of_arguments = len(sys.argv)

    if no_of_arguments == 1:
        print('No instruction file has been called!')
        print('Exiting...')
    elif no_of_arguments == 2:
        print('Using the following instruction file to project the MRI scanning...')
        print(sys.argv[1])
        project_MRI_scanning(instruction_str=sys.argv[1])
    
  
    """for y in count_cal_dict.keys():
            for month in count_cal_dict[y].keys():
                m = np.where(months==month)[-1][-1]
                print(cal.prmonth(y,m))
                print('')
                print(count_cal_dict[y][month])"""