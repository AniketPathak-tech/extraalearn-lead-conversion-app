# Import necessary libraries
import requests
import streamlit as st

# URL of the deployed Flask backend (paste your backend's public URL here,
# or set it as the BACKEND_URL environment variable when running the app)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:7860").rstrip("/")

# Set the title of the Streamlit app
st.title("ExtraaLearn Lead Conversion Predictor")

# ------------------------------------------------------------------
# Section for online (single lead) prediction
# ------------------------------------------------------------------
st.subheader("Online Prediction")

# Collect the lead's details from the user
age = st.number_input("Age", min_value=18, max_value=80, value=45, step=1)
current_occupation = st.selectbox("Current Occupation", ["Professional", "Unemployed", "Student"])
first_interaction = st.selectbox("First Interaction", ["Website", "Mobile App"])
profile_completed = st.selectbox("Profile Completed", ["High", "Medium", "Low"])
website_visits = st.number_input("Website Visits", min_value=0, max_value=100, value=3, step=1)
time_spent_on_website = st.number_input("Time Spent on Website (seconds)", min_value=0, max_value=10000, value=600, step=10)
page_views_per_visit = st.number_input("Page Views per Visit", min_value=0.0, max_value=50.0, value=3.0, step=0.1)
last_activity = st.selectbox("Last Activity", ["Email Activity", "Phone Activity", "Website Activity"])
print_media_type1 = st.selectbox("Saw the Newspaper Ad", ["No", "Yes"])
print_media_type2 = st.selectbox("Saw the Magazine Ad", ["No", "Yes"])
digital_media = st.selectbox("Saw the Digital Media Ad", ["No", "Yes"])
educational_channels = st.selectbox("Heard through Educational Channels", ["No", "Yes"])
referral = st.selectbox("Came through a Referral", ["No", "Yes"])

# Convert the user input into a dictionary (the keys must match the backend's feature names)
lead_data = {
    "age": age,
    "current_occupation": current_occupation,
    "first_interaction": first_interaction,
    "profile_completed": profile_completed,
    "website_visits": website_visits,
    "time_spent_on_website": time_spent_on_website,
    "page_views_per_visit": page_views_per_visit,
    "last_activity": last_activity,
    "print_media_type1": print_media_type1,
    "print_media_type2": print_media_type2,
    "digital_media": digital_media,
    "educational_channels": educational_channels,
    "referral": referral,
}

# Make a prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    # Send the lead's data to the Flask backend as JSON
    response = requests.post(f"{BACKEND_URL}/v1/lead", json=lead_data)

    if response.status_code == 200:
        # Read the prediction and the conversion probability from the JSON response
        result = response.json()
        st.write(f"Prediction: **{result['prediction']}**")
        st.write(f"Conversion probability: **{result['conversion_probability']:.1%}**")
        if result["predicted_class"] == 1:
            st.success("This lead is likely to convert. Prioritise it for sales follow-up.")
        else:
            st.info("This lead is less likely to convert. Keep it in the standard nurture flow.")
    else:
        st.error(f"Error making prediction: {response.text}")

# ------------------------------------------------------------------
# Section for batch prediction
# ------------------------------------------------------------------
st.subheader("Batch Prediction")

# Let the user upload a CSV file with the 13 feature columns (and optionally an ID column)
uploaded_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

# Make batch predictions when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        # Send the uploaded file to the Flask backend
        response = requests.post(
            f"{BACKEND_URL}/v1/leadbatch",
            files={"file": ("leads.csv", uploaded_file.getvalue(), "text/csv")},
        )

        if response.status_code == 200:
            # Show the predictions as a table
            predictions = pd.DataFrame(response.json())
            st.success(f"Predictions generated for {len(predictions)} leads.")
            st.dataframe(predictions)
        else:
            st.error(f"Error making batch prediction: {response.text}")
