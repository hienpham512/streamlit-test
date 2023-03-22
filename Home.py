import streamlit as st
import os

st.set_page_config(
    page_title="GoCanopy"
)

import pandas as pd
import streamlit as st

st.write("# Welcome to GoCanopy! 👋")

filename = "original.xlsx"

if not os.path.isfile(filename):
    uploaded_file = st.file_uploader("Upload your xlsx file to start!")
    
    if uploaded_file is None:
        st.warning("Please upload a file to get started.")
    else:
        df = pd.read_excel(uploaded_file)
        #save the original file to local
        df.to_excel('original.xlsx', index=False)
        with open('file_uploaded_name.txt', 'w') as f:
            f.write(uploaded_file.name)
        st.success("File uploaded successfully!")
else:
    st.success("File uploaded successfully!")
    st.write("File name: ", open('file_uploaded_name.txt', 'r').read())
    uploaded_file = st.file_uploader("Want to upload new xlsx file?")
    if uploaded_file is not None:
        #save the original file to local
        with open('file_uploaded_name.txt', 'w') as f:
            f.write(uploaded_file.name)
        st.success("File uploaded successfully!")
