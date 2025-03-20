from flask import Flask, request, render_template, jsonify  # Import jsonify
import numpy as np
import pandas as pd
import pickle
import bcrypt
import sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, url_for, session


# flask app
app = Flask(__name__)
app.secret_key = "sam123"


# Create users table if it doesn't exist
def create_users_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    # print("Table 'users' created successfully.")

# Call this function when the app starts
create_users_table()


# Create search_history table if it doesn't exist
def create_search_history_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    searched_symptoms TEXT,
                    predicted_disease TEXT,
                    description TEXT,
                    precautions TEXT,
                    medications TEXT,
                    recommended_workouts TEXT,
                    recommended_diet TEXT,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()
    # print("Table 'users history' created successfully.")


# Call table creation functions
create_search_history_table()


def create_contact_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
print("Table  created successfully.")

# Call this function when the app starts
create_contact_table()



# ----------------------------------------------
# SIGNUP (REGISTER) ROUTE
# ----------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # print(f"✅ Route accessed! Method: {request.method}")

    if request.method == "POST":
        print("✅ POST request received!")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # print(f"🔹 Received: {username}, {email}, {password}")

        if not username or not email or not password:
            print("❌ Missing fields!")
            flash("All fields are required!", "danger")
            return render_template("signup.html")

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        # print(f"🔐 Hashed password: {hashed_password}")  # Debugging

        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            # print("✅ Connected to database")  # Debugging

            # Ensure the 'users' table exists before inserting
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            table_exists = c.fetchone()
            if not table_exists:
                # print("❌ Table 'users' does NOT exist!")
                flash("Database error: Table does not exist!", "danger")
                return render_template("signup.html")

            # Insert user data
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                      (username, email, hashed_password))
            conn.commit()
            # print("✅ Data inserted successfully!")  # Debugging

            conn.close()
            flash("Account created! You can now log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            print("❌ Integrity Error: Email already exists!")  # Debugging
            flash("Email already exists. Try a different one.", "danger")
        except sqlite3.OperationalError as e:
            # print(f"❌ Database Error: {e}")  # Debugging
            flash("Database error! Please contact support.", "danger")

    return render_template("signup.html")



# ----------------------------------------------
# LOGIN ROUTE
# ----------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user[3]):  # ✅ Fixed line
            session["user_id"] = user[0]  # Store user ID
            session["username"] = user[1]  # Store username
            return redirect(url_for("home"))

    return render_template("login.html")

# ----------------------------------------------
# DASHBOARD (PROTECTED ROUTE)
# ----------------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for("login"))
    
    return render_template("dashboard.html", username=session["username"])

# ----------------------------------------------
# LOGOUT ROUTE
# ----------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# load databasedataset===================================
sym_des = pd.read_csv("datasets/symtoms_df.csv")
precautions = pd.read_csv("datasets/precautions_df.csv")
workout = pd.read_csv("datasets/workout_df.csv")
description = pd.read_csv("datasets/description.csv")
medications = pd.read_csv('datasets/medications.csv')
diets = pd.read_csv("datasets/diets.csv")


# load model===========================================
svc = pickle.load(open('models/svc.pkl','rb'))


#============================================================
# custome and helping functions
#==========================helper funtions================
def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]

    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]

    wrkout = workout[workout['disease'] == dis] ['workout']


    return desc,pre,med,die,wrkout

symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

# Model Prediction function
def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))
    for item in patient_symptoms:
        input_vector[symptoms_dict[item]] = 1
    return diseases_list[svc.predict([input_vector])[0]]




# creating routes========================================


@app.route("/")
def index():
    return render_template("index.html")


# Define a route for the home page
@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if "user_id" not in session:
            flash("You need to log in first.", "warning")
            return redirect(url_for("login"))

        user_id = session["user_id"]
        symptoms = request.form.get('symptoms')

        print(symptoms)  # Debugging

        if symptoms == "Symptoms" or not symptoms.strip():
            message = "Please either write symptoms or you have written misspelled symptoms"
            return render_template('index.html', message=message)

        # Process symptoms
        user_symptoms = [s.strip("[]' ") for s in symptoms.split(',')]

        try:
            predicted_disease = get_predicted_value(user_symptoms)  # Your ML model function
            dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)  # Fetch details

            # Convert lists to strings for storage
            symptoms_text = ", ".join(user_symptoms)
            precautions_text = ", ".join(precautions[0])
            medications_text = ", ".join(medications[0])
            diet_text = ", ".join(rec_diet[0])
            workout_text = ", ".join(workout.tolist())

            # Save search history to the database
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute('''INSERT INTO search_history 
                        (user_id, searched_symptoms, predicted_disease, description, precautions, medications, recommended_workouts, recommended_diet, search_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (user_id, symptoms_text, predicted_disease, dis_des, precautions_text, medications_text, workout_text, diet_text, datetime.now()))
            conn.commit()
            conn.close()

            return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                                   my_precautions=precautions[0], medications=medications,
                                   my_diet=rec_diet, workout=workout)

        except KeyError as e:
            message = f"Invalid symptom: {str(e)}. Please check your input."
            return render_template('index.html', message=message)

    return render_template('index.html')


@app.route("/history")
def history():
    if "user_id" not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''SELECT searched_symptoms, predicted_disease, description, precautions, medications, recommended_workouts, recommended_diet, search_date 
                 FROM search_history 
                 WHERE user_id = ? 
                 ORDER BY search_date DESC''', (user_id,))
    history_data = c.fetchall()
    conn.close()

    return render_template("history.html", history=history_data)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not logged in"})

    user_id = session["user_id"]

    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    





# about view funtion and path
@app.route('/about')
def about():
    return render_template("about.html")

# contact view funtion and path
@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route("/contact-submit", methods=["POST"])
def contact_submit():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    subject = request.form.get("subject")
    message = request.form.get("message")

    if not name or not email or not subject or not message:
        return jsonify({"status": "error", "message": "All fields are required!"})

    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO contact_messages (name, email, phone, subject, message) VALUES (?, ?, ?, ?, ?)", 
                  (name, email, phone, subject, message))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Message sent successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/view-messages")
def view_messages():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM contact_messages ORDER BY submitted_at DESC")
    messages = c.fetchall()
    conn.close()
    return render_template("messages.html", messages=messages)


@app.route("/delete_history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    user_id = session["user_id"]
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("DELETE FROM search_history WHERE id = ? AND user_id = ?", (history_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# developer view funtion and path
@app.route('/developer')
def developer():
    return render_template("developer.html")

# about view funtion and path
@app.route('/blog')
def blog():
    return render_template("blog.html")


if __name__ == '__main__':

    app.run(debug=True)