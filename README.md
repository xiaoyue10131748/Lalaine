# Lalaine
## Table of contents

- [Quick start](#quick-start)
- [Status](#status)
- [What's included](#whats-included)
- [Bugs and feature requests](#bugs-and-feature-requests)
- [Contributing](#contributing)
- [Creators](#creators)
- [Thanks](#thanks)
- [Copyright and license](#copyright-and-license)


## Enviroment requirement 

- MacOS
- A rooted iOS device

## What's included in dynamic anlaysis pipeline
- UI Automation
- Sensive API Hooking
- Network monitor

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
### gather call trace and network traffic by dynamically exexuting an app in rooted device. 
- launch macaca server to connects with device: `macaca server --verbose`
- launch Fiddler to capture/decrypt Traffic from iOS Device: `Tools > Options > HTTPS and check Decrypt HTTPS traffic`
- put the app binary code (.ipa) in the *app* folder
- run the script to execute app and gather data: `python batch_ui_frida_test.py 0 .`

### analyze call trace and network traffic to extract (data, purpose) from code behavior.
- run the script `python analyze_log.py 0 .`

### perform complaince check.
- run the script `python compliance_check 0 .`

