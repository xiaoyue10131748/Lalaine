# Lalaine

## Environment requirement 
- MacOS
- Xcode 13
- A rooted iOS device

## What's included in the analysis pipeline
- [Downloader](#downloader-usage)
- [Static Assessment Framework](#saf-usage)(SAF)
- [Dynamic Assessment Framework](#daf-usage) (DAF)
  - UI Automation
  - Sensitive API Hooking
  - Network Monitor
  - Inference (data, purpose) 
  - Compliance check

## Environment Setup
### Setup python environment
- install [Python 3.10.10](https://www.python.org/downloads/release/python-31010/)
- `python3.10 -m venv LalaineEnv` 
- `source LalaineEnv/bin/activate` 
- `cd Lalaine`
- `python -m pip install wheel setuptools`
- `brew install cmake libomp `
- `pip install -r requirements.txt`

### UI Automation
> We utilize Macaca, an open-source automation testing framework that supports various types of applications including native, mobile, hybrid, web, and mobile web applications. Macaca offers automation drivers, environment support, peripheral tools, and integration solutions to tackle challenges such as test automation and client-side performance. In addition, we configure NoSmoke, a cross-platform UI crawler that scans view trees, performs OCR operations, and generates and executes UI test cases.
- install macaca <https://macacajs.github.io/guide/environment-setup.html#macaca-cli>
- install nosmoke <https://macacajs.github.io/NoSmoke/guide/>

### Sensitive API Hooking
> We utilize Frida, a dynamic code instrumentation toolkit. We inject snippets of JavaScript into native apps on iOS. We built our hooking framework on top of the Frida API.

- install Frida’s CLI tools on MacOS: <https://frida.re/docs/installation/> 
- configure Frida on your rooted iOS device: <https://frida.re/docs/ios/>

### Network Monitor
> We utilized Fiddler, which is a web debugging proxy tool that monitors, analyzes, and modifies the traffic on the iOS device. 
- install Fiddler on your MacOS: <https://docs.telerik.com/fiddler/configure-fiddler/tasks/configureformac>
- configure your rooted iOS device: <https://docs.telerik.com/fiddler/configure-fiddler/tasks/configureforios>


## Downloader Usage
- Put the information of the app that you want to download in *app_info.json*
- App binary downloader
  - install [ipatool](https://github.com/majd/ipatool)
  - Auth with your own AppleID and password `ipatool auth login -e <email> -p <password>`
  - `cd downloader`
  - `python app_binary_downloader.py --input_file ./app_info.json  --result_dir ./ipa/`
  - The results will be in the folder */ipa/*
- Privacy label crawler
  - `cd downloader`
  - download [ChromeDriver](https://chromedriver.chromium.org/home) which is compatible with your browser and put it under the folder *downloader*
  - `python privacy_label_crawler.py --input_file ./app_info.json  --result_dir ./label/ --driver_path ./chromedriver`
  - The results will be in the folder */label/*

## SAF Usage
- `cd staticScanner`
- Put the binary of app (.ipa) you want to static scan under the folder */app*
- Run the command `python find_in_decrypted_ipas.py  -f ./API_List.txt  -i ./app/`
- More options:
- <img width="627" alt="image" src="https://user-images.githubusercontent.com/38227314/227998697-8542c197-5573-428a-b569-e3d1ed51b7f7.png">
- The results will be in the file *find_in_decrypted_ret.txt*

## DAF Usage
### Step one: gather call trace and network traffic by dynamically executing an app in a rooted device. 
- Put the app binary code (.ipa) in the *app* folder *0* (you can create more folders to allow batch analysis). You can use ipatool to download app: <https://github.com/majd/ipatool>
- Launch the macaca server to connect with device: `macaca server --verbose`
- Launch Fiddler to capture/decrypt Traffic from iOS Device: `Tools > Options > HTTPS and check Decrypt HTTPS traffic`. *After finishing the dynamic testing, save the network traffic under the default path **./result/0/har/**; (If you save it in another folder, you need to specify it when running analyze_log.py)*
- Obtain your iOS device ID by running `xcrun xctrace list devices`
- Run the script to execute the app and gather data: `python batch_ui_frida_test.py -d . -n 0 -i <device id> -s <smoke_path>`
- Options:
- <img width="630" alt="image" src="https://user-images.githubusercontent.com/38227314/227680270-f0811749-bbf0-4bfa-999b-13f82ad0b47b.png">


### Step two: analyze call trace and network traffic to extract (data, purpose) from code behavior.
- Download the [corpus.csv](https://drive.google.com/file/d/1isjddxbu-yGHBfQc9xlicVVPRde_cBc_/view?usp=share_link) and put it under **purpose_prediction/data/**
- Download [privacy label of apps](<https://drive.google.com/file/d/1k3FulkLvOhgLV_hU-hkxnuvnP4FF3tXz/view?usp=share_link>) we crawled from app store and put it under **data** folder. If the app you want to test is not on the list, you can manually add it to this file to allow further analysis. 
- Run the script `python analyze_log.py -d .  -n 0`
- Options:
- <img width="628" alt="image" src="https://user-images.githubusercontent.com/38227314/227628542-4248517d-38cc-42e3-9927-55065dfef037.png">
- Analyzing result can be found in **./result/0/prediction_output/**

### Step three: perform compliance check.

- Run the script `python compliance_check.py -d . -n 0`
- Options:
- <img width="626" alt="image" src="https://user-images.githubusercontent.com/38227314/227682071-a990112d-fd26-455c-b0dc-5278b1adf4b4.png">
- Analyzing result can be found in **./result/0/inconsistency_output/**


## Other materials
The other materials (e.g., l-data, privacy ontology, severity breakdown, etc) can be found in <https://sites.google.com/view/privacylabel/home>

