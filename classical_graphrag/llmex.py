# Simple table extraction using llmshera and Streamlit 
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from llmsherpa.readers import LayoutPDFReader

llmsherpa_api_url = "http://127.0.0.1:5010/api/parseDocument?renderFormat=all"

pdf_url = "https://abc.xyz/assets/91/b3/3f9213d14ce3ae27e1038e01a0e0/2024q1-alphabet-earnings-release-pdf.pdf"
pdf_reader = LayoutPDFReader(llmsherpa_api_url)

st.title('Table extraction using llmsherpa')


uploaded_file = st.file_uploader("Choose a file")
st.markdown("""---""")

#########################

# Sample data (replace with your actual data)
df_list = []


if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    with open('store.pdf', 'wb') as pdf_file:
        pdf_file.write(bytes_data)
    doc = pdf_reader.read_pdf('./store.pdf')
    # html_string = doc.tables()[5].to_html()
    data_list = [_table.to_html() for _table in doc.tables()]

    for html_string in data_list:
        soup = BeautifulSoup(html_string, 'html.parser')
        table = soup.find('table')

        # Extract table data into rows and columns
        if table:
            table_data = []
            for row in table.find_all('tr'):
                cells = [cell.text.strip() for cell in row.find_all(['th', 'td'])]
                table_data.append(cells)

            # Create pandas DataFrame (handle potential column name issues)
            df = pd.DataFrame(table_data[1:])
            df = df.fillna("None", inplace=False)
        df_list.append(df)

        # st.table(df)
    else:
        print(f"Tables are not found...")

    if "current_index" not in st.session_state:
        st.session_state["current_index"] = 0

    # Display current data item
    st.write(f"Extracted Table:")
    st.table(df_list[st.session_state["current_index"]])

    col1, col2 = st.columns(2)

    if col1.button("Previous"):
        if st.session_state["current_index"] > 0:
            st.session_state["current_index"] -= 1

    if col2.button("Next"):
        if st.session_state["current_index"] < len(df_list) - 1:
            st.session_state["current_index"] += 1