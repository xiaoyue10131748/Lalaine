import json
import sys, os
import logging
import argparse
import time
import re
#from bs4 import BeautifulSoup, SoupStrainer
import queue

#from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.pool import Pool, ThreadPool
from functools import partial
import threading
import multiprocessing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.proxy import Proxy, ProxyType

from bs4 import BeautifulSoup

global_overall_start_time = time.time()

class Global_Config():
  def __init__(
    self,
    input_file,
    input_dir,
    result_dir,
    result_file,
    error_file,
    interval,
    timeout,
    peroid_stop,
    driver_type,
    driver_path,
    thread_num,
  ):
    self.interval = interval
    self.input_file = input_file
    self.input_dir = input_dir
    self.result_dir = result_dir
    self.result_file = result_file
    self.error_file = error_file
    self.driver_path = driver_path
    self.driver_type = driver_type
    self.thread_num = thread_num
    self.result_queue = queue.Queue()
    self.is_stop = False
    self.timeout = timeout
    self.peroid_stop = peroid_stop
    self.done_count = 0
    self.error_count = 0
    self.dump_count = 0
    self.privacyNoOpen_count = 0
    self.versionNoOpen_count = 0
    self.appPageNoOpen_count = 0
    self.appNoResponse_count = 0
    self.OtherError_count = 0
    self.PROXY = None

def write_json(row, result_file):
  fp = open(result_file, 'a')
  fp.write(json.dumps(row)+'\n')
  fp.flush()
  fp.close()

def set_selenium_driver(
  gc,
):
  if gc.driver_type == 'firefox':
      """
          firefox driver
      """
      opts = FirefoxOptions()
      opts.add_argument("--headless")

      #from selenium.webdriver.firefox.options import Options
      #opts = Options()
      #opts.headless = False
      if gc.PROXY:
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True
        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            "httpProxy": gc.PROXY,
            #"ftpProxy": PROXY,
            "sslProxy": gc.PROXY,
        }
        #driver = webdriver.Firefox(firefoxdriver, options=opts, capabilities=firefox_capabilities)
        #driver.get('https://www.iplocation.net/find-ip-address')
      firefoxdriver = gc.driver_path
      driver = webdriver.Firefox(firefoxdriver, options=opts)#, service_log_path=os.devnull)
  
  if gc.driver_type == 'chrome':
      """
          chrome driver
      """
      options = Options()
      #options.headless = True
      options.add_argument("--headless")
      chromedriver = gc.driver_path
      driver = webdriver.Chrome(chromedriver, options=options)
  #increase timeout to prevent TimedPromise timed out after 5000 ms
  driver.set_page_load_timeout(gc.timeout)
  driver.implicitly_wait(gc.timeout)
  return driver

def crawl_iosStore(
  gc,
  json_item,
):
  #if gc.privacyNoOpen_count >=10:
  #  logging.warning("More than 10 app can't open privacy button")
  if not gc.event.is_set():
    try:
      error_sign = False
      page_not_exist_sign = False
      appid = json_item['appid']
      country = json_item['country']
      bundleid = json_item['bundleid']
      appname = json_item['appname']
      url = baseurl+'us/app/'+appname+'/'+'id'+appid
      #url = 'https://apps.apple.com/us/app/淘特-十月特省节/id1340376323'
      #print(url)
      json_item['url'] = url
      json_item['timestamp'] = time.time()

      driver = set_selenium_driver(gc)
      driver.get(url)
      time.sleep(2)
      response = driver.page_source

      if 'we-connecting' in response:
        url = baseurl+'cn/app/'+appname+'/'+'id'+appid
        json_item['url'] = url
        json_item['language'] = 'chinese'
        driver.get(url)
        time.sleep(2)
        response = driver.page_source
        if 'we-connecting' in response:
          response = None
          page_not_exist_sign = True
      else:
        json_item['language'] = 'english'

      if response:
        if 'selfclear is-apps-theme' in response:
          try:
            # privacy button
            if json_item['language'] == 'english':
              privacy_button= WebDriverWait(
                  driver, gc.timeout
                ).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'See Details')]"))
                )
              #print(privacy_button)
              privacy_button.click()
              time.sleep(1)
            if json_item['language'] == 'chinese':
              privacy_button= WebDriverWait(
                  driver, gc.timeout
                ).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '查看详情')]"))
                )
              #print(privacy_button)
              privacy_button.click()
              time.sleep(1)
            if 'app-privacy__modal-heading' in driver.page_source:
              #gc.done_count+=1
              json_item['privacy_response'] = driver.page_source
              #gc.result_queue.put(json_item)
            else:
              error_sign = True
              gc.privacyNoOpen_count+=1
              time.sleep(gc.interval)
              json_item['error'] = 'privacyNoOpen'
              #write_json(json_item, gc.error_file)
        
            #what's new button
            if not error_sign:
              if "whats-new__headline" in response:
                close_button= WebDriverWait(
                    driver, gc.timeout
                  ).until(
                  EC.element_to_be_clickable((By.XPATH, "//button[@class='we-modal__close']"))
                  )
                close_button.click()
                time.sleep(2)
                if json_item['language'] == 'english':
                    version_button= WebDriverWait(
                        driver, gc.timeout
                      ).until(
                      EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Version History')]"))
                      )
                    version_button.click()
                    time.sleep(1)             
                if json_item['language'] == 'chinese':
                    version_button= WebDriverWait(
                        driver, gc.timeout
                      ).until(
                      EC.element_to_be_clickable((By.XPATH, "//button[contains(., '版本记录')]"))
                      )
                    version_button.click()
                    time.sleep(1)
                if 'version-history__headline' in driver.page_source:
                  soup = BeautifulSoup(driver.page_source, 'html.parser')
                  json_item['version_response']= str(soup.find("div", class_='we-modal__content__wrapper'))
                  #json_item['version_response'] = driver.page_source
                  gc.done_count+=1
                  gc.result_queue.put(json_item)
                else:
                  error_sign = True
                  gc.versionNoOpen_count+=1
                  time.sleep(gc.interval)
                  json_item['error'] = 'versionNoOpen'
                  #write_json(json_item, gc.error_file)
              else:
                gc.done_count+=1
                json_item['version_response'] = ''
                gc.result_queue.put(json_item)
              if error_sign:
                gc.error_count+=1
                write_json(json_item, gc.error_file)
            else:
              gc.error_count+=1
              write_json(json_item, gc.error_file)   

          except TimeoutException:
            gc.error_count+=1
            json_item['error'] = 'timeout'
            write_json(json_item, gc.error_file)
          except Exception as e:
            gc.error_count+=1
            gc.OtherError_count+=1
            json_item['error'] = 'other error'
            write_json(json_item, gc.error_file)
        else:
          gc.error_count+=1
          gc.appPageNoOpen_count+=1
          json_item['error'] = 'no app page'
          write_json(json_item, gc.error_file)
      else:
        if page_not_exist_sign:
          gc.error_count+=1
          json_item['error'] = 'page not exists'
          write_json(json_item, gc.error_file)          
        else:
          gc.error_count+=1
          gc.appNoResponse_count+=1
          json_item['error'] = 'no response'
          write_json(json_item, gc.error_file)
        
      driver.quit()
      time.sleep(5)#3 on imac, 5 on server
      #3.3/app on server, 4.3/app on imac will not get blocked
    
    except KeyError:
      pass

def multithread_crawler(
    gc,
):
    fp = open(gc.input_file, 'r')
    data = json.load(fp)
    fp.close()
    print("# of app before remove finished:", len(data))
    if len(gc.finished_appid_set) != 0:
      remove_idx = set()
      for k in range(len(data)):
        if data[k]['appid'] in gc.finished_appid_set:
          remove_idx.add(k)
      data = [_ for i, _ in enumerate(data) if i not in remove_idx]

    gc.total_num_app = len(data)
    logging.warning('# of app left to crawl: %d', gc.total_num_app)

    logging.warning('start crawling')
    pool = ThreadPool(gc.thread_num)
    m = multiprocessing.Manager()
    gc.event = m.Event()

    _phish_func = partial(crawl_iosStore, gc)

    pool.map_async(_phish_func, data)

    logging.warning('start sleeping')
    time.sleep(gc.peroid_stop)
    logging.warning('end sleeping')
    gc.event.set()
    print('set event')
    pool.close()
    gc.event.wait()
    print('after wait')
    pool.terminate()
    print("pool terminate")

    """
    #pool.map(_phish_func, data)
    #pool.close()
    #pool.join()
    """

    logging.warning("finish all threads")
    gc.is_stop = True


def save_results(
    gc,
):
    logging.warning('start saving')
    while True:
      try:
        if gc.is_stop:
          time.sleep(30)
          if gc.result_queue.empty():
            logging.warning('it is time to quit')
            break
        if gc.result_queue.empty():
          time.sleep(gc.interval)
          continue
        item = gc.result_queue.get(block=False,)
        write_json(item, gc.result_file)
        gc.dump_count += 1
        if gc.dump_count % 10000 == 0:
          logging.warning('(10k) dumped %d results', gc.dump_count)
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
          '%d tasks completed, %d dumped, %d error, %d privacy not open, %d version not open, %d app page not open, %d app no return response, %d other error, %d left, time cost is %d minutes', 
          gc.done_count,
          gc.dump_count,
          gc.error_count,
          gc.privacyNoOpen_count,
          gc.versionNoOpen_count,
          gc.appPageNoOpen_count,
          gc.appNoResponse_count,
          gc.OtherError_count,
          gc.total_num_app-gc.done_count-gc.error_count,
          (time.time() - global_overall_start_time)//60,
      )
    except AttributeError:
      continue
    if gc.is_stop:
      break

def check_finished(
  gc,
  result_dir,
):
  gc.finished_appid_set = set()
  number_error_line = 0
  for (folderdir, foldernames, filenames) in os.walk(result_dir):
    for filename in filenames:
      if not filename.endswith('.json'):
        continue
      with open(os.path.join(folderdir, filename)) as fp:
        for line in fp:
          try:
            line = json.loads(line.strip())
            gc.finished_appid_set.add(line['appid'])
          except Exception:
            number_error_line+=1
            continue
  
  logging.warning("already finished %d", len(gc.finished_appid_set))
  print("number of error line:", number_error_line)

if __name__ == "__main__":
  format_str = '%(asctime)s - %(levelname)s - %(message)s -%(funcName)s'
  logging.basicConfig(level=logging.WARNING, format=format_str)
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', type=str)
  parser.add_argument('--input_dir', type=str)
  parser.add_argument('--result_dir', type=str)
  parser.add_argument('--interval', type=int, default=5)
  parser.add_argument('--timeout', type=int, default=60)#seconds
  parser.add_argument('--peroid_stop', type=int, default=120)#seconds
  parser.add_argument('--driver_type', type=str,
                      choices=['chrome', 'firefox',], default='chrome')
  parser.add_argument('--driver_path', type=str)
  parser.add_argument('--thread_num', type=int, default=6)
  options = parser.parse_args()
  input_file = options.input_file
  input_dir = options.input_dir
  result_dir = options.result_dir
  interval = options.interval
  timeout = options.timeout
  peroid_stop = options.peroid_stop
  driver_type = options.driver_type
  driver_path = options.driver_path
  thread_num = options.thread_num
  #result_dir = os.path.join(result_dir, str(20220415))
  if not os.path.exists(result_dir):
    os.makedirs(result_dir)

  result_file = os.path.join(result_dir, str(time.time()).split('.')[0]+'.json')
  error_file = os.path.join(result_dir, str(time.time()).split('.')[0]+'_error.json')
  gc = Global_Config(input_file, input_dir, result_dir, result_file, error_file, interval, 
                    timeout, peroid_stop, driver_type, driver_path, thread_num,)

  check_finished(gc, result_dir)
  
  baseurl = 'https://apps.apple.com/'

  message_thread = threading.Thread(target=alive_message, args=(gc,))
  message_thread.start()
  sthread = threading.Thread(target=save_results, args=(gc,))
  sthread.start()
  multithread_crawler(gc,)
  message_thread.join()
  sthread.join()

  logging.warning(
      '%d tasks completed, %d dumped, %d error, time cost is %d minutes, %d hours, %d seconds', 
      gc.done_count,
      gc.dump_count,
      gc.error_count,
      (time.time() - global_overall_start_time)//60,
      (time.time() - global_overall_start_time)//3600,
      (time.time() - global_overall_start_time),
  )
