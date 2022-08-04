---
marp: true

---
## Webテクノロジ
Webアプリケーション作成課題
2122084 伴 匠生
<!-- paginate: true -->
<!-- footer: ©︎2022 Takumi Ban -->
---
## 何を作ったか
### オリジナル機械学習モデルの検知結果を共有・競争するアプリ
- **目的**
自分で作成した機械学習モデルを使用して、実際にデータを与え推論をさせ
その推論結果を記録・共有すること
- **なぜ作ったか**
課題などで全員が同じものを推論・検知するモデルを構築した時に実際に精度を競うことができたら、精度の検証や向上に有効だと考えたから
参考)[シンギュラリティバトルクエスト](https://singularitybattlequest.club/Competitions/index.html)

---
## 何を作ったか
- 今回は物体検知モデル**YOLOv5**の学習済みモデルの検知結果を共有できるアプリを作成
参考)[YOLOv5 -GitHub](https://github.com/ultralytics/yolov5)
※本アプリケーションの機能を実行するために物体検知モデルYOLOv5を使用している
　YOLOv5に関係する一切の権利は著作者に帰属する


---
## ファイル構成
```
.
├── README.md #現在開いているファイル
├── app.py # アプリケーションの実行ファイル
├── sugoi.db # データベース(sqlite)
├── templates # htmlファイル
│   ├── history.html
│   ├── index.html
│   ├── layout.html
│   ├── login.html
│   ├── play.html
│   ├── register.html
│   └── upload.html
├── upload # アプリケーションを通してアップロードされたファイル置き場
│   ├── images
│   │   └── bus.jpg
│   └── models
│       └── yolov5s.pt
└── yolov5 # 物体検知モデルYOLOv5
```

---
## 機能
- ログイン・ユーザ登録機能
ユーザの判別機能
- オリジナル学習モデルアップロード機能
本アプリケーションを通じて推論を行うための学習モデルをアップロードする機能
- 検出結果閲覧機能
推論を実行したユーザ名・実際のラベル・推論結果のラベルを共有・閲覧する機能
- 推論実行機能
オリジナルの機械学習モデルを使用して推論をワンクリックで実行できる機能
モデルパスや検出画像パスの指定は自動、面倒なパス指定の必要はない

---
## DB定義
- ユーザ情報を格納するテーブル
パスワードはハッシュ化して保存

| id | ユーザ名 | パスワード |
| :---: | :---: | :---: |
| 1 | nenai | kokofkwgew |

- 推論結果を保存するテーブル

| id | ユーザ名 | 正解ラベル | 推論結果ラベル |
| :---: | :---: | :---: | :---: |
| 1 | nenai | 0 | 0 |
| 2 | sleep | 1 | 2 | 

※表内のデータは例

---
## 実装
- フロントエンド
HTML・Bootstrap・JavaScript
- バックエンド
  - 言語: Python
  - フレームワーク: Flask
  - データベース: sqlite