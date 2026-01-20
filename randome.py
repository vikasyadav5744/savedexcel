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

expirynifty=dt.date(2026,1,27)      

def color_01(row):
    # Check the 'chang' column to decide the color
    if row['chang'] > 0:
        return ['background-color: red; color: black'] * len(row)
    elif row['chang'] < 0:
        return ['background-color: green; color: black'] * len(row)
    return [''] * len(row)

def apply_style(row):
    # Check the 'chang' column to decide the color 
    if row['val'] > 0:
        return ['background-color: green; color: black']
    elif row['val'] < 0:
        return ['background-color: pink; color: black'] 
    elif row['val'] == 0:
        return ['background-color: light-green; color: black'] 
    return [''] 


def shifting(val):
    if val >0:
        return 'shifted from top to bottom'
    elif val < 0:
        return 'shifted from bottom to top'
    elif val == 0:
        return 'stable / strong'

def sevent5(df, s):
    spot=df['Spot_Price'].iloc[0]
    upper = spot + 150
    lower  = spot - 150
    maxs = int(df.loc[ df[s] == df[s].max(), 'STRIKE'].iloc[0])
    try:
        above_seven = int(df.loc[(df[s] >= (df[s].max()*0.75)) & (df[s] == (df[s].nlargest(2).iloc[-1])), 'STRIKE'].iloc[0])
        if above_seven!=None:
            return above_seven 
        else:
            return 0  
    except:
        return 0

# defining function for WTT and WTB

def smax12(df, s):
    spot=df['Spot_Price'].iloc[0]
    upper = spot + 200
    lower  = spot - 200
    maxs = int(df.loc[ df[s] == df[s].max(), 'STRIKE'].iloc[0])
    try:
        above_seven = int(df.loc[(df[s] >= (df[s].max()*0.75)) & (df[s] == (df[s].nlargest(2).iloc[-1])), 'STRIKE'].iloc[0])
        if (spot > maxs)& (above_seven !=0)&(above_seven > maxs):
            return "WTT " + "- at " + ' ' + str(above_seven) + ' '+ 'from'+ ' '+ str(maxs)
        elif (spot > maxs)& (above_seven !=0)&(above_seven > maxs) &(spot < above_seven):
            return "WTT " + "- at " + ' ' + str(above_seven)+ ' '+ 'from'+ ' '+ str(maxs)
        elif (spot > maxs)& (above_seven !=0)&(above_seven > maxs) &(spot > above_seven):
            return "WTT " + "- at " + ' ' + str(above_seven) + ' '+ 'from'+ ' '+ str(maxs)
        elif (spot < maxs)& (above_seven !=0)&(above_seven > maxs) &(spot < above_seven):
            return "WTT " + "- at " + ' ' + str(above_seven) + ' '+ 'from'+ ' '+ str(maxs)
        # WTB scenerioes 
        elif (spot < maxs)& (above_seven !=0)&(above_seven < maxs):
            return "WTB " + "- at " + ' ' + str(above_seven) + ' '+ 'from'+ ' '+ str(maxs)
        elif (spot > maxs)& (above_seven !=0)&(above_seven< maxs):
            return "WTB " + "- at " + ' ' + str(above_seven) + ' '+ 'from'+ ' '+ str(maxs)
        elif (spot < maxs)& (above_seven !=0)&(spot < above_seven):
            return "WTB " + "- at " + ' ' + str(above_seven) + ' '+ 'from'+ ' '+ str(maxs)
    except:
        return "strong" + "- at " + ' ' + str(maxs)  


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
  col1, col2, col3, col4, col5, col6, col7=st.columns(7)
  with col1:
    upperval=st.number_input("upper value", step=100, value=500, key='up1')
  with col2:
    Date=st.date_input("Date", format="DD/MM/YYYY", width='stretch', key='val2')
  with col3:
    Expiry=st.date_input("Expiry",format="DD/MM/YYYY", width='stretch', key='val3', value=expirynifty)
  with col4:
    spot=int(st.number_input("Please give spot price", key='spot1', value=26000, step=100))
  with col5:
    Time=st.number_input("Please give time", key='time1')
  if data!=None:
    df=pd.read_csv(data, skiprows=1, usecols=['OI', 'CHNG IN OI', 'VOLUME', 'IV', 'LTP', 'CHNG','BID QTY', 'BID', 'ASK', 'ASK QTY', 'STRIKE', 'BID QTY.1', 'BID.1','ASK.1', 'ASK QTY.1', 'CHNG.1', 'LTP.1','IV.1', 'VOLUME.1','CHNG IN OI.1', 'OI.1'])
    df=df.rename(columns={'CHNG':'CHNG','CHNG.1':'CHNG.1','OI':'CALL_OI','CHNG IN OI':'CALL_CHNG','VOLUME':'CALL_VOLUME','VOLUME.1':'PUT_VOLUME', 'CHNG IN OI.1':'PUT_CHNG','OI.1':'PUT_OI', 'LTP':'CALL_LTP', 'LTP.1':'PUT_LTP'})
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
    df['volceprice']= df['STRIKE']+((df['PUT_VOLUME']/df['CALL_VOLUME'])*50)
    df['volpeprice']= df['STRIKE']-((df['PUT_VOLUME']/df['CALL_VOLUME'])*50)
    df['Sum_CE']=(df['CALL_OI'].sum())
    df['Sum_PE']=(df['PUT_OI'].sum())
    df['Overall_Pcr']=(df['Sum_PE'] / df['Sum_CE'])
    
    # WTT status 
    df['ce_status'] = (smax12(df, 'CALL_OI'))
    df['volce_status'] = smax12(df, 'CALL_VOLUME')
    df['pe_status'] = smax12(df, 'PUT_OI')
    df['volpe_status'] = smax12(df, 'PUT_VOLUME')
    # support and ressistance status calculation
    df['cemaxstr'] =int(df.loc[(df['CALL_OI'] == df['CALL_OI'].max()), 'STRIKE'].iloc[0])
    df['pemaxstr'] =int(df.loc[(df['PUT_OI'] == df['PUT_OI'].max()), 'STRIKE'].iloc[0])
    df['volcemaxstr'] =int(df.loc[(df['CALL_VOLUME'] == df['CALL_VOLUME'].max()), 'STRIKE'].iloc[0])
    df['volpemaxstr'] =int(df.loc[(df['PUT_VOLUME'] == df['PUT_VOLUME'].max()), 'STRIKE'].iloc[0])
    df['cesevent5str'] =sevent5(df, 'CALL_OI')
    df['volcesevent5str']  = sevent5(df, 'CALL_VOLUME')
    df['pesevent5str'] = sevent5(df, 'PUT_OI')
    df['volpesevent5str'] =sevent5(df, 'PUT_VOLUME')  
    name=str(df.Time.iloc[0]).replace('.','_')
    name1=str('_data')
    name2=str('.csv')
    fullname=name+name1+name2
    # download button
    # if code does not work remove below line
    df101=df[['IV','IV.1','volcesevent5str','volpesevent5str','pesevent5str','cesevent5str','volpemaxstr','volcemaxstr','pemaxstr','cemaxstr', 'ce_status','volce_status','pe_status','volpe_status','STRIKE','CHNG','CHNG.1','CALL_OI','CALL_CHNG','CALL_VOLUME','PUT_VOLUME', 'PUT_CHNG','PUT_OI', 'CALL_LTP', 'PUT_LTP','ceper','peper','cvper','pvper','ceprice','peprice','Sum_CE','Sum_PE','Overall_Pcr','Time','Expiry','Date','Spot_Price']]
    csv=df101.to_csv().encode("utf-8")
    with col6:
        st.download_button(label="Download CSV", data=csv, file_name=fullname, mime="text/csv",icon=":material/download:", key="donw1", width='stretch') 
    with col7:
        st.write(fullname)
    put=int(df['Sum_PE'].iloc[0])
    call=int(df['Sum_CE'].iloc[0])
    pcr= df['Overall_Pcr'].iloc[0].round(3)
    
    st.write(f"""<div style="background-color: #5e7066; font-size:20px; padding: 25px; border-radius: 20px; text-align: center; margin:10px"> <p> PUT:({put})</p>  <p> PCR: ({pcr}) <p/> CALL: ({call})   </div>""", unsafe_allow_html=True)
    # WTT status 
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">Resistance</div>""", unsafe_allow_html=True)
    with col2:
         st.write(f"""<div style="background-color:#426e4b; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">support</div>""", unsafe_allow_html=True)
    
    #  nature of resistance and support
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px; text-align: center; margin:3px;"> CALLs OI :- {df.ce_status.iloc[0]}</div>""", unsafe_allow_html=True)
    with col2:
        st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">VOLUME :-{df.volce_status.iloc[0]}</div>""", unsafe_allow_html=True)
    with col3:
        st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">Spot :- {df.Spot_Price.iloc[0]}</div>""", unsafe_allow_html=True)
    with col4:
        st.write(f"""<div style="background-color:#426e4b; font-size:20px; padding:5px; border-radius: 5px;text-align: center; margin:3px;">VOLUME :- {df.volpe_status.iloc[0]}</div>""", unsafe_allow_html=True)     
    with col5:
        st.write(f"""<div style="background-color: #68a181; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">PUTs OI:- {df.pe_status.iloc[0]} </div>""", unsafe_allow_html=True)
       

    main_data=df.copy()[['STRIKE','CALL_OI','CALL_CHNG','CALL_VOLUME','PUT_VOLUME', 'PUT_CHNG','PUT_OI', 'CALL_LTP', 'PUT_LTP','ceper','peper','cvper','pvper','ceprice','peprice','Sum_CE','Sum_PE','Overall_Pcr','Time','Expiry','Date','Spot_Price']]
    
    spot1 =df.Spot_Price[0]
    if spot1>0:
      round1 =spot1.round(-2)
      strike1= round1-upperval
      strike2 = round1+upperval
      df=df[df.STRIKE.between(strike1,strike2)]
      df1=df.copy()
      spot2=spot1.round(-2)
      resis_range1= df.loc[df['STRIKE']==spot2, 'volceprice'].iloc[0]
      resis_range2= df.loc[df['STRIKE']==spot2, 'ceprice'].iloc[0]
      support_range1= df.loc[df['STRIKE']==spot2, 'volpeprice'].iloc[0]
      support_range2= df.loc[df['STRIKE']==spot2, 'peprice'].iloc[0]
      st.write('spot:', spot2,'Current Ressistance:', int(resis_range1), '-', int(resis_range2))
      st.write('spot:', spot2,'Current Support:', int(support_range1), '-', int(support_range2))
      st.write("option Chain")
      df2=df1.style.apply(highlight_second_highest,subset=['CALL_OI','PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG']).map(color_two, subset=['STRIKE']).format(precision=0).map(color_all, subset=['ceper','peper','Spot_Price', 'ceprice', 'peprice', 'cvper','pvper']).format(precision=2, subset=['Time']).map(color_background_red, subset=['CHNG', 'CHNG.1']).map(color_all, subset=['CALL_LTP', 'PUT_LTP', 'IV','IV.1'])        #.apply(highlight_row1, axis=1, subset=['STRIKE','ceprice', 'peprice', 'cvper', 'pvper'])    
      st.dataframe(df2, hide_index=True, width ='stretch', height=600, column_order=['Time','IV', 'CALL_LTP','CHNG','ceper','CALL_CHNG','CALL_OI','CALL_VOLUME','cvper','ceprice','STRIKE','peprice','pvper','PUT_VOLUME','PUT_OI','PUT_CHNG','peper','PCRval', 'Spot_Price','CHNG.1','PUT_LTP', 'IV.1'] )
                    
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
    st.write(df)
      
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
        merged_df1=merged_df[['IV','IV.1','volcesevent5str','volpesevent5str','pesevent5str','cesevent5str','volpemaxstr','volcemaxstr','pemaxstr','cemaxstr', 'ce_status','volce_status','pe_status','volpe_status','STRIKE','CHNG','CHNG.1','CALL_OI','CALL_CHNG','CALL_VOLUME','PUT_VOLUME', 'PUT_CHNG','PUT_OI', 'CALL_LTP', 'PUT_LTP','ceper','peper','cvper','pvper','ceprice','peprice','Sum_CE','Sum_PE','Overall_Pcr','Time','Expiry','Date','Spot_Price']]
        csv1=merged_df1.to_csv().encode("utf-8")
        st.download_button(label="Download master CSV", data=csv1, file_name=fullname1, mime="text/csv",icon=":material/download:",key="donw223")
        st.write(merged_df1)        
with tab3:
    newdata = st.file_uploader("csv file upload", key='newdata1')
    if newdata is not None:
        newdata=pd.read_csv(newdata, encoding='latin_1')
        newdata['volceprice']= newdata['STRIKE']+((newdata['PUT_VOLUME']/newdata['CALL_VOLUME'])*50)
        newdata['volpeprice']= newdata['STRIKE']-((newdata['PUT_VOLUME']/newdata['CALL_VOLUME'])*50)
        newdata = newdata.drop_duplicates(subset=['Time', 'STRIKE'], keep='first', ignore_index=True)
        name31=str(newdata.Time.iloc[0]).replace('.','_')
        name32=str('_removed_dupli')
        name33=str('.csv')
        fullname31=name31+name32+name33
        csv12=newdata.to_csv().encode("utf-8")
        st.download_button(label="Download CSV", data=csv12, file_name=fullname31, mime="text/csv",icon=":material/download:", key="donw121") 
                       
        # support and ressistance status calculation
        newdata['cemaxstr'] =int(newdata.loc[(newdata['CALL_OI'] == newdata['CALL_OI'].max()), 'STRIKE'].iloc[0])
        newdata['pemaxstr'] =int(newdata.loc[(newdata['PUT_OI'] == newdata['PUT_OI'].max()), 'STRIKE'].iloc[0])
        newdata['volcemaxstr'] =int(newdata.loc[(newdata['CALL_VOLUME'] == newdata['CALL_VOLUME'].max()), 'STRIKE'].iloc[0])
        newdata['volpemaxstr'] =int(newdata.loc[(newdata['PUT_VOLUME'] == newdata['PUT_VOLUME'].max()), 'STRIKE'].iloc[0])
        newdata['cesevent5str'] =sevent5(newdata, 'CALL_OI')
        newdata['volcesevent5str']  = sevent5(newdata, 'CALL_VOLUME')
        newdata['pesevent5str'] = sevent5(newdata, 'PUT_OI')
        newdata['volpesevent5str'] =sevent5(newdata, 'PUT_VOLUME')
        time_10= newdata.Time.unique()
        
        show=st.checkbox("show shifting")
        mf = newdata.copy()
        mf= mf.sort_values(by=['Time'])
        dropping_dip = mf.drop_duplicates()
        dropping_dip['calloi_status']= dropping_dip['cemaxstr'].diff().fillna(0).apply(shifting)
        dropping_dip['callvol_status']= dropping_dip['volcemaxstr'].diff().fillna(0).apply(shifting)
        dropping_dip['putoi_status']= dropping_dip['pemaxstr'].diff().fillna(0).apply(shifting)
        dropping_dip['putvol_status']= dropping_dip[ 'volpemaxstr'].diff().fillna(0).apply(shifting)
        dropping_dip['call75_status']= dropping_dip[ 'cesevent5str'].diff().fillna(0).apply(shifting)
        dropping_dip['put75_status']= dropping_dip[ 'pesevent5str'].diff().fillna(0).apply(shifting)
        dropping_dip['putvol75_status']= dropping_dip['volpesevent5str'].diff().fillna(0).apply(shifting)
        dropping_dip['callvol75_status']= dropping_dip[ 'volcesevent5str'].diff().fillna(0).apply(shifting)
        dropping_dip =dropping_dip[['Time','cemaxstr','cesevent5str','volcemaxstr','volcesevent5str', 'pemaxstr','pesevent5str','volpemaxstr', 'volpesevent5str','calloi_status', 'callvol_status','putoi_status','putvol_status','call75_status','put75_status','putvol75_status','callvol75_status']].drop_duplicates()
        col1, col2=st.columns(2)
        with col1:
            timeopt=newdata.Time.unique()
            timesel=st.selectbox("select time from here", key='select1', options=timeopt)
            newdata0=newdata[newdata.Time==timesel]
        with col2:     
            upperval1=st.number_input("upper value", step=100, value=500, key='ups1')
        spot2 =newdata0.Spot_Price.iloc[0]
        if spot2>0:
            round1 =spot2.round(-2)
            strike1= round1-upperval1
            strike2 = round1+upperval1
            newdata2=newdata0[newdata0.STRIKE.between(strike1,strike2)]
             # WTT status 
            newdata2['ce_status'] = smax12(newdata2, 'CALL_OI')
            newdata2['volce_status'] = smax12(newdata2, 'CALL_VOLUME')
            newdata2['pe_status'] = smax12(newdata2, 'PUT_OI')
            newdata2['volpe_status'] = smax12(newdata2, 'PUT_VOLUME')
            # market range using vol pcr
            spot2=round1.round(-2)
            resis_range1= newdata2.loc[newdata2['STRIKE']==spot2, 'volceprice'].iloc[0]
            resis_range2= newdata2.loc[newdata['STRIKE']==spot2, 'ceprice'].iloc[0]
            support_range1= newdata2.loc[newdata2['STRIKE']==spot2, 'volpeprice'].iloc[0]
            support_range2= newdata2.loc[newdata2['STRIKE']==spot2, 'peprice'].iloc[0]
            st.write('spot:', spot2,'Current Ressistance:', int(resis_range1), '-', int(resis_range2))
            st.write('spot:', spot2,'Current Support:', int(support_range1), '-', int(support_range2))
            st.write("option Chain")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">Resistance</div>""", unsafe_allow_html=True)
            with col2:
                st.write(f"""<div style="background-color:#426e4b; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">Support</div>""", unsafe_allow_html=True)                    
            #  nature of resistance and support
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px; text-align: center; margin:3px;"> CALLs OI :- {newdata2.ce_status.iloc[0]}</div>""", unsafe_allow_html=True)
            with col2:
                st.write(f"""<div style="background-color: #871c30; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">VOLUME :-{newdata2.volce_status.iloc[0]}</div>""", unsafe_allow_html=True)
            with col3:
                st.write(f"""<div style="background-color: #871c30; font-size:20px: padding: 5px; border-radius: 5px;text-align: center; margin:3px;">Spot :- {newdata2.Spot_Price.iloc[0]} </div>""", unsafe_allow_html=True)
            with col4:
                st.write(f"""<div style="background-color:#426e4b; font-size:20px; padding:5px; border-radius: 5px;text-align: center; margin:3px;">VOLUME :- {newdata2.volpe_status.iloc[0]}</div>""", unsafe_allow_html=True)
            with col5:
                st.write(f"""<div style="background-color: #68a181; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">PUTs OI:- {newdata2.pe_status.iloc[0]} </div>""", unsafe_allow_html=True)

            #  nature of shifting
            col1, col2, col3, col4, = st.columns(4)
            with col1:
                st.write(f"""<div style="background-color: #7dc9aa; font-size:20px; padding: 5px; border-radius: 5px; text-align: center; margin:3px;"> CALLs OI :- {dropping_dip.calloi_status.iloc[0]}</div>""", unsafe_allow_html=True)
            with col2:
                st.write(f"""<div style="background-color: #7dc9aa; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">VOLUME :-{dropping_dip.callvol_status.iloc[0]}</div>""", unsafe_allow_html=True)
            with col3:
                st.write(f"""<div style="background-color: #7dc9aa; font-size:20px; padding: 5px; border-radius: 5px;text-align: center; margin:3px;">PUTs OI:- {dropping_dip.putoi_status.iloc[0]} </div>""", unsafe_allow_html=True)
            with col4:
                st.write(f"""<div style="background-color:#7dc9aa; font-size:20px; padding:5px; border-radius: 5px;text-align: center; margin:3px;">VOLUME :- {dropping_dip.putvol_status.iloc[0]}</div>""", unsafe_allow_html=True)
 
            df2=newdata2.style.apply(highlight_second_highest,subset=['CALL_OI','PUT_OI','CALL_VOLUME','PUT_VOLUME','CALL_CHNG','PUT_CHNG']).map(color_two, subset=['STRIKE']).format(precision=0).map(color_all, subset=['ceper','peper','Spot_Price', 'ceprice', 'peprice', 'cvper','pvper']).format(precision=2, subset=['Time']).map(color_background_red, subset=['CHNG', 'CHNG.1']).map(color_all, subset=['CALL_LTP', 'PUT_LTP','IV','IV.1'])      #.apply(highlight_row1, axis=1, subset=['STRIKE','ceprice', 'peprice', 'cvper', 'pvper'])
            st.dataframe(df2, hide_index=True, width ='stretch', height=600, column_order=['Time','IV','CALL_LTP','CHNG','ceper','CALL_CHNG','CALL_OI','CALL_VOLUME','cvper','ceprice','STRIKE','peprice','pvper','PUT_VOLUME','PUT_OI','PUT_CHNG','peper','PCRval', 'Spot_Price','CHNG.1','PUT_LTP','IV.1'],)
            if show==True:
                st.write(dropping_dip) 
            def top12(df, val):
                current= df[val].iloc[-1]
                previous= df[val].iloc[-2]
                if (current == previous):
                    return "stable at "+ ' ' + str(current) 
                elif (current != previous) & (current < previous):
                    return "shifted from top to bottom" 
                elif (current != previous) & (current > previous):
                    return "shifted from bottom to top" 
                fus={'time':[8.20,8.40,9.15,9.36,10.30], 'call':[26000, 26300,25400,26000,29000]}
                fus1= pd.DataFrame(fus)
                #fus1= fus1.sort_values(by=['time'], ascending=False)
                fus1['status']= top12(fus1,'call')
                fus1['chang']= fus1['call'].diff().fillna(0)
                fus1['shift'] = fus1.chang.apply(shifting)
                st.write(fus1)
                # 3. Display in Streamlit
                st.dataframe(fus1.style.apply(apply_style, axis=1))
           
            strikes = list(newdata.STRIKE.unique())
            col1, col2, col3, col4, col5, col6=st.columns(6)
            spot_price = newdata0.Spot_Price.iloc[0].round(-2)
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
        
        def background(df):
            macs=[''] * len(df)
            if df['ce_chang'] < 0:
                macs[0] = ['background-color:red; color: black']
            elif df['ce_chang'] > 0:
                macs[0] =  ['background-color:green; color: black']
            return macs
            
        col1, col2, col3=st.columns(3)
        with col1:
            strike_0= st.selectbox("select the begning STRIKE", options=strikes, key='strike0', index=tel3_strike)
            strike_detail0 =newdata[newdata['STRIKE']==strike_0][['Time','CALL_OI', 'PUT_OI','CALL_CHNG', 'PUT_CHNG']]
            strike_detail0 = strike_detail0.sort_values(by=['Time'])
            strike_detail0['ce_chang'] =strike_detail0['CALL_OI'].diff().fillna(0)
            strike_detail0['pe_chang'] =strike_detail0['PUT_OI'].diff().fillna(0)
            strike_detail0['ce_intra'] =strike_detail0['CALL_CHNG'].diff().fillna(0)
            strike_detail0['pe_intra'] =strike_detail0['PUT_CHNG'].diff().fillna(0)
            strike_detail0 = strike_detail0.sort_values(by=['Time'], ascending= False)
            #strike_detail0= strike_detail0.style.apply(background, axis=1)
            st.dataframe(strike_detail0,hide_index=True, column_order=['Time','CALL_OI','ce_chang','PUT_OI', 'pe_chang', 'CALL_CHNG','ce_intra','PUT_CHNG','pe_intra'])
        with col2:
            strike_one= st.selectbox("select the begning STRIKE", options=strikes, key='strike', index=tel4_strike)
            strike_detail =newdata[newdata['STRIKE']==strike_one][['Time','CALL_OI', 'PUT_OI', 'CALL_CHNG', 'PUT_CHNG']]
            strike_detail = strike_detail.sort_values(by=['Time'])
            strike_detail['ce_chang'] =strike_detail['CALL_OI'].diff().fillna(0)
            strike_detail['pe_chang'] =strike_detail['PUT_OI'].diff().fillna(0)
            strike_detail['ce_intra'] =strike_detail['CALL_CHNG'].diff().fillna(0)
            strike_detail['pe_intra'] =strike_detail['PUT_CHNG'].diff().fillna(0)
            strike_detail = strike_detail.sort_values(by=['Time'], ascending= False)
            st.dataframe(strike_detail, hide_index=True,  column_order=['Time','CALL_OI','ce_chang','PUT_OI', 'pe_chang', 'CALL_CHNG','ce_intra','PUT_CHNG','pe_intra'] )
        with col3:
            strike_1= st.selectbox("select the begning STRIKE", options=strikes, key='strike1', index=tel5_strike)
            strike_detail1 =newdata[newdata['STRIKE']==strike_1][['Time','CALL_OI', 'PUT_OI','CALL_CHNG', 'PUT_CHNG']]
            strike_detail1 = strike_detail1.sort_values(by=['Time'])
            strike_detail1['ce_chang'] =strike_detail1['CALL_OI'].diff().fillna(0)
            strike_detail1['pe_chang'] =strike_detail1['PUT_OI'].diff().fillna(0)
            strike_detail1['ce_intra'] =strike_detail1['CALL_CHNG'].diff().fillna(0)
            strike_detail1['pe_intra'] =strike_detail1['PUT_CHNG'].diff().fillna(0)
            strike_detail1 = strike_detail1.sort_values(by=['Time'], ascending= False)  
            st.dataframe(strike_detail1,hide_index=True, column_order=['Time','CALL_OI','ce_chang','PUT_OI', 'pe_chang', 'CALL_CHNG','ce_intra','PUT_CHNG','pe_intra']  )   
        st.write( "for getting clear view about market direction")
        pcr_calc = newdata[['Time', 'Sum_PE', 'Sum_CE', 'Overall_Pcr']].drop_duplicates()
        col1, col2=st.columns(2)
        with col1:
            st.write( pcr_calc)
        with col2:
            st.line_chart(pcr_calc, x='Time', y=['Overall_Pcr'], color=['#26B669'])
        L123 =newdata[['Time','ce_status', 'volce_status', 'Spot_Price','pe_status','volpe_status' ]].drop_duplicates()
        st.write(L123)
        
        
# adding data to master file 

with tab4:
    st.write("please upload file in historical tab")
    # st.write(newdata[['Time','ce_status', 'volce_status', 'Spot_Price','pe_status','volpe_status' ]])
    col1, col2=st.columns(2)
    with col1:
        but01 = st.link_button("Option Chain", url="https://www.nseindia.com//option-chain", type='primary', use_container_width=True)
    with col2:
        but02 = st.link_button("Sahi Platform", url="https://sahi.com/", type='primary',  use_container_width=True) 
    
       
