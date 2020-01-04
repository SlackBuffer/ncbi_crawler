chrome.extension.onMessage.addListener(function(request, sender, sendResponse) {
    switch (request.command) {
        case 'setItem':
            localStorage[request.name] = request.data;
            return;
        case 'getItem':
            var retValue = localStorage[request.name];
            // console.log(localStorage);
            sendResponse(retValue);
            return;
        case 'deleteItem':
            if (typeof localStorage[request.name] !== 'undefined') {
                delete localStorage[request.name];
            }
            return;
        case 'fetchdata':
            pdata = request.pdata;
            // console.log(pdata);
            if(pdata.length){
                var post_url = "http://www.novopro.cn/impactfactor/";
                // console.log(post_url);
                $.post(post_url, { "jn": pdata },
                    function(data){
                        // console.log(data);
                        retval = {data:data, post_url:post_url};
                        sendResponse(retval);
                    });
            }
            return true;
            // return true;  indicate you wish to send a response asynchronously
            // (this will keep the message channel open to the other end until sendResponse is called)
        case 'updateItem':
            if(request.name == 'serverURL'){
                var url = "http://www.novopro.cn/impactfactor/";
                console.log(url);
                $.ajax({
                    type: 'GET',
                    url: url,
                    data:{su:'novopro'},
                    cache: false,
                    success: function (resp) {
                        var arr = eval('(' + resp + ')');
                        console.log(arr);
                        var serverURL = arr['su'];
                        var lastUpdate = arr['time'];
                        var foreceUpdate = arr['fu'];
                        var curTime = Math.round(new Date().getTime()/1000);
                        // console.log(lastUpdate-curTime);
                        localStorage['serverURL'] = serverURL;
                        localStorage['lastUpdate'] = lastUpdate;
                        sendResponse(localStorage['serverURL']);
                        // console.log("success");
                    },
                    error: function () {
                        var serverURL = 'http://sci-hub.tw/';
                        var lastUpdate = Math.round(new Date().getTime()/1000);
                        localStorage['serverURL'] = serverURL;
                        localStorage['lastUpdate'] = lastUpdate;
                        sendResponse(serverURL);
                        // console.log("error");
                    }
                });
                // console.log("zuihoumian");
            }
    }
});


function newForm(action, pmid){
    var form = $('<form></form>');
    form.attr('action', action);
    form.attr('method', 'post');
    // form的target属性决定form在哪个页面提交
    // _self -> 当前页面 _blank -> 新页面
    form.attr('target', "_blank");
    var request = $('<input type="hidden" name="request" />');
    request.attr('value', pmid);
    form.append(request);
    var plugChek = $('<input type="hidden" name="sci-hub-plugin-check" />');
    plugChek.attr('value', '');
    return form;
}

function onClickHandler(info) {
    if (info.menuItemId == 'Sci-HubContextMenu') {
        if ( /10\.[0-9]{4,5}\/[^\s]+[^\.\s\)]+/.test(info.selectionText) || /[0-9]{8}/.test(info.selectionText) || info.selectionText.indexOf('dx.doi.org') >= 0) {
            var selectionText = info.selectionText;
            var m = selectionText.match(/([0-9]{8})/);
            var m1 = selectionText.match(/(10\.[0-9]{4,5}\/[^\s]+[^\.\s\)]+)/);
            if (m && m[1]){
                var pmid = m[1];
                action = localStorage.serverURL;
                form = newForm(action, pmid);
                $(document.body).append(form);
                console.log(form);
                form.submit();
                form.remove();
            }else if( m1 && m1[1] ){
                var sepChar = '/';
                if(/\/$/.test(localStorage.serverURL)){
                    sepChar = '';
                }
                chrome.tabs.create({ url: localStorage.serverURL + sepChar + m1[1] });
            }
        }else{
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
                chrome.tabs.sendMessage(tabs[0].id, {message:"invalid-parameter", sender:"novopro"}, function(response) {
                    ;
                });//end  sendMessage
            }); //end query
        }
    };
};
chrome.contextMenus.onClicked.addListener(onClickHandler);

chrome.contextMenus.create({
    type: 'normal',
    title: "Sci-Hub Search" + ': %s',
    id: 'Sci-HubContextMenu',
    contexts:['selection']
});

(function () {
    if(!("serverURL" in localStorage)){
        // console.log("here");
        var url = "http://www.novopro.cn/impactfactor/";
        // console.log(url);
        $.ajax({
            type: 'GET',
            url: url,
            data:{su:'novopro'},
            cache: false,
            success: function (resp) {
                var arr = eval('(' + resp + ')');
                console.log(arr);
                var serverURL = arr['su'];
                var lastUpdate = arr['time'];
                var foreceUpdate = arr['fu'];
                var curTime = Math.round(new Date().getTime()/1000);
                // console.log(lastUpdate-curTime);
                localStorage['serverURL'] = serverURL;
                localStorage['lastUpdate'] = lastUpdate;
            },
            error: function () {
                var serverURL = 'http://sci-hub.tw/';
                var lastUpdate = Math.round(new Date().getTime()/1000);
                localStorage['serverURL'] = serverURL;
                localStorage['lastUpdate'] = lastUpdate;
            }
        });
    }else{
        // console.log("fuck");
    }
})();