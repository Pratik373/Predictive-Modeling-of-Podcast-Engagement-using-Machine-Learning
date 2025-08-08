# 🎧 Predictive Modeling of Podcast Engagement Using Machine Learning

## 📌 Objective
This project aims to predict the **listening time (in minutes)** for podcast episodes based on various features like episode duration, genre, host/guest popularity, number of ads, and sentiment. It uses supervised machine learning models to assist podcast platforms in optimizing content engagement.

---

## 📁 Project Structure

```
PODCAST_PROJECT/
│
├── app.py                  # Flask web application
├── dep/                    # Dependencies
├── .gitignore              # Ignore .pkl files, cache, etc.
├── download_model.sh       # Shell script to download .pkl model files
├── feature_columns.pkl     # Feature columns
├── random_forest.pkl       # (Ignored from Git - download required)
├── scaler.pkl              # (Ignored from Git - download required)
├── README.md               # Project documentation (this file)
```

---

## 🧠 Features Used
- Podcast Name
- Episode Title & Length
- Genre
- Host & Guest Popularity
- Publication Day and Time
- Number of Ads
- Episode Sentiment
- Listening Time (target)

---

## ⚙️ Tech Stack
- Python 3.x
- Flask
- scikit-learn
- Pandas, NumPy
- MySQL (for DB integration)
- Git + GitHub

---

## 🚀 Getting Started

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/Pratik373/Predictive-Modeling-of-Podcast-Engagement-using-Machine-Learning.git
cd Predictive-Modeling-of-Podcast-Engagement-using-Machine-Learning
```

### 2️⃣ Install Dependencies
```bash
pip install -r dep/requirements.txt
```

### 3️⃣ Download Trained Models
Run the following script to fetch `.pkl` files from Google Drive:
```bash
chmod +x download_model.sh
./download_model.sh
```

This will download:
- `random_forest.pkl`
- `scaler.pkl`

⚠️ These files are ignored in Git for size reasons.

### 4️⃣ Run the Flask App
```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

---

## 📈 Evaluation Metric

The model is evaluated using **RMSE and R2score** — RMSE effectively measures the average magnitude of prediction errors, providing insight into how close the predicted engagement levels are to the actual values, while R² score indicates how well the model explains the variability of the engagement data, making both metrics suitable for assessing and ranking predicted engagement levels accurately.

---
## Tableau Link
https://public.tableau.com/app/profile/pratik.dange/viz/Podcast_Project_Dashboard/Dashboard2

<img width="1366" height="719" alt="image" src="https://github.com/user-attachments/assets/4709b2f0-da38-4e86-8f6b-c801f7bceaf9" />



## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👥 Contributors

- **Chinmay Thete** – Model building, feature engineering, Data cleaning.
- **Pratik373** – Exploratory Data Analysis, Data Visualization, Model building, UI.
- **Vaibhav9006** – Statistical analysis, Data Visualization, Model building, UI and deployment.
- **Tejas Sorte** – statistical analysis,Model building, Neural Network.
