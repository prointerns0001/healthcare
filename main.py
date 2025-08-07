from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv("api.env")

genai.configure(api_key=os.getenv("API_KEY"))

with open(r"Medical Reports\billu.txt", "r") as file:
    medical_report = file.read()

model = genai.GenerativeModel("gemini-1.5-flash")

def safe_generate(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "No response generated."
    except Exception as e:
        return f"Error: {e}"

def Cardiologist():
    prompt = f"""
    Act like a cardiologist. You will receive a medical report of a patient.
                    Task: Review the patient's cardiac workup, including ECG, blood tests, Holter monitor results, and echocardiogram.
                    Focus: Determine if there are any subtle signs of cardiac issues that could explain the patient’s symptoms. Rule out any underlying heart conditions, such as arrhythmias or structural abnormalities, that might be missed on routine testing.
                    Recommendation: Provide guidance on any further cardiac testing or monitoring needed to ensure there are no hidden heart-related concerns. Suggest potential management strategies if a cardiac issue is identified.
                    Please only return the possible causes of the patient's symptoms and the recommended next steps.
                    Medical Report: {medical_report}
    """
    return safe_generate(prompt)

def Psychologist():
    prompt = f"""
    Act like a psychologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a psychological assessment.
                    Focus: Identify any potential mental health issues, such as anxiety, depression, or trauma, that may be affecting the patient's well-being.
                    Recommendation: Offer guidance on how to address these mental health concerns, including therapy, counseling, or other interventions.
                    Please only return the possible mental health issues and the recommended next steps.
                    Patient's Report: {medical_report}
    """
    return safe_generate(prompt)

def Pulmonologist():
    prompt = f"""
    Act like a pulmonologist. You will receive a patient's report.
                    Task: Review the patient's report and provide a pulmonary assessment.
                    Focus: Identify any potential respiratory issues, such as asthma, COPD, or lung infections, that may be affecting the patient's breathing.
                    Recommendation: Offer guidance on how to address these respiratory concerns, including pulmonary function tests, imaging studies, or other interventions.
                    Please only return the possible respiratory issues and the recommended next steps.
                    Patient's Report: {medical_report}
    """
    return safe_generate(prompt)

def MultidisciplinaryTeam(cardiology, psychology, pulmonology):
    prompt = f"""
     Act like a multidisciplinary team of healthcare professionals.
                You will receive a medical report of a patient visited by a Cardiologist, Psychologist, and Pulmonologist.
                Task: Review the patient's medical report from the Cardiologist, Psychologist, and Pulmonologist, analyze them and come up with a list of 3 possible health issues of the patient.
                Just return a list of bullet points of 3 possible health issues of the patient and for each issue provide the reason.
    - Cardiologist Report: {cardiology}
    - Psychologist Report: {psychology}
    - Pulmonologist Report: {pulmonology}
    """
    return safe_generate(prompt)

cardio_report = Cardiologist()
psych_report = Psychologist()
pulmo_report = Pulmonologist()

with open("final_diagnosis.txt", "w", encoding="utf-8") as f:
    f.write("--- Cardiologist Report ---\n")
    f.write(cardio_report + "\n\n")
    
    f.write("--- Psychologist Report ---\n")
    f.write(psych_report + "\n\n")
    
    f.write("--- Pulmonologist Report ---\n")
    f.write(pulmo_report + "\n\n")
    
    f.write("--- Multidisciplinary Team Summary ---\n")
    f.write(MultidisciplinaryTeam(cardio_report, psych_report, pulmo_report))
