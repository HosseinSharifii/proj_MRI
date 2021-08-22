
import pandas as pd 
import numpy as np
import calendar as cal

from datetime import timedelta

def project_timetable(data_frame,
                    instruction,
                    counter_calendar):

    # generate output dataframe 
    df = data_frame
    output_df = df.loc[df['redcap_repeat_instrument'].isna()]
    output_df = output_df[['mouse_date_of_birth']]
    output_df['ref_date'] = pd.Series()
    
    count_cal_dict = counter_calendar
    # determine the last time of scanning 
    # otherwise pick DOB as the reference date 
    # for calculating the projection
    
    for id in df.index.unique():
        print('id is',id)
        if 'mri' in np.array(df['redcap_repeat_instrument'].loc[id]):

            last_scan_rep = df['redcap_repeat_instance'].loc[id].max()
            output_df['ref_date'].loc[id] = \
                df['mri_date'].loc[(df['redcap_repeat_instance']==last_scan_rep)&\
                    (df.index==id)].to_list()[0]
            remained_scans = instruction['max_scan_reps'] - last_scan_rep
        else:
            output_df['ref_date'].loc[id] = df['mouse_date_of_birth'].loc[id]
            remained_scans = instruction['max_scan_reps']

        
        while remained_scans > 0:
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
                month = np.array(cal.month_name)[m]
                
                if count_cal_dict[y][month][w][d_index]>0:
                    output_df[next_scan_date_col].loc[id] = next_scan_date
                    selected_date += 1
                    count_cal_dict[y][month][w][d_index] -= 1
                    output_df['ref_date'].loc[id] = next_scan_date
                    print(f'Projection {proj_number}: {next_scan_date}', flush=True)
                    
                else:
                    next_scan_date += timedelta(days=1)

    # now remove the ref_date col from the output data frame 
    output_df = output_df.drop(columns='ref_date')
    
    if 'output_proj_str' in instruction:
        output_file_str = instruction['output_proj_str']
        format = output_file_str.split('/')[-1].split('.')[-1]
        if format == 'xlsx':
            output_df.to_excel(output_file_str)
        elif format == 'csv':
            output_df.to_csv(output_file_str)
        print(f'Projection spread sheet is saved to {output_file_str}')

    return output_df
    
def get_week_of_month(year, month, day):
    x = np.array(cal.monthcalendar(year, month))
    week_of_month = np.where(x==day)[0][0] 

    return week_of_month