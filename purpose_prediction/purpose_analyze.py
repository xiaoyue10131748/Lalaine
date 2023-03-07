import os
import sys
import json
import pandas as pd
from purpose_prediction.utils_predict import predict_line
from purpose_prediction.utils_traffic import ParsedURL, ParsedHeader, ParsedBody


TEST_FLAG = False
BUNDLE_ID2INFO_PATH = './data/id2info.json'
CRUNCHBASE_PATH = './data/collected_info_0531.xlsx'

'''
COLUMNS = ['app', 'company', 'bundle_id', 'app_category', 'subdomain', 'domain', 'suffix', 'path',
           'url_arg_keys', 'domain_category', 'QH_keys', 'QB_type', 'QB_len',  'QB_keys',
           'SH_keys', 'SB_type', 'SB_len',  'SB_keys', 'purpose']
'''
COLUMNS = ['app', 'company', 'bundle_id', 'app_category', 'subdomain', 'domain', 'suffix', 'path',
           'url_arg_keys', 'domain_category', 'QH_keys', 'QB_type', 'QB_len',  'QB_keys',
           'SH_keys', 'SB_type', 'SB_len',  'SB_keys', 'caller_class', 'caller_method',
           'API_class', 'API_method', 'API_freq', 'purpose']


def get_domain2categories(path: str = CRUNCHBASE_PATH) -> dict:
    df = pd.read_excel(path, engine='openpyxl')
    res = {}
    for i in range(len(df)):
        domain = df.loc[i, 'domain']
        if not isinstance(domain, str):
            continue
        categories = df.loc[i, 'categories']
        if not isinstance(categories, str):
            continue
        res[domain] = categories.split(',')
    print('{} domains loaded'.format(len(res)))
    return res


def extract_features_from_file(path: str, is_groundtruth: bool = False, predict: bool = False, saved_columns: list = []) -> pd.DataFrame:
    df = pd.read_excel(path, engine='openpyxl')
    print('{} has {} rows'.format(path, len(df)))
    print('Droping duplicates')
    df = df.drop_duplicates(subset=[
                            'request_header_list', 'requestBody_list', 'response_header_list', 'responseBody_list'], keep='first')
    df.reset_index(drop=True, inplace=True)
    print('{} has {} rows'.format(path, len(df)))

    res = pd.DataFrame(columns=COLUMNS)

    id2name_company = json.load(open(BUNDLE_ID2INFO_PATH))
    domain2categories = get_domain2categories()

    if predict:
        predict_stat = {}

    count = 0
    for i in range(len(df)):
        if i % 100 == 0:
            print('Analyzing {}/{}'.format(i, len(df)))
        url = df.loc[i, 'url_list']
        if not isinstance(url, str):
            continue
        data = df.loc[i, 'return_list']
        if not isinstance(data, str):
            continue

        if is_groundtruth:
            purpose = df.loc[i, 'purpose']
            if not isinstance(purpose, str):
                continue
            res.loc[count, 'purpose'] = purpose

        bundle_id = df.loc[i, 'bundle_id_list']
        if bundle_id in id2name_company:
            res.loc[count, 'app'] = id2name_company[bundle_id]['name']
            res.loc[count, 'company'] = id2name_company[bundle_id]['company']
            res.loc[count, 'app_category'] = id2name_company[bundle_id]['category']
        res.loc[count, 'bundle_id'] = bundle_id

        domain = ParsedURL(url)
        res.loc[count, 'domain'] = domain.domain
        res.loc[count, 'suffix'] = domain.suffix
        res.loc[count, 'subdomain'] = domain.subdomain
        res.loc[count, 'path'] = domain.path
        res.loc[count, 'url_arg_keys'] = ','.join(domain.arg_keys)
        if domain.domain in domain2categories:
            res.loc[count, 'domain_category'] = ','.join(
                domain2categories[domain.domain])

        request_header = ParsedHeader(df.loc[i, 'request_header_list'])
        request_body = ParsedBody(df.loc[i, 'requestBody_list'])

        res.loc[count, 'QH_keys'] = ','.join(
            request_header.featured_keys)
        res.loc[count, 'QB_type'] = request_header.content_type
        qh_len = request_header.content_length
        if not qh_len:
            qh_len = request_body.size
        res.loc[count, 'QB_len'] = qh_len
        res.loc[count, 'QB_keys'] = ','.join(request_body.keys)

        # log
        res.loc[count, 'request_header_list'] = str(request_header.kv)
        res.loc[count, 'requestBody_list'] = str(request_body.body)

        response_header = ParsedHeader(df.loc[i, 'response_header_list'])
        response_body = ParsedBody(df.loc[i, 'responseBody_list'])

        res.loc[count, 'SH_keys'] = ','.join(
            response_header.featured_keys)
        res.loc[count, 'SB_type'] = response_header.content_type
        sh_len = response_header.content_length
        if not sh_len:
            sh_len = response_body.size
        res.loc[count, 'SB_len'] = sh_len
        res.loc[count, 'SB_keys'] = ','.join(response_body.keys)

        # log
        res.loc[count, 'response_header_list'] = str(response_header.kv)
        res.loc[count, 'responseBody_list'] = str(response_body.body)

        # res.loc[count, 'API_class'] = df.loc[i, 'className_list']
        # res.loc[count, 'API_method'] = df.loc[i, 'API_list']
        # res.loc[count, 'API_freq'] = df.loc[i, 'invoke_list']

        # saved columns
        for col in saved_columns:
            res.loc[count, col] = df.loc[i, col]

        if predict:
            purpose, reason = predict_line(res.loc[count, :])
            res.loc[count, 'purpose'] = purpose
            res.loc[count, 'reason'] = reason
            if purpose in predict_stat:
                predict_stat[purpose] += 1
            else:
                predict_stat[purpose] = 1
        count += 1

    if predict:
        print(predict_stat)
    return res


def extract_features_from_batch(dirs: list) -> pd.DataFrame:
    res = pd.DataFrame(columns=COLUMNS)
    for dir in dirs:
        for subdir in os.listdir(dir):
            if subdir.startswith('.'):
                continue
            mapping_dir = os.path.join(
                dir, subdir, 'analyze_output', 'mapping_result')
            if not os.path.exists(mapping_dir):
                print('{} does not exist'.format(mapping_dir))
                continue
            for file in os.listdir(mapping_dir):
                if file.startswith('.') or file.startswith('~'):
                    continue
                file_path = os.path.join(mapping_dir, file)
                print('processing {}'.format(file_path))
                df = extract_features_from_file(file_path)
                if df.empty:
                    continue
                res = pd.concat([res, df])
                if TEST_FLAG:
                    # only select one app from each folder
                    break
    return res


def generate_groundtruth_file(src: str = './traffic/all_yue_jiale.xlsx', dst: str = 'train_yue.xlsx'):
    df = extract_features_from_file(src, is_groundtruth=True)
    # df = df.drop_duplicates(subset=GROUNDTRUTH_COLUMNS)
    # df = df.drop_duplicates(subset=['request_header_list', 'requestBody_list',
    #                         'response_header_list', 'responseBody_list'], keep='first')
    df.to_excel(dst, index=False)
    # df.to_csv(dst+'.csv', index=False)
    # df.to_excel(dst+'.xlsx', index=False)
    print('File {} generated'.format(dst))


def generate_analyze_file(src: str = './analyze/total_with_send_data_tag.xlsx', dst: str = './analyze/total_test.xlsx'):
    # df = pd.DataFrame(columns=COLUMNS)
    df = extract_features_from_file(src, is_groundtruth=False, saved_columns=[
                                    'bundle_id_list',
                                    'className_list', 'API_list', 'return_list', 'invoke_list', 'url_list',
                                    'request_header_list', 'requestBody_list', 'response_header_list',
                                    'responseBody_list', 'note_list', 'matchRule', 'keyData',
                                    'app_url_list', 'app_true_label', 'send_data_tag'], predict=True)
    # df = df.drop_duplicates(subset=['request_header_list', 'requestBody_list',
    # 'response_header_list', 'responseBody_list'], keep='first')
    # df.to_excel(dst, index=False)
    # df = pd.DataFrame(columns=COLUMNS)
    writer = pd.ExcelWriter(dst, engine='xlsxwriter', engine_kwargs={
                            'options': {'strings_to_urls': False}})
    df.to_excel(writer, index=False)
    writer.save()

    # df.to_csv(dst+'.csv', index=False)
    # df.to_excel(dst+'.xlsx', index=False)
    print('File {} generated'.format(dst))


def generate_omit_file(src: str = './analyze/omitDisclosure.xlsx', dst: str = './analyze/omit_test.xlsx'):
    # omit_data_list
    df = extract_features_from_file(src, is_groundtruth=False, saved_columns=[
                                    'app_true_label', 'omit_data_list'], predict=True)
    # df.to_excel(dst, index=False)
    writer = pd.ExcelWriter(dst, engine='xlsxwriter', engine_kwargs={
                            'options': {'strings_to_urls': False}})
    df.to_excel(writer, index=False)
    writer.save()

    print('File {} generated'.format(dst))


def generate_new_predict_file(src: str = './train_test.xlsx', dst: str = './train_test_anno.xlsx'):
    df = extract_features_from_file(src, predict=True)

    df = df.sort_values(by=['domain'])
    df.to_excel(dst, index=False)
    print('File {} generated'.format(dst))


def generate_batch_file(src_list: list = ['./frida/jiale', './frida/feifan', '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/',
                                          '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result2/'], dst: str = 'predit_data1.xlsx'):
    if TEST_FLAG:
        src_list = [src_list[0]]
    df = extract_features_from_batch(src_list)
    # df = df.drop_duplicates(subset=BATCH_COLUMNS)
    df = df.drop_duplicates(subset=['request_header_list', 'requestBody_list',
                            'response_header_list', 'responseBody_list'], keep='first')
    # df.to_csv(file_name+'.csv', index=False)
    df.to_excel(dst, index=False)


def get_id_and_keys(file_name: str) -> tuple:
    df = pd.read_excel(file_name)
    keys = set()
    if df.empty:
        return None, None
    for i in range(len(df)):
        id = df.loc[i, 'bundle_id_list']
        request_keys = ParsedBody(df.loc[i, 'requestBody_list']).keys()
        response_keys = ParsedBody(df.loc[i, 'responseBody_list']).keys()
        for key in request_keys:
            # if not unicode
            if not isinstance(key, str):
                continue
            keys.add(key)
        for key in response_keys:
            if not isinstance(key, str):
                continue
            keys.add(key)

    return id, keys


def get_body_key_desc(src_list: list = ['./frida/jiale', './frida/feifan', '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/',
                                        '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result2/', ], dst: str = 'keys_desc.xlsx'):
    if TEST_FLAG:
        src_list = [src_list[0]]

    res = {}
    for src in src_list:
        for dir in os.listdir(src):
            if dir.startswith('.'):
                continue
            mapping_dir = os.path.join(
                src, dir, 'analyze_output', 'mapping_result')
            if not os.path.exists(mapping_dir):
                print('{} does not exist'.format(mapping_dir))
                continue
            for file in os.listdir(mapping_dir):
                if file.startswith('.') or file.startswith('~'):
                    continue
                file_path = os.path.join(mapping_dir, file)
                print('processing {}'.format(file_path))
                id, keys = get_id_and_keys(file_path)
                if not id:
                    continue
                for key in keys:
                    if key not in res:
                        res[key] = set()
                    res[key].add(id)

    df = pd.DataFrame(columns=['body_key', 'bundle_id_len'])
    for key in res:
        df.loc[len(df)] = [key, len(res[key])]
    df = df.sort_values(by=['bundle_id_len'], ascending=False)
    df.to_excel(dst, index=False, encoding='utf-8', engine='xlsxwriter')
    print('File {} generated'.format(dst))


if __name__ == "__main__":
    # open xlsx
    if len(sys.argv) > 1:
        TEST_FLAG = True

    # preprocessed files
    # run preprocess_apple.py first

    #generate_groundtruth_file()
    # generate_batch_file()

    # generate_new_predict_file()
    # get_body_key_desc()
    # generate_analyze_file(src='./analyze/total_with_send_data_tag.xlsx', dst='./analyze/total_test.xlsx')
    #generate_analyze_file(src='./analyze/zixiaoResult_total_with_send_data_tag.xlsx', dst='./analyze/zixiao_test_all_info.xlsx')
    #generate_omit_file(src='./analyze/zixiaoResult_omitDisclosure.xlsx',dst='./analyze/zixiao_omit_test.xlsx')
    # generate_analyze_file()
    #generate_omit_file()
    #generate_omit_file(src='/Volumes/Seagate/Privacy_Label/measurement_study/result/omitAppsResult_total_with_send_data_tag_negelect.xlsx', dst='./analyze/omitAppsResult_total_with_send_data_tag_negelect_with_purpose.xlsx')
    generate_analyze_file(src='/Volumes/Seagate/Privacy_Label/measurement_study/result/omitAppsResult_total_with_send_data_tag.xlsx', dst='./analyze/omitAppsResult_total_with_purpose.xlsx')

