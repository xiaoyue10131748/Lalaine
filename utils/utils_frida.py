import os
import sys
import json
import pandas as pd


SYSTEM_CLASS_PATH = './utils/xcode_def_classnames.txt'
SYSTEM_CLASSES = open(SYSTEM_CLASS_PATH, 'r').read().splitlines()


def find_next_back_trace(lines: list, index: int = 0) -> int:
    for i in range(index, len(lines)):
        if lines[i].lstrip().startswith('Backtrace:'):
            return i
    return -1


def find_next_class_name(lines: list, index: int = 0) -> int:
    for i in range(index, len(lines)):
        if lines[i].lstrip().startswith('[*] Class Name:'):
            return i
    return -1

def find_next_empty_line(lines: list, index: int = 0) -> int:
    for i in range(index, len(lines)):
        if lines[i].strip() == '':
            return i
    return -1


def find_caller(lines: list) -> tuple:
    for line in lines:
        start = line.find('[')
        if start == -1:
            continue
        end = line.find(']')
        if end == -1:
            continue
        caller = line[start+1:end]
        if caller.find(' ') == -1:
            # print('Error: {}'.format(line))
            continue
        class_name = caller.split(' ')[0]
        method_name = caller.split(' ')[1]
        if not class_name:
            continue
        if class_name in SYSTEM_CLASSES:
            continue
        return (class_name, method_name)
    return None


def find_API(part_list: list) -> str:
    for line in part_list:
        if line.startswith('[*] Method Name:'):
            return line.split("[*] Method Name:")[1].strip()
    return None




def extract_caller_from_file(file: str) -> list:
    if not os.path.exists(file):
        return []
    start_index = end_index = 0
    caller_l = []
    f = open(file, 'r')
    try:
        lines = f.read().splitlines()
    except:
        print('Error: {}'.format(file))
        sys.exit(1)

    while True:
        start_index = find_next_back_trace(lines, end_index)
        if start_index == -1:
            break
        end_index = find_next_empty_line(lines, start_index)
        if end_index == -1:
            end_index = len(lines)
        caller = find_caller(lines[start_index+1:end_index])
        if caller:
            caller_l.append(caller)

    return caller_l

#{- coordinate:{Flurry}}
def extract_API_caller_from_file(file: str) -> dict:
    if not os.path.exists(file):
        return {}
    start_index = end_index = 0
    api_caller_dic = {}
    f = open(file, 'r')
    try:
        lines = f.read().splitlines()
    except:
        print('Error: {}'.format(file))
        sys.exit(1)

    while True:

        start_index = find_next_back_trace(lines, end_index)
        if start_index == -1:
            break
        end_index = find_next_empty_line(lines, start_index)
        if end_index == -1:
            end_index = len(lines)
        caller = find_caller(lines[start_index+1:end_index])
        API = find_API(lines[start_index-7:end_index])
        if caller and API:
            if API not in api_caller_dic:
                caller_list=set()
                caller_list.add(caller)
                api_caller_dic[API]=caller_list
            else:
                api_caller_dic[API].add(caller)
    return api_caller_dic




def count_API_caller_from_file(file: str) -> dict:
    if not os.path.exists(file):
        return {}
    start_index = end_index = 0
    api_caller_dic = {}
    f = open(file, 'r')
    try:
        lines = f.read().splitlines()
    except:
        print('Error: {}'.format(file))
        sys.exit(1)

    while True:

        start_index = find_next_back_trace(lines, end_index)
        if start_index == -1:
            break
        end_index = find_next_empty_line(lines, start_index)
        if end_index == -1:
            end_index = len(lines)
        caller = find_caller(lines[start_index+1:end_index])
        API = find_API(lines[start_index-7:end_index])
        if caller and API:
            if API not in api_caller_dic:
                caller_list=[]
                caller_list.append(caller)
                api_caller_dic[API]=caller_list
            else:
                api_caller_dic[API].append(caller)
    return api_caller_dic




def extract_api_caller_dic_from_dir(dir: str) -> dict:
    ret = {}
    for sub_dir in os.listdir(dir):
        # print(sub_dir)
        if not os.path.isdir(os.path.join(dir, sub_dir)):
            continue
        # frida_dir = dir + sub_dir + '/frida_output/'
        frida_dir = os.path.join(dir, sub_dir, 'frida_output')
        # print(frida_dir)
        if not os.path.exists(frida_dir):
            continue
        for file in os.listdir(frida_dir):
            if file.startswith('.'):
                continue
            api_caller_dic = extract_API_caller_from_file(os.path.join(frida_dir, file))
            bundle_id = get_bundle_id(file)
            ret[bundle_id]=api_caller_dic
    return ret



def extract_caller_from_dir(dir: str) -> list:
    caller_l = []
    for sub_dir in os.listdir(dir):
        if not os.path.isdir(os.path.join(dir, sub_dir)):
            continue
        frida_dir = os.path.join(dir, sub_dir, 'frida_output')
        if not os.path.exists(frida_dir):
            continue
        for file in os.listdir(frida_dir):
            if file.startswith('.'):
                continue
            caller_l += extract_caller_from_file(os.path.join(frida_dir, file))
    return caller_l


def get_bundle_id(file: str) -> str:
    return file.split('_')[0]


def extract_class_bundle_id_from_dir(dir: str) -> dict:
    ret = {}
    for sub_dir in os.listdir(dir):
        # print(sub_dir)
        if not os.path.isdir(os.path.join(dir, sub_dir)):
            continue
        # frida_dir = dir + sub_dir + '/frida_output/'
        frida_dir = os.path.join(dir, sub_dir, 'frida_output')
        # print(frida_dir)
        if not os.path.exists(frida_dir):
            continue
        for file in os.listdir(frida_dir):
            if file.startswith('.'):
                continue
            classes = extract_caller_from_file(os.path.join(frida_dir, file))
            for class_name, method_name in classes:
                full_method_name = (class_name, method_name)
                bundle_id = get_bundle_id(file)
                if full_method_name not in ret:
                    ret[full_method_name] = [bundle_id]
                elif bundle_id not in ret[full_method_name]:
                    ret[full_method_name].append(bundle_id)
    return ret


def get_all_classes(dirs: list = ['./frida/jiale', './frida/feifan']) -> list:
    l = []
    for dir in dirs:
        l += extract_caller_from_dir(dir)

    print(l)
    class_names = [i[0] for i in l]
    class_names = list(set(class_names))
    class_names.sort()
    return class_names



def get_all_api_caller_dic_from_dirs(dirs: list = ['./frida/jiale', './frida/feifan']) -> dict:
    dic = {}
    for dir in dirs:
        coming_dic=extract_api_caller_dic_from_dir(dir)
        for k,v in coming_dic.items():
            dic[k]=v
    return dic


def get_all_class2bundle_id(dirs: list = ['./frida/jiale', './frida/feifan']) -> dict:
    dic = {}
    for dir in dirs:
        coming_dic=extract_class_bundle_id_from_dir(dir)

        #extend dic when key exists
        for key, value in dic.items():
            if key in coming_dic.keys():
                value.extend(coming_dic[key])

        #add dic when key not exists
        for k, v in coming_dic.items():
            if k not in dic.keys():
                dic[k]=v
    #remove duplication
    clean_dir={}
    for k, v in dic.items():
        clean_dir[k]=list(set(v))
    return clean_dir


def write_class2bundle_id_to_excel(dic: dict, path: str) -> None:
    df = pd.DataFrame()
    for full_method, bundle_id_list in dic.items():
        df = pd.concat([df, pd.DataFrame({'class': full_method[0], 'method': full_method[1], 'bundle_id_list': [
                       bundle_id_list], 'length': len(bundle_id_list)})])
    df = df.sort_values(by=['class'])
    df.to_excel(path, engine='openpyxl', index=False)


if __name__ == '__main__':
    # JIALE_DIR = './frida/jiale/'
    # FEIFAN_DIR = './frida/feifan/'

    #dirs = ['./frida/jiale', './frida/feifan', '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result', '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result2']
    dirs = ['./frida/jiale', './frida/feifan']
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/appMakerResult")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/JialePost")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/luyixing_unzip")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/minPost")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/xiaoyue_unzip")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/zixiaoResult")

    # classnames = get_all_classes()
    # print(classnames)
    # with open('./frida/class_names.txt', 'w') as f:
    #     f.write('\n'.join(classnames))

    class2bundle_id = get_all_class2bundle_id(dirs)
    write_class2bundle_id_to_excel(class2bundle_id, './frida/caller_list_yue.xlsx')
    # print(class2bundle_id)

