from AIclass import AIHandler
import streamlit as st
import constants as constants
import toolbox

st.set_page_config(page_title="AI HANDLER", layout="wide")
st.title("AI HANDLER")
toolbox.init_db()

port = st.text_input("请输入端口号：", help=":)", key="port").strip()
ip = st.text_input("请输入IP地址：", key="ip").strip()
system_message = st.text_input("请输入系统消息（可留空）：", key="system_message", value="你是一个有帮助的AI助手。").strip()

if not ip or not port:
    st.warning("IP地址和端口号不能为空！")
else:
    if 'started' not in st.session_state:
        st.session_state.started = False

    if st.button("启动AI对话终端"):
        st.session_state.started = True
    
    if st.session_state.started:
        with st.spinner("正在启动控制台对话程序，请稍等...", show_time=True):
            try:
                aihandler = AIHandler(
                    ip=ip,
                    port=port,
                    models=constants.MODELS,
                    system_message=system_message
                )
                aihandler.run()

            except Exception as e:
                st.error(e, title="ERROR!")
                exit(0)