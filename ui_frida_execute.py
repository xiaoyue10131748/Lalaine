# -*- coding: utf-8 -*-
import asyncio
import time
import  datetime, time
import threading
import sys
import time
import frida
from install import *
import subprocess
import logging
import signal
import tqdm


logging.basicConfig(
       format = '▸ %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(levelname)s %(message)s',
        level = logging.INFO,
       datefmt = '%H:%M:%S',
    )


async def start_UI_crawler():
    #723e928699a1813c67d06b0c825a56333f91e338 (iphone 8 13.7)
    #5f8ed661a709152639f093cf45f09487595ff304
    #d4249935d52f1766a8139ac17e06f2e46e86836c
    #6baa682616264e25c65c25304fb3e1d95e56028a (se)
    #00008020-001564210E78002E (sultan)
    #066fe19b5c1523b4635d852bb9617969a0e384c6 (se 13.0)
    p = await asyncio.create_subprocess_exec('/usr/local/lib/node_modules/nosmoke/bin/nosmoke', '-u', '00008020-001564210E78002E',"-s")
    fut = p.communicate()
    try:
        pcap_run = await asyncio.wait_for(fut, timeout=250)
    except asyncio.TimeoutError:
        p.kill()
        await p.communicate()
        print("ui crawler time out")
        print("restart UI crawler")


    '''
    try:
        pcap_run = await asyncio.wait_for(fut,timeout=35)
    except Exception:
        try:
            p.kill()
        except ProcessLookupError:
            pass
        raise 
    '''




def on_message(message,data):
    file_name="./frida_tmp.txt"
    with open(file_name, 'a+',encoding = "utf8") as f:
        if message['type'] == 'send':
            f.write(message['payload'] + "\n\n")
 


def frida_attach(device, bundleID):
   while True:
        applications = device.enumerate_applications()
        for application in applications:
            if application.identifier == bundleID:
                #print(application.pid)
                if application.pid !=0:
                    app_name = application.name
                    session = device.attach(app_name)
                    print("attached")
                    return session
                else:
                    time.sleep(2)



async def frida_process(bundleID,ROOT):  
    device = frida.get_usb_device(10)
    session = frida_attach(device, bundleID)
    print("executed")
    await asyncio.sleep(1)
    with open(ROOT+"/hook_sensitive_api.js","r", encoding = "utf8") as f:
        script = session.create_script(f.read())
    
    script.on("message",on_message)
    script.load()
    sys.stdin.read()
    session.detach()
    sys.exit("detach...")
    


def thread_loop_task(loop):

    # 为子线程设置自己的事件循环
    asyncio.set_event_loop(loop)

    future = asyncio.gather(start_UI_crawler())
    loop.run_until_complete(future)
    loop.close()


async def print_process(flen):
    for _ in tqdm.tqdm(range(flen)):
        await asyncio.sleep(0.1)



def signal_test(bundleID, ROOT):
    # 创建一个事件循环thread_loop
    thread_loop = asyncio.new_event_loop() 

    # 将thread_loop作为参数传递给子线程
    t = threading.Thread(target=thread_loop_task, args=(thread_loop,))
    t.daemon = True
    t.start()

    asyncio.run(print_process(100))

    try:
        asyncio.run(frida_process(bundleID,ROOT))
    except:
        file_name=ROOT+"/frida_tmp.txt"
        with open(file_name, 'a+',encoding = "utf8") as f:
            f.write("[!] frida hooking exception."+ "\n\n")




if __name__ == "__main__":
    bundleID="ai.cloudmall.ios"
    signal_test(bundleID)













