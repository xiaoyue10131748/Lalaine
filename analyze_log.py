import json
from haralyzer import HarParser, HarPage
import datetime
import os
import xlsxwriter
import pandas as pd
import sys
import openpyxl
from analyzeUtils.append_privacy_Label_incorr_inade import append_privacy_Label_incorr_inade
from analyzeUtils.append_privacy_Label_omit import append_privacy_Label_omit
from analyzeUtils.analyzeByAPI import match_by_API
from analyzeUtils.analyzeByKey import match_by_KEY
from purpose_prediction.purpose_analyze import generate_analyze_file
from purpose_prediction.purpose_analyze import generate_omit_file
from purpose_prediction.purpose_analyze import prepare_analyze_file
from purpose_prediction.purpose_analyze import prepare_omit_file
from purpose_prediction.PurposeIdentifier import predict_purpose
from purpose_prediction.preprocess_incorr_inade_1 import *
from purpose_prediction.preprocess_omit_2 import *
from purpose_prediction.problems_3 import *

from network_parser import parse_raw_network
import glob

root=""
RETRAIN=True


def merge(merge_root, total_file, folder_num):
    file_list=[]
    # specifying the path to csv files
    for folder in range(int(folder_num),int(folder_num)+1):
        #path = "/Volumes/Seagate/Privacy_Label/batch_dynamic_test/result/"+str(folder)+"/analyze_output/mapping_result"
        path1 =merge_root+str(folder)+"/analyze_output/mapping_result"
        path2 = merge_root + str(folder) + "/analyze_output/key_mapping_result"

        # csv files in the path
        file_list.extend( glob.glob(path1 + "/*.xlsx"))
        file_list.extend(glob.glob(path2 + "/*.xlsx"))

    excl_list = []

    for file in file_list:
        excl_list.append(pd.read_excel(file))

    excl_merged = pd.DataFrame()

    for excl_file in excl_list:
        # appends the data into the excl_merged
        # dataframe.
        excl_merged = excl_merged.append(
            excl_file, ignore_index=True)

    writer = pd.ExcelWriter(total_file, engine='xlsxwriter', options={'strings_to_urls': False})
    excl_merged.to_excel(writer)
    writer.close()



def generate_analyze_result(root,folder):
    #parse raw network from har
    har_path="/Users/xiaoyue-admin/Documents/Fiddler2/Captures/har"
    parse_raw_network(root, folder, har_path)

    #map call trace with network traffic
    match_by_API(root, folder)
    match_by_KEY(root, folder)
    total_file=root+"/result/"+folder+"/"+folder+".xlsx"
    merge(root+"/result/", total_file, folder)

    #append privacy label in apple store
    alignment_path = root + "/result/" + folder + "/alignment_output/"
    if not os.path.exists(alignment_path):
        os.makedirs(alignment_path)
    output_file_incorr_inade=alignment_path+"total_with_send_tag_"+folder+".xlsx"
    append_privacy_Label_incorr_inade(total_file, output_file_incorr_inade)

    output_file_omit=alignment_path+"total_with_send_tag_neglect"+folder+".xlsx"
    append_privacy_Label_omit(total_file,output_file_omit)

    prediction_path = root + "/result/" + folder + "/prediction_output/"
    if not os.path.exists(prediction_path):
        os.makedirs(prediction_path)



    predict_file_incorr_inade = prediction_path + "prediction_total_with_send_tag_incorr_inade_" + folder + ".xlsx"
    df=prepare_analyze_file(output_file_incorr_inade)
    feature_src=prediction_path+"feature_extraction_incorr_inade_"+ folder + ".csv"
    df.to_csv(feature_src, index=False)
    #feature_dst=prediction_path+"purpose_prediction_incorr_inade_"+ folder + ".csv"
    predict_purpose(feature_src,predict_file_incorr_inade,RETRAIN)


    predict_file_omit = prediction_path+ "prediction_total_with_send_tag_prediction_omit_" + folder + ".xlsx"
    df2 = prepare_omit_file(output_file_omit)
    feature_src2 = prediction_path + "feature_extraction_omit_" + folder + ".csv"
    df2.to_csv(feature_src2, index=False)
    # feature_dst=prediction_path+"purpose_prediction_incorr_inade_"+ folder + ".csv"
    predict_purpose(feature_src2, predict_file_omit,RETRAIN)





    #find_inconsistency
    '''
    final_inconsistency_file=root+"/result/"+folder+"/"+"inconsistency.xlsx"
    step_one(predict_file_incorr_inade)
    step_two(predict_file_omit)
    step_three(final_inconsistency_file)
    '''

#def compliance_check():


if __name__ == '__main__':
    folder = sys.argv[1]
    root = sys.argv[2]
    generate_analyze_result(root,folder)
