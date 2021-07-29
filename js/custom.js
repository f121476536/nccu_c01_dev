//20210701
ShowRSData(GetPRSAPIResult(), null);

//瀏覽器Call C01，好像無法
/*
var paraString = {  
    "time":"2018-08-08T12:00:00Z",
    "requestId":"AAA",
    "action":"start","deviceId":"SPEAKER",
    "content": "HELLOWOLRD"
    };

var url = 'http://10.234.161.69:8882'
paraString = JSON.stringify(paraString)
console.log(paraString);
CallC01API(paraString)
*/

//取得圖像辨識後Pic結果(包含分析結果、辨識後圖片)
EmoResult = GetEmotionAPIResult();
//console.log(EmoResult);
//顯示在視窗上面
$('#emo-usr-pic').attr('src','https://i.imgur.com/' + EmoResult['img_id'] + '.jpg');
$('#emo-usr-result').text(EmoResult['emotion'] );




function test_click(_vote){
    console.log(_vote);
    url = 'http://140.119.127.32:81/v1/get_pic_config/'
    CallAPI(url, ShowAPIPage, '');
}

function ShowAPIPage(_Data, _null){
    console.log(_Data);
}

function CallC01API(_url, _body){
    
    //console.log(_url);
    try
    {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", _url);
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('Accept', '*/*');
        //xhr.setRequestHeader("content-type","application/x-www-form-urlencoded");
        xhr.onload = function () {
            if (this.readyState == 4 && this.status == 200) 
            {
                var JsonContent = JSON.parse(xhr.responseText);
                console.log(JsonContent);
            }
        }
        xhr.send(_body);
    }
    catch(err)
    {
        print('function CallAPI: ' + err);
    }
};


function SetSubjectsTagLayout(_arr){
    
    //依照數字大小排序
    _arr.sort(function(a,b){
        return a.length - b.length;
    });
    
    result = []
    for (var i = 0; i < _arr.length ; i++)
    {
        //如果是純英文且大於26字元的話，則不要顯示
        if(escape(_arr[i]).indexOf("%u")<0 && _arr[i].length>26)
        {   
            break;
        }  
            result.push(_arr[i]);
    }
    
    //console.log(result);
    return result;
}


/*於獨立頁面中，顯示Top 10 Holding畫面*/
function ShowRSData(_Data, _null){
    let RSUpperHalf = '<md-content layout-xs="column" layout="row" class="RScolumn _md md-primoExplore-theme layout-xs-column layout-row">';
    let RSBlock = '';
    let PinIn = '';
    for (var i = 0; i < _Data.length ; i++)
    {
        //Add bottom half if API Data are more than 5.
        if(i==5)
        {
            RSBlock += '</md-content>' + '<md-content layout-xs="column" layout="row" class="RScolumn _md md-primoExplore-theme layout-xs-column layout-row">';
        }

        //mms_id = _Data[i]['mms_id'];
        let author = _Data[i]['author'];
        let pic_url = _Data[i]['pic_url'];
        let primo_url = _Data[i]['primo_url'];
        let subjects = SetSubjectsTagLayout(_Data[i]['subjects']);
        let title = _Data[i]['title'];
        let CallNumber = _Data[i]['CallNumber'];
        let CallNumber_url = _Data[i]['CallNumber_url'];

        RSBlock_subject = '<div class="gridmax-grid-post-categories"><span class="gridmax-sr-only">Posted in </span>';

        if(subjects.length>0){
            for(var j = 0; j < subjects.length; j++)
            {
                TagPrimoSearchURL = 'https://nccu.primo.exlibrisgroup.com/discovery/search?query=sub,contains,' + encodeURI(subjects[j]) + '&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST&offset=0';
                RSBlock_subject += '<a href="' + TagPrimoSearchURL + '" rel="category">'+ subjects[j] + '</a>';
            }
        }

        /*索書號*/
        RSBlock_subject += '<a href="' + CallNumber_url + '" rel="category">' + CallNumber + ' </a>';
        RSBlock_subject += '</div>';

        //
        if( i == 0 || i == 5)
        {
            PinIn = '';
        }else{
            PinIn = 'flex-xs';
        }

        //點擊作者欄位，查找該作者
        author_primo_url = "https://nccu.primo.exlibrisgroup.com/discovery/search?query=creator,contains," + encodeURI(author) + "&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST&offset=0";

        RSBlock += '<div ' + PinIn + ' flex="20" layout="column" class="layout_culumn"><md-card class="RSdefault-card"><md-card-title><md-card-title-text ><a href="' + primo_url + '"><img class="rc_pic" src="' + pic_url + '" title="' + title + '"><div></div></a>' + RSBlock_subject + '<span class="md-headline" style="font-size:1em; line-height: normal;"><a href="' + primo_url + '"><b>' + title + '</b></a></span></md-card-title-text></md-card-title><md-card-content style="box-shadow:0 1px 3px 0 #d4d4d5, 0 0 0 1px #d4d4d5;"><p style=";bottom:10px;position:absolute;">' + '作者: ' + '<a href="' + author_primo_url + '">'+ author + '</a></p></md-card-content></md-card></div>';
    }

    RSUpperHalf += RSBlock + '</md-content>';
    $('#ShowRecommendationInfo').append(RSUpperHalf);
    //console.log(RSUpperHalf);
}

/*紅字顯示內容於Console端，開發debug用*/
function print(_word){
    
    console.log('%c' + _word,"color:red; font-size:20px");
};

/*推薦系統獨立頁面，右側的置頂功能*/
function RSGoToTop(){

    var mp = $('#RSTopMenu').offset().top;
    $('html, body').animate({scrollTop: mp}, 1000);
}


/*20210513*/
function RSChangeLayout(_mode){

    let SizeSetting = ["width","height","50vw","50vh","17vw","45vh"]
    //console.log(SizeSetting);
    //console.log(_mode);
    if(_mode == 'slide'){
        $("#ShowRecommendationInfo>.RScolumn").css("overflow-x","hidden");
        $("#ShowRecommendationInfo").hide(1000, function(){
            $(".RSdefault-card").css(SizeSetting[0], SizeSetting[2]);
            $(".RSdefault-card").css(SizeSetting[1], SizeSetting[3]);
            
            $("#RSslideshow").show(1000, function(){
                $("#RSslideshow > div:gt(0)").hide();       
            });
        
        }); 

    }else if(_mode == 'list')
    {
        $("#RSslideshow").hide(1000, function(){
            $(".RSdefault-card").css(SizeSetting[0], SizeSetting[4]);
            $(".RSdefault-card").css(SizeSetting[1], SizeSetting[5]);
            $("#ShowRecommendationInfo").show(1000);
        });
    }
}

function ClickDropdownById(_id){
    $('#' + _id).dropdown('hide');
}

function ClickDropdownItem(_item){
    console.log(_item); 
}

//2021.7.2
/*輸入URL，發起request並回傳結果至某一個function中*/
function CallAPI(_url, _callback, _HtmlId){
    
    //console.log(_url);
    try
    {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", _url);
        xhr.setRequestHeader('content-type', 'application/json');
        //xhr.setRequestHeader("content-type","application/x-www-form-urlencoded");
        xhr.onload = function () {
            if (this.readyState == 4 && this.status == 200) 
            {
                var JsonContent = JSON.parse(xhr.responseText);
                _callback(JsonContent , _HtmlId);
                //_callback(xhr.responseText , _HtmlId);
            }
        }
        xhr.send();
    }
    catch(err)
    {
        print('function CallAPI: ' + err);
    }
};

