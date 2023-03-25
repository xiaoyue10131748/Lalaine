
from analyzeUtils.append_privacy_Label_incorr_inade import append_privacy_Label_incorr_inade
from analyzeUtils.append_privacy_Label_omit import append_privacy_Label_omit
from analyzeUtils.analyzeByAPI import match_by_API
from analyzeUtils.analyzeByKey import match_by_KEY
from purpose_prediction.purpose_analyze import generate_analyze_file
from purpose_prediction.purpose_analyze import generate_omit_file

from purpose_prediction.preprocess_incorr_inade_1 import *
from purpose_prediction.preprocess_omit_2 import *
from purpose_prediction.problems_3 import *
import pandas as pd
from network_parser import parse_raw_network
import glob
from IPython.display import display
import pandas as pd
import argparse

def complaince_check(root,folder):
    prediction_path = root + "/result/" + folder + "/prediction_output/"
    predict_file_incorr_inade = prediction_path + "prediction_total_with_send_tag_incorr_inade_" + folder + ".xlsx"
    predict_file_omit=prediction_path+"prediction_total_with_send_tag_prediction_omit_"+folder+".xlsx"

    #find_inconsistency
    inconsistency_path =  root + "/result/" + folder + "/inconsistency_output/"
    if not os.path.exists(inconsistency_path):
        os.makedirs(inconsistency_path)

    final_inconsistency_file=inconsistency_path+"inconsistency.xlsx"
    if not os.path.exists(final_inconsistency_file):
        step_one(predict_file_incorr_inade)
        step_two(predict_file_omit)
        step_three(final_inconsistency_file)
    
    df=pd.read_excel(final_inconsistency_file)
    display(df)
    print("Find {} inconsistencies".format(len(df)))

#def compliance_check():


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Please specify the parameters")
    #parser.add_argument("-H", "--Help", help="Example: Help argument", required=False, default="")
    parser.add_argument("-d", "--dic", help="[Required] specify the repo directory, the default is current directory", required=True, default=".")
    parser.add_argument("-n", "--folder", help="[Required] specify which folder your test app in", required=True, default="0")

    argument = parser.parse_args()
    status = False

    if argument.dic:
        print("You have used '-d' or '--dic' with argument: {0}".format(argument.dic))
        status = True
    if argument.folder:
        print("You have used '-n' or '--folder' with argument: {0}".format(argument.folder))
        status = True

    if not status:
        print("Maybe you want to use -d or -n or -m?")

    complaince_check(argument.dic,argument.folder)