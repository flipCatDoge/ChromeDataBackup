# ChromeDataBackup
谷歌浏览器用户数据备份 Google Chrome user data backup

## 介绍 Introduction
今天（2024年10月14日），当我愉快的吃完午饭，回到电脑前，打开浏览器的时候，天塌了，我的浏览器数据全没了，经过再三确认，发现有一个用户的数据损坏了，无法恢复，另外两个用户的数据还在，真的是太痛啦！研究一番之后，才知道谷歌用户数据是可以很简单粗暴的进行备份的，只需要将浏览器的用户数据目录（默认路径为：C:\Users\用户名\AppData\Local\Google\Chrome\User Data）拷贝到其他位置即可。考虑到每次进行备份，需要鼠标点点点，因此，我写了这个软件，自动化备份用户数据。

## 脚本使用方法 Usage
1. 下载软件：ChromeDataBackup.exe（找到当前网页的Tags或者Releases页面，下载“ChromeDataBackup_V1.0.exe”即可）
2. 将软件放置到任意目录，如：C:\Program Files\ChromeDataBackup
3. 打开软件，点击“开始备份”按钮，然后选择备份目录，等待备份完成即可。

## 注意事项 Attention
1. 备份前请关闭浏览器，否则会导致备份失败。
2. 请不要在备份过程中打开任何文件，否则会导致备份失败。
3. 由于恢复数据的情况很少，因此采用手动拷贝的方式进行恢复，软件就不提供恢复功能了。

## 数据备份及恢复参考文章：
[google浏览器chrome用户数据（拓展程序，书签等）丢失问题](https://blog.csdn.net/zqx1473/article/details/141353384?spm=1001.2101.3001.6650.4&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EYuanLiJiHua%7EPosition-4-141353384-blog-130823648.235%5Ev43%5Epc_blog_bottom_relevance_base8&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EYuanLiJiHua%7EPosition-4-141353384-blog-130823648.235%5Ev43%5Epc_blog_bottom_relevance_base8&utm_relevant_index=9)
