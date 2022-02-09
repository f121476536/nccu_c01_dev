
function HrefController() {
    this.qa_system = 'C01-run-qa-system://';
}

function ElementController() {
    this.start_btn_id = 'start_btn';
    this.clear_btn_id = 'clear_btn';
    this.refresh_btn_id = 'refresh_btn';
    this.ask_btn_id = 'ask_btn';
    this.question_box_id = 'resultContainer';
    this.loading_icon_id = 'audio_loading_icon';
    this.user_speak_layout_id = 'user_speak_layout';
    this.user_speak_id = 'user_speak';
    this.c01_speak_layout_id = 'c01_speak_layout';
    this.c01_speak_id = 'c01_speak';
    this.progress_bar_id = 'progress_bar';
    this.reset_btn_id = 'reset_btn';
}

function StaticFileLoader() {
    this.load_api_function = function (api_file) {
        var jq = document.createElement("script");
        jq.src = "lib/api-result/" + api_file;
        document.getElementsByTagName("head")[0].appendChild(jq);
    }
}

function AnswerMaker() {
    //開啟問答系統
    this.connect_QA_system = function () {
        new AudioRecognizer().download_audio_text();
        let href = new HrefController().qa_system;
        window.location.href = href;
        render = new UIRender();
        render.show_dialogue();

        //鎖住所有按鈕
        render.set_btn_disabled(elements.clear_btn_id);
        render.set_btn_disabled(elements.start_btn_id);
        //render.set_btn_disabled(elements.refresh_btn_id);
        render.set_btn_disabled(elements.ask_btn_id);
    }
}

function AudioRecognizer() {
    this.speech_recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.speech_recognition.lang = 'cmn-Hant-TW';

    //初始化語音辨識物件的狀態
    this.initialize_speech_recognition = function () {
        this.speech_recognition = new this.speech_recognition();
        this.speech_recognition.status = true
        this.speech_recognition.continuous = true;
        this.speech_recognition.interimResults = true;
    };

    //讀取語音辨識的結果文字
    this.process_audio = function (event) {
        elements = new ElementController();
        let resultContainer = document.getElementById(elements.question_box_id);
        let resultList = event.results;

        for (let i = 0; i < resultList.length; i++) {
            let result = resultList.item(i);
            console.log('result[0].transcript', result[0].transcript);

            try {
                let alternative = result.item(0);
                let text = alternative.transcript;
                resultContainer.value = text;
            } catch (ex) {
                console.log('ex =', ex);
            }
            if (result.isFinal) {
                console.log('result.isFinal =', result.isFinal);
                render = new UIRender();
                render.set_btn_abled(elements.start_btn_id);
                render.set_btn_abled(elements.ask_btn_id);
                render.hide_elemet_display(elements.loading_icon_id);
                this.stop();
                break;
            }
        }
    };

    //儲存語音辨識的結果文字
    this.download_audio_text = function () {
        //儲存語音辨識的結果
        elements = new ElementController();
        let audio_text = document.getElementById(elements.question_box_id).value;
        let file = new File([audio_text], "audio_text.txt", { type: "text/plain;charset=utf-8" });
        saveAs(file);
    }

    //語音轉文字
    this.speech_to_text = function () {
        elements = new ElementController();
        render = new UIRender();
        render.set_btn_disabled(elements.start_btn_id);
        render.set_btn_disabled(elements.ask_btn_id);
        render.clear_input_box(elements.question_box_id);
        //render.set_btn_text(elements.start_btn_id, '重新對話');
        render.show_elemet_display(elements.loading_icon_id);

        //隱藏對話框
        $('#' + elements.reset_btn_id).transition('hide');
        $('#' + elements.user_speak_layout_id).transition('hide');
        $('#' + elements.c01_speak_layout_id).transition('hide');

        //進行語音辨識
        if (this.speech_recognition) {
            this.initialize_speech_recognition()
            this.speech_recognition.start()
            this.speech_recognition.addEventListener("result", this.process_audio);
        }
    }
}

function UIRender() {
    this.set_btn_disabled = function (element_id) {
        let value = document.getElementById(element_id).className;
        new_value = value.split(' ').join(' disabled ');
        document.getElementById(element_id).className = new_value;
    }

    this.set_btn_abled = function (element_id) {
        let value = document.getElementById(element_id).className;
        new_value = value.replaceAll(' disabled', '');
        document.getElementById(element_id).className = new_value;
    }

    this.clear_input_box = function (element_id) {
        let element = document.getElementById(element_id);
        element.value = '';
    }

    this.set_btn_text = function (element_id, new_text) {
        let element = document.getElementById(element_id);
        origin_text = element.innerText;
        element.innerHTML = element.innerHTML.replace(origin_text, new_text);
    }

    this.hide_elemet_display = function (element_id) {
        // let element = document.getElementById(element_id);
        // element.style.visibility = 'hidden';
        $('#' + element_id).hide();
    }

    this.show_elemet_display = function (element_id) {
        // let element = document.getElementById(element_id);
        // element.style.visibility = 'visible';
        $('#' + element_id).show();
    }

    this.show_dialogue = function () {

        elements = new ElementController();
        $('#' + elements.progress_bar_id).transition('fade up');
        var $progress = $('#' + elements.progress_bar_id), $button = $(this), updateEvent;

        // restart to zero
        clearInterval(window.loading_progress)
        $progress.progress('reset');

        // updates every 10ms until complete
        window.loading_progress = setInterval(function () {
            $progress.progress('increment');
            $button.text($progress.progress('get value'));

            // stop incrementing when complete
            if ($progress.progress('is complete')) {
                clearInterval(window.loading_progress)
                $('#' + elements.progress_bar_id).transition('fade up');
                new StaticFileLoader().load_api_function("audio-anwser-result.js");

                //顯示讀者的問題
                setTimeout(function () {
                    let user_question = document.getElementById(elements.question_box_id).value;
                    if (user_question != '') {
                        $('#' + elements.user_speak_id).text(user_question);
                    }
                    $('#' + elements.user_speak_layout_id).transition('fade left');
                    new UIRender().clear_input_box(elements.question_box_id);

                    //顯示機器人的回答
                    setTimeout(function () {
                        let c01_anwser = get_audio_anwser()['word'];
                        $('#' + elements.c01_speak_id).html(c01_anwser);
                        $('#' + elements.c01_speak_layout_id).transition('fade right');

                        //顯示重新對話按鈕
                        setTimeout(function () {
                            $('#' + elements.reset_btn_id).transition('fade up');
                        }, 2000);
                    }, 2000);
                }, 500);
            }
        }, 50);

        $('#' + elements.progress_bar_id)
            .progress({
                duration: 100,
                total: 100,
                text: {
                    active: '{value} of {total} done'
                }
            });

    }

    this.clear_dialogue = function () {
        elements = new ElementController();
        this.clear_input_box(elements.question_box_id);
        //隱藏對話框
        // $('#' + elements.reset_btn_id).transition('hide');
        // $('#' + elements.user_speak_layout_id).transition('hide');
        // $('#' + elements.c01_speak_layout_id).transition('hide');
        $('#' + elements.reset_btn_id).transition('fade up');
        $('#' + elements.user_speak_layout_id).transition('fade left');
        $('#' + elements.c01_speak_layout_id).transition('fade right');
    }

    this.reset_dialogue = function () {
        //開啟所有按鈕
        this.set_btn_abled(elements.clear_btn_id);
        this.set_btn_abled(elements.start_btn_id);
        //this.set_btn_abled(elements.refresh_btn_id);
        this.set_btn_abled(elements.ask_btn_id);

        elements = new ElementController();
        //隱藏對話框
        $('#' + elements.reset_btn_id).transition('fade up');
        $('#' + elements.user_speak_layout_id).transition('fade left');
        $('#' + elements.c01_speak_layout_id).transition('fade right');
    }
}