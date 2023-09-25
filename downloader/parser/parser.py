import json
import sys, os
import logging
import argparse
import time
import re
from bs4 import BeautifulSoup, SoupStrainer
import queue

from multiprocessing.pool import Pool, ThreadPool
from functools import partial
import threading
import collections

global_overall_start_time = time.time()

class Global_Config():
  def __init__(
    self,
    input_file,
    result_dir,
    result_file,
    error_file,
    thread_num,
  ):
    self.input_file = input_file
    self.result_dir = result_dir
    self.result_file = result_file
    self.error_file = error_file
    self.thread_num = thread_num
    self.result_queue = queue.Queue()
    self.is_stop = False
    self.dump_count = 0
    self.error_line = 0

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def write_json(row, result_file):
  fp = open(result_file, 'a')
  #fp.write(json.dumps(row, indent = 4)+'\n')
  fp.write(json.dumps(row)+'\n')
  fp.flush()
  fp.close()


def chinese_to_english(privacy_type):
  string_privacy_type = str(privacy_type)
  for key, value in ch2en_dict.items():
    string_privacy_type = re.sub("\'{}\'".format(key), "\'{}\'".format(value), string_privacy_type)
  #print(string_privacy_type)
  import ast
  ch2en_privacy_type = ast.literal_eval(string_privacy_type)
  return ch2en_privacy_type


def read_file(
    gc,
):
  line_count = 0
  number_error_line = 0
  fp = open(gc.input_file, 'r')
  print("inputfile", gc.input_file)
  app_data_list = list()
  for line in fp:
    line_count+=1
    if line_count>=180000:
      continue
    try:
      row = json.loads(line)
      if row["appid"] in gc.finished_appid_set:
        continue
      app_data_list.append(line)
    except Exception as e:
      number_error_line+=1
  fp.close()
  print("total line:", line_count)
  print("number of error line in html:", number_error_line)
  return app_data_list
  """
  count=0
  while True:
    line=fp.readline()
    count+=1
    #if count!=32229:
        #continue
    row,flag=parse(line)
    #return
    if flag:
        write_json(row, output_file)
    print(count)
    #break
    #if not line:
        #break
  """
  
def get_app_rating(soup):
    #div = soup.findAll("div", {"class": "we-customer-ratings__averages"})
    cont = soup.select_one("div.we-customer-ratings__averages")

    try:
        ram = cont.select_one("span")
        #print(ram.text)
        return ram.text.strip()
    except Exception:
        return ""

def get_app_num_rating(soup):
    try:
        num_rating = soup.select_one("div.we-customer-ratings__count")
        num_rating = num_rating.text.strip('Ratings').strip()
        return num_rating
    except Exception:
        return ""

def parse(
    gc,
    line
):
    contain_ch_sign = False
    error_sign = False
    privacy_type={}
    data = json.loads(line)
    #print(data["appid"])
    #privacy_type["bundleid"]=data["bundleid"]
    privacy_type["appid"]=data["appid"]
    #if not data["appid"] in gc.finished_appid_set:
    try:
      privacy_type["appname"]=data["appname"]
    except KeyError:
      privacy_type["appname"] = ''
    try:
      privacy_type["country"]=data["country"]
    except KeyError:
      privacy_type["country"] = ''
    privacy_type["url"]=data["url"]
    #print(data["url"])
    privacy_type["language"]=data["language"]
    try:
      privacy_type["timestamp"]=data["timestamp"]
    except KeyError:
      pass
    try:
      try:
        soup = BeautifulSoup(data["privacy_response"],'html.parser')
      except KeyError:
        error_sign = True
        gc.error_line+=1
      if not error_sign:
        privacy_type['app_rating'] = get_app_rating(soup)
        privacy_type['app_num_rating'] = get_app_num_rating(soup)
        #parse privacy tag

        privacy_modals=soup.findAll("div", {"class": "app-privacy__modal-section"})

        for index,div in enumerate(privacy_modals):

            if index ==0:
                p=div.find("p")
                for a in p.find_all('a', href=True):
                    privacy_type["privacy link"]= a['href']
                privacy_type["developer desciprion"]=p.text.strip()
                continue

            h2=div.find("h2", {"class":"privacy-type__heading"})

            """
            if h2 and is_contains_chinese(h2.text):
                contain_ch_sign = True
                #privacy_type['response'] = data["response"]
                #privacy_type['error'] = 'contain chinese'
                #write_json(privacy_type, gc.error_file)
                break
            """

            if privacy_type["language"] == 'english':
              purpose_text = "Data Used to Track You"
            if privacy_type["language"] == 'chinese':
              purpose_text = "用于追踪您的数据"

            if h2 and h2.text ==purpose_text:
                #print(h2.text)
                grids = div.findAll("div", {"class": "privacy-type__grid-content"})
                data_type = {}
                for i, grid in enumerate(grids):

                    h3 = grid.find("h3", {"class": "privacy-type__data-category-heading"})
                    # Usage Data
                    #print("\t\t\t\t" + h3.text)
                    ul = grid.find("ul", {"class": "privacy-type__category-items"})
                    data_items = []
                    for litag in ul.findAll('li'):
                        #print("\t\t\t\t\t" + litag.text.strip())
                        data_items.append(litag.text.strip())
                    data_type[h3.text.strip()] = data_items
                privacy_type[h2.text] = data_type
                continue


            if h2:
                category={}
                #Data Linked to You:category{}
                #print(h2.text)

                grids=div.findAll("div", {"class":"privacy-type__grid-content"})
                prev_purpose=""
                for i, grid in enumerate(grids):
                    p=grid.previous_element

                    while p.name!="h3":
                            p=p.previous_element
                    purpose=p.text.strip()

                    #App Functionality
                    #print("\t\t\t" + purpose)
                    if prev_purpose!=purpose:
                        data_purpose=[]
                        prev_purpose=purpose

                    h4=grid.find("h4", {"class":"privacy-type__data-category-heading"})
                    #Usage Data
                    #print("\t\t\t\t" + h4.text)
                    ul=grid.find("ul",{"class":"privacy-type__category-items"})
                    data_items=[]
                    for litag in ul.findAll('li'):
                            #print("\t\t\t\t\t" + litag.text.strip())
                            data_items.append(litag.text.strip())
                    data_type={}
                    data_type[h4.text.strip()]=data_items
                    data_purpose.append(data_type)
                    category[purpose]=data_purpose

                privacy_type[h2.text]=category
        #json_object = json.dumps(privacy_type, indent = 4)
        #if not contain_ch_sign:
        #    gc.result_queue.put(privacy_type)
        #print(json_object)
        #return privacy_type,True

        ### parse info
        information_sec = soup.find('section', class_='section--information').find('dl', class_='information-list')
        #print(information_sec, '\n')
        divs = information_sec.find_all('div', class_='information-list__item')
        privacy_type['info'] = dict()
        for div in divs:
          #print(index, div, "\n")
          item = div.find('dt').get_text().strip()
          compatibility_subs = div.find('dd').find_all('dl')
          if compatibility_subs:
            privacy_type['info'][item] = dict()
            for compatibility_sub in compatibility_subs:
              sub_item = compatibility_sub.find('dt').get_text().strip()
              sub_item_content = compatibility_sub.find('dd').get_text().strip()
              privacy_type['info'][item][sub_item] = sub_item_content
          else:
            item_content = div.find('dd').get_text().strip()
            privacy_type['info'][item] = item_content
      
        #print(privacy_type)

        ### parse version
        try:
          if data["version_response"]:
            privacy_type['version'] = list()
            soup = BeautifulSoup(data["version_response"],'html.parser')
            lis = soup.find('ul', class_='version-history__items').find_all('li')
            for li in lis:
              each_version = dict()
              each_version['version_num'] = li.find('h4').get_text().strip()
              each_version['date'] = li.find('time').get_text().strip()
              each_version['info'] = re.sub(r'\s+', ' ', li.find('div').get_text().strip().rstrip('more').strip())
              privacy_type['version'].append(each_version)

          if privacy_type["language"] == 'chinese':
            #print(privacy_type,"\n")
            privacy_type = chinese_to_english(privacy_type)
          gc.result_queue.put(privacy_type)
        except KeyError:
          gc.error_line+=1
          
    except Exception as e:
        data['error'] = e
        write_json(data, gc.error_file)     

def parse_policy(
  gc,
  line,
):
    contain_ch_sign = False
    privacy_type={}
    data = json.loads(line)
    #print(data["appid"])
    privacy_type["bundleid"]=data["bundleid"]
    privacy_type["appid"]=data["appid"]
    #if not data["appid"] in gc.finished_appid_set:
    privacy_type["appname"]=data["appname"]
    privacy_type["country"]=data["country"]
    privacy_type["url"]=data["url"]
    #print(data["url"])
    privacy_type["language"]=data["language"]
    privacy_type["timestamp"]=data["timestamp"]
    try:
      privacy_type['response_code']=data['response_code']
    except KeyError:
      pass
    privacy_type['privacy link'] = data['privacy link']
    try:
        soup = BeautifulSoup(data['response_text'],'html.parser')
        text = re.sub('\s+', ' ', soup.get_text())
        privacy_type['policy_text'] = text.strip()
        gc.result_queue.put(privacy_type)
    except Exception as e:
        data['error'] = str(e)
        write_json(data, gc.error_file)

def multithread_parse(
    gc,
):
    app_data_list = read_file(gc)
    logging.warning("total number of app: %d", len(app_data_list))

    logging.warning('start parsing')
    pool = ThreadPool(thread_num)
    if target == 'appstore':
      _parse_func = partial(parse, gc)
      pool.map(_parse_func, app_data_list)
    if target == 'policy':
      _parse_func = partial(parse_policy, gc)
      pool.map(_parse_func, app_data_list)      
    pool.close()
    pool.join()
    logging.warning("finish all threads")
    gc.is_stop = True

def save_results(
    gc,
):
    logging.warning('start saving')
    while True:
      try:
        if gc.is_stop:
          time.sleep(10)
          if gc.result_queue.empty():
            logging.warning('it is time to quit')
            break
        if gc.result_queue.empty():
          time.sleep(2)
          continue
        item = gc.result_queue.get(block=False,)
        write_json(item, gc.result_file)
        gc.dump_count += 1
      except Exception as e:
        logging.warning('got exception in saving %s', e)

def alive_message(
  gc,
):
  alive_interval = 60
  while True:
    try:
      time.sleep(alive_interval)
      logging.warning(
          '%d tasks completed, %d error line, time cost is %d minutes', 
          gc.dump_count,
          gc.error_line,
          (time.time() - global_overall_start_time)//60,
      )
    except AttributeError:
      continue
    if gc.is_stop:
      break

def check_finished(
  gc,
):
  gc.finished_appid_set = set()
  number_error_line = 0
  if os.path.isfile(result_file):
    with open(result_file, 'r') as fp:
      for line in fp:
        try:
          line = json.loads(line.strip())
          gc.finished_appid_set.add(line['appid'])
        except Exception:
          number_error_line+=1
          continue
  if os.path.isfile(error_file):
    with open(error_file, 'r') as fp:
      for line in fp:
        try:
          line = json.loads(line.strip())
          gc.finished_appid_set.add(line['appid'])
        except Exception:
          number_error_line+=1
          continue
  logging.warning("already finished %d", len(gc.finished_appid_set))
  print("number of error line in finished file:", number_error_line)

if __name__ == "__main__":
  format_str = '%(asctime)s - %(levelname)s - %(message)s -%(funcName)s'
  logging.basicConfig(level=logging.WARNING, format=format_str)
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', type=str)
  parser.add_argument('--result_dir', type=str)
  parser.add_argument('--result_filename', type=str)
  #parser.add_argument('--start_index', type=int)
  #parser.add_argument('--end_index', type=int)
  parser.add_argument('--target', type=str,
                      choices=['appstore', 'policy',],)
  parser.add_argument('--ch2en_dictionary_file', type=str)
  parser.add_argument('--thread_num', type=int, default=10)
  options = parser.parse_args()
  input_file = options.input_file
  result_dir = options.result_dir
  result_filename = options.result_filename
  target = options.target
  ch2en_dictionary_file = options.ch2en_dictionary_file
  #start_index = options.start_index
  #end_index = options.end_index
  thread_num = options.thread_num

  if not os.path.exists(result_dir):
    os.makedirs(result_dir)

  if target == 'appstore':
    result_file = os.path.join(result_dir, result_filename+'_parse.json')
    error_file = os.path.join(result_dir, result_filename+'_parse_error.json')
  else:
    print("no such target")
    sys.exit(0)
  #if target == 'policy':
  #  result_file = os.path.join(result_dir, result_filename+'_policy_parse.json')
  #  error_file = os.path.join(result_dir, result_filename+'_policy_parse_error.json')    
  
  gc = Global_Config(input_file, result_dir, result_file, error_file, thread_num,)
  check_finished(gc)

  if ch2en_dictionary_file:
    fp = open(ch2en_dictionary_file, 'r')
    ch2en_dict = json.load(fp)
    fp.close()
  
  message_thread = threading.Thread(target=alive_message, args=(gc,))
  message_thread.start()
  sthread = threading.Thread(target=save_results, args=(gc,))
  sthread.start()
  multithread_parse(gc)
  message_thread.join()
  sthread.join()

  #app_data_list = read_file(gc)
  #parse(gc, app_data_list[0])

  logging.warning(
      '%d tasks completed, time cost is %d minutes, %d hours, %d seconds', 
      gc.dump_count,
      (time.time() - global_overall_start_time)//60,
      (time.time() - global_overall_start_time)//3600,
      (time.time() - global_overall_start_time),
  )
  
 
