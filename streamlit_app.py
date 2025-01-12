import streamlit as st
from router import pages

def main():    
     
   st.set_page_config(
         page_title="MPT-COMPROMISO 1",
         page_icon="src/assets/logo.jpg",
         layout="wide",
                        
      )

   st.logo("src/assets/logo.jpg")    
   pg = st.navigation( pages())
   pg.run()

if __name__ == '__main__':
   main()
