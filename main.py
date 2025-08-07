import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# --- PDF Generation Imports ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import navy, black

# --- Your Existing Code (with minor adjustments for GUI integration) ---

# Load environment variables from api.env file
load_dotenv("api.env")

# Configure the Generative AI model
try:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    messagebox.showerror("API Configuration Error", f"Failed to configure Google AI: {e}")
    exit()

# Global variable to hold the medical report content
medical_report = ""

def safe_generate(prompt):
    """Safely generates content from the model."""
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "No response generated."
    except Exception as e:
        return f"An error occurred during API call: {e}"

def Cardiologist():
    """Generates a cardiologist's report."""
    if not medical_report:
        return "Medical report is empty. Please select a file first."
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
    """Generates a psychologist's report."""
    if not medical_report:
        return "Medical report is empty. Please select a file first."
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
    """Generates a pulmonologist's report."""
    if not medical_report:
        return "Medical report is empty. Please select a file first."
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
    """Generates a multidisciplinary team summary."""
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


# --- GUI Application Code ---

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Medical Report Analyzer")
        self.root.geometry("1100x800")
        self.root.minsize(800, 600)
        self.root.configure(bg="#eaf4f4")

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", background="#2a9d8f", foreground="white", font=('Helvetica', 10, 'bold'))
        self.style.map("TButton", background=[('active', '#264653')])
        self.style.configure("TNotebook", background="#eaf4f4", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#cedbe0", padding=[10, 5], font=('Helvetica', 10, 'bold'))
        self.style.map("TNotebook.Tab", background=[("selected", "#2a9d8f")], foreground=[("selected", "white")])
        self.style.configure("TEntry", fieldbackground="white", bordercolor="#2a9d8f")

        self._create_widgets()

    def _create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#eaf4f4", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Top frame for patient name
        patient_frame = tk.Frame(main_frame, bg="#eaf4f4")
        patient_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(patient_frame, text="Patient's Name:", font=('Helvetica', 10, 'bold'), bg="#eaf4f4", fg="#264653").pack(side=tk.LEFT, padx=(0, 10))
        self.patient_name_entry = ttk.Entry(patient_frame, font=('Helvetica', 10), width=40)
        self.patient_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Controls frame for buttons
        controls_frame = tk.Frame(main_frame, bg="#eaf4f4")
        controls_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        controls_frame.grid_columnconfigure(1, weight=1)

        self.select_file_btn = ttk.Button(controls_frame, text="Select Medical Report", command=self.select_file)
        self.select_file_btn.grid(row=0, column=0, padx=(0, 10))

        self.file_label = tk.Label(controls_frame, text="No file selected", bg="#eaf4f4", fg="#264653", font=('Helvetica', 9))
        self.file_label.grid(row=0, column=1, sticky="ew", padx=10)

        self.generate_report_btn = ttk.Button(controls_frame, text="Generate Report", command=self.run_analysis_thread)
        self.generate_report_btn.grid(row=0, column=2, padx=(0,10))

        # *** NEW: Export PDF Button ***
        self.export_pdf_btn = ttk.Button(controls_frame, text="Export as PDF", command=self.export_to_pdf, state=tk.DISABLED)
        self.export_pdf_btn.grid(row=0, column=3)


        # PanedWindow to divide file view and report view
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#adb5bd")
        paned_window.grid(row=2, column=0, sticky="nsew")

        # Left frame for file content
        file_view_frame = tk.Frame(paned_window, bg="white", padx=5, pady=5)
        file_view_frame.grid_rowconfigure(1, weight=1)
        file_view_frame.grid_columnconfigure(0, weight=1)
        tk.Label(file_view_frame, text="Medical Report Content", font=('Helvetica', 12, 'bold'), bg="white", fg="#264653").grid(row=0, column=0, sticky="w", pady=(0,5))
        self.file_content_text = tk.Text(file_view_frame, wrap=tk.WORD, font=('Courier New', 10), state=tk.DISABLED, borderwidth=1, relief="solid")
        self.file_content_text.grid(row=1, column=0, sticky="nsew")
        paned_window.add(file_view_frame, width=400)


        # Right frame for reports (Notebook)
        self.notebook = ttk.Notebook(paned_window)
        paned_window.add(self.notebook)

        self.cardio_tab = self._create_tab("Cardiologist")
        self.psych_tab = self._create_tab("Psychologist")
        self.pulmo_tab = self._create_tab("Pulmonologist")
        self.summary_tab = self._create_tab("Final Diagnosis")

        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#e9c46a", fg="#264653")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    def _create_tab(self, title):
        frame = tk.Frame(self.notebook, bg="white", padx=10, pady=10)
        self.notebook.add(frame, text=title)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Helvetica', 11), state=tk.DISABLED, borderwidth=0, bg="white")
        text_widget.grid(row=0, column=0, sticky="nsew")
        return text_widget

    def select_file(self):
        global medical_report
        filepath = filedialog.askopenfilename(
            title="Select a Medical Report File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath: return
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                medical_report = file.read()
            self.file_label.config(text=os.path.basename(filepath))
            self.file_content_text.config(state=tk.NORMAL)
            self.file_content_text.delete(1.0, tk.END)
            self.file_content_text.insert(tk.END, medical_report)
            self.file_content_text.config(state=tk.DISABLED)
            self.status_bar.config(text="File loaded successfully.")
        except Exception as e:
            messagebox.showerror("File Read Error", f"Failed to read file: {e}")
            medical_report = ""
            self.file_label.config(text="No file selected")

    def run_analysis_thread(self):
        if not medical_report:
            messagebox.showwarning("No Report", "Please select a medical report file first.")
            return
        
        self.generate_report_btn.config(state=tk.DISABLED)
        self.export_pdf_btn.config(state=tk.DISABLED) # Disable export button during analysis
        self.status_bar.config(text="Generating reports... Please wait.")
        self._clear_reports()
        
        analysis_thread = threading.Thread(target=self.generate_reports)
        analysis_thread.start()

    def _clear_reports(self):
        """Clears the text in all report tabs."""
        for tab in [self.cardio_tab, self.psych_tab, self.pulmo_tab, self.summary_tab]:
            tab.config(state=tk.NORMAL)
            tab.delete(1.0, tk.END)
            tab.config(state=tk.DISABLED)

    def _update_tab_content(self, tab_widget, content):
        """Updates a specific tab with new content."""
        tab_widget.config(state=tk.NORMAL)
        tab_widget.delete(1.0, tk.END)
        tab_widget.insert(tk.END, content)
        tab_widget.config(state=tk.DISABLED)

    def generate_reports(self):
        cardio_report = Cardiologist()
        self.root.after(0, self._update_tab_content, self.cardio_tab, cardio_report)
        psych_report = Psychologist()
        self.root.after(0, self._update_tab_content, self.psych_tab, psych_report)
        pulmo_report = Pulmonologist()
        self.root.after(0, self._update_tab_content, self.pulmo_tab, pulmo_report)
        summary_report = MultidisciplinaryTeam(cardio_report, psych_report, pulmo_report)
        self.root.after(0, self._update_tab_content, self.summary_tab, summary_report)
        self.root.after(0, self.finalize_analysis)

    def finalize_analysis(self):
        self.generate_report_btn.config(state=tk.NORMAL)
        self.export_pdf_btn.config(state=tk.NORMAL) # Enable export button
        self.status_bar.config(text="Reports generated successfully.")
        messagebox.showinfo("Success", "All reports have been generated. You can now export to PDF.")

    def export_to_pdf(self):
        patient_name = self.patient_name_entry.get().strip()
        if not patient_name:
            messagebox.showwarning("Input Required", "Please enter the patient's name before exporting.")
            return

        summary_report = self.summary_tab.get("1.0", tk.END).strip()
        if not summary_report or summary_report == "No response generated.":
            messagebox.showwarning("No Report", "Please generate a report before exporting.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report As",
            initialfile=f"Medical_Report_{patient_name.replace(' ', '_')}.pdf"
        )
        if not filepath:
            return

        try:
            self.status_bar.config(text=f"Exporting PDF to {os.path.basename(filepath)}...")
            doc = SimpleDocTemplate(filepath,
                                    rightMargin=inch, leftMargin=inch,
                                    topMargin=inch, bottomMargin=inch)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom Styles
            styles.add(ParagraphStyle(name='TitleStyle', fontName='Helvetica-Bold', fontSize=18, alignment=TA_CENTER, spaceAfter=20, textColor=navy))
            styles.add(ParagraphStyle(name='PatientStyle', fontName='Helvetica', fontSize=12, alignment=TA_CENTER, spaceAfter=10))
            styles.add(ParagraphStyle(name='DateStyle', fontName='Helvetica-Oblique', fontSize=10, alignment=TA_CENTER, spaceAfter=20))
            styles.add(ParagraphStyle(name='HeadingStyle', fontName='Helvetica-Bold', fontSize=14, spaceBefore=12, spaceAfter=6, textColor=navy))
            styles.add(ParagraphStyle(name='BodyStyle', fontName='Helvetica', fontSize=11, alignment=TA_JUSTIFY, leading=14))

            # --- Build the PDF Document ---
            story.append(Paragraph("AI-Generated Medical Analysis", styles['TitleStyle']))
            story.append(Paragraph(f"Patient: {patient_name}", styles['PatientStyle']))
            story.append(Paragraph(f"Report Date: {datetime.datetime.now().strftime('%B %d, %Y, %I:%M %p')}", styles['DateStyle']))
            
            report_data = {
                "Final Diagnosis": self.summary_tab.get("1.0", tk.END),
                "Cardiologist Report": self.cardio_tab.get("1.0", tk.END),
                "Psychologist Report": self.psych_tab.get("1.0", tk.END),
                "Pulmonologist Report": self.pulmo_tab.get("1.0", tk.END),
            }

            for title, content in report_data.items():
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(title, styles['HeadingStyle']))
                # Replace newlines with <br/> tags for proper line breaks in the PDF
                formatted_content = content.strip().replace('\n', '<br/>')
                story.append(Paragraph(formatted_content, styles['BodyStyle']))
                if title != "Pulmonologist Report": # Don't add a page break after the last report
                    story.append(PageBreak())

            doc.build(story)
            self.status_bar.config(text="PDF exported successfully.")
            messagebox.showinfo("Success", f"Report successfully exported to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("PDF Export Error", f"An error occurred while exporting the PDF: {e}")
            self.status_bar.config(text="PDF export failed.")


if __name__ == "__main__":
    app_root = tk.Tk()
    app = MedicalApp(app_root)
    app_root.mainloop()
