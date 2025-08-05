import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

# Load model, scaler, and feature columns
with open("random_forest.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)

fields = [
    'Podcast_Name', 'Episode_Title', 'Episode_Length_minutes', 'Genre',
    'Host_Popularity_percentage', 'Publication_Day', 'Publication_Time',
    'Guest_Popularity_percentage', 'Number_of_Ads', 'Episode_Sentiment'
]
categorical_fields = ['Podcast_Name', 'Genre', 'Publication_Day', 'Publication_Time', 'Episode_Sentiment']
options = {
    'Podcast_Name': ['Mystery Matters', 'Joke Junction', 'Study Sessions',
       'Digital Digest', 'Mind & Body', 'Fitness First', 'Criminal Minds',
       'News Roundup', 'Daily Digest', 'Music Matters', 'Sports Central',
       'Melody Mix', 'Game Day', 'Gadget Geek', 'Global News',
       'Tech Talks', 'Sport Spot', 'Funny Folks', 'Sports Weekly',
       'Business Briefs', 'Tech Trends', 'Innovators', 'Health Hour',
       'Comedy Corner', 'Sound Waves', 'Brain Boost', "Athlete's Arena",
       'Wellness Wave', 'Style Guide', 'World Watch', 'Humor Hub',
       'Money Matters', 'Healthy Living', 'Home & Living',
       'Educational Nuggets', 'Market Masters', 'Learning Lab',
       'Lifestyle Lounge', 'Crime Chronicles', 'Detective Diaries',
       'Life Lessons', 'Current Affairs', 'Finance Focus', 'Laugh Line',
       'True Crime Stories', 'Business Insights', 'Fashion Forward',
       'Tune Time'],
    'Genre': ['Education', 'Technology', 'Comedy', 'Business', 'Music', 'Health', 'Lifestyle', 'News', 'Sports', 'True Crime'],
    'Publication_Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'Publication_Time': ['Morning', 'Afternoon', 'Evening', 'Night'],
    'Episode_Sentiment': ['Positive', 'Neutral', 'Negative']
}
db_config = {'host': 'localhost', 'user': 'root', 'password': 'root', 'database': 'podcast'}

@app.route("/", methods=["GET"])
def home():
    return render_template("form.html",
        fields=fields,
        prediction=None,
        categorical_fields=categorical_fields,
        options=options)

@app.route("/predict", methods=["POST"])
def predict():
    form_input = {field: request.form[field] for field in fields}
    numeric_fields = [
        'Episode_Length_minutes', 'Host_Popularity_percentage',
        'Guest_Popularity_percentage', 'Number_of_Ads'
    ]
    for field in numeric_fields:
        try:
            form_input[field] = float(form_input[field])
        except ValueError:
            form_input[field] = 0.0

    # Drop or ignore 'Episode_Title' if not used in model
    input_df = pd.DataFrame([form_input])
    input_df = input_df.drop(['Episode_Title'], axis=1)

    # One-hot encode
    input_ohe = pd.get_dummies(input_df)

    # Provide all expected columns and re-order, fill missing with 0
    input_ohe = input_ohe.reindex(columns=feature_columns, fill_value=0)

    # Scale inputs just like in training
    input_scaled = scaler.transform(input_ohe)

    # Predict
    prediction = model.predict(input_scaled)[0]

    # --- MySQL insert logic START ---
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO prediction_results
            (Podcast_Name, Episode_Length_minutes, Genre, Host_Popularity_percentage,
             Publication_Day, Publication_Time, Guest_Popularity_percentage,
             Number_of_Ads, Episode_Sentiment, prediction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            form_input['Podcast_Name'],
            form_input['Episode_Length_minutes'],
            form_input['Genre'],
            form_input['Host_Popularity_percentage'],
            form_input['Publication_Day'],
            form_input['Publication_Time'],
            form_input['Guest_Popularity_percentage'],
            form_input['Number_of_Ads'],
            form_input['Episode_Sentiment'],
            prediction
        )

        cursor.execute(insert_query, values)
        conn.commit()

    except mysql.connector.Error as err:
        print("MySQL Error:", err)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    # --- MySQL insert logic END ---

    return render_template(
        "form.html",
        fields=fields,
        prediction=prediction,
        categorical_fields=categorical_fields,
        options=options
    )

if __name__ == "__main__":
    app.run(debug=True)
