# AI-Assignment-1: 自動搜集圖像數據集與初步處理

## 習作簡介

本習作實現了一個自動化圖像數據集搜集和處理系統。系統能夠：
- 自動從網上搜尋圖像（使用 Bing 圖像搜索）
- 收集 3000-5000 個圖像
- 提取圖像的網址（src）和替代文字（alt）
- 自動下載圖像到本地資料夾
- 自動調整大小並置中裁剪為不超過 500x500 像素
- 編碼為 JPEG 格式（50-80 質量）
- 如果圖像大小超過 50KB，自動調整為更小的尺寸
- 統計並列出收集的圖像數量

## 系統要求

- Python 3.7 或更高版本
- 網絡連接

## 安裝

1. 克隆本倉庫：
```bash
git clone https://github.com/Spike-forward/AI-Assignment-1.git
cd AI-Assignment-1
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python image_collector.py "關鍵字"
```

例如，搜集貓的圖像：
```bash
python image_collector.py "cat"
```

### 進階選項

```bash
python image_collector.py [關鍵字] [選項]

必需參數:
  關鍵字              搜索的關鍵字

可選參數:
  -h, --help         顯示幫助信息
  --output DIR       輸出目錄（默認：images）
  --max-images N     最大圖像數量（默認：5000）
  --min-images N     最小圖像數量（默認：3000）
```

### 使用範例

1. 收集風景圖片，保存到 landscape 文件夾：
```bash
python image_collector.py "landscape" --output landscape
```

2. 收集最多 4000 張汽車圖片：
```bash
python image_collector.py "car" --max-images 4000
```

3. 收集建築圖片，要求至少 3500 張：
```bash
python image_collector.py "architecture" --min-images 3500
```

## 輸出結構

程序運行後會創建以下結構：

```
images/                    # 輸出目錄（或自定義目錄）
├── image_00001.jpg       # 處理後的圖像文件
├── image_00002.jpg
├── ...
└── metadata.json         # 元數據文件
```

### metadata.json 格式

```json
[
  {
    "filename": "image_00001.jpg",
    "original_url": "https://example.com/image.jpg",
    "alt_text": "圖像描述",
    "size": 45678
  },
  ...
]
```

## 圖像處理規格

所有下載的圖像都會經過以下處理：

1. **格式轉換**：轉換為 JPEG 格式
2. **尺寸調整**：調整為不超過 500x500 像素
3. **置中裁剪**：保持圖像主要內容居中
4. **質量優化**：使用 50-80 的 JPEG 質量
5. **大小限制**：確保文件大小不超過 50KB
   - 如果超過，自動降低質量或進一步縮小尺寸

## 功能特點

- ✅ 自動化搜索和下載
- ✅ 智能圖像處理和優化
- ✅ 保存元數據（URL 和 alt 文字）
- ✅ 進度顯示和統計
- ✅ 錯誤處理和重試機制
- ✅ 文件大小自動優化
- ✅ 符合 50KB 大小限制

## 技術實現

- **語言**：Python 3
- **網絡請求**：requests
- **HTML 解析**：BeautifulSoup4
- **圖像處理**：Pillow (PIL)

## 注意事項

1. 程序會自動處理網絡錯誤和下載失敗的情況
2. 下載過程中會有適當的延遲，避免對服務器造成過大壓力
3. 某些圖像可能因為各種原因無法下載，程序會自動跳過並繼續
4. 實際收集到的圖像數量可能少於目標數量，這取決於搜索結果的質量

## 許可證

MIT License

## 作者

AI Assignment 1 Project