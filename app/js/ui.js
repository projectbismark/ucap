/* Active Menu */
function ActiveMenu(){
    var user = UCapCore.findUser({uid:localStorage['uid']});
    user = UCapCore.users[user];
    var picture = (!user[6]) ? "default" : user[6];
    var name = (!user[1]) ? "Admin" : user[1];
    $('#accountInfo strong[name="userName"]').html(name);
    $('#accountInfo .profilePicThumb').attr('src', 'images/user_avatars/thumb/' + picture + '.jpg');
    $('#accountInfo .profilePicThumb').attr('title', name + '\'s Account');
}

/* Settings Page */
function SettingsPage() {
	UCapManager.loadModule({tar:'userContent', src:'settingAccount',act:'account',func:'Setting_account'})
}

function Setting_clearActive(){
    $('.activeDevice').remove();
}

function Setting_account() {
    $('input[name="household-address"]').val(UCapCore.household[1]);
    $('input[name="household-details"]').val(UCapCore.household[2]);
    var user = UCapCore.findUser({uid:localStorage['uid']});
    user = UCapCore.users[user];
    var picture = (!user[6]) ? "default" : user[6];
    $('#user-uid').val(user[0]);
    $('input[name="account-name"]').val(user[1]);
    $('input[name="account-email"]').val(user[8]);
    $('#profileCol .profilePic').attr('src', 'images/user_avatars/' + picture + '.jpg');
}

function Setting_point() {
	
}

function Settings_saveAccountInfo(){
    var householdAddress = $('input[name="household-address"]').val();
    var householdDetails = $('input[name="household-details"]').val();
    UCapCore.setHouseInfo({hid:UCapCore.household[0],address:householdAddress,details:householdDetails,photo:''});

    var newName = $('input[name="account-name"]').val();
    var newEmail = $('input[name="account-email"]').val();

    var user = UCapCore.findUser({uid:localStorage['uid']});
    user = UCapCore.users[user];

    $('#accountInfo strong[name="userName"]').html(newName);
    $('#accountInfo .profilePicThumb').attr('title', newName + '\'s Account');

    UCapCore.setUserInfo({hid:UCapCore.household[0], uid:user[0], name:newName, details:user[2], notify:user[3], notifypercent:user[4], notified:user[5], photo:user[6], role:user['7'], email:newEmail});
}

function Settings_selectAvatar(obj) {
    UCapManager.showDialog({src:obj.src,title:"Account Avatar",type:obj.type,style:"wide"});
}

function Settings_formatAvatarModal() {
    var avatars = ['default','barbarian_female','barbarian_male','child_female_dark','child_female_light','child_male_dark','child_male_light','client_female_dark',
                    'client_female_light','client_male_dark','client_male_light','cowboy','cowgirl','guitarist_female_dark',
                    'guitarist_female_light','guitarist_male_dark','guitarist_male_light','musician_female_dark',
                    'musician_female_light','musician_male_dark','musician_male_light','person_coffeebreak_female_dark','person_coffeebreak_female_light',
                    'person_coffeebreak_male_dark','person_coffeebreak_male_light','person_undefined_female_dark','person_undefined_female_light','person_undefined_male_dark','person_undefined_male_light','pilotoldfashioned_female_dark',
                    'pilotoldfashioned_female_light','pilotoldfashioned_male_dark','pilotoldfashioned_male_light','viking_female','viking_male'];
    $.each(avatars,function(index,value){
        var template = '<li><a href="javascript:Settings_saveAvatar({photoid:\''+value+'\'});"><img class="profilePic" src="images/user_avatars/'+ value +'.jpg" /></a></li>';
        $('#avatarList').append(template);
    });
}

function Settings_saveAvatar(obj){
    $('#modalBox').dialog( "close" );
    var uid = UCapManager.escape($('#user-uid').val());
    var user = UCapCore.findUser({uid:uid});
    user = UCapCore.users[user];
    user[6] = obj.photoid;
    $('#profileCol .profilePic').attr('src', 'images/user_avatars/'+ obj.photoid +'.jpg');
    $('#header .profilePicThumb').attr('src', 'images/user_avatars/thumb/'+ obj.photoid +'.jpg');
    Settings_saveAccountInfo();
}

function Settings_toggleChangePassword(){
    $('#changePassword').slideToggle('slow');
    $('#changePasswordFieldSet').slideToggle('slow');
}

function Settings_updateAccountPassword(){
    var uid = $('#user-uid').val();
    var user = UCapCore.findUser({uid:uid});
    user = UCapCore.users[user];
    var oldPass = $('input[name="old-account-password"]').val();
    var newPass = $('input[name="new-account-password"]').val();
    var confirmPass = $('input[name="confirm-new-account-password"]').val();
    if(newPass != confirmPass){
        UCapManager.notification("error", "The new password and confirm new password fields do not match. Please retype the password.");
    } else {
        UCapCore.changePassword({email:user[8],oldPass:oldPass,newPass:newPass});
        Settings_toggleChangePassword();
    }
}

/* History Page */
function HistoryPage() {

    var endDate = new Date();
    var startDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate() - 7);
    startDate = $.datepicker.formatDate("dd M yy",startDate);
    endDate = $.datepicker.formatDate("dd M yy",endDate);

    $("#startdate").val(startDate);
    $("#enddate").val(endDate);

    $( "#startdate").datepicker({
        minDate: -180,
        maxDate: 0,
        dateFormat: "dd M yy"
    });

    $("#enddate").datepicker({
        minDate: -90,
        maxDate: 0,
        dateFormat: "dd M yy"
    });

    History_showUsage();
}

function History_showUsage(){
    var start = $.datepicker.parseDate("dd M yy",  $( "#startdate").val());
    start = $.datepicker.formatDate( "yy-mm-dd", start);

    var end = $.datepicker.parseDate("dd M yy",  $( "#enddate").val());
    end = $.datepicker.formatDate( "yy-mm-dd", end);

    var deviceList = [];
    for(var x in UCapCore.devices){
        for(var y in UCapCore.devices[x]){
            deviceList.push(UCapCore.devices[x][y][0]);
        }
    }

    UCapCore.getDeviceUsageHistory({devices:deviceList,start:start,end:end,func:'History_drawGraph'});
    UCapCore.getHouseHoldDomainHistory({hid:UCapCore.household[0],num:10,start:start,end:end,func:'History_showList'});
    UCapCore.getSystemLogEx({hid:UCapCore.household[0],func:'History_formatSystemLog',start:start,end:end});

    $('#householdStats').slideDown('slow');
}

function History_drawGraph(obj){
    var total = 0;
    var dataSet = obj.data;
    var dataArray = [];
    for(var i in dataSet){
        for(var j in dataSet[i]){
            var temp = dataSet[i][j][0];
            temp = temp.split('-');
            dataSet[i][j][0] = Date.UTC(temp[0],temp[1]-1,temp[2]);
            dataSet[i][j][1] = Math.round(parseInt(dataSet[i][j][1])/1048576);
            total += dataSet[i][j][1];
        }
        dataArray.push({name:i,data:dataSet[i],borderWidth:0,shadow:false});
    }
    var template = "Total Household usage for this period: "+ total.toFixed(1);
    if(total/ 1073741824 < 1)
        template += " MB";
    else
        template += " GB";
    $('#totalUsage').html(template);
    UCapViz.drawTimeLine({tar:'usageChart',data:dataArray,yAxisLabel:'Bandwidth Usage (MB)'});
}

function History_showList(obj){
    var list = obj.data;
    var template = '<table id="topdomains" class="tablesorter"><thead><tr><th>Domain</th><th>Usage (MB)</th><th>Usage (%)</th></tr><thead><tbody>';

    for(var x in list){
		if (x == "other")
			continue;
		
        var usage;
        usage = (list[x][0][0]/ 1048576).toFixed(1);
        template += '<tr><td><strong>'+x+'</strong></td><td>'+usage+'</td><td>'+Math.round(list[x][0][1] * 100)+'<small class="light">%</small></td></tr>';
    }
    template += '</tbody></table>';
    $('#usageList').html(template);
    $("#topdomains").tablesorter({
		sortList: [[1,1]]	
	});
}

function History_formatSystemLog(obj){
    var log = obj.data;
    var template = '<ul>';
    var counter = 0;
    if(log != ""){
        log.reverse();
        for(var i in log){
            //if(counter < 5){
                template += History_systemLogFormatHelper({log:log[i]});
            //} else {
            //    break;
            //}
            //counter++;
        }    
    } else {
        template += '<li><em class="light">No changes were made during this period.</em></li>'
    }
    
    template += '</ul>';
    $('#logCanvas').html(template);
}

function History_systemLogFormatHelper(obj){
    var parms = obj.log[2].split(',');    
    var template;
    if(obj.log[1] == "DeviceUsage"){

        if(parms[1] == "capped"){
            var capped = (parms[5] != "f");
            var state = capped ? "enabled" : "disabled";
            template = 'Bandwidth cap was '+ state +' on '+parms[4]+'<br/>\
                         <span class="small light">'+ obj.log[3] +'</span>';
        } else if(parms[1] == "cap"){
            var cap = Math.round(parms[5]/1048576);
            template = 'Bandwidth cap for '+parms[4]+' was changed to '+ cap+' MB<br/>\
                         <span class="small light">'+ obj.log[3] +'</span>';
        }
    } else if(obj.log[1] == "HouseUsage") {
        var hcap;
        if(Math.round(parms[3]/ 1073741824) < 0.5)
            hcap = Math.round(parms[3]/ 1048576) + ' MB';
        else
            hcap = Math.round(parms[3]/ 1073741824) + ' GB';
        template = 'The household bandwidth cap was changed to '+ hcap +'<br/>\
                     <span class="small light">'+ obj.log[3] +'</span>';
    }
    return '<li>'+template+'</li>';
}

/* Network Page */
function NetworkPage() {
    UCapManager.loadModule({tar:'userContent', src:'networkOverview', act:'overview',func:'Network_deviceList'});
    UCapManager.startScheduler({func:'Network_deviceList', scope:"page", freq:3500});
}

function Network_deviceList() {
    var active = UCapManager.getCurrentSubPage();
    var view1DeviceList = [];
    var view2DeviceList = [];
    var activeDevice = '';
    for (var i = 0, j = UCapCore.users.length; i < j; i++) {
        if(UCapCore.devices[UCapCore.users[i][0]].length > 0){
            for(var l = 0, m = UCapCore.devices[UCapCore.users[i][0]].length; l < m; l++){
                var device = UCapCore.devices[UCapCore.users[i][0]][l];
                var picture = (!device[3]) ? "default" : device[3];
                var id = device[0];
                var title = device[1];
                var desc = device[2];
                var link = "javascript:loadModule({tar:'userContent',src:'deviceOverview',act:'"+ id +"',uid:'" + UCapCore.users[i][0] + "',did:'" + device[0] + "',func:'Network_deviceList'});";

                //View1 Stuff
                if(active == device[0]){
                    activeDevice = "<li id=\""+id+"\" class=\"activeDevice\"><div id=\"activeDevice\"><a href=\""+ link +"\"><img class=\"profilePic\" title=\""+ title +"\" src=\"images/avatars/thumb/"+ picture +".jpg\"/><div><b>"+ UCapManager.abridge({text:title,length:12}) +"</b><br/><em class=\"light\">"+ UCapManager.abridge({text:desc,length:20}) +"</em></div></a></div></li>";
                    activeDevice += "<li class=\"separator activeDevice\"></li>";
                    view1DeviceList.push("<li id=\""+ id +"-holder\"><img class=\"thumbPic\" title=\""+ title +"\" src=\"images/avatars/thumb/" + picture + ".jpg\"/></li>");
                } else {
                    view1DeviceList.push("<li id=\""+ id +"\"><a class=\"elementBlock\" href=\""+ link +"\" ><img class=\"thumbPic\" title=\""+ title +"\" src=\"images/avatars/thumb/" + picture + ".jpg\"/></a></li>");
                }

                //View2 Stuff
                var name = (active == device[0])? '<b>'+ UCapManager.abridge({text:title,length:20})+'</b>' : UCapManager.abridge({text:title,length:15});
                view2DeviceList.push("<li id=\""+ id +"\"><a class=\"elementBlock\" href=\""+ link +"\" ><img width=\"32px\" height=\"32px\" class=\"thumbPic\" title=\""+ title +"\" src=\"images/avatars/thumb/" + picture + ".jpg\"/> "+ name +" </a></li>");
            }
        }
    }
    if(view1DeviceList.length > 0){
        var template1 = '<ul id="deviceList" class="clearfix" >'+view1DeviceList.join('')+"</ul>";
        $('#deviceView1').html(template1);
        $('.activeDevice').remove();
        $('#userList').append(activeDevice).show('slow');
    } else {
        $('#deviceView1').html('');
        $('.activeDevice').remove();
        $('#userList').append(activeDevice).show('slow');
        $('#userList li').last().remove();
    }

    if(view2DeviceList.length > 0){
        var template2 = '<ul id="deviceList2" class="clearfix" >'+view2DeviceList.join('')+"</ul>";
        $('#deviceView2').html(template2);
    }
}

function Network_clearActive(){
    $('.activeDevice').remove();
}

function Network_deviceViewSwitcher(){
    if($('#deviceViews').is(':visible')){
        $('#deviceViews').slideUp();
    } else {
        $('#deviceViews').slideDown();
    }

    $('#deviceListView').click(function(){
        if(!$('#deviceListView').is('.active')){
            $('#deviceView1').hide("slide", { direction: "right" }, function(){
                $('#deviceView2').show("slide", { direction: "right" }, 1000);
            }, 1000);
            $('#deviceTileView').removeClass('active');
            $('#deviceListView').addClass('active');
        }
    });

    $('#deviceTileView').click(function(){
        if(!$('#deviceTileView').is('.active')){
            $('#deviceView2').hide("slide", { direction: "right" }, function(){
                $('#deviceView1').show("slide", { direction: "right" }, 1000);
            }, 1000);
            $('#deviceListView').removeClass('active');
            $('#deviceTileView').addClass('active');
        }
    });
}

/* Network Page > Network Overview */
function Network_networkOverview() {
    UCapManager.startScheduler({func:'Network_Overview_householdUsage', scope:"element", freq:1000});
    var dataArray = [];
    for (var i in UCapCore.devices)
    {    for(var j = 0, k = UCapCore.devices[i].length; j < k; j++){
            var devicename = UCapCore.devices[i][j][1];
            var deviceusage = (UCapCore.devices[i][j][6]/1048576);
            dataArray.push([devicename,deviceusage]);
        }
    }
    UCapViz.drawChart({tar:'chartarea',data:dataArray});
}

function Network_Overview_householdUsage() {
    var cap = UCapCore.household[4];
    var usage = UCapCore.household[5];
    var template1,template2, template3;
    if(!isNaN(cap) && !isNaN(usage) && !(cap < 0) && !(usage < 0)){
        //No Cap
        if(cap == -1 || cap == 0){
            template1 = "This household does not have an active bandwidth cap. <a href=\"javascript:loadModule({tar:'userContent',src:'networkManager',act:'manager',func:'Network_Manager_capManagement'});Network_clearActive();\">Would you like to set one?</a>";
            $('#household-usagestatus').html(template1);
            if(Math.round(usage/1073741824) <= 1)
                template2 = Math.round(usage / 1048576) + " MB being used.";
            else
                template2 = Math.round(usage / 1073741824) + " GB being used.";
            $('#household-usageprogress').html(template2);
            UCapViz.drawProgressBar({tar:"household-progressbar", val:0, disabled:true});
        } else {
            var progress = Math.round((usage / cap) * 100);
            template1 = "This household currently has ";
            if(Math.round((cap - usage)/1073741824) < 1)
                template1 += Math.round((cap - usage) / 1048576) + " MB of bandwidth left for this month."; //<br/>"+daysRemaining+" days until the next billing cycle starts.";
            else
                template1 += Math.round((cap - usage) / 1073741824) + " GB of bandwidth left for this month."; //<br/>"+daysRemaining+" days until the next billing cycle starts.";
            $('#household-usagestatus').html('<h3>'+template1+'</h3>');

            if(Math.round(usage/1073741824) <= 1)
                template2 = Math.round(usage / 1048576) + " MB or " + progress + "% of " + Math.round(cap / 1073741824) + "GB being used.";
            else
                template2 = Math.round(usage / 1073741824) + " GB or " + progress + "% of " + Math.round(cap / 1073741824) + "GB being used.";
            $('#household-usageprogress').html(template2);

            UCapViz.drawProgressBar({tar:"household-progressbar", val:progress});
			
			//Logic to calculate days remaining goes here.
//            var month = new Date().getMonth();
//            var billingDate = UCapCore.household[7].split(' ').slice(0,1);
//            billingDate = billingDate[0].split('-');
//            var day = billingDate[2];
//
//            var monthLength = new Date(billingDate[0], parseInt(month), 0).getDate();
//            var daysRemaining = monthLength-day;
			var today = new Date();
			var billingDay = UCapCore.household[7].split(' ');
			billingDay = billingDay[0].split('-');
			billingDay = new Date(billingDay[0], billingDay[1] - 1, billingDay[2]);
			billingDay.setMonth(billingDay.getMonth( ) + 1 );
			
			var daysRemaining = differenceInDays(today, billingDay);
			if (daysRemaining == 1)
				template3 = daysRemaining + " day";
			else
				template3 = daysRemaining + " days";
			template3 += " to end of billing cycle."
			$('#household-billingstatus').html('<h3>'+template3+'</h3>');
        }
    }
}

function Network_Manager_capManagement(){
	var startDay = UCapCore.household[7];
	if (startDay != undefined)
	{
		var startDay = UCapCore.household[7].split(' ').slice(0,1);
		startDay = startDay[0].split('-');
		startDay = new Date(startDay[0], parseInt(startDay[1] - 1), startDay[2]);
		startDay = $.datepicker.formatDate("dd M yy",startDay);
		$("#startday").val(startDay);
	}

    $( "#startday").datepicker({
        dateFormat: "dd M yy"
    });

    var deviceCapList = [];
    var allocatedBandwidth = 0;
    for (var i in UCapCore.devices)
    {    for(var j = 0, k = UCapCore.devices[i].length; j < k; j++)
        {
            var deviceId = UCapCore.devices[i][j][0];
            var deviceName = UCapCore.devices[i][j][1];
            var deviceDescription = UCapCore.devices[i][j][2];
            var picture = UCapCore.devices[i][j][3] != "" ? UCapCore.devices[i][j][3] : "default";

            var capped = (UCapCore.devices[i][j][4] != "f");
            var check = capped ? "checked=\"checked\"" : "";
            var enabled = capped ? "" : "disabled";

            var cap = capped && !isNaN(UCapCore.devices[i][j][5]) && UCapCore.devices[i][j][5] != -1 ? Math.round(UCapCore.devices[i][j][5] / 1048576) : ''; //bytes to Megabytes
            var deviceUsage = (UCapCore.devices[i][j][6] / 1048576).toFixed(0); //bytes to Megabytes
            var temp = '<tr>';
                temp += '<td class="textCenter"><input type="checkbox" name="'+ i + '-' + deviceId + '" value="'+ enabled +'" '+ check +'/></td>';
                temp += '<td class="textCenter"><img width="32" height="32" src="images/avatars/thumb/'+ picture +'.jpg" style="vertical-align:middle;" /></td>';
                temp += '<td>'+ deviceName +' <span class="light small">('+ deviceDescription +')</span></td>';
                temp += '<td>'+ deviceUsage +' MB </td>';
                temp += '<td  class="textCenter"><input name="'+ i + '-' + deviceId + '" type="text" class="inline smallField '+ enabled +'" value="'+ cap +'" />&nbsp;MB</td>';
                temp += '</tr>';
            deviceCapList.push(temp);

            if(capped)
                allocatedBandwidth += cap;
        }
    }

    if(Math.round(allocatedBandwidth/1024) < 1)
        $('strong[name="allocated-badwidth"]').html((allocatedBandwidth).toFixed(2)+" MB");
    else
        $('strong[name="allocated-badwidth"]').html((allocatedBandwidth/1024).toFixed(2)+" GB");

    if (deviceCapList.length > 0) {
        var headerTemplate = '<tr><th>Cap Enabled</th><th></th><th style="width:45%">Device</th><th>Device Usage</th><th>Cap Amount</th></tr>';
        $('#usageCaps').html(headerTemplate + deviceCapList.join(''));

        $('#usageCaps').delegate("input[type='text']", "click", function(e) {
            var details = $(this).attr('name').split('-');
            if($(this).is('.disabled')){
                $(this).removeClass('disabled');
            }
        });

        $('#usageCaps').delegate("input[type='text']", "change", function(e) {
            var details = $(this).attr('name').split('-');
            var device = UCapCore.findDevice({uid:details[0], did:details[1]});
            device = UCapCore.devices[details[0]][device];
            if($(this).val()*1048576 < device[6]){
                var devusage = Math.round(device[6] / 1048576);
                UCapManager.notification("error", "You cannot set a cap that is lower than the device's current usage which is "+devusage+" MB.");
            } else {
                Network_Manager_updateDeviceCap({uid: details[0] ,did: details[1],val: UCapManager.escape($(this).val())});
                var state = $(this).parent().parent().find("input[type='checkbox']");
                state.attr('checked','checked');
                Network_Manager_toggleDeviceCapping({uid: details[0] ,did: details[1],state:'t'});
            }
        });

        $('#usageCaps').delegate("input[type='checkbox']", "click", function(e) {
            var details = $(this).attr('name').split('-');
            var cap = $(this).parent().parent().find("input[type='text']");
            if($(this).is(':checked')){
                UCapManager.notification("error", "You cannot enable a device cap without setting a cap. Use the textbox to enter the device cap.");
                $(this).attr('checked', false);
            }else{
                var unsetCap =  cap.val();
                cap.val('');
                cap.addClass('disabled');
                var allocated = $('strong[name="allocated-badwidth"]').html().split(' ');

                if(allocated[1] == "GB")
                    $('strong[name="allocated-badwidth"]').html( (allocated[0] - (unsetCap/1024)).toFixed(2)+ ' GB');
                else
                    $('strong[name="allocated-badwidth"]').html( (allocated[0] - unsetCap).toFixed(2) + ' MB');

                Network_Manager_toggleDeviceCapping({uid: details[0] ,did: details[1],state:'f'});
            }
        });

    }
    var householdcap = (!isNaN(UCapCore.household[4]) && UCapCore.household[4] != -1) ? Math.round(UCapCore.household[4] / 1073741824) : 0;
    $('input[name="household-cap"]').val(householdcap);
}

function Network_Manager_toggleDeviceCapping(obj){
    UCapCore.setDeviceState({hid:UCapCore.household[0],uid:obj.uid,did:obj.did,state:obj.state});
}

function Network_Manager_updateDeviceCap(obj){
    var device = UCapCore.findDevice({uid:obj.uid, did:obj.did});
    device = UCapCore.devices[obj.uid][device];

    //old cap
    var oldcap = (device[4] != "f") ? device[5] : 1;
    var newcap = UCapManager.escape(obj.val) * 1048576;
    UCapCore.setDeviceCap({hid:UCapCore.household[0],uid:obj.uid,did:obj.did,cap:newcap});

    var allocatedBandwidth = $('strong[name="allocated-badwidth"]').html().split(" ");
    if(allocatedBandwidth[1] == "MB"){
        allocatedBandwidth[0] = parseInt(allocatedBandwidth[0]) + ((newcap - oldcap)/1048576);
        $('strong[name="allocated-badwidth"]').html((allocatedBandwidth[0]).toFixed(2)+" MB");
    } else {
        allocatedBandwidth[0] = parseInt(allocatedBandwidth[0]) + ((newcap - oldcap)/1073741824);
        $('strong[name="allocated-badwidth"]').html((allocatedBandwidth[0]).toFixed(2)+" GB");
    }
}

function Network_Manager_saveNetworkInfo() {
    var updatedCap = UCapManager.escape($('input[name="household-cap"]').val());
    updatedCap = Math.round(updatedCap * 1073741824);
    UCapCore.setHouseCap({hid:UCapCore.household[0],cap:updatedCap});
}

function Network_Manager_saveStartDate() {
    var startday = new Date(UCapManager.escape($('#startday').val()));
    var date = $.datepicker.formatDate( "yy-mm-dd", startday);
    UCapCore.updateStartDate({hid:UCapCore.household[0],start:date});
}

/* Network Page > Device Overview */
function Network_deviceOverview(obj) {
    var item = UCapCore.findDevice({uid:obj.uid, did:obj.did});
    item = UCapCore.devices[obj.uid][item];
    var picture = (!item[3]) ? "default" : item[3];
    $('#profileCol .profilePic').attr('src', 'images/avatars/' + picture + '.jpg');
    $('#user-uid').val(obj.uid);
    if ($('input[name="device-name"]').length > 0){
        $('input[name="device-name"]').val(item[1]);
    } else {
        $('span[name="device-name"]').html(item[1]);
    }
    $('#device-mac-address').html(item[0]);
	
	//OUI
	UCapCore.getOUI({oui_addr:item[0].substring(0,6),func:'Network_Device_getOUI'});

    if ($('input[name="device-description"]').length > 0){
        $('input[name="device-description"]').val(item[2]);
    } else {
        $('span[name="device-description"]').html(item[2]);
    }

    //Is Notification set?
	$('#notifypercent').val( item[8]  == null ? 50 : item[8]);
	if(item[7] == "t"){
        $('#notify').prop("checked", true);
	} else {
		$('#notify').prop("checked", false);
	}
	
	Network_Device_toggleDeviceNotification();
	
//    if ($('#notifypercent').length > 0){
//        $('#notifypercent').val( item[8]  == null ? 50 : item[8]);
//        if(item[7] == "t"){
//            $('#notify').prop("checked", true);
//
//        } else {
//            $('#notify').prop("checked", false);
//            $('#notification li:last-child').slideToggle("show");
//        }
//    }

    UCapManager.startScheduler({func:'Network_Device_usageProgress', args:'{uid:"' + obj.uid + '",did:"' + obj.did + '"}', scope:"element", freq:1300});
}

function Network_Device_getOUI(obj) {
    $('#device-mac-oui').html(obj.data[0]);
}

function Network_Device_selectAvatar(obj) {
    UCapManager.showDialog({src:obj.src, title:"Device Avatar", type:obj.type, style:"wide"});
}

function Network_Device_formatAvatarModal() {
    var avatars = ['blurayplayer_disc','computer','dvdbox_dvd','gamingwheel','hddvd',
    'homeserver','inkjetprinter','modem_blue','netbook','pda1','pda2','plasmadisplay1',
    'portablecomputer','portabledvdplayer','securitycamera','smartphone','tvsetretro',
    'bike', 'boat', 'butterfly', 'car', 'cat', 'cat_illustration', 'cupcake', 'default', 'elephant', 'fish', 'flower',
        'flower2', 'giraffes', 'guitar', 'headphones', 'monkey', 'orange', 'palmtree', 'penguin', 'plane', 'puppy', 'soccer'];
    $.each(avatars, function (index, value) {
        var func = "javascript:Network_Device_saveAvatar({photoid:'"+ value +"'});";
        var template = "<li><a href=\""+ func +"\"><img class=\"profilePic\" src=\"images/avatars/"+ value +".jpg\" /></a></li>";
        $('#avatarList').append(template);
    });
}

function Network_Device_saveAvatar(obj) {
    $('#modalBox').dialog("close");
    var uid = UCapManager.escape($('#user-uid').val());
    var did = UCapManager.escape($('#device-mac-address').html());
    var item = UCapCore.findDevice({uid:uid, did:did});
    item = UCapCore.devices[uid][item];
    item[3] = obj.photoid;
    $('#profileCol .profilePic').attr('src', 'images/avatars/' + obj.photoid + '.jpg');
    Network_Device_saveDeviceInfo();
}



// Draw the progress bar and update the usage.
function Network_Device_usageProgress(obj) {
    var item = UCapCore.findDevice({uid:obj.uid, did:obj.did});
    item = UCapCore.devices[obj.uid][item];
    var total = (!isNaN(item[5]) && item[5] != -1) ? Math.round(item[5] / 1048576) : 1; //bytes to Megabytes
    var used = (!isNaN(item[6]) && item[6] != -1) ? Math.round(item[6] / 1048576) : 1; //bytes to Megabytes
    var progress = Math.round((used / total) * 100);
    if (item[4] == "f") {
        UCapViz.drawProgressBar({tar:'bar', val:0, disabled:true});
        $('div[name="progress-status"]').html(used + " MB Used");
    } else {
        UCapViz.drawProgressBar({tar:'bar', val:progress});
        if(progress >= 100)
            $('div[name="progress-status"]').html("This device is currently capped.<br/> You have exceeded the bandwidth cap of " + total + "MB allocated to this device.");
        else
            $('div[name="progress-status"]').html(used + " MB or " + progress + "% of " + total + "MB Used");
    }
}

function Network_Device_toggleDeviceNotification()
{
	$('#notifypercent').prop('disabled', !$('#notify').prop("checked"));
}

function Network_Device_saveDeviceInfo() {
    var uid = UCapManager.escape($('#user-uid').val());
    var name = UCapManager.escape($('input[name="device-name"]').val());
    var did = UCapManager.escape($('#device-mac-address').html());
    var details = UCapManager.escape($('input[name="device-description"]').val());

    var item = UCapCore.findDevice({uid:uid, did:did});
    item = UCapCore.devices[uid][item];
    var photo = (!item[3]) ? "default" : item[3];

    UCapCore.setDeviceInfo({hid:UCapCore.household[0], uid:uid, did:did, name:name, details:details, photo:photo});

    var user = UCapCore.findUser({uid:uid});
    var notifypercent = parseInt(UCapManager.escape($('#notifypercent').val()), 10);

//    if((($('#notify').prop("checked") && item[7] == "f")) || ((!$('#notify').prop("checked")) && item[7] == "t")){
//        var notify;
//        if($('#notify').prop("checked") && item[7] == "f"){
//            $('#notification li:last-child').slideToggle("hide");
//            notify = "t";
//        } else {
//            $('#notification li:last-child').slideToggle("show");
//            notify = "f";
//        }
//        UCapCore.setDeviceInfoEx({hid:UCapCore.household[0], uid:uid, did:did, name:name, details:details, notify:notify, notifyperc:item[8], notified:user[5], photo:photo});
//    }
	
	var notify = $('#notify').prop("checked") ? "t" : "f";
	UCapCore.setDeviceInfoEx({hid:UCapCore.household[0], uid:uid, did:did, name:name, details:details, notify:notify, notifyperc:notifypercent, notified:UCapCore.users[1][5], photo:photo});


//    if(notifypercent != item[8]){
//        UCapCore.setDeviceInfoEx({hid:UCapCore.household[0], uid:uid, did:did, name:name, details:details, notify:item[7], notifyperc:notifypercent, notified:user[5], photo:photo});
//    }
}


/* Reward Page */
function RewardPage() {
	UCapManager.loadModule({tar:'userContent', src:'rewardOverview', act:'overview',func:'Reward_rewardOverview'});
}

function Reward_clearActive(){
    $('.activeDevice').remove();
}

function Reward_rewardOverview() {
    var today = new Date();
    var date = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1);
    date = $.datepicker.formatDate("dd M yy",date);

    $("#date").val(date);
    $( "#date").datepicker({
        minDate: -180,
        maxDate: -1,
        dateFormat: "dd M yy"
    });

    Reward_rewardOverview_showUsage();
}

function Reward_rewardOverview_showUsage() {
	var date = $.datepicker.parseDate("dd M yy",  $( "#date").val());
    date = $.datepicker.formatDate( "yy-mm-dd", date);

    var deviceList = [];
    for(var x in UCapCore.devices){
        for(var y in UCapCore.devices[x]){
            deviceList.push(UCapCore.devices[x][y][0]);
        }
    }

    UCapCore.getDeviceUsageOnDay({devices:deviceList,date:date,func:'Reward_rewardOverview_drawDeviceUsageGraph'});
    UCapCore.getBytesOnDay({hid:UCapCore.household[0],date:date,func:'Reward_rewardOverview_drawBandwidthUsageGraph'});
	UCapCore.getBytesOnDay({hid:UCapCore.household[0],date:date,func:'Reward_rewardOverview_drawBandwidthUsagePercentage'});
	UCapCore.getDeviceDomainOnDay({hid:UCapCore.household[0],num:5,date:date,func:'Reward_rewardOverview_showTopDomainList'});
    
    $('#rewardOverviewStat').slideDown('slow');
}

function Reward_rewardOverview_drawDeviceUsageGraph(obj) {
    var dataSet = obj.data;
    var dataArray = [];
	var total = 0;
	var timezone = getTimeZone();
	timezone = timezone * -1 * 60 * 60 * 1000;
	
    for(var i in dataSet){
        for(var j in dataSet[i]){
            var temp = dataSet[i][j][0];
            temp = temp.split(' ');
			var date = temp[0].split('-');
			var time = temp[1].split(':');
			var utc = Date.UTC(date[0],date[1]-1,date[2],time[0],time[1],time[2]);
            dataSet[i][j][0] = utc + timezone;
            dataSet[i][j][1] = Math.round(parseInt(dataSet[i][j][1])/1048576);
			total += dataSet[i][j][1];
        }
        dataArray.push({name:i,data:dataSet[i],borderWidth:0,shadow:false});
    }
	
	if (total > 0) {
    	UCapViz.drawHourlyUsage({tar:'usage_chartarea',data:dataArray,yAxisLabel:'Bandwidth Usage (MB)'});
		$('#usage_status').empty();		
	}
	else {
		var template = "There is no data for this period.";
		$('#usage_status').html(template);
		$('#usage_chartarea').empty();	
	}
}

function Reward_rewardOverview_drawBandwidthUsageGraph(obj) {
	var dataSet = obj.data;
    var dataArray = [];
	var total = 0;
	var timezone = getTimeZone();
	timezone = timezone * -1 * 60 * 60 * 1000;
	
    for(var i in dataSet) {
		var temp = dataSet[i][0];
		temp = temp.split(' ');
		var date = temp[0].split('-');
		var time = temp[1].split(':');
		var utc = Date.UTC(date[0],date[1]-1,date[2],time[0],time[1],time[2]);
		dataSet[i][0] = utc + timezone;
		dataSet[i][1] = Math.round(parseInt(dataSet[i][1])/1048576);
		total += dataSet[i][1];
    }
	dataArray.push({showInLegend:false,name:"Bandwidth Usage per Hour",data:dataSet,borderWidth:0,shadow:false});
	
	if (total > 0) {
    	UCapViz.drawHourlyUsage({tar:'bytes_chartarea',data:dataArray,yAxisLabel:'Bandwidth Usage (MB)'});
		$('#bytes_status').empty();		
	}
	else {
		var template = "There is no data for this period.";
		$('#bytes_status').html(template);
		$('#bytes_chartarea').empty();	
	}
}

function Reward_rewardOverview_drawBandwidthUsagePercentage(obj) {
	var dataSet = obj.data;
    var dataArray = [];
	var total = 0;
	var timezone = getTimeZone();
	timezone = -1 * timezone;
	
    for (var i in dataSet) {
		var temp = dataSet[i][0];
		temp = temp.split(' ');
		
		var time = temp[1].split(':');
		var date = new Date();
		date.setHours(parseInt(time[0],10) + timezone);
		var hour = "" + date.getHours();
		if (hour.length == 1)
			hour = "0" + hour;
		time = hour + ":00:00";
		
		var usage = Math.round(parseInt(dataSet[i][1])/1048576);
		total += usage;
		dataArray.push([time,usage]);
    }
	
	if (total > 0) {
    	UCapViz.drawHourlyUsageChart({tar:'bytes_piechartarea',data:dataArray});
	}
	else {
		$('#bytes_piechartarea').empty();	
	}
}

function Reward_rewardOverview_showTopDomainList(obj) {
	var list = obj.data;
	var timezone = getTimeZone();
	timezone = -1 * timezone;
	
	var reset_template = "No data for this period."
	for (var i = 0; i < 24; i++){
		if ( i <= 9)
			$('#time0' + i).html(reset_template);
		else
			$('#time' + i).html(reset_template);
	}	
	
	for (var entry in list) {
		var date = entry.split(' ');	
		var time = date[1].split(':');
		var date = new Date();
		date.setHours(parseInt(time[0],10) + timezone);
		var hour = "" + date.getHours();
		if (hour.length == 1)
			hour = "0" + hour;
		
		var template = '<table id="topdomains'+hour+'" class="tablesorter"><thead><tr><th>Domain</th><th>Usage (MB)</th></tr><thead><tbody>';
	
		for(var x in list[entry]){
			var domain = list[entry][x][0];
			if (domain == null)
				domain = "unknown";
			
			var usage = (list[entry][x][1]/ 1048576).toFixed(1);
			template += '<tr><td><strong>'+domain+'</strong></td><td>'+usage+'</td></tr>';
		}
		template += '</tbody></table>';
		
		$('#time' + hour).html(template);
		$('#topdomains' + hour).tablesorter({
			//sortList: [[1,1]]	
		});
	}
}

function Reward_redemption() {

}


/* Support */
function SupportPage() {
	UCapManager.loadModule({tar:'userContent', src:'faqs', act:'faqs',func:'Support_faqs'});
}

function Support_clearActive(){
    $('.activeDevice').remove();
}

function Support_faqs() {
	$('.faq-title').each(function() {
		var faq = $(this);
		var description = faq.next("div").slideUp(0);
		faq.prop("state", false);
    
		faq.click(function() {
			var state = faq.prop("state");
			if (state)
				faq.css("background", "url('images/arrow_right.png') no-repeat left center");
			else
				faq.css("background", "url('images/arrow_down.png') no-repeat left center");
			faq.prop("state", !state);
			
      		description.slideToggle("slow");
    	});
  	});
}

function Support_contact() {
	var user = UCapCore.findUser({uid:localStorage['uid']});
    user = UCapCore.users[user];
	
	var mForm = document.forms["contact_us_form"];
	mForm.name.value = user[1];
	mForm.email.value = user[8];
}

function Support_sendContactUsForm() {
	var mForm = document.forms["contact_us_form"];
		var mIssue = mForm.issue.value;
		var mName = mForm.name.value;
		var mEmail = mForm.email.value;
		var mMessage = mForm.message.value;
		
		$.ajaxSetup (
		{
			cache: false
		});
		
		var ajax_load = "<p><img src='mages/ajax-loader.gif' />Sending email...</p>";
		var loadUrl = "lib/sendcontact.php";
		var query = { issue: mIssue,
					  name: mName,
					  email: mEmail,
					  message: mMessage };
		
		$("#status").html(ajax_load);
		$.ajax ({
			type: "POST",
			url: loadUrl,
			data: query,
			dataType: "text",
			async: false,
			timeout: 5000, //5 seconds
			success: function(data) 
			{
				$("#status").html(data);
			},
			error: function(jqXHR, textStatus, errorThrown) 
			{
				$("#status").html("<p class='error'>" + jqXHR.status + ": " + jqXHR.statusText + "</p>");
			}
		});
}


/* Login */
function signIn() {
    UCapCore.userLogin({username:$('#username').val(), passwd:$('#password').val()});
}

function signOut() {
    UCapCore.userLogout();
}

function toggleReset(){
    $('.toggleReset').toggle();
}

function resetPassword(){
    var email = UCapManager.escape($('#username').val());
    UCapCore.lostPassword({email:email});
    $('.toggleReset').toggle();
}



/* Redirect Fn */
function loadModule(obj){
    UCapManager.loadModule(obj);
}

function showPage(obj){
    UCapManager.showPage(obj);
}

function uploadImage(){
    //inset logic here
}

function isAdmin() {
    return UCapCore.isAdmin();
}
