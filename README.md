<> 安裝:
1. 將整個目錄直接放置桌面即可，主程式為C01_main.py，會自動抓取C01_config.xml設定檔案。
2. 設定本機相關程式之目錄，如下項目所示:

2.1 C01_config.xml
2.1.1 下載檔案存放位置(/audio_text/from_dir)
2.1.2 ALMA API相關參數(/alma_api)
2.1.3 K8S集群API相關參數(sysk8s)
2.1.4 ROS API相關參數(/robot_api)
<!-- 2.1.5 Chrome主程式位置(run_chrome/file_dir) -->

2.2 C01_main.js
2.2.1 JS端呼叫用的API(APISources)
2.2.2 相關檔案或額外URL(本地檔案檔名/預設書封等)

2.3 C01_main.bat
2.3.1 本機python目錄(python_dir)、C01主程式目錄位置(program)
2.3.2 相關.bat當中，呼叫指定的main.ba目錄位置(program)

3. 機碼設定
請參考相關筆記步驟圖解
3.1 C01-qa-ask-question -> URL Protocol
3.1.1 DefaultIcon -> "D:\\hanwen\\git-repos\\nccu_c01_dev\\bat\\qa_ask_question.bat"
3.1.2 shell
3.1.2.1 open
3.1.2.1.1 command -> "D:\\hanwen\\git-repos\\nccu_c01_dev\\bat\\qa_ask_question.bat"

4. chrome瀏覽器擴充套件下載
4.1 Disable Download Bar(v1.5)

<> 啟動:
1. 上述設定配置完成後，直接將C01_main.html拉到google chrome開啟即可。