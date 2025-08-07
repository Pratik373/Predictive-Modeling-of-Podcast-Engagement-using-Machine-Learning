import pickle
import pandas as pd
from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

# --- Lazy ML resource loading ---
model = None
scaler = None
feature_columns = None

def load_resources():
    global model, scaler, feature_columns
    if model is None or scaler is None or feature_columns is None:
        with open("random_forest.pkl", "rb") as f:
            model = pickle.load(f)
        with open("scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        with open("feature_columns.pkl", "rb") as f:
            feature_columns = pickle.load(f)

# --- App fields and metadata ---
fields = [
    'Podcast_Name', 'Episode_Title', 'Episode_Length_minutes', 'Genre',
    'Host_Popularity_percentage', 'Publication_Day', 'Publication_Time',
    'Guest_Popularity_percentage', 'Number_of_Ads', 'Episode_Sentiment'
]

categorical_fields = ['Podcast_Name', 'Genre', 'Publication_Day', 'Publication_Time', 'Episode_Sentiment']

options = {
    'Podcast_Name': ["Athlete's Arena", "Brain Boost", "Business Briefs", "Comedy Corner", "Criminal Minds",
                     "Current Affairs", "Daily Digest", "Detective Diaries", "Digital Digest", "Educational Nuggets",
                     "Fashion Forward", "Finance Focus", "Fitness First", "Funny Folks", "Gadget Geek", "Game Day",
                     "Global News", "Health Hour", "Healthy Living", "Home & Living", "Humor Hub", "Innovators",
                     "Joke Junction", "Laugh Line", "Learning Lab", "Life Lessons", "Lifestyle Lounge",
                     "Market Masters", "Melody Mix", "Mind & Body", "Money Matters", "Music Matters",
                     "Mystery Matters", "News Roundup", "Sound Waves", "Sport Spot", "Sports Central",
                     "Sports Weekly", "Study Sessions", "Style Guide", "Tech Talks", "Tech Trends",
                     "True Crime Stories", "Tune Time", "Wellness Wave", "World Watch", "Business Insights"],
    'Genre': ['Education', 'Technology', 'Comedy', 'Business', 'Music', 'Health', 'Lifestyle', 'News', 'Sports', 'True Crime'],
    'Publication_Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'Publication_Time': ['Morning', 'Afternoon', 'Evening', 'Night'],
    'Episode_Sentiment': ['Positive', 'Neutral', 'Negative']
}

DASHBOARD1_URL = "https://public.tableau.com/views/Podcast_Project_Dashboard/Dashboard1"
DASHBOARD2_URL = "https://public.tableau.com/views/Podcast_Project_Dashboard/Dashboard2"

db_config = {'host': 'localhost', 'user': 'root', 'password': 'Tejas@123!', 'database': 'PODCAST'}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>Podcast Performance Predictor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        html, body {
            min-height: 100vh; width: 100vw; overflow-x: hidden;
        }
        body {
            min-height: 100vh; width: 100vw;
            background: #f6f9fb;
            background-image:
                /* SVG microphone */
                url('data:image/svg+xml;utf8,<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg"><g opacity="0.2"><ellipse cx="250" cy="280" rx="110" ry="160" fill="%237dafff"/><rect x="215" y="130" width="70" height="180" rx="35" fill="%234978c9"/><rect x="235" y="50" width="30" height="80" rx="15" fill="%234978c9"/><rect x="205" y="300" width="90" height="35" rx="17" fill="%23cccccc"/><rect x="240" y="335" width="20" height="80" rx="10" fill="%23cccccc"/></g></svg>'),
                /* SVG headphones floating */
                url('data:image/svg+xml;utf8,<svg width="400" height="220" xmlns="http://www.w3.org/2000/svg"><g opacity="0.16"><ellipse cx="200" cy="100" rx="140" ry="57" fill="%23b7e4f0"/><rect x="60" y="93" width="32" height="80" rx="16" fill="%23b7dee7"/><rect x="308" y="93" width="32" height="80" rx="16" fill="%23b7dee7"/><rect x="92" y="60" width="216" height="35" rx="17" fill="%2390c4e4"/><ellipse cx="200" cy="160" rx="32" ry="11" fill="%23cdddff"/></g></svg>');
            background-repeat: no-repeat, no-repeat;
            background-position: left -70px top -80px, right -60px bottom -25px;
            background-size: 380px 520px, 320px 180px;
            position: relative;
        }
        body:before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(42,51,73,0.18);
            z-index: 0;
        }
        .overlay-container {
            position: relative;
            z-index: 2;
            min-height: 99vh;
            width: 100vw;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .card-custom {
            background: rgba(255,255,255,0.97);
            box-shadow: 0 8px 40px rgba(0,0,0,0.11);
            border-radius: 22px;
            padding: 2.6rem 2.4rem 2rem 2.3rem;
            max-width: 1220px; width: 97vw;
            margin: 2.5vh auto;
        }
        h1 { font-size: 2.37rem; font-weight: 820; color: #12203a; text-align: center; margin-bottom: 1.07rem; letter-spacing: -2px; }
        .dashboard-link-row {
            display: flex;
            justify-content: center;
            gap: 2vw;
            margin-bottom: 1.31rem;
        }
        .btn-dash {
            background: #5c7fa4;
            border: none;
            color: #f0f4fb;
            font-weight: 640;
            border-radius: 32px;
            box-shadow: 0 2px 14px rgba(60,71,110,0.11);
            padding: 1rem 3vw; font-size: 1.22rem; min-width: 210px; transition: 0.18s;
        }
        .btn-dash:hover { background: #436186; color: #fff; box-shadow: 0 4px 18px #222d3e22; }
        label { font-weight: 600; color: #283045;}
        .form-select, .form-control { border-radius: 15px;}
        .prediction-result {
            margin-top: 1.3rem;
            padding: 1.20rem 1.13rem;
            border-radius: 17px;
            font-weight: 700;
            text-align: center;
            font-size: 1.22rem;
            box-shadow: 0 1px 8px #d3dae0ea;
            color: white;
            animation: popFade 0.7s;
        }
        .high    { background: linear-gradient(89deg,#36d176 82%,#1bac73); }
        .medium  { background: linear-gradient(89deg,#fcb92d 80%,#ee5e17);}
        .low     { background: linear-gradient(89deg,#e84845 80%,#a30000);}
        #prediction-chart-container {margin-top:1.13rem; background: #f8fbfe; border-radius:14px; box-shadow: 0 2px 7px #dde7f8;}
        .chart-title { font-weight:620; margin-bottom:.5rem;}
        @media (max-width:1100px) {.card-custom{padding:1.4rem .3rem;max-width:99vw}}
        @media (max-width:700px) {.dashboard-link-row {flex-direction:column;gap:1rem;}}
        @keyframes popFade {
            0%{opacity:0;transform:scaleY(0.7);}
            90%{opacity:1;transform:scaleY(1);}
        }
    </style>
</head>
<body>
  <div class="overlay-container">
    <div class="card-custom">
        <h1>🎙️ Podcast Engagement Predictor</h1>
        <div class="dashboard-link-row mb-2">
            <a href="/dashboard/1" class="btn btn-dash">View Dashboard 1</a>
            <a href="/dashboard/2" class="btn btn-dash">View Dashboard 2</a>
        </div>
        <form method="POST" action="/">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="Podcast_Name">Podcast Name</label>
              <select class="form-select" name="Podcast_Name" id="Podcast_Name" required>
                <option disabled {% if not request.form.get('Podcast_Name') %}selected{% endif %}>Select Podcast Name</option>
                {% for option in options['Podcast_Name'] %}
                  <option value="{{ option }}" {% if request.form.get('Podcast_Name')==option %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label for="Episode_Title">Episode Title</label>
              <input type="text" class="form-control" name="Episode_Title" id="Episode_Title" value="{{ request.form.get('Episode_Title', '') }}" required />
            </div>
          </div>
          <div class="row">
            <div class="col-md-4 mb-3">
              <label for="Episode_Length_minutes">Episode Length (min)</label>
              <input type="number" step="any" class="form-control" name="Episode_Length_minutes" id="Episode_Length_minutes" value="{{ request.form.get('Episode_Length_minutes', '') }}" required />
            </div>
            <div class="col-md-4 mb-3">
              <label for="Genre">Genre</label>
              <select class="form-select" name="Genre" id="Genre" required>
                <option disabled {% if not request.form.get('Genre') %}selected{% endif %}>Select Genre</option>
                {% for option in options['Genre'] %}
                  <option value="{{ option }}" {% if request.form.get('Genre')==option %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="col-md-4 mb-3">
              <label for="Episode_Sentiment">Sentiment</label>
              <select class="form-select" name="Episode_Sentiment" id="Episode_Sentiment" required>
                <option disabled {% if not request.form.get('Episode_Sentiment') %}selected{% endif %}>Select Sentiment</option>
                {% for option in options['Episode_Sentiment'] %}
                  <option value="{{ option }}" {% if request.form.get('Episode_Sentiment')==option %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
          </div>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="Host_Popularity_percentage">Host Popularity (%)</label>
              <input type="number" step="any" class="form-control" name="Host_Popularity_percentage" id="Host_Popularity_percentage" value="{{ request.form.get('Host_Popularity_percentage', '') }}" required />
            </div>
            <div class="col-md-6 mb-3">
              <label for="Guest_Popularity_percentage">Guest Popularity (%)</label>
              <input type="number" step="any" class="form-control" name="Guest_Popularity_percentage" id="Guest_Popularity_percentage" value="{{ request.form.get('Guest_Popularity_percentage', '') }}" required />
            </div>
          </div>
          <div class="row">
            <div class="col-md-4 mb-3">
              <label for="Publication_Day">Publication Day</label>
              <select class="form-select" name="Publication_Day" id="Publication_Day" required>
                <option disabled {% if not request.form.get('Publication_Day') %}selected{% endif %}>Select Day</option>
                {% for option in options['Publication_Day'] %}
                  <option value="{{ option }}" {% if request.form.get('Publication_Day')==option %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="col-md-4 mb-3">
              <label for="Publication_Time">Publication Time</label>
              <select class="form-select" name="Publication_Time" id="Publication_Time" required>
                <option disabled {% if not request.form.get('Publication_Time') %}selected{% endif %}>Select Time</option>
                {% for option in options['Publication_Time'] %}
                  <option value="{{ option }}" {% if request.form.get('Publication_Time')==option %}selected{% endif %}>{{ option }}</option>
                {% endfor %}
              </select>
            </div>
            <div class="col-md-4 mb-3">
              <label for="Number_of_Ads">Number of Ads</label>
              <input type="number" step="any" class="form-control" name="Number_of_Ads" id="Number_of_Ads" value="{{ request.form.get('Number_of_Ads', '') }}" required />
            </div>
          </div>
          <button type="submit" class="btn btn-success w-100 fw-bold">Predict Listening Time ⏱️</button>
        </form>
        {% if prediction is not none %}
            <div class="prediction-result {% if prediction > 60 %}high{% elif prediction > 30 %}medium{% else %}low{% endif %}">
              Predicted Listening Time: {{ prediction }} minutes
            </div>
            <div id="prediction-chart-container" class="p-3">
                <div class="chart-title">Input Feature Values</div>
                <canvas id="predictionChart"></canvas>
            </div>
            <script>
                const chartLabels = ['Length', 'Host Popularity', 'Guest Popularity', 'Ads'];
                const chartData = [
                    {{ input_data['Episode_Length_minutes'] }},
                    {{ input_data['Host_Popularity_percentage'] }},
                    {{ input_data['Guest_Popularity_percentage'] }},
                    {{ input_data['Number_of_Ads'] }}
                ];
                const barColors = ['#5c7fa4', '#58B09C', '#F29C50', '#ED6A5A'];
                new Chart(document.getElementById('predictionChart').getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: chartLabels,
                        datasets: [{
                            label: 'Input Value',
                            data: chartData,
                            backgroundColor: barColors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: { y: { beginAtZero: true } },
                        responsive: true,
                        plugins: { legend: { display: false } }
                    }
                });
            </script>
        {% endif %}
    </div>
  </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>Podcast Dashboard {{ dash_number }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
    <style>
        html, body { height: 100%; margin:0;padding:0;background:#e8eaf6; }
        .full-dash-container {
            display:flex;align-items:center;justify-content:center;
            height:99vh;width:100vw;
            margin:0; padding:0; box-sizing:border-box;
        }
        .dash-frame {
            background: #fff;
            border-radius:20px;
            box-shadow: 0 4px 40px #bcd1e685;
            padding: 1vw; margin:0;
        }
        h2 {text-align:center;margin:1.2vw 0 1vw 0; font-size:2.15rem;}
        .dashboard-iframe {
            width: 97vw; height: 83vh; min-width:350px; min-height:300px;
            border:0; border-radius:12px; background:#fafafa; max-width:1900px; display:block;
        }
        @media (max-width:600px){
            .dashboard-iframe{width:98vw;height:62vh;}
        }
    </style>
</head>
<body>
    <div class="full-dash-container">
        <div class="dash-frame">
            <h2>Podcast Dashboard {{ dash_number }}</h2>
            <iframe src="{{ dash_url }}?:embed=y&:showVizHome=no&:toolbar=yes"
                class="dashboard-iframe"
                allowfullscreen></iframe>
            <div style="margin-top:28px; text-align:center;"><a href="/" class="btn btn-outline-primary">← Back to Prediction</a></div>
        </div>
    </div>
</body>
</html>
"""


# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    input_data = {
        "Episode_Length_minutes": 0,
        "Host_Popularity_percentage": 0,
        "Guest_Popularity_percentage": 0,
        "Number_of_Ads": 0
    }

    if request.method == "POST":
        load_resources()
        form_input = {field: request.form.get(field) for field in fields}
        numeric_fields = ['Episode_Length_minutes', 'Host_Popularity_percentage',
                          'Guest_Popularity_percentage', 'Number_of_Ads']

        for field in numeric_fields:
            try:
                val = float(form_input[field])
            except (TypeError, ValueError):
                val = 0.0
            form_input[field] = val
            if field in input_data:
                input_data[field] = val

        input_df = pd.DataFrame([form_input])
        input_df = input_df.drop(['Episode_Title'], axis=1)
        input_ohe = pd.get_dummies(input_df)
        input_ohe = input_ohe.reindex(columns=feature_columns, fill_value=0)
        input_scaled = scaler.transform(input_ohe)

        try:
            prediction = model.predict(input_scaled)[0]
            prediction = round(prediction, 2)
        except Exception as e:
            print("Prediction error:", e)
            prediction = None

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            insert_query = """
    			INSERT INTO prediction_results
    			(episode_title, episode_length_minutes, genre, host_popularity_percentage,
     			guest_popularity_percentage, publication_day, publication_time,
     			number_of_ads, episode_sentiment, predicted_listening_time)
    			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		"""
            values = (
    			str(form_input['Episode_Title']),
    			float(form_input['Episode_Length_minutes']),
    			str(form_input['Genre']),
    			float(form_input['Host_Popularity_percentage']),
    			float(form_input['Guest_Popularity_percentage']),
    			str(form_input['Publication_Day']),
    			str(form_input['Publication_Time']),
    			int(form_input['Number_of_Ads']),
    			str(form_input['Episode_Sentiment']),
    			float(prediction) if prediction is not None else None
		)


            cursor.execute(insert_query, values)
            conn.commit()
            print("SAVED SUCCESSFULLY TO THE SQL SERVER")
        except mysql.connector.Error as err:
            print("MySQL Error:", err)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return render_template_string(HTML_TEMPLATE,
                                  fields=fields,
                                  categorical_fields=categorical_fields,
                                  options=options,
                                  prediction=prediction,
                                  input_data=input_data,
                                  request=request)

@app.route("/dashboard/<int:num>")
def dashboard(num):
    dash_url = DASHBOARD1_URL if num == 1 else DASHBOARD2_URL if num == 2 else None
    if dash_url is None:
        return "<h2>Invalid dashboard.</h2>", 404
    return render_template_string(DASHBOARD_TEMPLATE,
                                  dash_number=num,
                                  dash_url=dash_url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

