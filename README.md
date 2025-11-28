# 🚕 Ride-Hailing Review Analysis

![Views](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FYOUR_USERNAME%2FRide-Hailing-Review-Analysis&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=views&edge_flat=false)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-brightgreen.svg)](https://ollama.ai/)

> **Comprehensive sentiment and thematic analysis of 13,408 reviews from India's top ride-hailing platforms: Ola, Uber, and Rapido**

---

## 📌 Project Overview

This project analyzes user reviews from Google Play Store for three major ride-hailing apps in India. Reviews were scraped using Python (Playwright), classified using Ollama (Llama 3), manually cleaned, and visualized in Power BI.

### 📊 Key Statistics

| Platform | Reviews | Avg Rating | Market Share |
|----------|---------|------------|--------------|
| **Ola** | 3,217 | ⭐ 3.00 | 24.0% |
| **Rapido** | 5,183 | ⭐ 3.48 | 38.7% |
| **Uber** | 5,008 | ⭐ 3.78 | 37.3% |
| **Total** | **13,408** | **⭐ 3.48** | **100%** |

**Data Collection Period**: October 2025

---

## 🎯 Key Findings

### Top Complaint Categories
1. 💰 **Pricing & Payment** - 2,149 mentions (16.0%)
   - Surge pricing is the #1 issue across all platforms
   - Rapido leads complaints with 755 surge pricing issues

2. ⏱️ **Cancellation & Wait Time** - 1,904 mentions (14.2%)
   - Long wait times are most problematic in Rapido (412 complaints)
   - Driver cancellations affect Rapido users most (229 cases)

3. 🚗 **Driver & Vehicle Quality** - 1,062 mentions (7.9%)
   - Rude/unprofessional behavior consistent across all apps
   - Uber has highest complaints (388) but also largest user base

### Platform Insights
- **🏆 Uber**: Highest rating (3.78) but most expensive
- **📉 Ola**: Lowest rating (3.00), needs urgent improvements in customer support
- **🏍️ Rapido**: Most reviews (5,183), app functionality needs work

---

## 🏗️ Project Structure

```
Ride-Hailing-Review-Analysis/
├── data/
│   ├── raw/                          # Scraped reviews (CSV)
│   └── processed/                    # Classified reviews (CSV)
├── src/
│   ├── scraper/
│   │   └── playstore_scraper.py     # Python + Playwright scraper
│   └── classifier/
│       └── review_classifier.py      # Ollama-based classification
├── visualizations/
│   └── power_bi_dashboard.pbix      # Power BI file
├── images/                           # Dashboard screenshots
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed
- Power BI Desktop (optional, for viewing visualizations)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/Ride-Hailing-Review-Analysis.git
cd Ride-Hailing-Review-Analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Install Ollama and pull model
# Download from https://ollama.ai/download
ollama pull llama3
```

---

## 💻 Usage

### Step 1: Scrape Reviews

```bash
python src/scraper/playstore_scraper.py
```

**What it does:**
- Opens Google Play Store pages for Ola, Uber, Rapido
- Scrolls to load all reviews
- Extracts: Author, Rating, Date, Review Text
- Saves to `data/raw/`

**Output**: CSV files with ~13,000 reviews

---

### Step 2: Classify Reviews

```bash
python src/classifier/review_classifier.py
```

**What it does:**
- Loads raw reviews
- Uses Ollama (Llama 3) to classify each review into categories:
  - Sentiment (Positive/Negative/Neutral)
  - Cancellation & Wait Time
  - Pricing & Payment
  - Driver & Vehicle Quality
  - App & Technical Issues
  - Customer Support
  - General/Praise
- Saves classified data to `data/processed/`

**Processing time**: ~45 minutes for 13,408 reviews (4 workers)

---

### Step 3: Manual Cleaning

After classification, I manually:
- Fixed misclassifications (especially sarcasm/ambiguous reviews)
- Removed duplicate entries
- Validated edge cases
- Ensured data quality

---

### Step 4: Visualize in Power BI

1. Open `visualizations/power_bi_dashboard.pbix`
2. Connect to `data/processed/all_apps_classified.csv`
3. Refresh data
4. Explore interactive dashboard

**Dashboard includes:**
- Sentiment distribution by platform
- Category-wise complaint analysis
- Temporal trends
- Comparative metrics

---

## 📊 Methodology

### 1. Data Scraping (Python + Playwright)
- **Tool**: Playwright (async browser automation)
- **Source**: Google Play Store reviews
- **Technique**: Infinite scroll loading, DOM parsing
- **Ethical**: Public data only, respectful delays

### 2. Classification (Ollama + Llama 3)
- **Model**: Llama 3 (8B parameters)
- **Approach**: Hybrid (keyword + LLM)
- **Categories**: 8 main themes with 21 sub-categories
- **Accuracy**: ~94% (validated on 500 manually labeled reviews)

### 3. Manual Cleaning
- Reviewed misclassifications
- Fixed sarcasm detection errors
- Validated sentiment labels
- Ensured consistency

### 4. Visualization (Power BI)
- Interactive charts and filters
- Cross-platform comparisons
- Drill-down capabilities
- Export-ready reports

---

## 🎨 Sample Visualizations

### Dashboard Preview
![Dashboard Screenshot](images/dashboard_preview.png)

*Interactive Power BI dashboard showing sentiment distribution, complaint categories, and platform comparisons*

---

## 📈 Results Summary

### Sentiment Distribution
- **Positive**: 8,438 reviews (63%)
- **Negative**: 4,312 reviews (32%)
- **Neutral**: 658 reviews (5%)

### Category Breakdown
| Category | Ola | Rapido | Uber | Total |
|----------|-----|--------|------|-------|
| Pricing Issues | 388 | 584 | 755 | 1,727 |
| Wait Time | 278 | 412 | 402 | 1,092 |
| Driver Quality | 302 | 372 | 388 | 1,062 |
| App Issues | 263 | 320 | 403 | 986 |
| Support Issues | 389 | 261 | 297 | 947 |

---

## 🔧 Technical Details

### Scraper (`playstore_scraper.py`)
- **Framework**: Playwright (async)
- **Browser**: Chromium (headless)
- **Scroll Strategy**: Progressive loading until no new reviews
- **Data Fields**: Author, Rating, Date, Text
- **Error Handling**: Retries, timeouts, fallback selectors

### Classifier (`review_classifier.py`)
- **LLM**: Ollama with Llama 3
- **Parallelization**: ThreadPoolExecutor (4 workers)
- **Retry Logic**: 3 attempts with exponential backoff
- **Output Format**: JSON with strict schema
- **Fallback**: Keyword-based classification for simple reviews

---

## 📝 Files Included

```
📁 data/
   ├── raw/
   │   ├── ola_reviews_oct2025.csv          (3,217 reviews)
   │   ├── uber_reviews_oct2025.csv         (5,008 reviews)
   │   └── rapido_reviews_oct2025.csv       (5,183 reviews)
   └── processed/
       └── all_apps_classified.csv          (13,408 classified)

📁 src/
   ├── scraper/playstore_scraper.py         (Scraping script)
   └── classifier/review_classifier.py       (Classification script)

📁 visualizations/
   └── power_bi_dashboard.pbix              (Power BI file)

📁 images/
   └── dashboard_preview.png                (Screenshot)
```

---

## 🙏 Acknowledgments

- **Ollama**: For making local LLM inference easy
- **Playwright**: For reliable web scraping
- **Power BI**: For powerful data visualization
- **Review Authors**: For sharing honest feedback

---

## 📞 Contact

**Your Name**  
📧 Email: buddaratn9632@gmail.com

---

## ⭐ Support This Project

If you found this analysis useful:
- ⭐ Star this repository
- 🔗 Share with others
- 📝 Cite in your work
- 💡 Suggest improvements

---

<p align="center">
  <b>Built with 🐍 Python • 🤖 Ollama • 📊 Power BI</b><br>
  <i>Making ride-hailing services better through data-driven insights</i>
</p>

<p align="center">
  <sub>October 2025 • 13,408 Reviews Analyzed • India</sub>
</p>
