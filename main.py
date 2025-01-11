import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('secrets.env')

# Extract fields and placeholders from the uploaded PDF
def extract_template_fields(pdf_file):
    from PyPDF2 import PdfReader

    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Clean up the text
    # Replace multiple newlines or spaces with a single space
    text = ' '.join(text.split())
    # Add a new line after each colon
    text = text.replace(": ", ":\n")  # Handle spaces after colons
    text = text.replace(":", ":\n")  # Handle colons without spaces
    return text




def main():
    # Page configuration
    st.set_page_config(page_title="Custom Lesson Plan Creator", layout="wide")
    st.title("📝 Custom Lesson Plan Creator")

    # Upload Lesson Plan Template
    template_pdf = st.file_uploader("Upload your lesson plan template (PDF)", type=["pdf"])
    if template_pdf:
        st.success("Template uploaded successfully!")
        template_text = extract_template_fields(template_pdf)
        with st.expander("View Template"):
            st.text_area("Template Preview", template_text, height=300)

        # Section Mapping (manually define the coordinates for each section)
        section_mapping = {
            "Essential Standards": (100, 700),
            "Activities": (100, 650),
            "Objectives": (100, 600),
            "Differentiation": (100, 550),
            "Assessment": (100, 500),
        }
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Lesson Date")
            class_name = st.text_input("Class Name")
            unit_num = st.number_input("Unit #")
            unit_name = st.text_input("Unit Name")
            standard = st.text_input("Lesson Standard")
        with col2:
            class_period = st.selectbox("Class Period", options=['8A', '8B', '7A', '7B', '6A', '6B', 'All'])
            instructor = st.text_input("Instructor")
            lesson_num = st.number_input("Lesson #")
            lesson_name = st.text_input("Lesson Name")
            objective = st.text_input("Lesson Objective")

        # Customization Questions
        lesson_description = st.text_area(
            "Provide customization details for the lesson plan:",
            "Example: Describe the objectives, activities, differentiation techniques, etc.",
            height=150,
        )

        # Button to generate lesson plan
        if st.button("Generate Lesson Plan"):
            with st.spinner("Generating lesson plan..."):
                # Define prompt
                prompt_template = f"""
                Use the following template to create a custom lesson plan:
                TEMPLATE:
                {template_text}

                Customize it based on the following instructions:
                Lesson Date: {date}
                Class Period: {class_period}
                Class Name: {class_name}
                Instructor: {instructor}
                Unit Number: {unit_num}
                Unit Name: {unit_name}
                Lesson Number: {lesson_num}
                Lesson Name: {lesson_name}
                Lesson Standard: {standard}
                Lesson Objective: {objective}
                Lesson Description: {lesson_description}

                Ensure the lesson plan includes all of the sections in the {template_text}
                """
                prompt = PromptTemplate(template=prompt_template)

                # Set up LLM
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    st.error("API key is missing. Please add it to the 'secrets.env' file.")
                    return

                llm = OpenAI(temperature=0.7, api_key=api_key, max_tokens=2000)
                chain = LLMChain(prompt=prompt, llm=llm)

                # Run chain
                response = chain.run({})

                # Display generated content
                st.success("Lesson plan generated successfully!")
                st.text_area("Generated Lesson Plan", response, height=500)

if __name__ == "__main__":
    main()
