import glob
import fnmatch
import pathlib
import os
import json
import pandas as pd
import datetime
from pandas import json_normalize

DATA_FILENAME_PATTERN = 'part-*'
DATA_FOLDER = 'data/'
pathname = DATA_FOLDER + DATA_FILENAME_PATTERN

def listFilePaths():
    input_files = glob.glob(pathname)
    return(input_files)

def processRecords(filepaths): 
    records = [] 
    for filepath in filepaths:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                raw_record = json.loads(line)
                records.append(raw_record)
    normalized_records = json_normalize(records)
    normalized_records.columns = normalized_records.columns.str.strip()
    normalized_records = normalized_records.fillna(0).astype({"custom_params.changeInDistance":float, "custom_params.percentage":float, "custom_params.screenSize": float, "custom_params.time":float, "custom_params.timeToSelect":float})
    normalized_records["ts"] = pd.to_datetime(normalized_records["ts"], unit='ms')
    normalized_records["submit_time"] = pd.to_datetime(normalized_records["submit_time"] , unit='ms')

    return(normalized_records.drop(columns=['appid', 'city', 'country','debug_device','platform','sdk_ver','type','user_agent']))

def retrieveDataFrame():
    return(processRecords(listFilePaths()))


if __name__ == '__main__':
    print(retrieveDataFrame())