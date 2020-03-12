from main import process_match, append_list_as_row
import pandas as pd

def retry_failed():
    df = pd.read_csv('data/failed.csv')
    failed_list = df.values.tolist()

    flat_failed_list = [item for sublist in failed_list for item in sublist]

    for match in flat_failed_list:
        try:
            process_match(match, 'data/retried_data.csv', hora = False)
        except:
            append_list_as_row('data/failed_again.csv', [match])

def merge_csv_files(files):
    fout = open("data/merged_data.csv", "a")
    for num in range(len(files)):
        for line in open(files[num]):
             fout.write(line)
    fout.close()

if __name__ == '__main__':
    #files = ['data/2012_data.csv', 'data/2013_data.csv', 'data/2014_data.csv', 'data/2015_data.csv', 'data/2016_data.csv', 'data/2017_data.csv', 'data/2018_data.csv', 'data/2019_data.csv', 'data/retried_data.csv' ]
    #merge_csv_files(files)

    df = pd.read_csv('data/merged_data.csv')
