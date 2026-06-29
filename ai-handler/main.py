from ai_class import ai_handler
import constants as constants
import toolbox

import streamlit as st


def render_page():
    st.set_page_config(page_title=constants.PAGE_TITLE, layout="wide")
    st.title(constants.HEADING)
    
def accept_params():
    port = st.text_input(constants.PORT_PROMPT, help=":)", key="port").strip()
    ip = st.text_input(constants.IP_PROMPT, key="ip").strip()
    system_message = st.text_input(constants.SYSTEM_MESSAGE_PROMPT, key="system_message", value=constants.SYSTEM_MESSAGE_DEFAULT).strip()

    return ip, port, system_message

def run_ai(ip, port, system_message):
    with st.spinner(constants.SESSION_START_SPINNER, show_time=True):
            try:
                aihandler = ai_handler(
                    ip=ip,
                    port=port,
                    models=constants.MODELS,
                    system_message=system_message
                )
                aihandler.run()

            except Exception as e:
                st.error(e, title="ERROR!")
                return

def handle():
    render_page()
    toolbox.init_db()
    ip, port, system_message = accept_params()

    if not ip or not port:
        st.warning(constants.IP_PORT_WARNING_PROMPT)
        return
    
    st.session_state.setdefault("started", False)

    if st.button("启动AI对话终端"):
        st.session_state.started = True
        
    if st.session_state.started:
        run_ai(ip, port, system_message)
        
def __main__():
    handle()

if __name__ == "__main__":
    __main__()
