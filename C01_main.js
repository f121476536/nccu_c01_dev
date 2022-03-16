class InstrumentSlideshow {
    constructor() {
        this.elements = new ElementController();
        this.start_index = 1;
        this.end_index = 3;
        this.current_index = this.start_index;

    }
    get_current_index() {
        let tag = $('.ui.massive.rounded.image:not(.hidden)').attr('id');
        this.current_index = parseInt(tag.substr(-1), 10);
    }

    next_pic() {
        this.get_current_index();
        this.hide_image(`#${this.elements.INSTRUMNETSLIDESHOW}${this.current_index}`);
        this.inactive_dot(`#${this.elements.INSTRUMNETDOT}${this.current_index}`);
        this.current_index = this.current_index == this.end_index ? this.start_index : this.current_index += 1;
        this.show_image(`#${this.elements.INSTRUMNETSLIDESHOW}${this.current_index}`);
        this.active_dot(`#${this.elements.INSTRUMNETDOT}${this.current_index}`);
    }

    previous_pic() {
        this.get_current_index();
        this.hide_image(`#${this.elements.INSTRUMNETSLIDESHOW}${this.current_index}`);
        this.inactive_dot(`#${this.elements.INSTRUMNETDOT}${this.current_index}`);
        this.current_index = this.current_index == this.start_index ? this.end_index : this.current_index -= 1;
        this.show_image(`#${this.elements.INSTRUMNETSLIDESHOW}${this.current_index}`);
        this.active_dot(`#${this.elements.INSTRUMNETDOT}${this.current_index}`);
    }

    show_image(element) {
        $(element).transition('fade');
    }

    hide_image(element) {
        $(element).transition('toggle').css('display', 'none');
    }

    active_dot(dot) {
        $(dot).removeClass('outline');
    }

    inactive_dot(dot) {
        $(dot).addClass('outline');
    }

    click_dot(index) {
        this.get_current_index();
        this.hide_image(`#${this.elements.INSTRUMNETSLIDESHOW}${this.current_index}`);
        this.inactive_dot(`#${this.elements.INSTRUMNETDOT}${this.current_index}`);
        this.current_index = index;
        this.show_image(`#${this.elements.INSTRUMNETSLIDESHOW}${this.current_index}`);
        this.active_dot(`#${this.elements.INSTRUMNETDOT}${this.current_index}`);
    }

}

class APISources {
    constructor() {
        this.PRSCBF2FB = 'http://140.119.127.32:8003/v1/prs_get_topk_list_by_userid/dhl_two_floors_book/';
        this.PRSCBF2FBG = 'http://140.119.127.32:8003/v1/prs_get_topk_list_by_userid/dhl_two_floors_board_game/';
        this.PRSCBF2FJ = 'http://140.119.127.32:8003/v1/prs_get_topk_list_by_userid/dhl_two_floors_journal/';
    }
}

class WebTransferHandler {
    constructor() {
        this.xhr = new XMLHttpRequest();
    }

    send_request(url, callback) {
        try {
            this.xhr.open("GET", url);
            this.xhr.setRequestHeader('content-type', 'application/json');
            this.xhr.onload = function () {
                if (this.readyState == 4 && this.status == 200) {
                    let result = JSON.parse(this.responseText);
                    callback.parser_api_result(url, result);
                }
            }
            this.xhr.send();
        }
        catch (error_message) {
            console.log('%c' + error_message, "color:red; font-size:20px")
        }
    }
}

class Colors {
    constructor() {
        this.RED = 'red';
        this.ORANGE = 'orange';
        this.YELLOW = 'yellow';
        this.DARKYELLOW = 'rgb(191, 144, 0)';
        this.OLIVE = 'olive';
        this.GREEN = 'green';
        this.DARKGREEN = 'rgb(56, 87, 35)';
        this.TEAL = 'teal';
        this.BLUE = 'blue';
        this.DARKBLUE = 'rgb(31, 78, 121)';
        this.VIOLET = 'violet';
        this.PURPLE = 'purple';
        this.PINK = 'pink';
        this.BROWN = 'brown';
        this.GREY = 'grey';
        this.BLACK = 'black';
        this.WHITE = 'white';
    }

    is_rgb(color) {
        let result = color.indexOf('rgb') != -1 ? true : false;
        return result
    }
}

class SidesController {
    constructor() {
        this.start_side = 1;
        this.end_side = 3;
        this.current_index = this.start_side;
    }

    get_current_index() {
        this.current_index = parseInt($('.active.side').attr('id').substr(-1), 10);
    }

    set_next_side(element, side_element, mode) {
        $(element).shape('set next side', side_element).shape(mode);
    }

    slide_over() {
        this.get_current_index();
        this.current_index = this.current_index == this.end_side ? this.start_side : this.current_index += 1;
        this.set_next_side('.shape', `#side-${this.current_index}`, 'flip back');
    }

    slide_back() {
        this.get_current_index();
        this.current_index = this.current_index == this.start_side ? this.end_side : this.current_index -= 1;
        this.set_next_side('.shape', `#side-${this.current_index}`, 'flip over');
    }

}

class BooksHandler {
    constructor() {
        this.colors = new Colors();
    }

    get_book_package_by_raw_data(json_data) {
        let book_package = json_data['topk_list'];
        book_package = book_package.slice(1, -1).replaceAll('"', '%').replaceAll("'", '"').replaceAll('%', "'").replaceAll("}, {", "}|{").split("|");
        return book_package;
    }

    parser_book_information(book_information) {
        let data_json = JSON.parse(book_information)
        let information = {};
        information['mms_id'] = data_json['mms_id'];
        information['author'] = data_json['author'];
        if (data_json['author'] == null || data_json['author'] == '') {
            information['author'] = 'None';
        }
        information['pic_url'] = data_json['pic_url'];
        information['primo_url'] = data_json['primo_url'];
        information['subjects'] = data_json['subjects'].toString().split(',');
        information['title'] = data_json['title'];
        information['call_number'] = data_json['CallNumber'];
        information['call_number_url'] = data_json['CallNumber_url'];

        if (data_json.hasOwnProperty('is_cbf')) {
            information['is_cbf'] = data_json['is_cbf'].toLowerCase();
        }

        return new Book(information)
    }

    get_card_html_by_book(book) {
        let book_cover = this.set_book_cover_html(book.primo_url, book.pic_url, book.mms_id);
        let book_title = this.controll_title_length(book.title);
        book_title = this.set_book_title_html(book.primo_url, book.title, book.mms_id);
        let book_subjects = this.controll_subject_length(book.subjects);
        book_subjects = this.set_book_subjects_html(book_subjects, book.call_number, book.call_number_url, book.mms_id);
        let book_author = this.set_book_author_html(book.author, book.mms_id);
        let card_html = `<div class="column"><div class="ui floated card" style="height: 95%;">${book_cover}<div class="content">${book_title}${book_subjects}</div><div class="extra content">${book_author}</div></div><div></div></div>`;

        return card_html;
    }

    set_book_cover_html(href, image_src, mms_id) {
        let html = `<a class="ui small centered image" data-log-info="(${mms_id})"><img class="bookcover" src="${image_src}"></a>`;
        return html;
    }

    set_book_title_html(href, title, mms_id) {
        let html = `<div class="ui ${this.colors.BLACK} header" data-log-info="${title}(${mms_id})" style="overflow : hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;" title="${title}" data-content="${title}" data-variation="inverted">${title}</div>`;
        return html;
    }

    controll_title_length(title) {
        let max_length = 23 * 2;
        let length = 0;
        let filiter_title = '';
        for (var i = 0; i < title.length; i++) {
            if (length <= max_length) {
                length += title[i].replace(/[^\x00-\xff]/g, "xx").length;
                filiter_title += title[i];
            } else {
                filiter_title += '...';
                break;
            }
        }
        return title;
    }

    set_book_subjects_html(subjects, call_number, call_number_url, mms_id) {
        let tags = '';
        for (let i = 0; i < subjects.length; i++) {
            if (subjects[i] != '') {
                let href = `https://nccu.primo.exlibrisgroup.com/discovery/search?query=sub,contains,${encodeURI(subjects[i])}&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST&offset=0`;
                tags += `<a rel="category" data-log-info="${subjects[i]}(${mms_id})">${subjects[i]}</a>`;
            };
        }

        if (call_number != '') {
            tags += `<a rel="category" data-log-info="${call_number}(${mms_id})">${call_number}</a>`;
        }

        let html = `<div class="gridmax-grid-post-categories"><span class="gridmax-sr-only">Posted in </span>${tags}</div>`;
        return html;
    }

    controll_subject_length(subjects) {
        subjects.sort((x, y) => x.length - y.length);
        let max_length = 80;
        let length = 0;
        let filiter_subject = [];
        for (var i = 0; i < subjects.length; i++) {
            if (subjects[i] != ' ') {
                if (length <= max_length) {
                    length += subjects[i].length;
                    filiter_subject.push(subjects[i])
                }
            }

        }
        return filiter_subject;
    }

    set_book_author_html(author, mms_id) {
        let href = `https://nccu.primo.exlibrisgroup.com/discovery/search?query=creator,contains,${encodeURI(author)}&tab=Everything&search_scope=MyInst_and_CI&vid=886NCCU_INST:886NCCU_INST&offset=0`;
        let html = `<a href="${href}" target="_blank"  data-log-info="${author}(${mms_id})"><span><i class="user icon"></i>${author}</span></a>`;
        return html;
    }

    set_top_label_html(color, number) {
        let html = `<div class="ui fluid image"><div class="ui ${color} ribbon label" style="z-index:1;"><i class="list ol icon"></i>Top ${number}</div></div>`;
        return html;
    }

    set_book_source_label(color, name, message) {
        let ui_color = '';
        let css_color = '';
        if (this.colors.is_rgb(color)) {
            css_color = `border-color: ${color};`;
        } else {
            ui_color = ` ${color}`;
        }

        let html = `<div class="ui fluid image" title="${message}"><div class="ui${ui_color} right corner label" style="z-index:2;${css_color}"><h1 class="ui icon ${this.colors.WHITE} inverted header" style="left:9px;top:6px;z-index:2;">${name}</h1></div></div>`;
        return html;
    }

    string_insert(original_string, new_string, tag) {
        let point = original_string.indexOf(tag);
        let result = original_string.slice(0, point) + new_string + original_string.slice(point);
        return result
    }
}

class Book {
    constructor({ mms_id = '', author = '', pic_url = '', subjects = '', title = '', call_number = '', call_number_url = '', primo_url = '', is_cbf = 'false' }) {
        this.mms_id = mms_id;
        this.author = author;
        this.pic_url = pic_url;
        this.subjects = subjects;
        this.title = title;
        this.call_number = call_number;
        this.call_number_url = call_number_url;
        this.primo_url = primo_url;
        this.is_cbf = is_cbf;
    }
}

class BookSources {
    constructor() {
        this.colors = new Colors();
        this.element = new ElementController();
        this.source_map = {
            'dhl_two_floors_book': {
                'color': this.colors.RED,
                'name': '書本',
                'message': '此標籤表示此館藏的類型為書籍',
                'layout_row': this.element.INDEPENDENTPAGEDISPLAY1,
                'is_top': true
            },
            'dhl_two_floors_board_game': {
                'color': this.colors.GREEN,
                'name': '桌遊',
                'message': '此標籤表示此館藏的類型為桌遊',
                'layout_row': this.element.INDEPENDENTPAGEDISPLAY2,
                'is_top': false
            },
            'dhl_two_floors_journal': {
                'color': this.colors.BLUE,
                'name': '期刊',
                'message': '此標籤表示此館藏的類型為期刊',
                'layout_row': this.element.INDEPENDENTPAGEDISPLAY3,
                'is_top': false
            }
        };
    }

    parser_data_source(url) {
        let array = url.split('/');
        let data_source = array[array.length - 2];
        return data_source;
    }
}

class PromotionSystem {
    constructor() {
        this.colors = new Colors();
        this.ui = new UIRender();
        this.handler = new BooksHandler();
        this.elements = new ElementController();
        this.source = new BookSources();
        this.static_file = new StaticFileLoader();
        this.static_file.load_api_function("userinfo-result.js");
    }

    get_topn_parameters() {
        let n = 5;
        let label_colors = [this.colors.RED, this.colors.GREEN, this.colors.BLUE];
        let label_n = 3;
        let parameters = { 'n': n, 'label_colors': label_colors, 'label_n': label_n };
        return parameters;
    }

    parser_api_result(url, json_data) {

        if (window.prs_call_number < window.prs_call_max_number) {
            window.prs_call_number += 1

            let source_type = this.source.parser_data_source(url);
            let topn_parameters = this.get_topn_parameters();
            let book_package = this.handler.get_book_package_by_raw_data(json_data);
            let cards_html = '';
            for (let i = 0; i < book_package.length; i++) {
                if (i >= topn_parameters['n']) {
                    break;
                }

                let card_html = '';
                let book = this.handler.parser_book_information(book_package[i]);
                card_html += this.handler.get_card_html_by_book(book);

                //top n label
                // if (this.source.source_map[source_type]['is_top']) {
                //     if (window.top_label_number < topn_parameters['label_n']) {
                //         let top_label_html = this.handler.set_top_label_html(topn_parameters['label_colors'][i], parseInt(i) + 1);
                //         card_html = this.handler.string_insert(card_html, top_label_html, '<a href');
                //         window.top_label_number += 1;
                //     }
                // }

                let source_color = this.source.source_map[source_type]['color'];
                let source_name = this.source.source_map[source_type]['name'];
                let source_message = this.source.source_map[source_type]['message'];
                let book_new_label = this.handler.set_book_source_label(source_color, source_name, source_message);
                card_html = this.handler.string_insert(card_html, book_new_label, '<a');

                cards_html += card_html;
            }

            this.ui.add_html(this.source.source_map[source_type]['layout_row'], cards_html);
            this.ui.resize_image(".bookcover");
            this.ui.show_element('#' + this.elements.INDEPENDENTPAGEALLREADYLOADER);
            this.ui.hide_element('#' + this.elements.INDEPENDENTPAGERELOADER);
            this.ui.show_element_scaling('#' + this.elements.INDEPENDENTPAGE);
        }

        if (window.prs_call_number == (window.prs_call_max_number)) {
            this.ui.hide_element('#' + this.elements.INDEPENDENTPAGEALLREADYLOADER);
            this.ui.hide_element('#' + this.elements.COMMONREFRESH);
        }

    }

    tap_in_card() {
        this.ui.click_element(`#${this.elements.PROMOTIONPAGE2}`);
        $('#' + this.elements.PROMOTIONPAGEPROGRESSBAR).transition('fade up');
        var $progress = $('#' + this.elements.PROMOTIONPAGEPROGRESSBAR), $button = $(this), updateEvent;
        
        // restart to zero
        clearInterval(window.loading_progress)
        $progress.progress('reset');

        // updates every 10ms until complete
        window.loading_progress = setInterval(() => {
            $progress.progress('increment');
            $button.text($progress.progress('get value'));

            // stop incrementing when complete
            if ($progress.progress('is complete')) {
                clearInterval(window.loading_progress)
                $('#' + this.elements.PROMOTIONPAGEPROGRESSBAR).transition('fade up');
                let user = GetUserInfo()["user_account"];
                promotion_system_main(user);
                this.ui.click_element(`#${this.elements.PROMOTIONPAGE3}`);
            }
        }, 50);

        //顯示進度條
        $('#' + this.elements.PROMOTIONPAGEPROGRESSBAR).progress({
            duration: 100,
            total: 100,
            text: {
                active: '{value} of {total} done'
            }
        });

    }

    back_to_page() {
        this.ui.empty_element(`#${this.elements.INDEPENDENTPAGEDISPLAY1}`);
        this.ui.empty_element(`#${this.elements.INDEPENDENTPAGEDISPLAY2}`)
        this.ui.empty_element(`#${this.elements.INDEPENDENTPAGEDISPLAY3}`)
        this.ui.click_element(`#${this.elements.PROMOTIONPAGE1}`);
    }
}

function promotion_system_main(user) {
    let elements = new ElementController();
    let ui = new UIRender();

    if (user != 'anonymous') {
        let api = new APISources();
        let urls = [api.PRSCBF2FBG, api.PRSCBF2FB, api.PRSCBF2FJ];

        window.prs_call_number = 0;
        window.prs_call_max_number = urls.length;
        window.top_label_number = 0;

        for (var i = 0; i < urls.length; i++) {
            let web = new WebTransferHandler();
            let promtion_system = new PromotionSystem();
            let prs_api = urls[i] + user;
            web.send_request(prs_api, promtion_system);
        }
    } else {
        ui.hide_element('#' + elements.INDEPENDENTPAGERELOADER);
    }

}

class LocalProgramConnector {
    constructor() {
        this.qa_system = 'C01-run-qa-system://';
    }
}

class ElementController {
    constructor() {
        //問答客服系統
        this.STARTTALKINGBTN = 'start-talking-btn';
        this.CLEARTALKINGBTN = 'clear-talking-btn';
        this.ASKBTN = 'ask-btn';
        this.QUESTIONBOX = 'question-box';
        this.AUDIOLOADINGICON = 'audio-loading-icon';
        this.USERSPEAKLAYOUT = 'user-speak-layout';
        this.USERSPEAK = 'user-speak';
        this.C01SPEAKLAYOUT = 'c01-speak-layout';
        this.C01SPEAK = 'c01-speak';
        this.QAPROGRESBAR = 'qa-progress-bar';
        this.RETALKINGBTN = 'retalking-btn';

        //推廣尋書系統
        this.INSTRUMNETSLIDESHOW = 'instrument-slideshow-';
        this.INSTRUMNETDOT = 'instrument-slideshow-dot-';
        this.PROMOTIONPAGE1 = 'promotion-page1';
        this.PROMOTIONPAGE2 = 'promotion-page2';
        this.PROMOTIONPAGEPROGRESSBAR = 'promotion-progress-bar';
        this.PROMOTIONPAGE3 = 'promotion-page3';

        this.INDEPENDENTPAGE = 'show-recommendation-info';
        this.INDEPENDENTPAGEDISPLAY1 = 'display-1';
        this.INDEPENDENTPAGEDISPLAY2 = 'display-2';
        this.INDEPENDENTPAGEDISPLAY3 = 'display-3';
        this.INDEPENDENTPAGERELOADER = 'list-reloader';
        this.INDEPENDENTPAGEALLREADYLOADER = 'all-ready-list-reloader'
        this.COMMONREFRESH = 'refresh-alert';
    }
}


class StaticFileLoader {
    load_api_function(api_file) {
        var jq = document.createElement("script");
        jq.src = "lib/api-result/" + api_file;
        document.getElementsByTagName("body")[0].appendChild(jq);
    }
}

class AnswerMaker {
    constructor() {
        this.audio = new AudioRecognizer();
        this.local_program = new LocalProgramConnector();
        this.ui = new UIRender();
        this.elements = new ElementController();
        this.static_file = new StaticFileLoader();
    }

    connect_QA_system() {
        this.audio.download_audio_text();
        window.location.href = this.local_program.qa_system;
        this.show_dialogue();

        //鎖住所有按鈕
        this.ui.set_btn_disabled(this.elements.CLEARTALKINGBTN);
        this.ui.set_btn_disabled(this.elements.STARTTALKINGBTN);
        this.ui.set_btn_disabled(this.elements.ASKBTN);
    }

    show_dialogue() {
        $('#' + this.elements.QAPROGRESBAR).transition('fade up');
        var $progress = $('#' + this.elements.QAPROGRESBAR), $button = $(this), updateEvent;

        // restart to zero
        clearInterval(window.loading_progress)
        $progress.progress('reset');

        // updates every 10ms until complete
        window.loading_progress = setInterval(() => {
            $progress.progress('increment');
            $button.text($progress.progress('get value'));

            // stop incrementing when complete
            if ($progress.progress('is complete')) {
                clearInterval(window.loading_progress)
                $('#' + this.elements.QAPROGRESBAR).transition('fade up');
                this.static_file.load_api_function("audio-anwser-result.js");
                this.show_user_dialogue().then(this.show_c01_dialogue()).then(this.show_retalking_btn());
            }
        }, 50);

        //顯示進度條
        $('#' + this.elements.QAPROGRESBAR).progress({
            duration: 100,
            total: 100,
            text: {
                active: '{value} of {total} done'
            }
        });
    }

    //顯示讀者的問題
    show_user_dialogue() {
        return new Promise((resolve, reject) => {
            window.setTimeout(() => {
                let user_question = document.getElementById(this.elements.QUESTIONBOX).value;
                if (user_question != '') {
                    $('#' + this.elements.USERSPEAK).text(user_question);
                }
                $('#' + this.elements.USERSPEAKLAYOUT).transition('fade left');
                this.ui.clear_input_box(this.elements.QUESTIONBOX);
                resolve('show_user_dialogue');
            }, 500);
        });
    }

    //顯示機器人的回答
    show_c01_dialogue() {
        return new Promise((resolve, reject) => {
            window.setTimeout(() => {
                let c01_anwser = get_audio_anwser()['word'];
                $('#' + this.elements.C01SPEAK).html(c01_anwser);
                $('#' + this.elements.C01SPEAKLAYOUT).transition('fade right');
                resolve('show_c01_dialogue');
            }, 2000);
        });
    }

    //顯示重新對話的按鈕
    show_retalking_btn() {
        return new Promise((resolve, reject) => {
            window.setTimeout(() => {
                $('#' + this.elements.RETALKINGBTN).transition('fade up');
                resolve('show_retalking_btn');
            }, 3200);
        });
    }

    clear_dialogue() {
        this.ui.clear_input_box(this.elements.QUESTIONBOX);
    }

    reset_dialogue() {
        //開啟所有按鈕
        this.ui.set_btn_abled(this.elements.CLEARTALKINGBTN);
        this.ui.set_btn_abled(this.elements.STARTTALKINGBTN);
        this.ui.set_btn_abled(this.elements.ASKBTN);

        //隱藏對話框
        $('#' + this.elements.RETALKINGBTN).transition('fade up');
        $('#' + this.elements.USERSPEAKLAYOUT).transition('fade left');
        $('#' + this.elements.C01SPEAKLAYOUT).transition('fade right');
    }
}

class AudioRecognizer {
    constructor() {
        this.speech_recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.speech_recognition.lang = 'cmn-Hant-TW';
        this.elements = new ElementController();
        this.ui = new UIRender();
    }

    //初始化語音辨識物件的狀態
    initialize_speech_recognition() {
        this.speech_recognition = new this.speech_recognition();
        this.speech_recognition.status = true
        this.speech_recognition.continuous = true;
        this.speech_recognition.interimResults = true;
    };

    //儲存語音辨識的結果文字
    download_audio_text() {
        let audio_text = document.getElementById(this.elements.QUESTIONBOX).value;
        let file = new File([audio_text], "audio_text.txt", { type: "text/plain;charset=utf-8" });
        saveAs(file);
    }

    //語音轉文字
    speech_to_text() {
        this.ui.set_btn_disabled(this.elements.STARTTALKINGBTN);
        this.ui.set_btn_disabled(this.elements.ASKBTN);
        this.ui.clear_input_box(this.elements.QUESTIONBOX);
        this.ui.show_elemet_display(this.elements.AUDIOLOADINGICON);

        //隱藏對話框
        $('#' + this.elements.RETALKINGBTN).transition('hide');
        $('#' + this.elements.USERSPEAKLAYOUT).transition('hide');
        $('#' + this.elements.C01SPEAKLAYOUT).transition('hide');

        //進行語音辨識
        if (this.speech_recognition) {
            this.initialize_speech_recognition()
            this.speech_recognition.start()
            this.speech_recognition.addEventListener("result", this.process_audio);
        }
    }

    //讀取語音辨識的結果文字
    process_audio(event) {
        let elements = new ElementController();
        let ui = new UIRender();
        let resultContainer = document.getElementById(elements.QUESTIONBOX);
        let resultList = event.results;

        for (let i = 0; i < resultList.length; i++) {
            let result = resultList.item(i);
            //console.log('result[0].transcript', result[0].transcript);

            try {
                let alternative = result.item(0);
                let text = alternative.transcript;
                resultContainer.value = text;
            } catch (ex) {
                console.log('ex =', ex);
            }
            if (result.isFinal) {
                console.log('result.isFinal =', result.isFinal);
                ui.set_btn_abled(elements.STARTTALKINGBTN);
                ui.set_btn_abled(elements.ASKBTN);
                ui.hide_elemet_display(elements.AUDIOLOADINGICON);
                this.stop();
                break;
            }
        }
    };
}

//要改同名的問題
class UIRender {
    set_btn_disabled(element_id) {
        let value = document.getElementById(element_id).className;
        let new_value = value.split(' ').join(' disabled ');
        document.getElementById(element_id).className = new_value;
    }

    set_btn_abled(element_id) {
        let value = document.getElementById(element_id).className;
        let new_value = value.replaceAll(' disabled', '');
        document.getElementById(element_id).className = new_value;
    }

    clear_input_box(element_id) {
        let element = document.getElementById(element_id);
        element.value = '';
    }

    set_btn_text(element_id, new_text) {
        let element = document.getElementById(element_id);
        origin_text = element.innerText;
        element.innerHTML = element.innerHTML.replace(origin_text, new_text);
    }

    hide_elemet_display(element_id) {
        $('#' + element_id).hide();
    }

    show_elemet_display(element_id) {
        $('#' + element_id).show();
    }

    add_html(element_id, html) {
        $('#' + element_id).append(html);
    }

    replace_html(element_id, html) {
        $('#' + element_id).replaceWith(html);
    }

    resize_max_height(element_class) {
        var heights = new Array();
        $('.' + element_class).each(function (i) {
            heights[i] = $(this).outerHeight();
        });
        $('.' + element_class).height(Math.max.apply(null, heights));
    }

    hide_element(element_id) {
        $(element_id).hide();
    }

    show_element(element_id) {
        $(element_id).show();
    }

    show_element_scaling(element_id) {
        $(element_id).transition('hide').transition('scale');
    }

    resize_image(element) {
        let default_cover = 'https://proxy-ap.hosted.exlibrisgroup.com/exl_rewrite/books.google.com/books/content?id=123&printsec=frontcover&img=1&zoom=5&edge=curl';
        let invalid_pic_height = [143, 1];

        $(element).each(function (i) {
            let img = $(this);
            $("<img/>").attr("src", $(img).attr("src")).on('load', function () {
                if (invalid_pic_height.indexOf(this.height) != -1) {
                    $(img).attr('src', default_cover);
                }
                $(img).css("height", "212px");
            })
        })
    }

    click_element(element) {
        $(element).click();
    }

    empty_element(element) {
        $(element).empty();
    }
}