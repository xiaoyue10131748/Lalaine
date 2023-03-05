from analyze import *
import glob
import pandas as pd


def merge():
    file_list=[]
    # specifying the path to csv files
    for folder in range(0,85):
        path = "/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/"+str(folder)+"/analyze_output/mapping_result"

        # csv files in the path
        file_list.extend( glob.glob(path + "/*.xlsx"))

    # list of excel files we want to merge.
    # pd.read_excel(file_path) reads the excel
    # data into pandas dataframe.
    excl_list = []

    for file in file_list:
        excl_list.append(pd.read_excel(file))

    # create a new dataframe to store the
    # merged excel file.
    excl_merged = pd.DataFrame()

    for excl_file in excl_list:
        # appends the data into the excl_merged
        # dataframe.
        excl_merged = excl_merged.append(
            excl_file, ignore_index=True)

    # exports the dataframe into excel file with
    # specified name.
    excl_merged.to_excel('all_xiaoyue.xlsx', index=False)


def search(className,folder):
    file_list=[]
    # specifying the path to csv files
    
    path = "/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/"+str(folder)+"/frida_output/"

    # csv files in the path
    file_list.extend( glob.glob(path + "/*.txt"))

    for file in file_list:
        flag=False
        f=open(file,"r")
        content=f.readlines()
        f.close()
        for c in content:
            if className in c:
                print(file.split("/")[-1])
                flag=True
                break
        if flag:
            continue



if __name__ == '__main__':
    
    '''
    for folder in range(31,32):
        analyze_one_batch(folder)
    '''

    
    merge()
    # importing the required modules

    
    '''
    className="CLLocation"
    folder=32
    search(className,folder)
    '''
