# IoTハンズオン：Azure IoT + AI 実践編

## 概要
ある現場の動画から切り出した画像を使って作業者の滞在状況をトラッキングして可視化する一連を体験いただきます。

## 事前準備
- Azure サブスクリプションの準備
- [Power BI Desktop のインストール](https://powerbi.microsoft.com/ja-jp/downloads/)
- [Python 3.7+ のインストール](https://www.python.org/downloads/)
- [Azure IoT Device SDK (python)](https://github.com/Azure/azure-iot-sdk-python/tree/master/azure-iot-device#installation) および必要パッケージのインストール
    ```
    pip install azure-iot-device
    pip install numpy
    pip install pandas
    pip install opencv-python
    ```     
- [サンプルコードおよびサンプルデータ](https://github.com/yahanda/hands-on-iot-customvision)のダウンロード

## 資料
こちらの[PDF資料](https://github.com/yahanda/hands-on-iot-customvision/raw/main/Hands-On-IoT-AI_CustomVision.pdf)で、Azure各サービスの概説およびハンズオン手順をまとめています

## 所要目安
約3時間

## ハンズオン構成 
![arch](https://raw.githubusercontent.com/wiki/yahanda/hands-on-iot-customvision/hands-on-arch.jpg)

## 推論結果
Custom Vision による作業者の検出結果例
![results](https://raw.githubusercontent.com/wiki/yahanda/hands-on-iot-customvision/person-detection-results.gif)
