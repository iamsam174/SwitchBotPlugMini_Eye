# SwitchBot PlugMini Eye Control App

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

マウス操作、または視線入力デバイス（Eye Tracker）を使用して **SwitchBot プラグミニ** を直感的に制御するためのアプリケーションです。

大きな操作パネルと複数の動作モードを備えており、肢体不自由な方のスイッチ操作支援（ICT救助）や、特定の作業中に手を離さずに家電を制御するハンズフリー用途を想定して設計されています。

---

## 🚀 主な機能

* **直感的な巨大ボタン**: 視線入力や不随意運動のある方でも捉えやすい、カスタマイズ可能な巨大操作エリア。
* **3つの動作モード**:
    1.  **クリック/注視でタイマー実行**: ボタンを押す（または一定時間注視する）と設定秒数だけON。
    2.  **マウスオーバーでタイマー実行**: マウスポインターが重なるだけで自動的にタイマー開始。
    3.  **ホールド実行**: マウスポインターがボタン内にある間だけON、離すとOFF。
* **カメラ映像の重畳**: 操作ボタンの背景にウェブカメラの映像を表示。対象物や自身の姿勢を確認しながら操作可能。
* **自由なレイアウト**: ボタンサイズの変更（4段階）や、画面内でのドラッグ＆ドロップによる自由な位置移動に対応。
* **非同期BLE通信**: UIをフリーズさせることなく、Bluetooth Low Energy（BLE）経由でデバイスを制御。

---

## 🛠 セットアップ

### 1. 動作環境
* **OS**: Windows 10 / 11（Bluetooth 内蔵、または USB Bluetooth アダプタ搭載）
* **Python**: 3.8 以上

### 2. 依存ライブラリのインストール
ターミナルまたはコマンドプロンプトで以下のコマンドを実行してください。

```bash
pip install bleak opencv-python pillow
