import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from core import process, ProviderError
from storage import history

load_dotenv()
st.set_page_config(page_title='SmartRoute',page_icon='🧭',layout='wide')
st.title('🧭 SmartRoute')
st.caption('An explainable model-routing baseline for comparing speed, cost and answer quality.')
with st.sidebar:
    st.header('Settings')
    demo=st.toggle('Demo mode',value=True,help='Demo responses do not call an AI model and are not real AI answers.')
    mode=st.selectbox('Routing mode',['auto','small','large'],format_func=lambda x:{'auto':'Automatic','small':'Always small','large':'Always large'}[x])
    st.caption('Configure model IDs and optional prices in .env. Demo mode needs no API key.')
    if not demo and not os.getenv('GEMINI_API_KEY'): st.warning('Set GEMINI_API_KEY in .env to use live mode.')
    st.info('Routing is based on simple rules. It can make mistakes; check answers yourself.')
tab1,tab2,tab3=st.tabs(['Ask','History','Evaluate'])
with tab1:
    with st.form('ask'):
        question=st.text_area('Your question',placeholder='For example: What is a Python list?',height=150,max_chars=12000)
        submitted=st.form_submit_button('Send question',type='primary')
    if submitted:
        try:
            with st.spinner('Preparing response...'): r=process(question,mode,demo)
            st.session_state['last_result']=r
        except (ValueError,ProviderError) as e: st.error(str(e))
    if 'last_result' in st.session_state:
        r=st.session_state['last_result']
        st.subheader('Answer'); st.write(r['answer'])
        a,b,c,d=st.columns(4); a.metric('Model',r['model']); b.metric('Tier',r['tier'].title()); c.metric('Response time',f"{r['latency_ms']:.0f} ms"); d.metric('Estimated cost',f"${r['estimated_cost_usd']:.6f}" if r['estimated_cost_usd'] is not None else 'Not configured')
        st.caption('Routing reason: '+r['reason']); st.caption('Tokens: '+str(r['input_tokens'] if r['input_tokens'] is not None else 'unavailable')+' input / '+str(r['output_tokens'] if r['output_tokens'] is not None else 'unavailable')+' output. Cost excludes any usage not captured by these token counts.')
with tab2:
    records=history()
    st.subheader('Recent requests')
    if records:
        st.dataframe(pd.DataFrame(records),hide_index=True,use_container_width=True)
        st.download_button('Download history as CSV',pd.DataFrame(records).to_csv(index=False),'smartroute_history.csv','text/csv')
    else: st.info('No requests saved yet.')
    st.caption('History is stored locally in SQLite. It can contain your questions and responses.')
with tab3:
    st.subheader('How to evaluate')
    st.write('Use the evaluation CSV provided in the project. Ask the same questions in Automatic and Always large modes. Manually judge answer quality, then compare response time and cost. Do not treat demo output as an evaluation.')
    st.write('The project does not include measured accuracy or savings yet. Costs depend on your configured prices and usage, and estimates may omit billable tokens or provider fees.')
