from ai_class import ai_handler
from app_render import app_renderer
import constants as constants
import toolbox

import streamlit as st

def accept_params():
    port = st.text_input(constants.PORT_PROMPT, help=":)", key="port").strip()
    ip = st.text_input(constants.IP_PROMPT, key="ip").strip()
    system_message = st.text_input(constants.SYSTEM_MESSAGE_PROMPT, key="system_message", value=constants.SYSTEM_MESSAGE_DEFAULT).strip()

    return ip, port, system_message

def get_init_message():
    with open(constants.INIT_MESSAGE_PATH, "r", encoding="utf-8") as f:
        init_message = f.read()

    return init_message

def run_ai(ip, port, system_message, user_input, chat, settings, render, selected_model):
    with st.spinner(constants.SESSION_START_SPINNER, show_time=True):
            try:
                aihandler = ai_handler(
                    ip=ip,
                    port=port,
                    system_message=system_message,
                    user_input=user_input,
                    chat=chat,
                    settings=settings,
                    render=render,
                    selected_model=selected_model
                )
                aihandler.run()

            except Exception as e:
                st.error(e, title="ERROR!")
                return
            
def get_render(ip, port, system_message, init_message):
    with st.spinner(constants.RENDER_START_SPINNER, show_time=True):
        try:
            render = app_renderer(ip, port, system_message, init_message)
            
            return render
        
        except Exception as e:
            st.error(e, title="RENDERER FAILED TO LOAD!")
            return

def handle():
    toolbox.init_db()
    ip, port, system_message = accept_params()
    init_message = get_init_message()

    if not ip or not port:
        st.warning(constants.IP_PORT_WARNING_PROMPT)
        return
    
    st.session_state.setdefault("started", False)

    if st.button("启动AI对话终端"):
        st.session_state.started = True
        
    if st.session_state.started:
        render = get_render(ip, port, system_message, init_message)
        render.startup_checks()

        run_ai(ip, port, system_message, render.user_input, render.chat, render.settings, render, render.selected_model)
        
def __main__():
    handle()

if __name__ == "__main__":
    __main__()
