# Import necessary libraries

from flask import Flask, request, jsonify

# Initialise the Flask application
lead_conversion_predictor_api = Flask("ExtraaLearn Lead Conversion Predictor")

# Load the serialized pipeline (preprocessing + classifier) once, when the server starts
model = joblib.load("extraalearn_model_v1_0.joblib")

# Names of the numerical features the model expects
NUMERIC_FIELDS = ["age", "website_visits", "time_spent_on_website", "page_views_per_visit"]

# Names of the categorical features and the values the model was trained on
CATEGORICAL_FIELDS = {
    "current_occupation": ["Professional", "Unemployed", "Student"],
    "first_interaction": ["Website", "Mobile App"],
    "profile_completed": ["Low", "Medium", "High"],
    "last_activity": ["Email Activity", "Phone Activity", "Website Activity"],
    "print_media_type1": ["Yes", "No"],
    "print_media_type2": ["Yes", "No"],
    "digital_media": ["Yes", "No"],
    "educational_channels": ["Yes", "No"],
    "referral": ["Yes", "No"],
}

# All 13 input features, and the labels for the predicted class
FEATURES = NUMERIC_FIELDS + list(CATEGORICAL_FIELDS)
LABELS = {0: "Not Converted", 1: "Converted"}


# Define the route for the home page
@lead_conversion_predictor_api.get("/")
def home():
    return "Welcome to the ExtraaLearn Lead Conversion Prediction API"


# Define the endpoint to predict the conversion of a single lead
@lead_conversion_predictor_api.post("/v1/lead")
def predict_lead():
    # Get the JSON data from the request
    lead_data = request.get_json()

    # Check that every required feature was sent
    missing = [f for f in FEATURES if f not in lead_data]
    if missing:
        return jsonify({"error": "Missing fields: " + ", ".join(missing)}), 400

    # Check that every categorical feature has a value the model knows
    for field, allowed in CATEGORICAL_FIELDS.items():
        if lead_data[field] not in allowed:
            return jsonify({"error": f"'{field}' must be one of {allowed}."}), 400

    # Extract the relevant information from the lead data
    sample = {
        "age": lead_data["age"],
        "current_occupation": lead_data["current_occupation"],
        "first_interaction": lead_data["first_interaction"],
        "profile_completed": lead_data["profile_completed"],
        "website_visits": lead_data["website_visits"],
        "time_spent_on_website": lead_data["time_spent_on_website"],
        "page_views_per_visit": lead_data["page_views_per_visit"],
        "last_activity": lead_data["last_activity"],
        "print_media_type1": lead_data["print_media_type1"],
        "print_media_type2": lead_data["print_media_type2"],
        "digital_media": lead_data["digital_media"],
        "educational_channels": lead_data["educational_channels"],
        "referral": lead_data["referral"],
    }

    # Convert the extracted data into a DataFrame (the pipeline does the encoding itself)
    input_data = pd.DataFrame([sample])

    # Predict the class (0 / 1) and the probability of conversion
    prediction = int(model.predict(input_data)[0])
    probability = float(model.predict_proba(input_data)[0][1])

    # Return the prediction as a JSON response
    return jsonify({
        "predicted_class": prediction,
        "prediction": LABELS[prediction],
        "conversion_probability": round(probability, 4),
    })


# Define the endpoint to predict the conversion of a batch of leads from a CSV file
@lead_conversion_predictor_api.post("/v1/leadbatch")
def predict_lead_batch():
    # Get the uploaded CSV file from the request
    file = request.files["file"]

    # Read the file into a DataFrame
    input_data = pd.read_csv(file)

    # Check that all the feature columns are present
    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": "Missing columns: " + ", ".join(missing)}), 400

    # Predict the class and the probability for every lead
    features = input_data[FEATURES]
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]

    # Use the ID column to label the results if the file has one
    ids = input_data["ID"].tolist() if "ID" in input_data.columns else list(range(len(input_data)))

    # Build the JSON response
    results = [
        {
            "ID": ids[i],
            "prediction": LABELS[int(predictions[i])],
            "conversion_probability": round(float(probabilities[i]), 4),
        }
        for i in range(len(input_data))
    ]
    return jsonify(results)


# Run the Flask app (the Dockerfile starts it with gunicorn instead)
if __name__ == "__main__":
    lead_conversion_predictor_api.run(host="0.0.0.0", port=7860, debug=False)
