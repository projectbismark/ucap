$(document).ready(function() {
    UCapCore.isAuthed();
});

var UCapManager = {
    dispatcher: [],

    /* Initialize Data*/
    initializeData: function(){
        var hid = localStorage["hid"];
        UCapCore.getHouse({hid:hid});
        UCapCore.getUsers({hid:hid});
        UCapManager.startScheduler({func:'UCapCore.getUsers',args:'{hid:"'+hid+'"}',scope:"application",freq:5000});
        UCapManager.startScheduler({func:'UCapCore.getHouse',args:'{hid:"'+hid+'"}',scope:"application",freq:5500});
    },

    /* Basic Page & Module Loaders */
    showLoginPage: function() {
        UCapManager.loadInactiveHeader();
        $('#content').load('views/login.html');
    },

    showPage: function(obj) {
        //first stop any schedulers from other pages.
        UCapManager.cleanScheduler({scope:"page"});
        UCapManager.loadActiveHeader();
        $('#content').load('views/' + obj.pageID + '.html',function(){
            if(obj.func)eval(obj.func + "()");
        }).hide().fadeIn(800);
        UCapManager.setMenuTabActive(obj.pageID);
    },

    getCurrentPage: function(){
        return localStorage['currentPage'];
    },

    setCurrentPage: function(pageID){
        localStorage['currentPage'] = pageID;
    },

    getCurrentSubPage: function(){
        return localStorage['currentSubPage'];
    },

    setCurrentSubPage: function(pageID){
        localStorage['currentSubPage'] = pageID;
    },

    loadActiveHeader: function () {
        $('#header').load('views/elements/activeHeader.html');
    },

    loadInactiveHeader: function() {
        $('#header').load('views/elements/inactiveHeader.html');
    },

    /* Menu Bar */
    setMenuTabActive: function(divID)  {
        $('#menu').load('views/elements/topMenu.html', function() {
            $("#menuBar").removeClass("active");
            $("li#" + divID).addClass("active");
            UCapManager.setCurrentPage(divID);
            UCapManager.setCurrentSubPage("");
        });
    },

    hideMenuBar: function() {
        $('#menu').html('');
    },


    loadModule: function (obj) {
        $('#' + obj.tar).load('views/elements/' + obj.src + '.html', function() {
            if (obj.act !== null) {
                $('#' + UCapManager.getCurrentSubPage()).parent().children(".active").removeClass("active");
                $('#' + obj.act).addClass("active");
                UCapManager.cleanScheduler({scope:"module"});
                UCapManager.setCurrentSubPage(obj.act);
            }
            if(obj.src == "networkOverview"){
                Network_networkOverview();
            }else if(obj.src == "deviceOverview"){
                Network_deviceOverview({uid:obj.uid,did:obj.did});
            }
            if(obj.func)eval(obj.func + "()");
        }).hide().fadeIn(500);
    },


    /* General Helpers */
    supportsLocalStorage: function() {
        return Modernizr.localstorage;
    },

    startScheduler: function(obj) {
        //execute once
        if(obj.args)
                eval(obj.func + "(" + obj.args + ")");
            else
                eval(obj.func + "()");

        //now start the scheduler
        var schedulerID = window.setInterval(function() {
            if(obj.args)
                eval(obj.func + "(" + obj.args + ")");
            else
                eval(obj.func + "()");
        }, obj.freq);

        var tmp = new Array(schedulerID,obj.scope);
        UCapManager.dispatcher.push(tmp);
    },

    stopScheduler: function(obj) {
        window.clearInterval(obj.id);
    },

    cleanScheduler: function(obj){
        var bkp = UCapManager.dispatcher;
        for(var i=0, l=bkp.length; i<l; i++){
            if(bkp[i][1] == obj.scope){
                UCapManager.stopScheduler({id:bkp[i][0]});
                var removeItem = bkp[i];
                UCapManager.dispatcher = $.grep(UCapManager.dispatcher, function(value){
                    return value != removeItem;
                });
            }
        }

        if(obj.scope == "application"){
             UCapManager.cleanScheduler({scope:"page"});
        }

        if(obj.scope == "page"){
            UCapManager.cleanScheduler({scope:"module"});
        }

        if(obj.scope == "module"){
            UCapManager.cleanScheduler({scope:"element"});
        }
    },

    escape: function(str) {
        return str.replace(/'/g, "\\'");
    },

    capFirstLetter: function(str){
        str = str.toLowerCase().replace(/\b[a-z]/g, function(letter) {
            return letter.toUpperCase();
        });
        return str;
    },

    abridge: function (obj) {
        var txt = obj.text;
        var len = obj.length;
        var dots = '&#8230;';
        if (txt.length <= len)
            return txt;
        else
            return $.trim(txt.substring(0, len)) + dots;
    },

    /* Notification */
    notification: function(type, msg) {
        $('#noticeBox').removeClass();
        $('#noticeBox .content').html(msg);
        if (type == 'error') {
            $('#noticeBox').addClass('error-toast').fadeIn('slow', function () {
                $('#noticeBox').delay(4000).fadeOut('slow');
            });
        } else {
            $('#noticeBox').addClass('notice-toast').fadeIn('slow', function () {
                $('#noticeBox').delay(4000).fadeOut('slow');
            });
        }
    },

    /* Dialog Box */
    showDialog: function(obj){
    $('#modalBox').load('views/elements/' + obj.src + '.html', function() {
            if(obj.src == "avatarSelectModal"){
                if(obj.type == "device")
                    Network_Device_formatAvatarModal();
                else if (obj.type == "user")
                    Settings_formatAvatarModal();
            }

            if(obj.src == "formModal"){
               eval(obj.fn + "()");
            }

            var width;
            if(obj.style == "wide"){
                width  = 3*($(document).width()/5);
            } else {
                width = 1.5*($(document).width()/5);
            }

            $( "#modalBox" ).dialog({
                minWidth: width,
    			maxHeight: $(document).height()-($(document).height()/6),
    			modal: true,
                show: 'fade',
                hide: 'fade',
                position: ['center','center'],
                title: obj.title,
                dialogClass: 'modalFormat'
    		});
        });
    }
};

/*
  Class UCapViz

  Handles all data visualization functions for uCap.
 */
var UCapViz = {
    drawProgressBar: function(obj) {
        if(obj.val < 100)
            $('.ui-progressbar').removeClass('full');

        if(obj.disabled){
            $("#" + obj.tar).progressbar({
                disabled: true
            });
        } else {
            if(!isNaN(obj.val)){
                $("#" + obj.tar).progressbar({
                    value: obj.val,
                    complete: function(ui) {
                        $('.ui-progressbar').addClass('full');
                    }
                });
            }
        }
    },
    //See: http://www.highcharts.com/ref/
    drawTimeLine: function(obj){
        new Highcharts.Chart({
            chart: {
                renderTo: obj.tar,
                type: 'line'
            },
            title: {
                text: obj.title ? obj.title : ''
            },
            legend: {
                        layout: 'vertical',
                        align: 'right',
                        verticalAlign: 'top',
                        x: 0,
                        y: 50,
                        borderWidth: 0
            },
            tooltip: {
                formatter: function() {
                    var d = new Date(this.x);
                    return '<b>'+ this.series.name +'</b><br/><em>Date: </em>'+ d.toDateString() +'<br/><em>Usage: </em>'+ this.y + 'MB';
                },
                borderWidth: 1
            },
            xAxis: {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                                day: '%e %b'
                        },
                        gridLineColor: "#E1E1E1"
            		},
            yAxis: {
                    gridLineColor: "#E1E1E1",
                    minorGridLineDashStyle: "Dot",
                    title: {
                        text: obj.yAxisLabel ? obj.yAxisLabel : ''
                        }
                    },
            series: obj.data,
            credits:{enabled:false}
        });
    },

    drawChart: function(obj) {
        new Highcharts.Chart({
            chart: {
                renderTo: obj.tar
            },
            title: {
                text: obj.title ? obj.title : ''
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(2) +' %'+ ' ('+ this.point.y.toFixed(2) +' MB)';
                }
            },
            legend: {
            			layout: 'vertical',
            			align: 'right',
            			verticalAlign: 'top',
            			x: 0,
            			y: 50,
            			borderWidth: 0
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    showInLegend: true
                }
            },
            series: [{
                type: 'pie',
                data: obj.data,
                borderWidth:1,
                shadow:false
            }],
            credits:{enabled:false}
        });
    }
};
