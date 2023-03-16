# 1 - Add the Excel files (left bar folder and drag and drop)
# Update the filename
xls_filename = "Standardized Input Datatape for Dzango v41.xlsx"

# 2 - Install the packages


# 3 - load the data


import base64
from fuzzywuzzy import fuzz
import pandas as pd
import unicodedata
import streamlit as st

uploaded_file = st.file_uploader("Choose a file")

# Load the dataset
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

# Define the threshold for similarity score
    threshold = 80

    # Create a dictionary to store the unique values and their counts
    unique_values = {}

    #remove all duplicate city and sort it
    city_values = df['City'][~df['City'].isna()].str.strip()
    city_unique = sorted(list(set(city_values)))

    # 4 - Quick checks

    print(city_unique[:5])
    print(len(city_unique))

    # 5 - Normalize the strings to remove accents
    city_norm = []
    for i in range(len(city_unique)):
      city_norm.append(unicodedata.normalize('NFKD', city_unique[i]).encode('ASCII', 'ignore').decode('utf8'))

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
            city_fuzzy_df = pd.concat([city_fuzzy_df,pd.DataFrame({'City': [val], 'Group': [list(city_fuzzy_keys).index(key) + 1], 'Same': [1], 'Chosen': [1]})], ignore_index=True)
          else:
            city_fuzzy_df = pd.concat([city_fuzzy_df,pd.DataFrame({'City': [val], 'Group': [list(city_fuzzy_keys).index(key) + 1], 'Same': [0], 'Chosen': [0]})], ignore_index=True)

    # Export the DataFrame to a CSV file
    # city_fuzzy_df.to_csv('/content/city_fuzzys.csv', encoding='utf-8-sig', index=False)

    #make a script click to download the csv file
    def get_table_download_link(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
        return href

    st.markdown(get_table_download_link(city_fuzzy_df), unsafe_allow_html=True)

    print(city_fuzzy_df.head(5))

    # 7 - After we have cleaned the city_fuzzys.csv, rename city_cleaned.csv and upload it. This will create the output data_updated_cities excel

    # def get_indices(lst, value):
    #     return [i for i, x in enumerate(lst) if x == value]

    # # Load the cleaned dataset (cities_cleaned are the ones post cleaning)
    # city_clean_df = pd.read_csv('/content/city_cleaned.csv', encoding='utf-8-sig')

    # city_clean_city = list(city_clean_df['City'])

    # # print(city_clean_city)

    # df_mod = df
    # df_mod["City"]=df_mod["City"].str.strip()

    # for i in range(len(df_mod["City"])):
    #   if df_mod["City"][i] in city_clean_city:
    #       ls = get_indices(city_clean_city, df_mod["City"][i])
    #       for j in ls:
    #         if city_clean_df["Same"].iloc[j] == 1:
    #           df_mod.loc[i, "City"]  = city_clean_df["City"].loc[ (city_clean_df["Group"]==city_clean_df["Group"][j]) & (city_clean_df["Same"]==1) & (city_clean_df["Chosen"]==1)].iloc[0]
    #           break

    # # print(pd["City"])
    # df_mod.to_excel('/content/data_updated_cities.xlsx', encoding='utf-8-sig', index=False)


    # # print(df["City"][15] )
    # # df["City"][17] in city_clean_city

    # city_values2 = df_mod['City'][~df_mod['City'].isna()]
    # city_unique2 = sorted(list(set(city_values2)))
    # len(city_unique)-len(city_unique2)
