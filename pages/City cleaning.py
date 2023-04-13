import io
import os
import base64
from rapidfuzz import fuzz
import pandas as pd
import unicodedata
import streamlit as st


def get_indices(lst, value):
    return [i for i, x in enumerate(lst) if x == value]

def convert_df(df, type):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    if type == 'csv':
        return df.to_csv().encode('utf-8-sig')

def cityCleaning():
    filename = "original.xlsx"

    df = pd.read_excel(filename)
    # Define the threshold for similarity score
    threshold = 80

    #remove all duplicate city and sort it
    city_values = df['City'][~df['City'].isna()].str.strip()
    city_unique = sorted(list(set(city_values)))

    # 4 - Quick checks

    print(city_unique[:5])
    print(len(city_unique))

    # 5 - Normalize the strings to remove accents
    city_norm = []
    for i in range(len(city_unique)):
      city_norm.append(unicodedata.normalize('NFKD', city_unique[i]).encode('ASCII', 'ignore').decode('utf-8-sig'))

    #print(city_norm[0:5])

    # 6 - Checking the similarity between words with fuzzy and create the output city_fuzzys.csv


    #create list of fuzzy city
    city_fuzzys = {}

    # Loop through each value in the column
    for i in range(len(city_unique)):
        for j in range(i+1, len(city_unique)):

            # Use the fuzzywuzzy library to calculate the similarity score
            score = fuzz.ratio(city_norm[i], city_norm[j])

            # If the similarity score is above the threshold and the indices are not equal, add it to the city_fuzzys dictionary
            if score >= threshold:
                if city_unique[i] in city_fuzzys:
                    city_fuzzys[city_unique[i]].extend([city_unique[j]])
                else:
                    city_fuzzys[city_unique[i]] = [city_unique[i]]
                    city_fuzzys[city_unique[i]].extend([city_unique[j]])

    # print(city_fuzzys)

    city_fuzzy_keys = city_fuzzys.keys()

    # Convert city_fuzzys dictionary to a DataFrame
    city_fuzzy_df = pd.DataFrame(columns=['City', 'Group', 'Same','Chosen'])
    for key, value in city_fuzzys.items():
        # Add 0 for each value in the list
        for val in value:
          if val == key:
            city_fuzzy_df = pd.concat([city_fuzzy_df,pd.DataFrame({'City': [val], 'Group': [str(list(city_fuzzy_keys).index(key) + 1)], 'Same': [str(1)], 'Chosen': [str(1)]})], ignore_index=True)
          else:
            city_fuzzy_df = pd.concat([city_fuzzy_df,pd.DataFrame({'City': [val], 'Group': [str(list(city_fuzzy_keys).index(key) + 1)], 'Same': [str(0)], 'Chosen': [str(0)]})], ignore_index=True)
        city_fuzzy_df = pd.concat([city_fuzzy_df,pd.DataFrame({'City': [''], 'Group': [''], 'Same': [''], 'Chosen': ['']})], ignore_index=True)
    
    #make a script to edit the csv file and download it with the changes

    st.experimental_data_editor(city_fuzzy_df, use_container_width=True, key=None, )
    #make a script click to download the csv file


    with open('city_fuzzy.csv', 'w') as f:
        f.write(city_fuzzy_df.to_csv(index=False))

    st.download_button(
        label="Download fuzzy city as CSV",
        data=convert_df(city_fuzzy_df, "csv"),
        file_name='city_fuzzy.csv',
        mime='text/csv',
    )

def update_xlsx(city_clean_df, df):
    city_clean_city = list(city_clean_df['City'])

    df_mod = df
    df_mod["City"]=df_mod["City"].str.strip()

    for i in range(len(df_mod["City"])):
        if df_mod["City"][i] in city_clean_city:
            ls = get_indices(city_clean_city, df_mod["City"][i])
            for j in ls:
                if city_clean_df["Same"].iloc[j] == 1:
                    df_mod.loc[i, "City"]  = city_clean_df["City"].loc[ (city_clean_df["Group"]==city_clean_df["Group"][j]) & (city_clean_df["Same"]==1) & (city_clean_df["Chosen"]==1)].iloc[0]
                    break
    

    df_mod.to_excel("original.xlsx", index=False)

    st.write("# Step 4: Download the updated xlsx file")

    #download the updated xlsx file
    def get_table_download_link_xlsx(df_mod):
        """Generates a link allowing the data in a given pandas dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        excel_file = io.BytesIO() # Create a bytes buffer for the Excel file
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter') # Create a Pandas Excel writer using XlsxWriter as the engine
        df.to_excel(writer, index=False) # Convert the dataframe to an Excel file
        writer.save() # Save the Excel file to the bytes buffer
        excel_file.seek(0) # Set the pointer to the beginning of the file
        b64 = base64.b64encode(excel_file.read()).decode() # Encode the Excel file in base64
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="original.xlsx">Download xlsx file</a>'
        return href

    
    st.markdown(get_table_download_link_xlsx(df_mod), unsafe_allow_html=True)
    


if not os.path.isfile("original.xlsx"):
    st.warning("Please upload a file to get started.")
else:
    st.write("# Step 1: Process city fuzzy csv")

    st.write("File name: ", open('file_uploaded_name.txt', 'r').read())

    filename = "city_fuzzy.csv"

    nextStep = False

    if os.path.isfile(filename):
        if st.button('Re-clean city'):
            cityCleaning()
        else:
            df = pd.read_csv(filename)
            # Display the DataFrame in the Streamlit app
            st.experimental_data_editor(df, use_container_width=True, key=None)
            st.download_button(
                label="Download fuzzy city as CSV",
                data=convert_df(df, "csv"),
                file_name='city_fuzzy.csv',
                mime='text/csv',
            )
            with open('city_fuzzy.csv', 'w') as f:
                    f.write(df.to_csv(index=False))
        nextStep = True
        
    else:
        if st.button('Clean City'):
            cityCleaning()
            nextStep = True

    if (nextStep):
    
        st.write("# Step 2: Download and edit the city fuzzy csv file")
        st.write("*After have cleaned city fuzzy csv file, upload it in next step*")

        st.write("# Step 3: Upload the city csv file")

        uploaded_file = st.file_uploader("upload cleaned city csv file here", type="csv")
        if uploaded_file is None:
            st.warning("Please upload a cleaned city csv file to start!")
        else:
            city_clean_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            # st.experimental_data_editor(city_clean_df, use_container_width=True)
            st.experimental_data_editor(city_clean_df, use_container_width=True, key=None)
            df = pd.read_excel("original.xlsx")
            st.write(df.head(5))
            update_xlsx(city_clean_df, df)

