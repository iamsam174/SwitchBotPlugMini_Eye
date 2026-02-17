# SwitchBot PlugMini Eye Control App

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

重度肢体不自由児・者が視線入力デバイス（Tobii Eye Tracker 5など）やアクセシビリティスイッチ入力でマウスクリックできるインターフェイスを使用して、SwitchBotプラグミニに接続された家電品を操作するためのWindowsアプリです。

大きな操作パネルと複数の動作モードを備えており、重度肢体不自由・者のスイッチ操作支援や、特定の作業中に手を離さずに家電を制御するハンズフリー用途を想定して設計されています。

---

## 📺 使い方動画（YouTube）
[こちらから操作の様子をご覧いただけます](https://youtu.be/TDidwv3S9KU)

---

## 📥 ダウンロード
右側の **[Releases]** セクション、または [こちらのリリースページ](https://github.com/iamsam174/SwitchBotPlugMini_Eye/releases/latest) から、最新の **EXEファイル** と **かんたんガイド(PDF)** をダウンロードできます。

---

## 🚀 主な機能

 ・巨大操作パネル: 視線入力でも捉えやすい大きなボタン。

 ・ 3つの動作モード:

　 ①クリック/注視実行（設定秒数ON）

　 ②マウスオーバー実行（重なるとタイマー開始）

　 ③ホールド実行（ポインターがある間だけON）

・カメラ表示: ボタン背景にウェブカメラ映像を表示可能。

・自由な移動: 操作ボタンは画面上の好きな場所へドラッグ可能。

---

## 🛠 セットアップ
　1. 動作環境: Windows 10/11, Python 3.8+。

 2. ライブラリのインストール:

  Bash
  pip install bleak opencv-python pillow

 3.起動:

  Bash
  python SwitchBotPlugMini_Eye.py

---

## 📖 使い方
1. スキャン: 「🔍 SwitchBotプラグミニを探査」をクリック。

2. 接続: リストからデバイスを選び「接続」をクリック。

3. 設定: タイマー秒数や動作モード、カメラ出力を選択。

4. 操作: 中央の大きなボタンでプラグを制御。

---

## ⌨️ キーボードショートカット
 ・ F11: 全画面切替

 ・ Esc: 全画面解除

 ・ 1 / 2 / 3: 動作モードの即時切替

---

## 🔧 技術情報
 ・ BLE通信: bleak を使用（UUID: cba20002-224d-11e6-9fb8-0002a5d5c51b）。

 ・ GUI: tkinter による非同期制御。

 ・ 制限: Windows専用（winsound 使用のため）。

---

## 📄 ライセンス
MIT License のもとで公開されています。
