# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
from geopy.distance import geodesic
import folium
import os

app = Flask(__name__)

# Load your dataset
merged_df = pd.read_csv('merged_df.csv')  # Make sure this file is in the same folder

# Classify risk level
def classify_risk(rate):
    if rate > 7:
        return "High"
    elif rate > 3:
        return "Medium"
    else:
        return "Low"

# Add RISK_LEVEL if not already present
if 'RISK_LEVEL' not in merged_df.columns:
    merged_df['RISK_LEVEL'] = merged_df['RISK_RATE'].apply(classify_risk)

# Generate the map and save it
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

for _, row in merged_df.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        popup_info = f"""
        <b>District:</b> {row['DISTRICT'].title()}<br>
        <b>State:</b> {row['STATE/UT'].title()}<br>
        <b>Total Rape:</b> {row['TOTAL_RAPE']}<br>
        <b>Risk Rate:</b> {round(row['RISK_RATE'], 2)}<br>
        <b>Risk Level:</b> {row['RISK_LEVEL']}
        """
        color = 'red' if row['RISK_LEVEL'] == 'High' else 'orange' if row['RISK_LEVEL'] == 'Medium' else 'green'

        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            popup=folium.Popup(popup_info, max_width=300),
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

# Save map
os.makedirs("static", exist_ok=True)
m.save("static/district_risk_map.html")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_risk_by_location', methods=['POST'])
def get_risk_by_location():
    try:
        data = request.get_json()
        user_lat = data.get('lat')
        user_lon = data.get('lon')

        valid_df = merged_df.dropna(subset=['Latitude', 'Longitude'])

        def calc_distance(row):
            return geodesic((user_lat, user_lon), (row['Latitude'], row['Longitude'])).km

        valid_df['distance'] = valid_df.apply(calc_distance, axis=1)
        nearest = valid_df.loc[valid_df['distance'].idxmin()]

        return jsonify({
            "district": nearest['DISTRICT'].title(),
            "risk_rate": round(nearest['RISK_RATE'], 2),
            "risk_level": nearest['RISK_LEVEL'],
            "total_rape": int(nearest['TOTAL_RAPE'])
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
