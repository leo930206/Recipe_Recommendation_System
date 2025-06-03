# 食材運用推薦系統

## 專案介紹

智慧食材推薦系統是一套以 Python 開發的桌面應用程式，旨在幫助使用者根據手邊現有的食材，推薦最適合的食譜，達成有效利用剩餘食材、減少浪費及購買食材的目標。本系統結合網路爬蟲、資料處理與快速搜尋技術，提供簡潔且實用的使用介面，方便使用者快速找到可烹調的菜餚。

## 主要功能

- **食材輸入介面**：可輸入多種食材，系統將根據現有食材智能推薦食譜。
- **同義詞處理**：利用同義詞對照表解決食材名稱不一致問題，提高搜尋命中率。
- **結果排序**：優先推薦使用者擁有最多食材且缺少食材最少的食譜。
- **詳細食譜展示**：包含食譜名稱、標籤、食材清單、份量、烹調時間及詳細步驟。
- **使用者介面**：基於 Tkinter 製作，支援動態排版與自動換行，提升操作體驗。

## 技術說明

- 資料爬取：使用 Python 的 requests 和 BeautifulSoup 套件，從 icook 愛料理網站爬取食譜相關資訊。
- 資料處理：利用 Pandas 進行資料清洗與結構化。
- 同義詞處理：建立同義詞對照表，於搜尋前將輸入食材轉換成統一標準。
- 搜尋優化：
  - 導入快取機制，將預處理後資料使用 pickle 存於本地，加速程式啟動。
  - 使用倒排索引（Inverted Index）技術，減少搜尋比對範圍，提高效能。
- 排序邏輯：
  - 優先顯示使用者擁有食材數量多的食譜。
  - 同數量情況下，優先顯示缺少食材數量少的食譜。
- GUI：採用 Tkinter，配合自訂 FlowFrame 元件實現動態排版與視窗自適應。

## 環境需求

- Python 3.8 以上
- 需要安裝的套件：
  - pandas
  - openpyxl
  - tkinter（Python 內建）

可使用以下指令安裝所需套件：

`pip install pandas openpyxl`

## 使用說明
1. 確保已安裝所需 Python 套件。
2. 執行 icook_scraper.py 以爬取最新食譜資料，資料將儲存為 recipes.xlsx。(如果想用預設食譜 可以跳過此步驟)
3. 使用 create_synonyms_excel.py 產生或更新同義詞表 synonyms.xlsx。(如果想用預設食譜 可以跳過此步驟)
4. 執行主程式 recipe_recommendation_system.py。
5. 在輸入框輸入你擁有的食材（多個以空格分隔），點擊「開始搜尋」。
6. 系統會顯示符合條件的食譜，並可查看詳細內容。

--------------------------------------------------------------

# Recipe Recommendation System

## Project Overview

The Recipe Recommendation System is a desktop application developed in Python designed to help users find the most suitable recipes based on the ingredients they currently have. The system aims to effectively utilize leftover ingredients, reduce food waste, and minimize unnecessary ingredient purchases. By combining web scraping, data processing, and fast search techniques, the system provides a simple and practical user interface, enabling users to quickly discover dishes they can cook.

## Main Features

- **Ingredient Input Interface**: Allows users to input multiple ingredients, and the system intelligently recommends recipes based on available ingredients.
- **Synonym Handling**: Uses a synonym dictionary to resolve inconsistencies in ingredient names, improving search accuracy.
- **Result Sorting**: Prioritizes recipes where users have the most ingredients and require the fewest missing ones.
- **Detailed Recipe Display**: Shows recipe name, tags, ingredient list, servings, cooking time, and step-by-step instructions.
- **User Interface**: Built with Tkinter, supports dynamic layout and automatic text wrapping for improved user experience.

## Technical Details

- Data Crawling: Uses Python libraries such as requests and BeautifulSoup to scrape recipe data from the icook website.
- Data Processing: Uses Pandas for data cleaning and structuring.
- Synonym Handling: Builds a synonym mapping table to standardize ingredient names before searching.
- Search Optimization:
  - Implements caching using Python’s pickle to store preprocessed data locally, speeding up startup.
  - Utilizes an inverted index to reduce search scope and increase efficiency.
- Sorting Logic:
  - Recipes with more owned ingredients are prioritized.
  - If the number of owned ingredients is the same, recipes with fewer missing ingredients are prioritized.
- GUI: Developed with Tkinter and enhanced with a custom FlowFrame component for dynamic layout and responsive window adaptation.

## Environment Requirements

- Python 3.8 or higher
- Required packages:
  - pandas
  - openpyxl
  - tkinter (built into Python)

Install required packages using:

`pip install pandas openpyxl`

## Usage Instructions
1. Make sure required Python packages are installed.
2. Run icook_scraper.py to crawl the latest recipe data, which will be saved as recipes.xlsx. (Skip if you want to use the default recipe data)
3. Use create_synonyms_excel.py to generate or update the synonym dictionary file synonyms.xlsx. (Skip if you want to use the default synonym file)
4. Run the main program recipe_recommendation_system.py.
5. Input your available ingredients in the input box (multiple ingredients separated by spaces), then click "Start Search".
6. The system will display a list of matching recipes and you can view detailed recipe information.
