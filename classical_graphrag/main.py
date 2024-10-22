import streamlit as st  
import asyncio  
from pdf_to_txt import extract_text_from_image_pdf  
from index import run_indexing  
from query import query  
  
def main():  
    st.title("PDF to Text Converter and Indexer")  
  
    # File uploader  
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")  
  
    if uploaded_file is not None:  
        # Convert PDF to text  
        output = "input/text_file.txt"  
        text = extract_text_from_image_pdf(uploaded_file, output)  
  
        # Index the text  
        run_indexing()  
  
        # Generate output (await the coroutine)  
        output = asyncio.run(query())  
  
        # Display the results  
        # st.subheader("Extracted Text")  
        # st.text_area("Text", text, height=200)  
  
        st.subheader("Generated Output")  
        st.write(output)  
  
if __name__ == "__main__":  
    main()  
