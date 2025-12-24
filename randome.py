import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import datetime as dt
import os
import csv
from pathlib import Path

# change the main file name from here
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None) 

pd.options.mode.copy_on_write = True

expirynifty=dt.date(2025,12,30) 

# defining functions
def sell01(val):
    if val <0.30:
        return 'Oversold'
    elif val <0.80:
        return 'Sell'
    elif val <1.5:
        return 'Buy'
    else:
        return 'Overbought'
        
def highlight_status(val):
    if val == "Oversold":
        return "background-color: #C33536; color:black"
    elif val == "Sell": 
        return "background-color: #F18485; color:black"
    elif val == "Buy":
        return "background-color: #82C368; color:black"
    else:
        return "background-color: #50A52E; color:black"
  
def highlight_second_highest(s):
  max_val = s.max()
  second_highest = s.nlargest(2).iloc[-1]  # get second largest value
  threshold = 0.75 * max_val
  threshold1 = 0.90 * max_val
  threshold2 = 0.80 * max_val
  
  def color_val(val):
    if val > threshold1 and val == second_highest:
      return 'background-color: #8c8418; color:black'
    elif val > threshold2 and val == second_highest:
      return 'background-color:  #e3e086; color:black'
    elif val > threshold and val == second_highest:
      return 'background-color:lightyellow;color:black'
    elif val == max_val:
      return 'background-color: green; color:black'
    else:
      return 'background-color:#e1e5e6; color:black'     
  return s.apply(color_val)
# other codes
def highlight_negative(val):
  color = 'red' if val < 0 else 'green' 
  return f'color: {color}'

def color_two(val, props='background-color:orange; color:black'):
  return props if val >0 else ''

def color_all(val, props='background-color:#ceeded; color:black'):
  return props if val >0 else props
    
def color_background_red(val):  
  return 'background-color:#f7f4d6; color:green' if val > 0 else 'background-color:#f7f4d6; color:red'
  
# visualiazation / interpretation of data

tab1, tab2, tab3, tab4=st.tabs(["Today's NIFTY", "Addition to Master File", "Historical", "others"])
with tab1:
  data = st.file_uploader("csv file upload", key='upload1')
  col1, col2, col3, col4, col5, col6=st.columns(6)
  with col1:
    Date=st.date_input("Date", format="DD/MM/YYYY", width='stretch', key='val2')
  with col2:
    Expiry=st.date_input("Expiry",format="DD/MM/YYYY", width='stretch', key='val3', value=expirynifty)
  with col3:
    spot=int(st.number_input("Please give spot price", key='spot1', value=26000, step=100))
  with col4:
    Time=st.number_input("Please give time", key='time1')
  if data!=None:
    df=pd.read_csv(data, skiprows=1, usecols=['OI', 'CHNG IN OI', 'VOLUME', 'IV', 'LTP', 'CHNG','BID QTY', 'BID', 'ASK', 'ASK QTY', 'STRIKE', 'BID QTY.1', 'BID.1','ASK.1', 'ASK QTY.1', 'CHNG.1', 'LTP.1','IV.1', 'VOLUME.1','CHNG IN OI.1', 'OI.1'])
    df=df.rename(columns={'OI':'CALL_OI','CHNG IN OI':'CALL_CHNG','VOLUME':'CALL_VOLUME','VOLUME.1':'PUT_VOLUME', 'CHNG IN OI.1':'PUT_CHNG','OI.1':'PUT_OI', 'LTP':'CALL_LTP', 'LTP.1':'PUT_LTP'})
    df=df.replace({",":'', "'":''}, regex=True).replace(r'(?<!^)-', '', regex=True).replace('-',0).astype(float)
    df['Spot_Price']=spot
    df['Date']=Date
    df['Expiry']=Expiry
    df['Time']=Time
    df['ceper']=(df['CALL_OI']/df['CALL_OI'].max())*100
    df['peper']=(df['PUT_OI']/df['PUT_OI'].max())*100
    df['cvper']=(df['CALL_VOLUME']/df['CALL_VOLUME'].max())*100
    df['pvper']=(df['PUT_VOLUME']/df['PUT_VOLUME'].max())*100 
    df['ceprice']= df['STRIKE']+((df['PUT_OI']/df['CALL_OI'])*50)
    df['peprice']= df['STRIKE']-((df['PUT_OI']/df['CALL_OI'])*50)
    df['Sum_CE']=(df['CALL_OI'].sum())
    df['Sum_PE']=(df['PUT_OI'].sum())
    df['Overall_Pcr']=(df['Sum_PE'] / df['Sum_CE'])
    main_data=df.copy()[['CALL_OI','CALL_CHNG','CALL_VOLUME','PUT_VOLUME', 'PUT_CHNG','PUT_OI', 'CALL_LTP', 'PUT_LTP','ceper','peper','cvper','pvper','ceprice','peprice','Sum_CE','Sum_PE','Overall_Pcr','Time','Expiry','Date','Spot_Price']]
    name=str(df.Time.iloc[0]).replace('.','_')
    name1=str('_data')
    name2=str('.csv')
    fullname=name+name1+name2
    st.write(fullname)
    # download button
    # if code does not work remove below line
    df101=df[['CALL_OI','CALL_CHNG','CALL_VOLUME','PUT_VOLUME', 'PUT_CHNG','PUT_OI', 'CALL_LTP', 'PUT_LTP','ceper','peper','cvper','pvper','ceprice','peprice','Sum_CE','Sum_PE','Overall_Pcr','Time','Expiry','Date','Spot_Price']]
    csv=df101.to_csv().encode("utf-8")
    st.download_button(label="Download CSV", data=csv, file_name=fullname, mime="text/csv",icon=":material/download:", key="donw1") 
    st.write(main_data)
    spot1 =df.Spot_Price[0]
    if spot1>0:
      round1 =spot1.round(-2)
      put=df['Sum_PE'].iloc[0]
      call=df['Sum_CE'].iloc[0]
      pcr= df['Overall_Pcr'].iloc[0]
      st.write(put, call,pcr)
            
      upperval=st.number_input("upper value", step=100, value=500, key='up1')
      strike1= round1-upperval
      strike2 = round1+upperval
      df=df[df.STRIKE.between(strike1,strike2)]
      df1=df.copy()
      df2=df1.style.apply(highlight_second_highest,subset=['CALL_OI','PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG']).map(color_two, subset=['STRIKE']).format(precision=0).map(color_all, subset=['ceper','peper','Spot_Price', 'ceprice', 'peprice', 'cvper','pvper']).format(precision=2, subset=['Time']).map(color_background_red, subset=['CHNG', 'CHNG.1']).map(color_all, subset=['CALL_LTP', 'PUT_LTP'])    
      st.dataframe(df2, hide_index=True, width =600, height=600, column_order=['Time','CALL_LTP','CHNG','ceper','CALL_CHNG','CALL_OI','CALL_VOLUME','cvper','ceprice','STRIKE','peprice','pvper','PUT_VOLUME','PUT_OI','PUT_CHNG','peper','PCRval', 'Spot_Price','CHNG.1','PUT_LTP'], use_container_width=True)
                    
#     bar chart coding
      df2=df.copy()
      option_list=df2.STRIKE.unique()
      col1, col2=st.columns(2)
      with col1:
        list1=st.selectbox("Select Strike1", options=option_list, index=0, key='list01', width=200)
      with col2:
        list2=st.selectbox("Select Strike2", options=option_list, index=len(option_list)-2, key='list22', width=200)
      col1, col2,col3=st.columns(3)
      with col1:
        data_refined=df2[df2.STRIKE.between(list1, list2)]
        st.bar_chart(data_refined, x='STRIKE', y=['CALL_VOLUME', 'PUT_VOLUME'], color=['#B62626', '#26B669'], stack=False)
      with col2:
          st.bar_chart(data_refined, x='STRIKE', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'], stack=False)         
      with col3:
          st.bar_chart(data_refined, x='STRIKE', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'], stack=False)

# adding data to master file 
with tab2:
    col1, col2=st.columns(2)
    with col1:
        data_one = st.file_uploader("csv file upload", key='upload101',accept_multiple_files=True)
    with col2:
      data_two = st.file_uploader("upload_master file", key='upload102')
    if data_one!=None and data_two!=None:
        df_list = [pd.read_csv(f) for f in data_one]
        combined_df = pd.concat(df_list, ignore_index=True)
        data2=pd.read_csv(data_two)
        merged_df = pd.concat([combined_df,data2], ignore_index=True).sort_values(by=['Time'], ascending=False)
        # download button
        name2=str(merged_df.Time.iloc[0]).replace('.','_')
        name21=str('_master_File')
        name22=str('.csv')
        fullname1=name2+name21+name22
        st.write(fullname1)
        # if code does not work remove below line
        merged_df1=merged_df[['CALL_OI','CALL_CHNG','CALL_VOLUME','PUT_VOLUME', 'PUT_CHNG','PUT_OI', 'CALL_LTP', 'PUT_LTP','ceper','peper','cvper','pvper','ceprice','peprice','Sum_CE','Sum_PE','Overall_Pcr','Time','Expiry','Date','Spot_Price']]
        csv1=merged_df1.to_csv().encode("utf-8")
        st.download_button(label="Download master CSV", data=csv1, file_name=fullname1, mime="text/csv",icon=":material/download:",key="donw223")
        st.write(merged_df1)        

with tab3:
    newdata = st.file_uploader("csv file upload", key='newdata1')
    if newdata is not None:
        newdata=pd.read_csv(newdata, encoding='latin_1')
        timeopt = newdata.Time.unique()
        timesel=st.selectbox("select time from here", key='select1', options=timeopt)
        newdata0=newdata[newdata.Time==timesel]
        st.write(newdata0)
        newdata1=newdata0.reindex()
        st.write(newdata1)
        spot2 =newdata1.Spot_Price.iloc[0]
        if spot2>0:
            round1 =spot2.round(-2)
            strike1= round1-500
            strike2 = round1+500
            st.write(strike1,strike2, spot2)
            st.write(newdata1)
            newdata2=newdata1[newdata1.STRIKE.between(strike1,strike2)]
            df2=newdata2.style.apply(highlight_second_highest,subset=['CALL_OI','PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG']).map(color_two, subset=['STRIKE']).format(precision=0).map(color_all, subset=['ceper','peper','Spot_Price', 'ceprice', 'peprice', 'cvper','pvper']).format(precision=2, subset=['Time']).map(color_background_red, subset=['CHNG', 'CHNG.1']).map(color_all, subset=['CALL_LTP', 'PUT_LTP'])
            st.dataframe(df2, hide_index=True, width =600, height=600, column_order=['Time','CALL_LTP','CHNG','ceper','CALL_CHNG','CALL_OI','CALL_VOLUME','cvper','ceprice','STRIKE','peprice','pvper','PUT_VOLUME','PUT_OI','PUT_CHNG','peper','PCRval', 'Spot_Price', 'CHNG.1','PUT_LTP'], use_container_width=True)
    
            strikes = list(newdata.STRIKE.unique())
            col1, col2, col3, col4, col5, col6=st.columns(6)
            spot_price = newdata1.Spot_Price.iloc[0].round(-2)
            tel1_strike=strikes.index(spot_price-200)
            tel2_strike=strikes.index(spot_price-100)
            tel3_strike=strikes.index(spot_price-50)
            tel4_strike=strikes.index(spot_price)
            tel5_strike=strikes.index(spot_price+50)
            tel6_strike=strikes.index(spot_price+100)
            st.write(spot_price, tel6_strike)
            with col1:
                chart_strike= st.selectbox("select the begning Time", options=strikes, key='chart1', index=tel1_strike)
                detail=newdata[newdata['STRIKE']==chart_strike][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
                st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])
                chart_chng= st.selectbox("select the begning Time", options=strikes, key='chart_chng1', index=tel1_strike)
                chart_chng_data=newdata[newdata['STRIKE']==chart_chng][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
                st.line_chart(chart_chng_data, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])
            with col2:
                chart_strike2= st.selectbox("select the begning Time", options=strikes, key='chart2', index=tel2_strike)
                detail=newdata[newdata['STRIKE']==chart_strike2][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
                st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])
                chart_chng2= st.selectbox("select the begning Time", options=strikes, key='chart_chng2', index=tel2_strike)
                chart_chng_data2=newdata[newdata['STRIKE']==chart_chng2][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
                st.line_chart(chart_chng_data2, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])  
            with col3:
               chart_strike3= st.selectbox("select the begning Time", options=strikes, key='chart3', index=tel3_strike)
               detail=newdata[newdata['STRIKE']==chart_strike3][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
               st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])
               chart_chng3= st.selectbox("select the begning Time", options=strikes, key='chart_chng3', index=tel3_strike)
               chart_chng_data3=newdata[newdata['STRIKE']==chart_chng3][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
               st.line_chart(chart_chng_data3, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])

            with col4:
                chart_strike4= st.selectbox("select the begning Time", options=strikes, key='chart4', index=tel4_strike)
                detail=newdata[newdata['STRIKE']==chart_strike4][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
                st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])
                chart_chng4= st.selectbox("select the begning Time", options=strikes, key='chart_chng4', index=tel4_strike)
                chart_chng_data4=newdata[newdata['STRIKE']==chart_chng4][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
                st.line_chart(chart_chng_data4, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])
            with col5:
                chart_strike5= st.selectbox("select the begning Time",options=strikes, key='chart5', index=tel5_strike)
                detail=newdata[newdata['STRIKE']==chart_strike5][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
                st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])
                chart_chng5= st.selectbox("select the begning Time",options=strikes, key='chart_chng5', index=tel5_strike)
                chart_chng_data5=newdata[newdata['STRIKE']==chart_chng5][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
                st.line_chart(chart_chng_data5, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])
            with col6:
                chart_strike6= st.selectbox("select the begning Time", options=strikes, key='chart6', index=tel6_strike)
                detail=newdata[newdata['STRIKE']==chart_strike6][['Time','CALL_OI','PUT_OI']].sort_values(by='Time', ascending=False)
                st.line_chart(detail, x='Time', y=['CALL_OI', 'PUT_OI'], color=['#B62626', '#26B669'])
                chart_chng6= st.selectbox("select the begning Time",options=strikes, key='chart_chng6', index=tel6_strike)
                chart_chng_data6=newdata[newdata['STRIKE']==chart_chng6][['Time','CALL_CHNG','PUT_CHNG']].sort_values(by='Time', ascending=False)
                st.line_chart(chart_chng_data6, x='Time', y=['CALL_CHNG', 'PUT_CHNG'], color=['#B62626', '#26B669'])
        
        def background(val):
            max=val.max()
            seven=max*0.75
            mhalf=max/2
            if val<mhalf:
                return ['background-color:red']
            elif val<seven:
                return ['background-color:green']
            else:
                return ['background-color:yellow']
            
        col1, col2, col3=st.columns(3)
        with col1:
            strike_0= st.selectbox("select the begning STRIKE", options=strikes, key='strike0', index=tel3_strike)
            strike_detail0 =newdata[newdata['STRIKE']==strike_0][['Time','CALL_OI', 'PUT_OI','CALL_CHNG', 'PUT_CHNG']]
            st.dataframe(strike_detail0,hide_index=True)
        with col2:
            strike_one= st.selectbox("select the begning STRIKE", options=strikes, key='strike', index=tel4_strike)
            strike_detail =newdata[newdata['STRIKE']==strike_one][['Time','CALL_OI', 'PUT_OI', 'CALL_CHNG', 'PUT_CHNG']]
            st.dataframe(strike_detail, hide_index=True)
        with col3:
            strike_1= st.selectbox("select the begning STRIKE", options=strikes, key='strike1', index=tel5_strike)
            strike_detail1 =newdata[newdata['STRIKE']==strike_1][['Time','CALL_OI', 'PUT_OI','CALL_CHNG', 'PUT_CHNG']]
            st.dataframe(strike_detail1,hide_index=True)   
  
# adding data to master file 

with tab4:
    st.write("codes for testing anything")
    
        

            
    



    
       
    
  


















































