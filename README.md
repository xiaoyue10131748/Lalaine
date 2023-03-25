# Lalaine

## Enviroment requirement 
- MacOS
- Xcode 13
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
- install [Python 3.10.10](https://www.python.org/downloads/release/python-31010/)
- `python3.10 -m venv LalaineEnv` 
- `source LalaineEnv/bin/activate` 
- `cd Lalaine`
- `pip install -r requirements.txt`
### Step one: gather call trace and network traffic by dynamically executing an app in rooted device. 
- Put the app binary code (.ipa) in the *app* folder *0* (you can create more folder to allow batch analysis). You can use ipatool to download app: <https://github.com/majd/ipatool>
- Launch macaca server to connects with device: `macaca server --verbose`
- Launch Fiddler to capture/decrypt Traffic from iOS Device: `Tools > Options > HTTPS and check Decrypt HTTPS traffic`. *After finishing the dynamic testing, save the network traffic under the default path **./result/0/har/**; (If you save it in other folder, you need specify it when run analyze_log.py)*
- Obtain your iOS device ID by runing `xcrun xctrace list devices`
- Run the script to execute app and gather data: `python batch_ui_frida_test.py -d . -n 0 -i <device id> -s <smoke_path>`
- Options:
- <img width="630" alt="image" src="https://user-images.githubusercontent.com/38227314/227680270-f0811749-bbf0-4bfa-999b-13f82ad0b47b.png">


### Step two: analyze call trace and network traffic to extract (data, purpose) from code behavior.
- Download the [corpus.csv](https://drive.google.com/file/d/1isjddxbu-yGHBfQc9xlicVVPRde_cBc_/view?usp=share_link) and put it under **purpose_prediction/data/**
- Run the script `python analyze_log.py -d .  -n 0`
- More parameters are detailed as follows:
- <img width="628" alt="image" src="https://user-images.githubusercontent.com/38227314/227628542-4248517d-38cc-42e3-9927-55065dfef037.png">
- Analyzing result can be found in **./result/0/prediction_output/**

### Step three: perform compliance check.
- Download [privacy label of apps](<https://drive.google.com/file/d/1k3FulkLvOhgLV_hU-hkxnuvnP4FF3tXz/view?usp=share_link>) we crawled from app store and put it under *data* folder. If the app you want to test is not on the list, you can mannully add it to this file to allow further complaince check. 
- Run the script `python compliance_check.py -d . -n 0`
- Options:
- <img width="626" alt="image" src="https://user-images.githubusercontent.com/38227314/227682071-a990112d-fd26-455c-b0dc-5278b1adf4b4.png">
- Analyzing result can be found in **./result/0/inconsistency_output/**


## Other materials
The other materials (e.g., l-data, privacy ontology,serverity break down, ect) can be found in <https://sites.google.com/view/privacylabel/home>

