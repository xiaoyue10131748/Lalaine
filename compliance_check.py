
from analyzeUtils.append_privacy_Label_incorr_inade import append_privacy_Label_incorr_inade
from analyzeUtils.append_privacy_Label_omit import append_privacy_Label_omit
from analyzeUtils.analyzeByAPI import match_by_API
from analyzeUtils.analyzeByKey import match_by_KEY
from purpose_prediction.purpose_analyze import generate_analyze_file
from purpose_prediction.purpose_analyze import generate_omit_file

from purpose_prediction.preprocess_incorr_inade_1 import *
from purpose_prediction.preprocess_omit_2 import *
from purpose_prediction.problems_3 import *

from network_parser import parse_raw_network
import glob


def complaince_check(root,folder):
    predict_file_incorr_inade=root+"/result/"+folder+"/"+"prediction_total_with_send_tag_incorr_inade_"+folder+".xlsx"
    predict_file_omit=root+"/result/"+folder+"/"+"prediction_total_with_send_tag_prediction_omit_"+folder+".xlsx"
    #find_inconsistency
    final_inconsistency_file=root+"/result/"+folder+"/"+"inconsistency.xlsx"
    step_one(predict_file_incorr_inade)
    step_two(predict_file_omit)
    step_three(final_inconsistency_file)


#def compliance_check():


if __name__ == '__main__':
    folder = sys.argv[1]
    root = sys.argv[2]
    complaince_check(root,folder)