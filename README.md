# Lalaine

## Enviroment requirement 
- MacOS
- A rooted iOS device

## What's included in dynamic anlaysis pipeline
- UI Automation
- Sensive API Hooking
- Network monitor
- Inference (data, purpose) 
- Compliance check

## Enviroment Setup
### UI Automation
> We utilize Macaca, an open-source automation testing framework that supports various types of applications including native, mobile, hybrid, web, and mobile web applications. Macaca offers automation drivers, environment support, peripheral tools, and integration solutions to tackle challenges such as test automation and client-side performance.In addition, we configure NoSmoke, a cross-platform UI crawler that scans view trees, performs OCR operations, and generates and executes UI test cases.
- install macaca <https://macacajs.github.io/guide/environment-setup.html#macaca-cli>
- install nosmoke <https://macacajs.github.io/NoSmoke/guide/>


### Sensive API Hooking
> We utilize Frida, a dynamic code instrumentation toolkit. We inject snippets of JavaScript into native apps on iOS. We built our hooking framework on top of the Frida API.

- install Frida’s CLI tools on MacOS: <https://frida.re/docs/installation/> 
- configure Frida on your rooted iOS device: <https://frida.re/docs/ios/>

### Network monitor
> We utilized Fiddler, which is a web debugging proxy tool that monitors, analyzes and modifies the traffic on iOS device. 
- install Fiddler in your MacOS: <https://docs.telerik.com/fiddler/configure-fiddler/tasks/configureformac>
- configure your rooted iOS device: <https://docs.telerik.com/fiddler/configure-fiddler/tasks/configureforios>



## Usage
### Step zero: setup python environment
- install Python 3.10.10
- `python3.10 -m venv LalaineEnv` 
- `source LalaineEnv/bin/activate` 
- `pip install -r requirements.txt`
### Step one: gather call trace and network traffic by dynamically executing an app in rooted device. 
- put the app binary code (.ipa) in the *app* folder *0*(you can create more folder to allow batch analysis). You can use ipatool to download app: <https://github.com/majd/ipatool>
- launch macaca server to connects with device: `macaca server --verbose`
- launch Fiddler to capture/decrypt Traffic from iOS Device: `Tools > Options > HTTPS and check Decrypt HTTPS traffic`
- run the script to execute app and gather data: `python batch_ui_frida_test.py 0 .`

### Step two: analyze call trace and network traffic to extract (data, purpose) from code behavior.
- run the script `python analyze_log.py -d "."  -n 0`
- More parameters are detailed as follows:
  <img width="628" alt="image" src="https://user-images.githubusercontent.com/38227314/227628542-4248517d-38cc-42e3-9927-55065dfef037.png">


### Step three: perform compliance check.
- download privacy label of apps we crawled from app store and put it under *data* folder: <https://drive.google.com/file/d/1k3FulkLvOhgLV_hU-hkxnuvnP4FF3tXz/view?usp=share_link>. If the app you want to test is not on the list, you can mannully add it to this file to allow further complaince check. 
- run the script `python compliance_check.py 0 .`

## Other materials
The other materials (e.g., l-data, privacy ontology,serverity break down, ect) can be found in <https://sites.google.com/view/privacylabel/home>

