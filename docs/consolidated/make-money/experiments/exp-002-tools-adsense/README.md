# Exp-002: 工具站 AdSense

## 假設
所有 GitHub Pages 工具站（計算機、PDF工具、壓縮工具等）如果能串接 Google AdSense，
只要有每日 100 UV，就能產生穩定廣告收益。

## 方法
1. 在所有工具站的 HTML 插入 Google AdSense code
2. 使用 GitHub Actions 自動化部署最新版本
3. 透過 YouTube Shorts description + SEO 導流

## 優先工具站
| 站點 | 類型 | 流量潛力 |
|------|------|---------|
| calculators | 日常計算（BMI/百分比/貸款） | 🟢 高 |
| pdf-tools | 圖片轉PDF/合併 | 🟢 高 |
| image-compressor | 圖片壓縮 | 🟢 高 |
| qr-code-generator | QR Code | 🟡 中 |
| color-tools | 調色盤/漸層 | 🟡 中 |
| dev-tools | 開發者工具 | 🟡 中 |
| token-cost-calculator | LLM費用估算 | 🟢 高 |
| ai-image-size-calculator | AI尺寸計算 | 🟢 高 |

## 實作
在每個工具站的 `index.html` 加入 AdSense 廣告程式碼區塊，
使用 responsive ad units 自適應螢幕大小。

## KPI
- [ ] AdSense 申請通過
- [ ] 每日 page views
- [ ] 每日廣告曝光次數
- [ ] RPM（每千次曝光收益）
- [ ] 月收入

## 結果

記錄開始日期：—
AdSense 核准日期：—
第一筆收入日期：—
