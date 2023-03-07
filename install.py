import os


INSTALL=["./app/0/com.gannett.news.local.11AliveNews_461033172_v45.ipa"]
def install(ipa):
    if ipa in INSTALL:
        print("the app has been installed")
        return 0
    #os.system("tidevice pair")
    cmd="ideviceinstaller -i " +ipa
    #cmd="tidevice install "  +ipa
    status=os.system(cmd)
    if status==0:
        print("install successfully")
    else:
        print("install failed")
    #os.system("tidevice unpair")
    return status


def decrypted_app(bundleid):
    cmd="python3 /Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/frida_dump/frida-ios-dump/dump.py " + bundleid+ " -o " + "/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/frida_dump/frida-ios-dump/app/" + bundleid+"_decryped.ipa" 
    status=os.system(cmd)
    if status==0:
        print("dump successfully")
    else:
        print("dump failed")



def uninstall(bundleid):
    print(bundleid)
    #os.system("tidevice pair")
    cmd="ideviceinstaller -U " +bundleid + " -w"
    #cmd="tidevice uninstall " +bundleid 
    os.system(cmd)
    #os.system("tidevice unpair")


def get_old_bundle_id(ipa):
    cells = ipa.split("-")
    appid = cells[-4]
    bundle_id = ipa.split(appid)[0][:-1]
    return bundle_id


def get_bundle_id(ipa):
    cells = ipa.split("_")
    #appid = cells[-1]
    #bundle_id = ipa.split(appid)[0][:-1]
    bundle_id = ipa.split("_")[0]
    return bundle_id



if __name__ == '__main__':
    input_path= '/Users/xiaoyue-admin/Documents/privacy_label/app/1/fake_signed_ipas/'
    files = os.listdir(input_path)
    for ipa in files:
        bundleid=get_bundle_id(ipa)
        #install(input_path+ipa)
        uninstall(bundleid)
        break