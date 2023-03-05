//frida -U -f ai.cloudmall.ios  -l hook_sensitive_api.js   --no-pause
//frida -U -f com.t2s.ArongIndianTakeaway -l hook_sensitive_api.js   --no-pause

console.log("[*] Started: Modify Return Value");
send("[*] Started: Modify Return Value");
function show_modify_function_return_value(className_arg, funcName_arg) {
    try {
        var className = className_arg;
        var funcName = funcName_arg;
        var hook = eval('ObjC.classes.' + className + '["' + funcName + '"]');
        Interceptor.attach(hook.implementation, {
            onLeave: function (retval) {
                console.log("\n[*] Class Name: " + className);
                console.log("[*] Method Name: " + funcName);
                console.log("\t[-] Type of return value: " + typeof retval);
                console.log("\t[-] Return Value: " + ObjC.Object(retval).toString());
                console.log('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));


                send("\n[*] Class Name: " + className);
                send("[*] Method Name: " + funcName);
                send("\t[-] Type of return value: " + typeof retval);
                send("\t[-] Return Value: " + ObjC.Object(retval).toString());
                send('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));

            }
        });

    }
    catch (error) {
        console.log("funcName_arg " + funcName)
        console.log("[!] funcName_arg Exception: ");
    }
}



function check_if_invoked(className_arg, funcName_arg) {
    //Your class name here
    var className = className_arg;
    //Your function name here
    var funcName = funcName_arg;
    var hook = eval('ObjC.classes.' + className + '["' + funcName + '"]');
    Interceptor.attach(hook.implementation, {
        onEnter: function (args) {
            console.log("\n[*] Class Name: " + className);
            console.log("[*] Method Name: " + funcName);
            console.log('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));

            send("\n[*] Class Name: " + className);
            send("[*] Method Name: " + funcName);
            send('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));

        }
    });

}


show_modify_function_return_value("ASIdentifierManager", "- advertisingIdentifier")

//YOUR_CLASS_NAME_HERE and YOUR_EXACT_FUNC_NAME_HERE
//show_modify_function_return_value("YOUR_CLASS_NAME_HERE", "YOUR_EXACT_FUNC_NAME_HERE")
//show_modify_function_return_value("advertisingIdentifier", "UUIDString")
//show_modify_function_return_value("ASIdentifierManager", "- advertisingIdentifier")

//show_modify_function_return_value("sharedManager", "advertisingIdentifier")
//show_modify_function_return_value("NSUUID", "init")

//Device ID


show_modify_function_return_value("UIDevice", "- identifierForVendor")


//location
show_modify_function_return_value("CLLocation", "- coordinate")
show_modify_function_return_value("CLLocation", "- altitude")
show_modify_function_return_value("CLLocation", "- floor")
show_modify_function_return_value("CLLocation", "- horizontalAccuracy")
show_modify_function_return_value("CLLocation", "- verticalAccuracy")
show_modify_function_return_value("CLLocation", "- timestamp")
check_if_invoked("CLLocationManager", "- requestWhenInUseAuthorization")


//contacts
show_modify_function_return_value("CNContact", "- namePrefix")
show_modify_function_return_value("CNContact", "- givenName")
show_modify_function_return_value("CNContact", "- middleName")
show_modify_function_return_value("CNContact", "- familyName")
show_modify_function_return_value("CNContact", "- previousFamilyName")
show_modify_function_return_value("CNContact", "- nickname")
show_modify_function_return_value("CNContact", "- phoneticGivenName")
show_modify_function_return_value("CNContact", "- phoneticMiddleName")
show_modify_function_return_value("CNContact", "- phoneticFamilyName")
show_modify_function_return_value("CNContact", "- jobTitle")
show_modify_function_return_value("CNContact", "- departmentName")
show_modify_function_return_value("CNContact", "- organizationName")
show_modify_function_return_value("CNContact", "- phoneticOrganizationName")
show_modify_function_return_value("CNContact", "- postalAddresses")
show_modify_function_return_value("CNContact", "- urlAddresses")
show_modify_function_return_value("CNContact", "- phoneNumbers")
show_modify_function_return_value("CNContact", "- socialProfiles")
show_modify_function_return_value("CNContact", "- emailAddresses")
show_modify_function_return_value("CNContact", "- birthday")
show_modify_function_return_value("CNContact", "- dates")
show_modify_function_return_value("CNContact", "- nonGregorianBirthday")
show_modify_function_return_value("CNContact", "- note")
show_modify_function_return_value("CNContact", "- emailAddresses")
show_modify_function_return_value("CNContactStore", "- unifiedMeContactWithKeysToFetch:error:")




//Product Interaction
/*
show_modify_function_return_value("UIDevice", "- orientation")
show_modify_function_return_value("UIDevice", "- UIDeviceOrientation")
show_modify_function_return_value("UIDevice", "- UIDeviceOrientationIsPortrait")
show_modify_function_return_value("UIDevice", "- UIDeviceOrientationIsLandscape")
show_modify_function_return_value("UIDevice", "- UIDeviceOrientationIsFlat")
show_modify_function_return_value("UIDevice", "- UIDeviceOrientationIsValidInterfaceOrientation")
*/


//Performance Data
//show_modify_function_return_value("UIDevice", "- name")
//show_modify_function_return_value("UIDevice", "- systemName") //ios
//show_modify_function_return_value("UIDevice", "- systemVersion") //13.7
//show_modify_function_return_value("UIDevice", "- model") // model
//show_modify_function_return_value("UIDevice", "- localizedModel") // iPhone
show_modify_function_return_value("UIDevice", "- batteryLevel")
//show_modify_function_return_value("UIDevice", "- batteryMonitoringEnabled")
show_modify_function_return_value("UIDevice", "- batteryState")
//show_modify_function_return_value("UIDevice", "- UIDeviceBatteryState")


//payment
show_modify_function_return_value("SKPayment", "- applicationUsername")


//health & fitness
//show_modify_function_return_value("HKSample", "- startDate")
//show_modify_function_return_value("HKStatistics", "- endDate")
//show_modify_function_return_value("HKStatisticsCollection", "- statistics")
//show_modify_function_return_value("HKStatisticsCollection", "- statisticsForDate:")
//show_modify_function_return_value("HKStatisticsCollection", "- enumerateStatisticsFromDate:toDate:withBlock:")
show_modify_function_return_value("HKHealthStore", "- biologicalSexWithError:")
show_modify_function_return_value("HKHealthStore", "- bloodTypeWithError:")
show_modify_function_return_value("HKHealthStore", "- dateOfBirthComponentsWithError:")
show_modify_function_return_value("HKHealthStore", "- fitzpatrickSkinTypeWithError:")
show_modify_function_return_value("HKHealthStore", "- wheelchairUseWithError:")




// Intercept the CCCrypt call.
Interceptor.attach(Module.findExportByName('libcommonCrypto.dylib', 'CCCrypt'), {
    onEnter: function (args) {
        // Save the arguments
        this.operation = args[0]
        this.CCAlgorithm = args[1]
        this.CCOptions = args[2]
        this.keyBytes = args[3]
        this.keyLength = args[4]
        this.ivBuffer = args[5]
        this.inBuffer = args[6]
        this.inLength = args[7]
        this.outBuffer = args[8]
        this.outLength = args[9]
        this.outCountPtr = args[10]

        console.log('CCCrypt(' +
            'operation: ' + this.operation + ', ' +
            'CCAlgorithm: ' + this.CCAlgorithm + ', ' +
            'CCOptions: ' + this.CCOptions + ', ' +
            'keyBytes: ' + this.keyBytes + ', ' +
            'keyLength: ' + this.keyLength + ', ' +
            'ivBuffer: ' + this.ivBuffer + ', ' +
            'inBuffer: ' + this.inBuffer + ', ' +
            'inLength: ' + this.inLength + ', ' +
            'outBuffer: ' + this.outBuffer + ', ' +
            'outLength: ' + this.outLength + ', ' +
            'outCountPtr: ' + this.outCountPtr + ')')

        send('CCCrypt(' +
            'operation: ' + this.operation + ', ' +
            'CCAlgorithm: ' + this.CCAlgorithm + ', ' +
            'CCOptions: ' + this.CCOptions + ', ' +
            'keyBytes: ' + this.keyBytes + ', ' +
            'keyLength: ' + this.keyLength + ', ' +
            'ivBuffer: ' + this.ivBuffer + ', ' +
            'inBuffer: ' + this.inBuffer + ', ' +
            'inLength: ' + this.inLength + ', ' +
            'outBuffer: ' + this.outBuffer + ', ' +
            'outLength: ' + this.outLength + ', ' +
            'outCountPtr: ' + this.outCountPtr + ')')

        if (this.operation == 0) {
            // Show the buffers here if this an encryption operation
            //console.log("In buffer:")
            /*
            console.log(hexdump(ptr(this.inBuffer), {
                length: this.inLength.toInt32(),
                header: true,
                ansi: true
            }))
            console.log("Key: ")
            console.log(hexdump(ptr(this.keyBytes), {
                length: this.keyLength.toInt32(),
                header: true,
                ansi: true
            }))
            console.log("IV: ")
            console.log(hexdump(ptr(this.ivBuffer), {
                length: this.keyLength.toInt32(),
                header: true,
                ansi: true
            }))
            */

            send("In buffer:")
            send(this.inBuffer.add(0x00).readCString())


        }
    },
    onLeave: function (retVal) {
        if (this.operation == 1) {
            // Show the buffers here if this a decryption operation
            /*
            console.log("Out buffer:")
            console.log(hexdump(ptr(this.outBuffer), {
                length: Memory.readUInt(this.outCountPtr),
                header: true,
                ansi: true
            }))
            console.log("Key: ")
            console.log(hexdump(ptr(this.keyBytes), {
                length: this.keyLength.toInt32(),
                header: true,
                ansi: true
            }))
            console.log("IV: ")
            console.log(hexdump(ptr(this.ivBuffer), {
                length: this.keyLength.toInt32(),
                header: true,
                ansi: true
            }))


            */
            console.log("Out buffer:")
            send("Out buffer:")
            send(this.outBuffer.add(0x00).readCString())

        }
    }
})



if (ObjC.available) {
    var paths = [
        "/Applications/blackra1n.app",
        "/Applications/Cydia.app",
        "/Applications/FakeCarrier.app",
        "/Applications/Icy.app",
        "/Applications/IntelliScreen.app",
        "/Applications/MxTube.app",
        "/Applications/RockApp.app",
        "/Applications/SBSetttings.app",
        "/Applications/WinterBoard.app",
        "/bin/bash",
        "/bin/sh",
        "/bin/su",
        "/etc/apt",
        "/etc/ssh/sshd_config",
        "/Library/MobileSubstrate/DynamicLibraries/LiveClock.plist",
        "/Library/MobileSubstrate/DynamicLibraries/Veency.plist",
        "/Library/MobileSubstrate/MobileSubstrate.dylib",
        "/pguntether",
        "/private/var/lib/cydia",
        "/private/var/mobile/Library/SBSettings/Themes",
        "/private/var/stash",
        "/private/var/tmp/cydia.log",
        "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
        "/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist",
        "/usr/bin/cycript",
        "/usr/bin/ssh",
        "/usr/bin/sshd",
        "/usr/libexec/sftp-server",
        "/usr/libexec/ssh-keysign",
        "/usr/sbin/frida-server",
        "/usr/sbin/sshd",
        "/var/cache/apt",
        "/var/lib/cydia",
        "/var/log/syslog",
        "/var/mobile/Media/.evasi0n7_installed",
        "/var/tmp/cydia.log"
    ];
    var f = Module.findExportByName("libSystem.B.dylib", "stat64");
    Interceptor.attach(f, {
        onEnter: function (args) {
            this.is_common_path = false;
            var arg = Memory.readUtf8String(args[0]);
            for (var path in paths) {
                if (arg.indexOf(paths[path]) > -1) {
                    console.log("Hooking native function stat64: " + arg);
                    send("Hooking native function stat64: " + arg);
                    this.is_common_path = true;
                    //return -1;
                }
            }
        },
        onLeave: function (retval) {
            if (this.is_common_path) {
                console.log("stat64 Bypass!!!");
                send("stat64 Bypass!!!");
                retval.replace(-1);
            }
        }
    });
    var f = Module.findExportByName("libSystem.B.dylib", "stat");
    Interceptor.attach(f, {
        onEnter: function (args) {
            this.is_common_path = false;
            var arg = Memory.readUtf8String(args[0]);
            for (var path in paths) {
                if (arg.indexOf(paths[path]) > -1) {
                    console.log("Hooking native function stat: " + arg);
                    send("Hooking native function stat: " + arg);
                    this.is_common_path = true;
                    //return -1;
                }
            }
        },
        onLeave: function (retval) {
            if (this.is_common_path) {
                console.log("stat Bypass!!!");
                send("stat Bypass!!!");
                retval.replace(-1);
            }
        }
    });
}





function show_modify_function_NSDATA(className_arg, funcName_arg) {
    try {
        var className = className_arg;
        var funcName = funcName_arg;
        var hook = eval('ObjC.classes.' + className + '["' + funcName + '"]');
        Interceptor.attach(hook.implementation, {
            onLeave: function (retval) {
                console.log("\n[*] Class Name: " + className);
                console.log("[*] Method Name: " + funcName);
                console.log("\t[-] Type of return value: " + typeof retval);
                console.log("\t[-] Return Value: " + ObjC.Object(retval).toString());
                console.log('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));


                send("\n[*] Class Name: " + className);
                send("[*] Method Name: " + funcName);
                send("\t[-] Type of return value: " + typeof retval);
                var objcData = ObjC.Object(retval);  //NSData
                var strBody = objcData.bytes().readUtf8String(objcData.length()); //NSData 转换成 string
                send("\t[-] Return Value: " + strBody);
                send('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));

            }
        });

    }
    catch (error) {
        console.log("funcName_arg " + funcName)
        console.log("[!] funcName_arg Exception: ");
    }
}

show_modify_function_NSDATA("ASAuthorizationAppleIDCredential", "- identityToken")
//user ID
show_modify_function_return_value("ASAuthorizationAppleIDCredential", "- user")
show_modify_function_return_value("ASAuthorizationAppleIDCredential", "- fullName")
show_modify_function_return_value("ASAuthorizationAppleIDCredential", "- email")
show_modify_function_return_value("SKMutablePayment", "- applicationUsername")
show_modify_function_return_value("SKPayment", "- applicationUsername")

// console.log("[*] Started: hooking getifaddrs");

const getifaddrs = new NativeFunction(Module.findExportByName('libsystem_info.dylib', 'getifaddrs'), 'int', ['pointer']);
const freeifaddrs = new NativeFunction(Module.findExportByName('libsystem_info.dylib', 'freeifaddrs'), 'void', ['pointer']);

const IFADDRS_OFFSET_NEXT = 0;
const IFADDRS_OFFSET_NAME = IFADDRS_OFFSET_NEXT + Process.pointerSize;
const IFADDRS_OFFSET_FLAGS = IFADDRS_OFFSET_NAME + Process.pointerSize;
const IFADDRS_OFFSET_ADDR = IFADDRS_OFFSET_FLAGS + Process.pointerSize;

const IFF_UP = 0x1;
const IFF_LOOPBACK = 0x8;

const AF_INET = 2;
const AF_INET6 = 30;

function getInterfaceAddresses() {
    const result = [];
    const ptrBuf = Memory.alloc(Process.pointerSize);
    if (getifaddrs(ptrBuf) === 0) {
      const interfaces = Memory.readPointer(ptrBuf);
      try {
        for (let cur = interfaces; !cur.isNull(); cur = Memory.readPointer(cur.add(IFADDRS_OFFSET_NEXT))) {
          const flags = Memory.readUInt(cur.add(IFADDRS_OFFSET_FLAGS));
          if ((flags & IFF_UP) === 0 || (flags & IFF_LOOPBACK) !== 0)
            continue;
          const addr = readSockAddr(Memory.readPointer(cur.add(IFADDRS_OFFSET_ADDR)));
          if (addr === null)
            continue;
          const name = Memory.readUtf8String(Memory.readPointer(cur.add(IFADDRS_OFFSET_NAME)));
          result.push({
            name: name,
            address: addr
          });
        }
      } finally {
        freeifaddrs(interfaces);
      }
    }
	for (var i = 0; i < result.length; i++ ) {
        console.log("Interface name: "+result[i].name+" Address: "+result[i].address);
        send("Interface name: "+result[i].name+" Address: "+result[i].address);
    }
    // console.log('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));
    // send('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));
    return result;
  }


function show_ip_addr() {
    try {
        var hook = Module.findExportByName('libsystem_info.dylib', 'getifaddrs');

        // var hook = eval('ObjC.classes.' + className + '["' + funcName + '"]');
        // Interceptor.attach(hook.implementation, {
        Interceptor.attach(hook, {
            onEnter: function (args){
                console.log("[*] Entering getifaddrs");
                send("[*] Entering getifaddrs");
                console.log('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));
                send('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));
            },
            onLeave: function (retval) {
                console.log("[*] Leaving getifaddrs");
                send("[*] Leaving getifaddrs");
                getInterfaceAddresses();
                // console.log("\t[-] Type of return value: " + typeof retval);
                // const interfaces = Memory.readPointer(saved_arg);
                // try {
                //   for (let cur = interfaces; !cur.isNull(); cur = Memory.readPointer(cur.add(IFADDRS_OFFSET_NEXT))) {
                //     const flags = Memory.readUInt(cur.add(IFADDRS_OFFSET_FLAGS));
                //     if ((flags & IFF_UP) === 0 || (flags & IFF_LOOPBACK) !== 0)
                //       continue;
                //     const addr = readSockAddr(Memory.readPointer(cur.add(IFADDRS_OFFSET_ADDR)));
                //     if (addr === null)
                //       continue;
                //     const name = Memory.readUtf8String(Memory.readPointer(cur.add(IFADDRS_OFFSET_NAME)));
                //     result.push({
                //       name: name,
                //       address: addr
                //     });
                //   }
                // } finally {
                //   freeifaddrs(interfaces);
                // }
            //     console.log("\n[*] Class Name: " + className);
            //     console.log("[*] Method Name: " + funcName);

            //     console.log("\t[-] Return Value: " + ObjC.Object(retval).toString());
            //     console.log('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));
            //     send("\n[*] Class Name: " + className);
            //     send("[*] Method Name: " + funcName);
            //     send("\t[-] Type of return value: " + typeof retval);
            //     send("\t[-] Return Value: " + ObjC.Object(retval).toString());
            //     send('\tBacktrace:\n\t' + Thread.backtrace(this.context, Backtracer.ACCURATE).map(DebugSymbol.fromAddress).join('\n\t'));

            }
        });

    }
    catch (error) {
        console.log("funcName_arg " + funcName)
        console.log("[!] funcName_arg Exception: ");
    }
}

function readSockAddr(address) {
  const family = Memory.readU8(address.add(1));
  if (family === AF_INET || family === AF_INET6) {
    let ip = '';
    if (family === AF_INET) {
      for (let offset = 4; offset !== 8; offset++) {
        if (ip.length > 0)
          ip += '.';
        ip += Memory.readU8(address.add(offset));
      }
    } else {
      for (let offset = 8; offset !== 24; offset += 2) {
        if (ip.length > 0)
          ip += ':';
        ip += toHex(Memory.readU8(address.add(offset))) +
            toHex(Memory.readU8(address.add(offset + 1)));
      }
    }
    return ip;
  } else {
    return null;
  }
}

function toHex(v) {
  let result = v.toString(16);
  if (result.length === 1)
    result = '0' + result;
  return result;
}


show_ip_addr();

// add serialNumber: https://developer.apple.com/documentation/externalaccessory/eaaccessory/1613811-serialnumber
// buildVersion
//udid
