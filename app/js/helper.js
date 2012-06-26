/*
 Class UCapCore

 Handles all data abstraction from the uCap Server.
 */

var UCapCore = {
    household:[],
    users:[],
    devices:[],
    authed:false,

    isAuthed:function () {
        $.jsonRPC.request('ucap.is_authed', {
            success:function (data) {
                var result = data["result"];
                if(result == 1){
                    if(!UCapCore.authed){
                        UCapManager.initializeData();
                        setTimeout(function(){UCapManager.showPage({pageID:UCapManager.getCurrentPage(),func: UCapManager.capFirstLetter(UCapManager.getCurrentPage())+'Page'})}, 250);
                    }
                    UCapCore.authed = true;
                } else {
                    UCapManager.showLoginPage();
                }
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'ucap.is_authed', params:''});
    },

    isAdmin: function(){
        var user = UCapCore.users[UCapCore.findUser({uid:localStorage['uid']})];
        return !!(user[7] == "admin");
    },

    userLogout:function () {
        $.jsonRPC.request('ucap.user_logout', {
            success:function () {
                UCapManager.showLoginPage();
                UCapManager.hideMenuBar();
                UCapManager.cleanScheduler({scope:"application"});
                localStorage.clear();
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'ucap.user_logout', params:''});
    },

    userLogin:function (obj) {
        $.jsonRPC.request('ucap.user_login', {params:[obj.username, obj.passwd],
            success:function (data) {
                var result = data["result"];
                if(result[0] == "-1"){
                   $('#loginForm .error').html("The username or password you entered is incorrect.").fadeIn("slow");
                } else {
                    UCapCore.authed = true;
                    localStorage['hid'] = result[2];
                    localStorage['uid'] = obj.username;
                    UCapManager.initializeData();
                    setTimeout(function(){UCapManager.showPage({pageID:'network',func:'NetworkPage'})}, 250);
                }
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'ucap.user_login', params:obj.username});
    },

    changePassword:function (obj) {
        $.jsonRPC.request('ucap.change_password', {params:[obj.email, obj.oldPass, obj.newPass],
            success:function (data) {
                var result = data["result"];
                if (result[0] == "0") {
                    UCapManager.notification("notice", "The password has been changed successfully!");
                } else {
                    UCapManager.notification("error", "You entered the old password incorrectly. Please try again.");
                }
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'ucap.change_password', params:obj.email});
    },

    resetPassword:function (obj) {
        $.jsonRPC.request('ucap.lost_password', {params:[obj.email],
            success:function (data) {
                var result = data["result"];
                if (result[0] == "0") {
                    UCapManager.notification("notice", "An email has been sent to your address. Please follow the instructions to reset your password.");
                } else {
                    UCapManager.notification("error", "There is no account associated with this email.");
                }
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'ucap.lost_password', params:obj.email});
    },

    getHouse:function (obj) {
        $.jsonRPC.request('ucap.getHouseMetaInfo', {params:[obj.hid],
            success:function (data) {
                var result = data["result"];
                UCapCore.household = result[1];
				
				/* Temporary hack for updating billing cycle */
				var today = new Date();
				var billingday = UCapCore.household[7].split(' ');
				billingday = billingday[0].split('-');
				billingday = new Date(billingday[0], billingday[1], billingday[2]);
			
				var daysRemaining = differenceInDays(today, billingday);
				if (daysRemaining < 0) {
					var date = $.datepicker.formatDate( "yy-mm-dd", billingday);
					UCapCore.household[7] = date + " 00:00:00";
					UCapCore.updateStartDate({hid:UCapCore.household[0],start:date});
				}
            },
            error:function () {
                UCapManager.notification("error", "Error: getHouse."); //Oops! You are not connected to the internet. Please try again later.
                UCapManager.cleanScheduler({scope:"application"});
            }
        });
        UCapCore.logAction({fname:'getHouseMetaInfo', params:obj.hid});
    },

    getUsers:function (obj) {
        $.jsonRPC.request('ucap.getHouseUsersDetails', {params:[obj.hid],
           success:function (data) {
                var result = data["result"];
                UCapCore.users = result[1].sort();
                if (UCapCore.users.length > 0) {
                    for (var i = 0, l = UCapCore.users.length; i < l; i++) {
                        UCapCore.getDevices({hid:obj.hid, uid:UCapCore.users[i][0]});
                    }
                }
            },
            error:function () {
                UCapManager.notification("error", "Error: getUsers");
                UCapManager.cleanScheduler({scope:"application"});
            }
         });
        UCapCore.logAction({fname:'getHouseUsersDetails', params:obj.hid});
    },

    getHouseCap:function (obj) {
        $.jsonRPC.request('ucap.HouseUsage', {params:['get', 'cap', obj.hid],
            success:function (data) {
                var result = data["result"];
                UCapCore.household.push(result[1]);
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'HouseUsage', params:'get,cap,' + obj.hid});
    },

    getHouseUsage:function (obj) {
        $.jsonRPC.request('ucap.HouseUsage', {params:['get', 'usage', obj.hid],
            success:function (data) {
                var result = data["result"];
                UCapCore.household.push(result[1]);
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'HouseUsage', params:'get,usage,' + obj.hid});
    },

    setHouseCap:function (obj) {
        $.jsonRPC.request('ucap.HouseUsage', {params:['set', 'cap', obj.hid, obj.cap],
            success:function (data) {
                var result = data["result"];
                if (result == "Error")
                    UCapManager.notification("error", "Oops! Something went wrong. Please try again later.");
                else
                    UCapManager.notification("notice", "The bandwidth cap for this Household has been updated!");
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'HouseUsage', params:'set,cap,' + obj.hid + ',' + obj.cap});
    },

    setUserCap:function (obj) {
        $.jsonRPC.request('ucap.UserUsage', {params:['set', 'cap', obj.hid, obj.uid, obj.cap],
            success:function (data) {
                var result = data["result"];
                if (result == "Error")
                    UCapManager.notification("error", "Oops! Something went wrong. Please try again later.");
                else
                    UCapManager.notification("notice", "The bandwidth cap for this account has been updated!");
            },
            error:function () {
            }
        });
        UCapCore.logAction({fname:'UserUsage', params:'set,cap,' + obj.hid + ',' + obj.uid + ',' + obj.cap});
    },

    setHouseInfo:function (obj) {
        $.jsonRPC.request('ucap.updateHouseMetaInfo', {params:[obj.hid, obj.address, obj.details, obj.photo],
            success:function () {
                UCapManager.notification("notice", "Household information has been updated!");
            },
            error:function () {
                UCapManager.notification("error", "Error: setHouseInfo");
            }
        });
        UCapCore.logAction({fname:'updateHouseMetaInfo', params:obj.hid + ',' + obj.address + ',' + obj.details + ',' + obj.photo});
    },

    setUserInfo:function (obj) {
        $.jsonRPC.request('ucap.updateUserMetaInfo', {params:[obj.hid, obj.uid, obj.name, obj.details, obj.notify, obj.notifypercent, obj.notified, obj.photo, obj.role, obj.email],
            success:function () {
                UCapManager.notification("notice", "Account information has been updated!");
            },
            error:function () {
                UCapManager.notification("error", "Error: setUserInfo");
            }
        });
        UCapCore.logAction({fname:'updateUserMetaInfo', params:obj.hid + ',' + obj.uid + ',' + obj.name + ',' + obj.details + ',' + obj.notify + ',' + obj.notifypercent + ',' + obj.notified + ',' + obj.photo + ',' + obj.role + ',' + obj.email});
    },

    addUser:function (obj) {
        $.jsonRPC.request('ucap.addUser', {params:[obj.hid, obj.uid, obj.name, obj.details, obj.email, obj.passwd, obj.role, obj.notify, obj.notifypercent, obj.notified, obj.photo],
            success:function () {
                UCapManager.notification("notice", "An account has been created for " + obj.name);
            },
            error:function () {
                UCapManager.notification("error", "Error: addUser");
            }
        });
        UCapCore.logAction({fname:'addUser', params:obj.hid + ',' + obj.uid + ',' + obj.name + ',' + obj.details + ',' + obj.email + ',' + obj.passwd + ',' + obj.role + ',' + obj.notify + ',' + obj.notifypercent + ',' + obj.notified + ',' + obj.photo});
    },

    addHouse:function (obj) {
        $.jsonRPC.request('ucap.addHouse', {params:[obj.hid, obj.address, obj.details, obj.photo],
            success:function () {
                UCapManager.notification("notice", "New Household, " + obj.name + " was added to uCap.");
            },
            error:function () {
                UCapManager.notification("error", "Error: addHouse");
            }
        });
        UCapCore.logAction({fname:'addHouse', params:obj.hid + ',' + obj.address + ',' + obj.details + ',' + obj.photo});
    },

    addDevice:function (obj) {
        $.jsonRPC.request('ucap.addDevice', {params:[obj.hid, obj.uid, obj.name, obj.details, "['" + obj.mac + "']", obj.photo],
            success:function () {
                UCapManager.notification("notice", obj.name + " with MAC Address " + obj.mac + ", was added to uCap.");
            },
            error:function () {
                UCapManager.notification("error", "Error: addDevice");
            }
        });
        UCapCore.logAction({fname:'addDevice', params:obj.hid + ',' + obj.uid + ',' + obj.name + ',' + obj.details + ',' + "['" + obj.mac + "']" + ',' + obj.photo});
    },

    getDevices:function (obj) {
        $.jsonRPC.request('ucap.getUserDevicesDetails', {params:[obj.hid, obj.uid],
            success:function (data) {
                var result = data["result"];
                UCapCore.devices[obj.uid] = result[1].sort(function(a, b){
                                                             var x = a[1].toLowerCase(), y = b[1].toLowerCase();
                                                             return x < y ? -1 : x > y ? 1 : 0;
                                                        });
            },
            error:function () {
                UCapManager.notification("error", "Error: getDevices");
            }
        });
        UCapCore.logAction({fname:'getUserDevicesDetails', params:obj.hid + ',' + obj.uid});
    },

    setDeviceCap:function (obj) {
        $.jsonRPC.request('ucap.DeviceUsage', {params:['set', 'cap', obj.hid, obj.uid, obj.did, obj.cap],
            success:function (data) {
                var result = data["result"];
                if (result == "Error")
                    UCapManager.notification("error", "Oops! Something went wrong. Please try again later.");
                else
                    UCapManager.notification("notice", "The bandwidth cap for this device has been updated!");
            },
            error:function () {
                UCapManager.notification("error", "Error: setDeviceCap");
            }
        });
        UCapCore.logAction({fname:'DeviceUsage', params:'set,cap,' + obj.hid + ',' + obj.uid + ',' + obj.did + ',' + obj.cap});
    },

    setDeviceInfo:function (obj) {
        $.jsonRPC.request('ucap.updateDeviceMetaInfo', {params:[obj.hid, obj.uid, obj.did, obj.name, obj.details, obj.photo],
            success:function () {
                UCapManager.notification("notice", "The device information has been updated!");
            },
            error:function () {
                UCapManager.notification("error", "Error: setDeviceInfo");
            }
        });
        UCapCore.logAction({fname:'updateDeviceMetaInfo', params:obj.hid + ',' + obj.uid + ',' + obj.did + ',' + obj.name + ',' + obj.details + ',' + obj.photo});
    },

    setDeviceInfoEx:function (obj) {
        $.jsonRPC.request('ucap.updateDeviceMetaInfo_ex', {params:[obj.hid, obj.uid, obj.did, obj.name, obj.details, obj.notify, obj.notifyperc, obj.notified, obj.photo],
            success:function (data) {
                UCapManager.notification("notice", "The device information has been updated!");
            },
            error:function () {
                UCapManager.notification("error", "Error: setDeviceInfo");
            }
        });
        UCapCore.logAction({fname:'updateDeviceMetaInfo', params:obj.hid + ',' + obj.uid + ',' + obj.did + ',' + obj.name + ',' + obj.details + ',' + obj.notify + ',' + obj.notifyperc + ',' + obj.notified + ',' + obj.photo});
    },

    setDeviceState:function (obj) {
        $.jsonRPC.request('ucap.DeviceUsage', {params:['set', 'capped', obj.hid, obj.uid, obj.did, obj.state],
            success:function (data) {
                var result = data["result"];
                if (result != "Error") {
                    if (obj.state == 't') {
                        UCapManager.notification("notice", "This device is under cap constraints.");
                    } else {
                        UCapManager.notification("notice", "This device is no longer capped.");
                    }
                } else {
                    UCapManager.notification("error", "Error: setDeviceState");                        //Oops! Something went wrong. Please try again later.
                }
            },
            error:function () {
                UCapManager.notification("error", "Error: setDeviceState");
            }
        });
        UCapCore.logAction({fname:'DeviceUsage', params:'set,capped,' + obj.hid + ',' + obj.uid + ',' + obj.did + ',' + obj.state});
    },

    logAction:function (obj) {
        var date = new Date();
        var hid = localStorage["hid"];
        $.jsonRPC.request('ucap.logging_calls', {params:[hid, obj.fname, obj.params, date.toUTCString()]});
    },

    getSystemLogEx:function(obj){
        $.jsonRPC.request('ucap.user_logs_ex', {params:[obj.hid,obj.start,obj.end],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})");
            },
            error:function () {
                UCapManager.notification("error", "Error: getUserLogs within Rage");
            }
        });
    },

    getSystemLog:function(obj){
        $.jsonRPC.request('ucap.user_logs', {params:[obj.hid],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})");
            },
            error:function () {
                UCapManager.notification("error", "Error: getUserLogs");
            }
        });
    },

    getDeviceUsageHistory:function(obj){
        $.jsonRPC.request('ucap.get_device_usage_interval', {params:[obj.devices,obj.start,obj.end],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})");
            },
            error:function () {
                UCapManager.notification("error", "Error: getDeviceUsageHistory");
            }
        });
        UCapCore.logAction({fname:'get_device_usage_interval', params:obj.devices + ',' + obj.start + ',' + obj.end});
    },

    getHouseHoldDomainHistory:function(obj){
        $.jsonRPC.request('ucap.get_device_domain_interval', {params:[obj.hid,obj.num,obj.start,obj.end],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})"); //eval executes a function call based on function name (obj.func)
            },
            error:function () {
                UCapManager.notification("error", "Oops! Looks like we don't have any history for that period.");
            }
        });
        UCapCore.logAction({fname:'get_device_domain_interval', params:obj.hid + ',' + obj.num + ',' + obj.start + ',' + obj.end});
    },

    updateStartDate:function(obj){
        $.jsonRPC.request('ucap.update_house_startdate', {params:[obj.hid,obj.start],
            success:function (data) {
                var result = data["result"];
                UCapManager.notification("notice", "Start day for household updated.");
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})"); //eval executes a function call based on function name (obj.func)
            },
            error:function () {
                UCapManager.notification("error", "Oops! Could not set the start date for this household");
            }
        });
        UCapCore.logAction({fname:'update_house_startdate', params:obj.hid + ',' + obj.start});
    },

    lostPassword:function(obj){
        $.jsonRPC.request('ucap.lost_password', {params:[obj.email],
            success:function (data) {
                var result = data["result"];
                UCapManager.notification("notice", "Your password has been reset and sent to your email.");
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})"); //eval executes a function call based on function name (obj.func)
            },
            error:function () {
                UCapManager.notification("error", "Oops! No account found.");
            }
        });
        UCapCore.logAction({fname:'lost_password', params:obj.email});
    },

    findUser:function (obj) {
        for (var i = 0, l = UCapCore.users.length; i < l; i++) {
            if (UCapCore.users[i][0] == obj.uid) {
                return i;
            }
        }
    },

    findDevice:function (obj) {
        if (!obj.uid || !obj.did) {
            return null;
        }
        for (var i = 0, l = UCapCore.devices[obj.uid].length; i < l; i++) {
            if (UCapCore.devices[obj.uid][i][0] == obj.did) {
                return i;
            }
        }
    },
	
	getDeviceUsageOnDay:function(obj){
        $.jsonRPC.request('ucap.get_device_usage_on_day', {params:[obj.devices,obj.date],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})");
            },
            error:function () {
                UCapManager.notification("error", "Error: getDeviceUsageOnDay");
            }
        });
        UCapCore.logAction({fname:'get_device_usage_on_day', params:obj.devices + ',' + obj.date});
    },
	
	getDeviceDomainOnDay:function(obj){
        $.jsonRPC.request('ucap.get_device_domain_on_day', {params:[obj.hid,obj.num,obj.date],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})"); //eval executes a function call based on function name (obj.func)
            },
            error:function () {
                UCapManager.notification("error", "Oops! Looks like we don't have any history for that period.");
            }
        });
        UCapCore.logAction({fname:'get_device_domain_on_day', params:obj.hid + ',' + obj.num + ',' + obj.date});
    },
	
	getBytesOnDay:function(obj){
        $.jsonRPC.request('ucap.get_bytes_on_day', {params:[obj.hid,obj.date],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})"); //eval executes a function call based on function name (obj.func)
            },
            error:function () {
                UCapManager.notification("error", "Oops! Looks like we don't have any history for that period.");
            }
        });
        UCapCore.logAction({fname:'get_bytes_on_day', params:obj.hid + ',' + obj.date});
    },
	
	getOUI: function(obj){
		$.jsonRPC.request('ucap.get_oui', {params:[obj.oui_addr],
            success:function (data) {
                var result = data["result"];
                if(obj.func)
                    eval(obj.func + "({data:"+JSON.stringify(result)+"})"); //eval executes a function call based on function name (obj.func)
            },
            error:function () {
                UCapManager.notification("error", "Error: getOUI");
            }
        });
        UCapCore.logAction({fname:'getOUI', params:obj.hid + ',' + obj.date});
	}
};