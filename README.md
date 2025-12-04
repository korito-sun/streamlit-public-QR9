AG6液晶演出検査機QRコード判定のstreamlitファイルの公開用リポジトリ　20251204
QRコード不良ダッシュボード公開方法覚え

参考URL
https://js2iiu.com/2025/05/15/streamlit-community-cloud/#toc13

１，Githubリポジトリ作成
　① GitHubで新しいリポジトリを作成
	https://github.com にアクセスし、ログイン
	画面右上の「＋」→「New repository」
	リポジトリ名を入力（streamlit-public-QR9）
	「Create repository」ボタンをクリック
　② ローカルからコードをコミット
	作成したas_st9_fileUp.pyとrequirements.txtを用意
	GitHubリポジトリ画面で「Add file」→「Upload files」
-----------------------------------
あなたが探しているボタンの場所
画像の真ん中あたり、水色の背景のエリアの中に以下の文章があります。

Get started by creating a new file or uploading an existing file.

手元のファイルをアップロードしたい場合は、この文章の uploading an existing file というリンクをクリックしてください。これが「Add file > Upload files」と同じ機能になります。

（もしブラウザ上で新しくファイルを作りたい場合は、その左の creating a new file をクリックします）
-----------------------------------

	両ファイルをドラッグ＆ドロップしてアップロード
	「Commit changes」ボタンで保存

２，Streamlit Community Cloudでデプロイ
	① Streamlit Cloud にアクセス
	https://streamlit.io/cloud
	② 「Creat app」をクリック
	③ 必要な設定を入力
Repository	ユーザー名/リポジトリ名（例：korito-sun/streamlit-public-QR9）
Branch	main（初期設定のままでOK）
File path	as_st9_fileUp.py（メインのアプリファイル名）
	④ 「Deploy」ボタンをクリック
		数十秒でアプリがデプロイされ、公開URLが発行されます
		https://app-public-qr9-qzeenwzledyjok4jh8xxq.streamlit.app/
