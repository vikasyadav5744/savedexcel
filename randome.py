import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime 
import time 
import os
from openpyxl import load_workbook

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None) 
pd.options.mode.copy_on_write = True

data= st.file_uploader("get your csv file for NIFTY", key='upload2')

if data==None:
    st.write("please upload csv file")
else:
    data=pd.read_excel(data)
    
    
    #second highest calculation
    
    def highlight_second_highest(s):
        max_val = s.max()
        second_highest = s.nlargest(2).iloc[-1]  # get second largest value
        threshold = 0.95 * max_val
        threshold1 = 0.90 * max_val
        threshold2 = 0.85 * max_val
        threshold3 = 0.80 * max_val
        threshold4 = 0.75 * max_val
        def color_val(val):
            if val > threshold and val == second_highest:
                return 'background-color: #806E0D; color:black'   
            elif val > threshold1 and val == second_highest:
                return 'background-color: #C5AA10; color:black '
            elif val > threshold2 and val == second_highest:
                return 'background-color: #F7DF5F; color:black'
            elif val > threshold3 and val == second_highest:
                return 'background-color: #FCEC8F; color:black'
            elif val > threshold4 and val == second_highest:
                return 'background-color: #faf8cf; color:black'   
            elif val == max_val:
                return 'background-color: green; color:black'
            else:
                return 'background-color:#e3e2de; color:black'
        return s.apply(color_val)

        # highlight negative
        
        def highlight_negative(val):
            color = 'red' if val < 0 else 'green' 
            return f'color: {color}'

        # 
        def color_two(val, props='background-color:orange; color:black'):
            return props if val >0 else ''
        
        def color_all(val, props='background-color:  #CFF2F8  ; color:black'):                  
            return props if val >0 else props
            
        def color_all_two(val, props='background-color:   #F6D48D   ; color:black'):               #D3F3F8
            return props if val >0 else props
    
        def color_all_three(val, props='background-color: #A4DDCE  ; color:black'): 
            return props if val >0 else props
    
        def color_background(val):  
            return 'background-color: #CFF2F8 ; color: green' if val > 0 else 'background-color:  #CFF2F8 ; color:red'    
   
######################### background change ####################
   
 st.write(data)


       



        





