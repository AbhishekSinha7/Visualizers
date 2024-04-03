import streamlit as st 
from lida import Manager, TextGenerationConfig , llm  
from dotenv import load_dotenv
import os
import openai
from PIL import Image
from io import BytesIO
import base64
import pandas as pd
import time

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def base64_to_image(base64_string):
    # Decode the base64 string
    byte_data = base64.b64decode(base64_string)
    
    # Use BytesIO to convert the byte data to image
    return Image.open(BytesIO(byte_data))


#library = "matplotlib"
library = "seaborn"
lida = Manager(text_gen = llm("openai"))
textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo-0301", use_cache=True)
st.set_page_config(layout='wide')
menu = st.sidebar.selectbox("Choose an Option", ["Dashboard","Analytics", "Code", "Graph"])


file_uploader = st.file_uploader("Upload your CSV", type="csv")    
if file_uploader is not None:
    df = pd.read_csv(file_uploader)
    summary = lida.summarize(df, summary_method="default", textgen_config=textgen_config)

if menu == "Dashboard":
    if file_uploader is not None:
        st.subheader("Summarization of your Data")
        st.write("") 
        st.write("")
        st.info("Dataset Preview")
        
        st.dataframe(df.head(50), use_container_width=True)

        st.write("") 
        st.write("")

        st.info("Dataset Shape")
        st.write('Number of Rows:', df.shape[0])
        st.write('Number of Columns:', df.shape[1])

        st.write("") 
        st.write("")
        st.info("Column Names and Data Types:")
        st.dataframe(df.dtypes, use_container_width=True)

        st.write("") 
        st.write("")

        if df.isnull().sum().sum() > 0:
            st.info("Null Values")
            st.dataframe(df.isnull().sum().sort_values(ascending=False),width=500)
            st.write("") 
            st.write("")
        else:
            st.info("No Null Values")
            st.write("")
        
        
        st.info("Summary Statistics")
        st.write(df.describe())
        
        st.write("") 
        st.write("")
        st.info("JSON View")
        st.write(summary)
        

elif menu == "Analytics":
    st.subheader("Analysis of the Data")
    if file_uploader is not None:
          
        st.write("") 
        st.write("")
        summary = lida.summarize(df, summary_method="default", textgen_config=textgen_config)

        st.info("Analysis of the Dataset")
        goals = lida.goals(summary, n=25, textgen_config=textgen_config)

        def show_Analytics():
            count =0
            for goal in goals:
                st.write("Q: ",goal.question)
                st.write("Id: ",goal.visualization)
                #st.write("Goal: ",goal.rationale)
                textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                charts = lida.visualize(summary=summary, goal=goal.visualization, textgen_config=textgen_config, library=library)  
                
                explanation = lida.explain(code=charts[0].code, library=library, textgen_config=textgen_config)
                chart_exp = None
                for section in explanation[0]:
                    if section["section"] == "accessibility":
                        chart_exp = section["explanation"]
                st.write("Explanation: ",chart_exp)

                img_base64_string = charts[0].raster
                img = base64_to_image(img_base64_string)
                st.image(img)
                count=count+3
                st.info("-------------------------------------------------------------------------------------------x-------------------------------------------------------------------------------------------")
                if count % 3==0:
                    time.sleep(20)

        while True:
            show_Analytics()



elif menu == "Code":
    st.subheader("Query your Data to Generate Code")
    if file_uploader is not None:
        
        text_area = st.text_area("Query your Data to Generate Code", height=200)
        code=0
        if st.button("Generate Code"):
            if len(text_area) > 0:
                st.info("Your Query: " + text_area)
                textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                user_query = text_area
                try:
                    summary = lida.summarize(df, summary_method="default", textgen_config=textgen_config)
                    charts = lida.visualize(summary=summary, goal=user_query, textgen_config=textgen_config)
                    explanation = lida.explain(code=charts[0].code, library=library, textgen_config=textgen_config)
                    code_exp = None
                    for section in explanation[0]:
                        if section["section"] == "visualization":
                            code_exp = section["explanation"]
                    st.write("Explanation: ",code_exp)
                    code = charts[0].code
                    st.code(code)
                except Exception as e:
                    raise ValueError("The request is Not properly specified or Not genuine: {}".format(str(e)))





elif menu == "Graph":
    st.subheader("Query your Data to Generate Graph")

    if file_uploader is not None:
        text_area = st.text_area("Query your Data to Generate Graph", height=200)
        if st.button("Generate Graph"):
            if len(text_area) > 0:
                st.info("Your Query: " + text_area)
                textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                summary = lida.summarize(df, summary_method="default", textgen_config=textgen_config)
                user_query = text_area
                charts = lida.visualize(summary=summary, goal=user_query, textgen_config=textgen_config)  
                #charts[0]
                try:
                    image_base64 = charts[0].raster
                    img = base64_to_image(image_base64)
                    st.image(img)
                except Exception as e:
                    raise ValueError("The request is not properly specified or Not genuine: {}".format(str(e)))            


hide_st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)