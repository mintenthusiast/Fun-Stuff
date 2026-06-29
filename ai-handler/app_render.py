import streamlit as st
import json
import ast

import toolbox
import constants as constants

class app:
    def __init__(self, ip, port, system_message, init_message):
        self.settings = st.session_state
        self.ip = ip
        self.port = port
        self.system_message = system_message
        self.init_message = init_message
        self.user_input = None
        self.chat = None
        self.selected_model = None
        self.url = toolbox.get_url(ip, port)

    def startup_checks(self):
        self.init_keys()
        st.set_page_config(page_title=constants.PAGE_TITLE, layout="wide")
        st.title(constants.HEADING)

        toolbox.connection_check(self.url)
        self.selected_model = toolbox.prompt_and_check(constants.MODELS)

    def render(self, history=""):
        st.title(constants.SUBHEADING)
        st.caption(constants.SUBHEADING_CAPTION + f"**{self.selected_model}**")
        st.divider()

        left, right = st.columns([4, 1], gap="large")

        self.user_input = st.chat_input(constants.CHAT_INPUT_PROMPT)
        self.chat = self.render_chat(left, history)
        self.render_tools(right, history)         
        
        return self.chat, self.user_input, self.selected_model, self.settings
    
    def init_keys(self):
        if "chat_history" not in self.settings:
            self.settings.chat_history = [
                {"role": "system", "content": self.system_message},
                {"role": "system", "content": self.init_message}
            ]

        if "streaming" not in self.settings:
            self.settings.streaming = False

        if "upload_key" not in self.settings:
            self.settings.upload_key = 0

        if "max_tokens" not in self.settings:
            self.settings.max_tokens = constants.DEFAULT_MAX_TOKENS

        if "used_tokens" not in self.settings:
            self.settings.used_tokens = 0

        if "temperature" not in self.settings:
            self.settings.temperature = constants.DEFAULT_TEMPERATURE
        
        if "top_p" not in self.settings:
            self.settings.top_p = constants.DEFAULT_TOP_P

    def render_chat(self, loc, history):      
        with loc:
            chat = st.container(height=650)

            with chat:
                for message in history[2:]:
                    if message["role"] in constants.ROLES:
                        with st.chat_message(message["role"]):
                            st.markdown(f"{constants.ROLES[message["role"]]}{message["content"]}")
                            if message["role"] == "assistant":
                                usage = message.get("usage")
                                if usage and usage.get("total_tokens"):
                                    total = usage["total_tokens"]
                                    st.info(f"{constants.TOKENS_USED_PROMPT}{total}")

                    elif message["role"] == "system":
                        if message["content"].startswith("E"):
                            st.error(message["content"])
                        elif message["content"].startswith("I"):
                            st.info(message["content"])
                        elif message["content"].startswith("W"):
                            st.warning(message["content"])

            return chat

    def render_tools(self, loc, history):
        with loc:
            st.subheader("工具盒")

            with st.expander(constants.UPPER_EXPANDER_TITLE, expanded=False):
                upload_history = st.file_uploader(
                    constants.FILE_UPLOADER_PROMPT,
                    type="jsonl",
                    key=f"upload_history_{self.settings.upload_key}"
                )

                if st.button(constants.FILE_UPLOADER_CONFIRMATION_PROMPT, use_container_width=True):
                    if upload_history is None:
                        st.rerun()
                        
                    try:
                        history = [{"role": "system", "content": self.system_message},
                                    {"role": "system", "content": self.init_message}]

                        for line in upload_history.getvalue().decode("utf-8").splitlines():
                            line = line.strip()

                            if line:
                                history.append(ast.literal_eval(line))

                        self.history = history
                        self.settings.chat_history = history
                        self.settings.upload_key += 1

                        st.success(constants.FILE_UPLOADER_SUCCESS_PROMPT)
                        st.rerun()

                    except json.JSONDecodeError as e:
                        st.error(constants.FILE_UPLOADER_JSON_FORMAT_ERROR_PROMPT + f"{e}")

                    except Exception as e:
                        st.error(constants.FILE_UPLOADER_OTHER_ERROR_PROMPT + f"{e}")

                st.download_button(
                    constants.FILE_DOWNLOADER_PROMPT,
                    data=toolbox.package_data(history),
                    file_name="streamlit_chat_history.jsonl",
                    use_container_width=True,
                )

                if st.button(constants.FILE_PREVIEWER_PROMPT, use_container_width=True):
                    self.check_history(history)
 
        
            with st.expander(constants.LOWER_EXPANDER_TITLE, expanded = False):
                st.slider(constants.SLIDER_MAX_TOKENS_PROMPT + f"{self.settings.max_tokens}", value=self.settings.max_tokens, key="max_tokens", max_value=5000)
                st.write(constants.SLIDER_USED_TOKENS_PROMPT + f"{self.settings.used_tokens} tokens")

                st.slider(constants.SLIDER_TEMPERATURE_PROMPT + f"{self.settings.temperature}", value=self.settings.temperature, key="temperature", max_value=2.00, min_value=0.01, step=0.01)
                st.slider(constants.SLIDER_TOP_P_PROMPT + f"{self.settings.top_p}", value=self.settings.top_p, key="top_p", min_value=0.01, max_value=1.00, step=0.01)
            
                st.toggle("Streaming", key="streaming")

                if st.button(constants.RESET_SESSION_PROMPT):
                    self.confirm_reset()

    @st.dialog(constants.FILE_PREVIEWER_DIALOGUE)
    def check_history(self, history):
        for entry in history[2:]:
            st.write(entry)

    @st.dialog("NYANCAT")
    def nyancat(self):
        try:
            st.video("https://www.youtube.com/watch?v=2yJgwwDcgV8")
        except Exception as e:
            st.exception(f"ERROR: {e}")

    def reset_session_state(self):
        for key in constants.VALUE_KEYS:
            del self.settings[key]

    @st.dialog(constants.RESET_CONFIRMATION_DIALOGUE)
    def confirm_reset(self):
        if st.button(constants.RESET_CONFIRMATION_PROMPT):
            self.reset_session_state()
            st.rerun()


