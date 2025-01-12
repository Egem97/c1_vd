import streamlit as st
import pandas as pd
from styles import styles

def index():
    styles(1)
    st.title("Home")
    st.image(image="src/assets/logo.jpg", caption="Municipalidad meta",)
