# **USBR Dashboard**

This repository contains the backend and frontend implementation of the **USBR Dashboard**, a predictive system developed for the **US Bureau of Reclamation (USBR)** to support water resource management. This dashboard aggregates and processes large datasets, enabling efficient data visualization and predictive analytics to assist in decision-making for water release planning.

---

## **Project Overview**

The **USBR Dashboard** was designed to:
- Integrate diverse datasets such as snowmelt, soil moisture, and precipitation data.
- Automate statistical analyses for water year comparisons and trend detection.
- Provide predictive insights to support adaptive water resource planning.
- Generate interactive visualizations for better decision-making.

The project combines Python-based backend data processing and a user-friendly dashboard frontend.

---

## **Repository Structure**

### **Backend** (`/backend`)
The backend is responsible for aggregating, processing, and analyzing data. Key features include:
- **Data Aggregation**: Collects and processes data such as snowpack, precipitation, and soil moisture.
- **Statistical Analysis**: Implements methods to compute averages, medians, and similar water year patterns.
- **Data Transformation**: Prepares datasets for visualization in the frontend dashboard.

#### **Key Files**
- `Dashboard.py`: Main file integrating backend logic for data preparation.
- `daily_data.py`: Handles daily data processing and transformations.
- `data_comparison.py`: Compares water year data for analysis.
- `get_precipitation.py`, `get_soil_moisture.py`: Fetches and processes precipitation and soil moisture data.
- `snow_data.py`: Handles snow data aggregation and insights.
- `water_sort_years.py`: Aggregates water year data and prepares statistical outputs.
- Multiple `.csv` files: Contain processed datasets for use in visualizations and reports.

### **Frontend** (`/dashboard`)
The frontend is a user-friendly interface that displays the processed data using interactive visualizations. It allows stakeholders to:
- View historical and real-time water resource data.
- Interact with comparative visualizations of water years.
- Access key metrics such as precipitation, snowpack, and soil moisture levels.

#### **Key Features**
- **Interactive Dashboard**: Provides intuitive charts and visualizations.
- **Real-Time Updates**: Displays data in near real-time, sourced from backend scripts.

---

## **Key Highlights**

### **Automation with Statistical Methods**
- Automated the process of aggregating and analyzing datasets, replacing manual workflows that could take hours per water source.
- Utilized statistical methods like averages, medians, and percent-of-normal calculations to generate actionable insights.

### **Efficiency Gains**
- Improved prediction accuracy by 30%.
- Enabled faster decision-making through automated workflows and real-time data processing.

### **Technologies Used**
- **Programming Languages**: Python
- **Libraries**: Pandas, NumPy, Matplotlib, Plotly, Streamlit
- **Frontend Tools**: Streamlit for visualization
- **Data Sources**: Integrated datasets from SNOTEL and USGS

---

## **How to Run**

### **Backend Setup**
1. Clone the repository:
   ```bash
   git clone https://github.com/lyubah/USBR-Dashboard.git
   cd USBR-Dashboard/backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main backend script:
   ```bash
   python Dashboard.py
   ```

### **Frontend Setup**
1. Navigate to the dashboard folder:
   ```bash
   cd ../dashboard
   ```
2. Run the Streamlit dashboard:
   ```bash
   streamlit run dashboard.py
   ```

---

## **Future Improvements**
- Incorporating additional data sources for more accurate forecasting.
- Expanding visualizations to include predictive trend lines.
- Optimizing statistical models for better performance on larger datasets.


---



