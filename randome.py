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
    
def newcal01(df):
    limit =pd.Series(df.Time.unique())
    result=pd.DataFrame()
    a=0
    while a < len(limit):
        mark=df[df['Time']==limit[a]]
        mark['call_max']=mark['CALL_OI'].max()
        mark['put_max']=mark['PUT_OI'].max()
        mark['CALL_OI_Per']=(mark['CALL_OI']/mark['call_max'])*100
        mark['PUT_OI_Per']=(mark['PUT_OI']/mark['put_max'])*100
        mark['CE_Vol_max']=mark['CALL_VOLUME'].max()
        mark['PE_Vol_max']=mark['PUT_VOLUME'].max()
        mark['CALL_VOL_Per']=(mark['CALL_VOLUME']/mark['CE_Vol_max'])*100
        mark['PUT_VOL_Per']=(mark['PUT_VOLUME']/mark['PE_Vol_max'])*100
        mark['Sum_CE']=mark['CALL_OI'].sum()
        mark['Sum_PE']=mark['PUT_OI'].sum()
        mark['Overall_PCR']=mark['Sum_PE']/mark['Sum_CE']
        mark['CE_Price']=mark['CALL_VOLUME']/mark['CE_Vol_max']*50 + mark['STRIKE']
        mark['PE_Price']= mark['STRIKE'] - mark['PUT_VOLUME']/mark['PE_Vol_max']*50 
        mark['PCR']=mark['PUT_OI']/mark['CALL_OI']
        mark['PCR_Val']=(mark['PCR'])*50
        result=pd.concat([result,mark], axis=0, join='outer', ignore_index=True)
        a+=1
        return result

datafile = newcal01(data)
datafile['Date'] = datafile['Date'].dt.date

tab1, tab2, tab3=st.tabs(["Table view of data", "Data charts / visualization", "time wise details of strike"])

with tab1:
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
    
    def highlight_negative(val):
        color = 'red' if val < 0 else 'green' 
        return f'color: {color}'

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
   
    col1, col2, col3, col4, col5, col6, col7, col8= st.columns(8)
   
    with col1:    
        time_01 = st.selectbox("please select time", options=datafile.Time.sort_values(ascending=False).unique(), key='time_01')
        stocktime = datafile [datafile ['Time']==time_01] 
        strike_option = list(stocktime.STRIKE.unique())  
        spot_price = stocktime.Spot_Price.iloc[0].round(-2)
        ind0 = strike_option.index(spot_price)
        ind1 = ind0-6
        ind2 = ind0+6
    with col2:
        con_strike1=st.selectbox("Select first strike", options=strike_option, index=ind1, key='first1')
    with col3:
        con_strike2=st.selectbox("Select first strike", options=strike_option,index=ind2, key='first2')
    
    refined = stocktime[stocktime.STRIKE.between(con_strike1, con_strike2)]       

    ####     highlighting row
    val =round(refined.Spot_Price.iloc[0],-2)
    def highlight_row(row):
        if row['STRIKE'] == val:
            return ['background-color:#D1B8CB'] *len(row)   
        else:
            return [''] *len(row)
        ##########
    def sell01(val):
                if val <0.30:
                    return 'Oversold'
                elif val <0.80:
                    return 'Sell'
                elif val <1.5:
                    return 'Buy'
                else:
                    return 'Overbought'
                
    datafile['View'] =datafile['Overall_PCR'].map(sell01)
    
    def highlight_status(val):
        if val == "Oversold":
            return "background-color: #C33536; color:black"
        elif val == "Sell": 
            return "background-color: #F18485; color:black"
        elif val == "Buy":
            return "background-color: #82C368; color:black"
        else:
            return "background-color: #50A52E; color:black"
    
    #######

    with col4:
        sleeptime =st.selectbox("Sleep Time", options=[3,6,9,12,15], index=0)

    with col5:
        sub_table1=st.button("Filter Data", key='fil1', type='primary', use_container_width=True)
        
    refined_new=refined.rename(columns={'CALL_CHNG':'CE.CHNG', 'CALL_OI':'CE.OI','CALL_VOLUME':'CE.VOL','PUT_VOLUME':'PE.VOL','PUT_OI':'PE.OI','PUT_CHNG':'PE.CHNG','CALL_OI_Per':'CE.Per','CALL_VOL_Per':'CE.VPer','CALL_LTP':'CE.LTP','CE_Price':'CE.Prc','PE_Price':'PE.Prc','PUT_LTP':'PE.LTP','PUT_VOL_Per':'PE.VPer','PUT_OI_Per':'PE.Per'})
    
    love007=refined_new.style.apply(highlight_second_highest, subset =['CE.CHNG','CE.OI','CE.VOL','PE.VOL','PE.OI','PE.CHNG'])\
         .format(precision=0).format(precision=2, subset=['Time', 'CHNG','CHNG.1','CE.LTP', 'PCR','PE.LTP','PE.VOL','CE.VPer']).format(precision=0, subset=['CE.OI','CE.VOL','PE.VOL','PE.OI','PE.CHNG','STRIKE'])\
         .map(color_two, subset=['STRIKE']) .map(color_all, subset=['IV','IV.1', 'BID QTY', 'BID',  'BID.1', 'BID QTY.1', 'ASK.1','ASK QTY.1', 'Spot_Price','ASK QTY', 'ASK', 'PE.LTP', 'CE.LTP', 'PCR', 'PCR_Val']).map(color_all_two, subset=['CE.Prc','PE.Prc']).map(color_all_three, subset=['CE.VPer', 'PE.VPer', 'PE.Per', 'CE.Per'])\
         .map(color_background, subset=['CHNG', 'CHNG.1']).apply(highlight_row, axis=1, subset=['STRIKE','CE.Prc', 'PE.Prc', 'CE.VPer', 'PE.VPer'])        

    if sub_table1==True:
        st.dataframe(love007, height=500, hide_index=True, column_order=['Time','CE.LTP','CHNG','CE.Per','CE.CHNG','CE.OI','CE.VOL','CE.VPer','CE.Prc','STRIKE','PE.Prc','PE.VPer','PE.VOL','PE.OI','PE.CHNG','PE.Per','CHNG.1','PE.LTP','Spot_Price', 'PCR', 'PCR_Val'], use_container_width=True)
        col1, col2, col3=st.columns(3)
        with col1:
            PCR= datafile[datafile['STRIKE']== round (datafile.Spot_Price.iloc[0], -2)] [['Time', 'Sum_CE','Sum_PE','Overall_PCR', 'View']].sort_values(by='Time', ascending=False).style.background_gradient(cmap='Greens', low=0.9, high=2, axis=0, subset=['Overall_PCR', 'Sum_PE']).background_gradient(cmap='Oranges',low=0.4, high=1, subset=['Sum_CE']).format(precision=2, subset=[ 'Time','Overall_PCR']).applymap(highlight_status, subset=['View'])        
            st.dataframe(PCR, hide_index=True, height=1400, use_container_width=True)
        with col2:
            st.line_chart(PCR, x='Time', y='Overall_PCR', color= ["#DE1BD1"],height=400, width=500)
            st.bar_chart(refined, x='STRIKE', y=['CALL_VOLUME', 'PUT_VOLUME'], stack=False, color= ["#F20712", "#19543F"], use_container_width=True)
            OI_chart=st.bar_chart(refined, x='STRIKE', y=['CALL_OI', 'PUT_OI'],  stack=False, color= ["#F20712", "#19543F"], use_container_width=True)
            OI_chart=st.bar_chart(refined, x='STRIKE', y=['CALL_CHNG', 'PUT_CHNG'], stack=False, color= ["#F20712", "#19543F"], use_container_width=True)       
       
        with col3:
            sumpe=datafile[datafile['STRIKE']== spot_price]
            st.line_chart(sumpe, x='Time', y=['Sum_CE', 'Sum_PE'], color=['#B62626', '#26B669'], height=400, width=500)
            OI_chart=st.bar_chart(refined, x='STRIKE', y=['CALL_VOLUME', 'PUT_VOLUME'], stack=False, color= ["#F20712", "#19543F"],horizontal=True, height=300, width=500)
            OI_chart=st.bar_chart(refined, x='STRIKE', y=['CALL_OI', 'PUT_OI'],  stack=False, color= ["#F20712", "#19543F"],horizontal=True, height=300,width=500)
                   
#   play button
    time_option1=datafile.Time.sort_values(ascending=True).unique()
    playdata=datafile[datafile['STRIKE'].between(con_strike1, con_strike2)]
    ############################### play button colde
    if 'page' not in st.session_state:
        st.session_state.page = 0 

# function for button of next and previous
    def previous():
        if st.session_state.page >0:
            st.session_state.page -=1
                
    def next():
        if (st.session_state.page +1) < len(time_option1):
            st.session_state.page +=1
    
    def play():
        val =0
        placeholder = st.empty() 
        while val < len (time_option1):
            frame = playdata[playdata['Time']== time_option1[val]]
            nextplay = frame.style.apply(highlight_second_highest, subset=['CALL_OI', 'PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG',])\
                .format(precision=1).map(color_two, subset=['STRIKE']).format(precision=2, subset=['Time'])\
                .map(color_all, subset=['CALL_OI_Per', 'CALL_LTP','PUT_LTP','PUT_OI_Per','Spot_Price','CALL_VOL_Per','PUT_VOL_Per','CE_Price','PE_Price'])\
                .format(precision=0, subset =['PE_Price','CE_Price']).apply(highlight_row, axis=1, subset=['STRIKE','CALL_LTP','PUT_LTP','PUT_VOL_Per','CHNG', 'CHNG.1','CALL_VOL_Per', 'CE_Price', 'PE_Price']) 
            placeholder = st.dataframe(nextplay,hide_index=True, column_order=['Time','CALL_OI_Per','CALL_CHNG','CALL_OI','CALL_VOLUME','CALL_VOL_Per','CALL_LTP','CE_Price','STRIKE','PE_Price','PUT_LTP','PUT_VOL_Per','PUT_VOLUME','PUT_OI','PUT_CHNG','PUT_OI_Per','Spot_Price'], use_container_width=True, height=800)
            val+=1
            time.sleep(sleeptime)
            placeholder.empty()
            
##### play buttons
    with col6:
        st.button("play", on_click=play, use_container_width=True, type='primary')

    with col7:
        previous01 = st.button("previous", on_click=previous, use_container_width=True, type='primary')
    
    with col8:
        next01= st.button("next", on_click=next, use_container_width=True, type='primary')

################ button logic
        if previous01 == True:
            frame = playdata[playdata['Time']== time_option1[st.session_state.page]]
            nextplay = frame.style.apply(highlight_second_highest, subset=['CALL_OI', 'PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG',])\
                    .format(precision=1).map(color_two, subset=['STRIKE']).format(precision=2, subset=['Time'])\
                    .map(color_all, subset=['CALL_OI_Per', 'CALL_LTP','PUT_LTP','PUT_OI_Per','Spot_Price','CALL_VOL_Per','PUT_VOL_Per','CE_Price','PE_Price'])\
                    .format(precision=0, subset =['PE_Price','CE_Price']).set_sticky(axis=1).apply(highlight_row, axis=1, subset=['STRIKE','CALL_LTP','PUT_LTP','PUT_VOL_Per','CHNG', 'CHNG.1','CALL_VOL_Per', 'CE_Price', 'PE_Price']) 
            st.dataframe(nextplay,hide_index=True, column_order=['Time','CALL_OI_Per','CALL_CHNG','CALL_OI','CALL_VOLUME','CALL_VOL_Per','CALL_LTP','CE_Price','STRIKE','PE_Price','PUT_LTP','PUT_VOL_Per','PUT_VOLUME','PUT_OI','PUT_CHNG','PUT_OI_Per','Spot_Price'], use_container_width=True, height=400)
            
            col1, col2, col3=st.columns(3)
            with col1:
                st.bar_chart(frame, x='STRIKE', y=['CALL_VOLUME', 'PUT_VOLUME'], stack=False, color= ["#F20712", "#19543F"])
            with col2:
                OI_chart=st.bar_chart(frame, x='STRIKE', y=['CALL_OI', 'PUT_OI'],  stack=False, color= ["#F20712", "#19543F"])
            with col3:
                OI_chart=st.bar_chart(frame, x='STRIKE', y=['CALL_CHNG', 'PUT_CHNG'], stack=False, color= ["#F20712", "#19543F"])

        if next01 == True:
            frame = playdata[playdata['Time']== time_option1[st.session_state.page]]
            nextplay =frame.style.apply(highlight_second_highest, subset=['CALL_OI', 'PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG',])\
                    .format(precision=1).map(color_two, subset=['STRIKE']).format(precision=2, subset=['Time'])\
                    .applymap(color_all, subset=['CALL_OI_Per', 'CALL_LTP','PUT_LTP','PUT_OI_Per','Spot_Price','CALL_VOL_Per','PUT_VOL_Per','CE_Price','PE_Price'])\
                    .format(precision=0, subset =['PE_Price','CE_Price']).set_sticky(axis=1).apply(highlight_row, axis=1, subset=['STRIKE','CALL_LTP','PUT_LTP','PUT_VOL_Per','CHNG', 'CHNG.1','CALL_VOL_Per', 'CE_Price', 'PE_Price']) 
            st.dataframe(nextplay,hide_index=True, column_order=['Time','CALL_OI_Per','CALL_CHNG','CALL_OI','CALL_VOLUME','CALL_VOL_Per','CALL_LTP','CE_Price','STRIKE','PE_Price','PUT_LTP','PUT_VOL_Per','PUT_VOLUME','PUT_OI','PUT_CHNG','PUT_OI_Per','Spot_Price'], use_container_width=True, height=400)
            col1, col2, col3=st.columns(3)
            with col1:
                st.bar_chart(frame, x='STRIKE', y=['CALL_VOLUME', 'PUT_VOLUME'], stack=False, color= ["#F20712", "#19543F"])
            with col2:
                OI_chart=st.bar_chart(frame, x='STRIKE', y=['CALL_OI', 'PUT_OI'],  stack=False, color= ["#F20712", "#19543F"])
            with col3:
                OI_chart=st.bar_chart(frame, x='STRIKE', y=['CALL_CHNG', 'PUT_CHNG'], stack=False, color= ["#F20712", "#19543F"])
# end of play button

with tab2:  
    tel1_strike=strike_option.index(spot_price-200)
    tel2_strike=strike_option.index(spot_price-100)
    tel3_strike=strike_option.index(spot_price-50)
    tel4_strike=strike_option.index(spot_price)
    tel5_strike=strike_option.index(spot_price+50)
    tel6_strike=strike_option.index(spot_price+100)

    col1, col2, col3, col4, col5, col6=st.columns(6)
    with col1:
        chart_strike= st.selectbox("select the begning Time", options=strike_option, key='chart1', index=tel1_strike)
        detail=datafile[datafile['STRIKE']==chart_strike][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
        st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])

        chart_chng= st.selectbox("select the begning Time", options=strike_option, key='chart_chng1', index=tel1_strike)
        chart_chng_data=datafile[datafile['STRIKE']==chart_chng][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
        st.line_chart(chart_chng_data, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669']) 
               
    with col2:
        
        chart_strike2= st.selectbox("select the begning Time", options=strike_option, key='chart2', index=tel2_strike)
        detail=datafile[datafile['STRIKE']==chart_strike2][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
        st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])

        
        chart_chng2= st.selectbox("select the begning Time", options=strike_option, key='chart_chng2', index=tel2_strike)
        chart_chng_data2=datafile[datafile['STRIKE']==chart_chng2][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
        st.line_chart(chart_chng_data2, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])  
            
    with col3:
        
        chart_strike3= st.selectbox("select the begning Time", options=strike_option, key='chart3', index=tel3_strike)
        detail=datafile[datafile['STRIKE']==chart_strike3][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
        st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])

        
        chart_chng3= st.selectbox("select the begning Time", options=strike_option, key='chart_chng3', index=tel3_strike)
        chart_chng_data3=datafile[datafile['STRIKE']==chart_chng3][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
        st.line_chart(chart_chng_data3, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])
        
    with col4:
       
        chart_strike4= st.selectbox("select the begning Time", options=strike_option, key='chart4', index=tel4_strike)
        detail=datafile[datafile['STRIKE']==chart_strike4][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
        st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])

        
        chart_chng4= st.selectbox("select the begning Time", options=strike_option, key='chart_chng4', index=tel4_strike)
        chart_chng_data4=datafile[datafile['STRIKE']==chart_chng4][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
        st.line_chart(chart_chng_data4, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])

    with col5:
       
        chart_strike5= st.selectbox("select the begning Time",options=strike_option, key='chart5', index=tel5_strike)
        detail=datafile[datafile['STRIKE']==chart_strike5][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
        st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])

       
        chart_chng5= st.selectbox("select the begning Time",options=strike_option, key='chart_chng5', index=tel5_strike)
        chart_chng_data5=datafile[datafile['STRIKE']==chart_chng5][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
        st.line_chart(chart_chng_data5, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])

    with col6:
        
        chart_strike6= st.selectbox("select the begning Time", options=strike_option, key='chart6', index=tel6_strike)
        detail=datafile[datafile['STRIKE']==chart_strike6][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
        st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])

        chart_chng6= st.selectbox("select the begning Time",options=strike_option, key='chart_chng6', index=tel6_strike)
        chart_chng_data6=datafile[datafile['STRIKE']==chart_chng6][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
        st.line_chart(chart_chng_data6, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])

with tab3:
    # st.line_chart(datafile, x='Time', y=['Sum_CE', 'Sum_PE'], color=['#B62626', '#26B669'])
    col1, col2, col3=st.columns(3)
    with col1:
        cmaplist=['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Grays', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_grey', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gist_yerg', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'grey', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r']
        cmap1=st.selectbox("CMAP Time Options", options=cmaplist, index=0, key='cmap1')
    with col2:
        cmap2=st.selectbox("CMAP CALL OI Options", options=cmaplist, index=17, key='cmap2')
    with col3:
        cmap3=st.selectbox("CMAP CHNG OI Options", options=cmaplist, index=21, key='cmap3')

    col1, col2, col3=st.columns(3)
    with col1:
        con_strike3=st.selectbox("Select first strike", options=strike_option, index=tel3_strike, key='first3')
        rem = datafile[datafile['STRIKE']==con_strike3][['Time', 'CALL_OI','PUT_OI', 'CALL_CHNG', 'PUT_CHNG', 'CALL_VOL_Per','PUT_VOL_Per', 'CALL_OI_Per', 'PUT_OI_Per' ]].sort_values(by='Time', ascending=False)
        remstl=rem.style.format(precision=2, subset=['Time','CALL_VOL_Per','PUT_VOL_Per', 'CALL_OI_Per', 'PUT_OI_Per']).background_gradient(cmap=cmap1, subset=['Time']).background_gradient(cmap=cmap2, subset=['CALL_OI', 'PUT_OI','CALL_VOL_Per','PUT_VOL_Per']).background_gradient(cmap= cmap3, subset=['CALL_CHNG', 'PUT_CHNG','CALL_OI_Per', 'PUT_OI_Per' ])
        st.dataframe(remstl,hide_index=True, height=1700)
        
    with col2:
        con_strike4=st.selectbox("Select first strike", options=strike_option, index=tel4_strike, key='first4')
        rem1 = datafile[datafile['STRIKE']==con_strike4][['Time','CALL_OI','PUT_OI', 'CALL_CHNG', 'PUT_CHNG', 'CALL_VOL_Per','PUT_VOL_Per', 'CALL_OI_Per', 'PUT_OI_Per']].sort_values(by='Time', ascending=False)
        remst2=rem1.style.background_gradient(cmap=cmap2, subset=['CALL_OI', 'PUT_OI','CALL_VOL_Per','PUT_VOL_Per']).background_gradient(cmap=  cmap3, subset=['CALL_CHNG', 'PUT_CHNG','CALL_OI_Per', 'PUT_OI_Per']).format(precision=2, subset=['Time','CALL_VOL_Per','PUT_VOL_Per', 'CALL_OI_Per', 'PUT_OI_Per'])
        st.dataframe(remst2, hide_index=True, height=1700)
    with col3:
        con_strike5=st.selectbox("Select first strike", options=strike_option, index=tel5_strike, key='first5')
        rem2 = datafile[datafile['STRIKE']==con_strike5][['Time','CALL_OI','PUT_OI', 'CALL_CHNG', 'PUT_CHNG','CALL_VOL_Per','PUT_VOL_Per', 'CALL_OI_Per', 'PUT_OI_Per']].sort_values(by='Time', ascending=False)
        remst3=rem2.style.background_gradient(cmap=cmap2, subset=['CALL_OI', 'PUT_OI','CALL_VOL_Per','PUT_VOL_Per']).background_gradient(cmap= cmap3, subset=['CALL_CHNG', 'PUT_CHNG', 'CALL_OI_Per', 'PUT_OI_Per']).format(precision=2, subset=['Time','CALL_VOL_Per','PUT_VOL_Per', 'CALL_OI_Per', 'PUT_OI_Per'])
        st.dataframe(remst3,  hide_index=True, height=1700)


       



        




