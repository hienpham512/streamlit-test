import io
import os
import base64
from rapidfuzz import fuzz
import pandas as pd
import unicodedata
import streamlit as st

def reduce_unique(strings):
    # read the string ad remove the duplicates
    strings = list(set(strings))
    # sort the list
    strings.sort()
    # return the list
    return strings

def match_fuzzy(tenants):
    obj = {}
    threshold = 83
    for i in range(len(tenants)):
        for j in range(i + 1, len(tenants)):
        # Use the fuzzywuzzy library to calculate the similarity score
            score = fuzz.partial_token_sort_ratio(tenants[i], tenants[j])

            # If the similarity score is above the threshold and the indices are not equal, add it to the tenant_fuzzys dictionary
            if score >= threshold:
                if tenants[i] in obj:
                    obj[tenants[i]].extend([{"tenant": tenants[j], "score": round(score, 2)}])
                else:
                    obj[tenants[i]] = [{"tenant": tenants[i], "score": 100}]
                    obj[tenants[i]].extend([{"tenant": tenants[j], "score": round(score, 2)}])
    return obj

def update_xlsx(tenant_cleaned_df_param, df):
    df_mod = df
    df_mod['Standardized Tenant Name'] = df_mod['Tenant Name'].apply(lambda s: "" if pd.isna(s) else s)
    df_mod['Standardized Tenant Name'] = df_mod['Standardized Tenant Name'].apply(lambda s: s.strip())
    df_tenants = list(df['Standardized Tenant Name'])

    #convert to data frame
    tenant_cleaned_df = pd.DataFrame(tenant_cleaned_df_param)

    #remove empty rows
    tenant_cleaned_df = tenant_cleaned_df.dropna(how='all')

    #remove same = 0
    tenant_cleaned_df = tenant_cleaned_df.loc[(tenant_cleaned_df['Same'] != 0)]


    tenant_cleaned_tenant = list(tenant_cleaned_df['Tenant'])

    for i in range(len(df_tenants)):
        if df_tenants[i] in tenant_cleaned_tenant:
            #find lists of tenants which includes tenant name
            find_tenant = tenant_cleaned_df.loc[(tenant_cleaned_df["Tenant"] == df_tenants[i])]
            #find the tenant name have been chosen in the first list and replace
            new_tenant_name = tenant_cleaned_df.loc[((tenant_cleaned_df["Group"] == list(find_tenant["Group"])[0]) & (tenant_cleaned_df["Chosen"] == 1))]
            if len(list(new_tenant_name["Tenant"])) ==0:
                    st.write(f'{df_tenants[i]} has no replacement')
            else: 
                df_tenants[i]=list(new_tenant_name["Tenant"])[0]

    df_mod['Standardized Tenant Name'] = df_tenants
    df_mod.to_excel("original.xlsx", index=False)

    st.write("# Step 4: Download the updated xlsx file")

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
    

def tenantCleaning():
    filename = "original.xlsx"
    df = pd.read_excel(filename)
    df['Standardized Tenant Name'] = df['Tenant Name'].apply(lambda s: "" if pd.isna(s) else s)
    df['Standardized Tenant Name'] = df['Standardized Tenant Name'].apply(lambda s: s.strip())

    tenant_unique = reduce_unique(df['Standardized Tenant Name'])

    fuzzy_tenants = match_fuzzy(tenant_unique)

    fuzzy_tenants_keys = fuzzy_tenants.keys()

    tenant_fuzzy_df = pd.DataFrame(columns=['Tenant', 'Group', 'Same','Chosen', 'Score'])

    for key, value in fuzzy_tenants.items():
        for val in value:
            if val['tenant'] == key:
                tenant_fuzzy_df = pd.concat([tenant_fuzzy_df,pd.DataFrame({'Tenant': [val['tenant']], 'Group': [list(fuzzy_tenants_keys).index(key) + 1], 'Same': [1], 'Chosen': [1], 'Score': [val['score']]})], ignore_index=True)
            else:
                tenant_fuzzy_df = pd.concat([tenant_fuzzy_df,pd.DataFrame({'Tenant': [val['tenant']], 'Group': [list(fuzzy_tenants_keys).index(key) + 1], 'Same': [0], 'Chosen': [0], 'Score': [val['score']]})], ignore_index=True)
        tenant_fuzzy_df = pd.concat([tenant_fuzzy_df,pd.DataFrame({'Tenant': [''], 'Group': [''], 'Same': [''], 'Chosen': [''], 'Score': ['']})], ignore_index=True)

    st.experimental_data_editor(tenant_fuzzy_df, use_container_width=True, key=None, )

    with open('tenant_fuzzy.csv', 'w') as f:
        f.write(tenant_fuzzy_df.to_csv(index=False))

    st.download_button(
        label="Download tenant fuzzy as CSV",
        data=convert_df(tenant_fuzzy_df, "csv"),
        file_name='tenant_fuzzy.csv',
        mime='text/csv',
    )


def convert_df(df, type):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    if type == 'csv':
        return df.to_csv().encode('utf-8-sig')

if not os.path.isfile("original.xlsx"):
    st.warning("Please upload a file to get started.")
else:
    st.write("# Step 1: Process tenant fuzzy csv")

    st.write("File name: ", open('file_uploaded_name.txt', 'r').read())

    filename = "tenant_fuzzy.csv"

    nextStep = False

    if os.path.isfile(filename):
        if st.button('Re-clean city'):
            tenantCleaning()
        else:
            df = pd.read_csv(filename)
            # Display the DataFrame in the Streamlit app
            st.experimental_data_editor(df, use_container_width=True, key=None)
            st.download_button(
                label="Download tenant fuzzy as CSV",
                data=convert_df(df, "csv"),
                file_name='tenant_fuzzy.csv',
                mime='text/csv',
            )
            with open('tenant_fuzzy.csv', 'w') as f:
                    f.write(df.to_csv(index=False))
        nextStep = True
    else:
        if st.button('Clean Tenant'):
            tenantCleaning()
            nextStep = True

    if (nextStep):
    
        st.write("# Step 2: Download and edit the tenant fuzzy csv file")
        st.write("*After have cleaned tenant fuzzy csv file, upload it in next step*")

        st.write("# Step 3: Upload the tenant cleaned csv file")

        uploaded_file = st.file_uploader("upload cleaned city csv file here", type="csv")
        if uploaded_file is None:
            st.warning("Please upload a cleaned city csv file to start!")
        else:
            tenant_clean_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            st.experimental_data_editor(tenant_clean_df, use_container_width=True, key=None)
            df = pd.read_excel("original.xlsx")
            st.write(df.head(5))
            update_xlsx(tenant_clean_df, df)