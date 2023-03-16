import streamlit as st
import pandas as pd

# define your HTML/CSS/JS code for the UI
html = """
<div>
  <h1>Hello, Streamlit!</h1>
  <p>This is my custom UI using HTML, CSS, and JavaScript.</p>
  <input type="file" id="file" />
</div>
"""

# render the UI using the components module
# st.components.v1.html(html, width=800, height=600)

# get the uploaded file from the UI
uploaded_file = st.file_uploader("Choose a file")

# if a file was uploaded, read it into a DataFrame
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    print(df)

    # display the DataFrame
    st.write(df)
