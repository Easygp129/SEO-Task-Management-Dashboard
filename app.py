import streamlit as st
import pandas as pd
from fpdf import FPDF
from PyPDF2 import PdfReader
from PIL import Image

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = {menu: [] for menu in [
        "1. Website Design, UI/UX, and Structure",
        "2. Technical SEO",
        "3. On-Page SEO",
        "4. Local SEO",
        "5. Off-Page SEO",
        "6. SEO KPIs",
    ]}

# Function to create a PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Task Management Report', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

    def add_image(self, image_path):
        self.image(image_path, x=10, y=None, w=100)

# Sidebar for menu navigation
st.sidebar.title("User Details")
username = st.sidebar.text_input("Enter your name:")
menu_options = {
    "1. Website Design, UI/UX, and Structure": [
        "Is the website design optimized for user experience?",
        "Are navigation menus, CTAs, and forms effective?",
        "Does the website meet Core Web Vitals standards (LCP, FID, CLS)?",
        "Has the mobile-first design been ensured?",
        "Have A/B tests and heatmaps been analyzed for improvements?",
    ],
    "2. Technical SEO": [
        "Is the website crawlable by search engines?",
        "Are XML sitemaps and robots.txt configured correctly?",
        "Does the site have proper canonical tags?",
        "Are there any 404 or broken links?",
        "Is structured data implemented correctly?",
    ],
    "3. On-Page SEO": [
        "Are title tags optimized with keywords?",
        "Do meta descriptions include target keywords?",
        "Is there proper keyword usage in headings and content?",
        "Are internal links implemented effectively?",
        "Are images optimized with alt text?",
    ],
    "4. Local SEO": [
        "Is the business listed on Google My Business?",
        "Are citations and directory listings consistent?",
        "Are reviews being managed and responded to?",
        "Is local content optimized for location-based keywords?",
        "Are there any local backlinks?",
    ],
    "5. Off-Page SEO": [
        "Are backlinks from authoritative websites?",
        "Are backlinks from diverse sources?",
        "Are social signals being leveraged for SEO?",
        "Is the brand reputation being monitored online?",
        "Are there any guest posting opportunities?",
    ],
    "6. SEO KPIs": [
        "Is organic traffic increasing?",
        "Are keyword rankings improving?",
        "Is the bounce rate decreasing?",
        "Are conversion rates improving?",
        "Are backlinks and domain authority increasing?",
    ],
}

selected_menu = st.sidebar.selectbox("Menu", list(menu_options.keys()))

# Function to render questions for each menu
def render_questions(questions):
    responses = {}
    for question in questions:
        responses[question] = st.radio(question, ["Working", "Pending", "Completed"], horizontal=True)
    return responses

# Convert responses dictionary to readable string
def format_responses(responses):
    return "\n".join([f"{q}: {r}" for q, r in responses.items()])

# Task input form based on the selected menu
st.title("Agency Dashboard")
st.subheader(f"{selected_menu}")

if selected_menu in menu_options:
    st.write(f"Answer the following questions about {selected_menu.split('. ')[1]}:")
    responses = render_questions(menu_options[selected_menu])

# Common input fields for all menus
# st.markdown('<span style="color: red;">Upload Evidence (optional): Images are not required</span>', unsafe_allow_html=True)
evidence = st.file_uploader("Upload Evidence (optional):", type=["pdf", "xlsx", "jpg", "jpeg", "png"])
notes = st.text_area("Notes/Updates:", placeholder="Add any relevant updates or notes here.")
quick_links = st.text_input("Quick Links:", placeholder="Add a link related to the task (optional)")
task_name = st.text_input("Task Name:")

# Process and display uploaded file
def process_evidence(file):
    if file is not None:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()
            return f"Extracted PDF Content:\n{pdf_text}", None
        elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            excel_data = pd.read_excel(file)
            return f"Extracted Excel Content:\n{excel_data.to_string(index=False)}", None
        elif file.type in ["image/jpeg", "image/png"]:
            image = Image.open(file)
            temp_path = f"temp_image.{file.type.split('/')[-1]}"
            image.save(temp_path)
            return "Uploaded an image.", temp_path
        else:
            return "Unsupported file type.", None
    return "No evidence uploaded.", None

if st.button("Add Task"):
    if task_name and username:
        evidence_details, image_path = process_evidence(evidence)
        formatted_responses = format_responses(responses)  # Format responses for readability
        task = {
            "Name": username,
            "Task": task_name,
            "Responses": formatted_responses,  # Save formatted responses
            "Evidence": evidence_details,
            "Image Path": image_path,
            "Notes": notes,
            "Quick Links": quick_links,
        }
        st.session_state.tasks[selected_menu].append(task)
        st.success("Task added successfully!")
    else:
        st.error("Please enter your name and task name.")

if st.session_state.tasks[selected_menu]:
    st.subheader(f"Task Overview for {selected_menu}")
    tasks_df = pd.DataFrame(st.session_state.tasks[selected_menu])
    st.table(tasks_df)

    if st.button("Download PDF Report"):
        pdf = PDF()
        pdf.add_page()
        pdf.chapter_title(f"Task Report for {username} - {selected_menu}")
        for task in st.session_state.tasks[selected_menu]:
            pdf.chapter_body(f"Task Name: {task['Task']}")
            for key, value in task.items():
                if key == "Image Path" and value:
                    pdf.add_image(value)
                elif key != "Image Path":
                    pdf.chapter_body(f"{key}: {value}")
            pdf.ln()

        try:
            # Generate PDF as a byte string
            pdf_data = pdf.output(dest='S').encode('latin-1')

            # Use the byte string in Streamlit's download button
            st.download_button(
                label="Download Report",
                data=pdf_data,
                file_name=f"Task_Report_{selected_menu.split('.')[0]}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")
