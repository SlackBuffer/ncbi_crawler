function isNumber(obj) {  
    return typeof obj === 'number' && !isNaN(obj)  
}
function setItem(name, data) {
    chrome.runtime.sendMessage({ command: 'setItem', name: name, data: data });
}

function getItem(name) {
    chrome.runtime.sendMessage({ command: 'getItem', name: name }, function(response) {
        window.localStorage[name] = response;
    });
}
function updateItem(name) {
    chrome.runtime.sendMessage({ command: 'updateItem', name: name }, function(response) {
        window.localStorage[name] = response;
    });
}

function newForm(action, method, pmid){
    var form = $('<form></form>');
    form.attr('action', action);
    form.attr('method', method);
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
(function () {
    getItem('serverURL');
})();
$(function(){
    $("#novopro-sci-hub").bind({
        "blur":function () {
            var serverURL = $(this).val();
            serverURL = serverURL.replace(/\s+/g, '');
            if(/^(http|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$/.test(serverURL)){
                serverURL = serverURL.replace(/[\\\/]+$/, '')
                serverURL = serverURL + "/"
                setItem('serverURL', serverURL);
                $(this).val(serverURL);
            }else if(!serverURL){
                localStorage.serverURL = '';
                updateItem('serverURL');
                var t = setInterval(function () {
                    $("#novopro-sci-hub").val("waiting...");
                    $('#novopro-fetch-pdf').val("Fetching sci-hub URL");
                    $('#novopro-fetch-pdf').attr("disabled",true);
                    if(localStorage.serverURL && /^http/i.test(localStorage.serverURL)){
                        $("#novopro-sci-hub").val(localStorage.serverURL);
                        $('#novopro-fetch-pdf').val("Fetch PDF");
                        $('#novopro-fetch-pdf').attr("disabled",false);
                        clearInterval(t);
                    }
                },50);
            }else{
                alert("Invalid sci-hub URL! \n\n Example: http://sci-hub.tw/ or https://sci-hub.tw/ \n\n Or you can leave it blank");
                $(this).val('');
                $(this).focus();
            }
        }
    });
    $("#novopro-fetch-pdf").click(function () {
        getItem('serverURL');
        var pmid = $("#novopro-doi").val();
        pmid = pmid.replace(/\s+/g, '');
        pmid = pmid.replace(/[\.\)]+$/, '');
        var method = "";
        action = localStorage.serverURL;
        if(/^([0-9]{8})$/.test(pmid)){
            method = 'post';
            form = newForm(action, method, pmid);
            $(document.body).append(form);
            // console.log(form);
            form.submit();
            form.remove();
        }else if(/^(10\.[0-9]{4,5}\/[^\s]+[^\.\s\)]+)$/.test(pmid)){
            var sepChar = '/';
            if(/\/$/.test(action)){
                sepChar = '';
            }
            chrome.tabs.create({ url: action + sepChar + pmid });
        }else{
            alert("Invalid Pubmed ID or doi");
            return false;
        }

    });
    $("#novopro-threshold").bind({
        "keyup": function () {
            $(this).css("ime-mode", "disabled");
            $(this).val($(this).val().replace(/[^\d\.]/g, ''));
            window.localStorage.setItem('threshold', $(this).val());
            // setItem('threshold', $(this).val());
        }
    });
    if(localStorage.serverURL){
        $("#novopro-sci-hub").val(localStorage.serverURL);
    }
    if(window.localStorage.enabled>0){
        $("#novopro-btnn").attr('isopen', 'true').animate({left:'33px'});
        $("#novopro-btn-box").css('background-color','green');
        $("#novopro-threshold").attr("disabled",false);
    }else{
        $("#novopro-btnn").attr('isopen', 'false').animate({left:'3px'});
        $("#novopro-btn-box").css('background-color','#838383');
        $("#novopro-threshold").attr("disabled",true);
    }
    $("#novopro-threshold").val(window.localStorage.threshold);
    $("#novopro-btn-box").click(function(){
      if($("#novopro-btnn").attr('isopen') == 'false'){
        $("#novopro-btnn").attr('isopen', 'true').animate({left:'33px'});
        $("#novopro-btn-box").css('background-color','green');
        $("#novopro-threshold").attr("disabled",false);
        window.localStorage.setItem('enabled', '1');
        // setItem('enabled', 'true');
      }else{
        $("#novopro-btnn").attr('isopen', 'false').animate({left:'3px'});
        $("#novopro-btn-box").css('background-color','#838383');
        $("#novopro-threshold").attr("disabled",true);
        window.localStorage.setItem('enabled', '0');
        // setItem('enabled', 'false');
      }
    });
});
