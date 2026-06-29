import requests
import streamlit as st
import json
import ast

import toolbox
import constants as constants

class ai_handler:
    def __init__(self, ip, port, models, system_message):
        self.ip = ip
        self.port = port    
        self.models = models
        self.system_message = system_message
        self.tokens_used = 0
        self.settings = st.session_state

        if (self.ip == "test" and self.port == "test"):
            self.url = "https://google.com"
        else:
            self.url = f"http://{self.ip}:{self.port}/v1/chat/completions"

        with open(constants.INIT_MESSAGE_PATH, "r", encoding="utf-8") as f:
            self.init_message = f.read()

        self.history = []

    def run(self):
        toolbox.connection_check(self.url)
        selected_model = toolbox.prompt_and_check(self.models)

        self.init_keys()

        st.title(constants.SUBHEADING)
        st.caption(constants.SUBHEADING_CAPTION + f"**{selected_model}**")
        st.divider()

        self.history = st.session_state.chat_history
        left, right = st.columns([4, 1], gap="large")

        chat = self.render_chat(left)
        self.render_tools(right)         
        
        user_input = st.chat_input(constants.CHAT_INPUT_PROMPT)

        if user_input:
            model_response = self.process_requests(user_input, chat, selected_model, streaming=st.session_state.streaming)
            toolbox.update_history("assistant", model_response, self.history, self.tokens_used)
            st.session_state.chat_history = self.history
            st.rerun()
            
    def process_requests(self, user_input, chat, selected_model, streaming=False):
        try:
            cmd_status, new_history = toolbox.handle_input(
                self.history,
                user_input,
                self.ip,
                self.port,
                chat
            )

            if cmd_status == 0:
                pass

            elif cmd_status == 1:
                st.success(constants.SESSION_EXIT_PROMPT)
                st.stop()

            elif cmd_status == 2:
                self.history = new_history

                if not streaming:
                    payload = {
                        "model": selected_model,
                        "stream": False,
                        "messages": self.history,
                        "max_tokens": st.session_state.max_tokens,
                        "top_p": st.session_state.top_p,
                        "temperature": st.session_state.temperature
                    }

                    with chat.spinner(constants.CHAT_OUTPUT_THINKING_PROMPT, show_time=True):
                        resp = requests.post(self.url, json=payload, timeout=constants.MAX_WAIT)
                        resp.raise_for_status()
                        res_data = resp.json()

                        model_response = res_data["choices"][0]["message"]["content"]
                        usage = res_data.get("usage")
                        self.get_token_cost(usage)

                        return model_response
                
                if streaming:
                    with chat.spinner(constants.CHAT_OUTPUT_THINKING_PROMPT, show_time=True):   
                        with chat.chat_message("assistant"):
                            model_response = st.write_stream(self.stream(selected_model))

                    return model_response

            if cmd_status == 3:
                self.history = new_history

        except requests.exceptions.RequestException as e:
            chat.error(f"ERROR: {constants.REQUEST_ERROR_PROMPT}{e}")
            toolbox.update_history("system", f"ERROR: {constants.REQUEST_ERROR_PROMPT}{e}", self.history)

        except KeyError as e:
            chat.error(f"ERROR: {constants.KEY_ERROR_PROMPT}{e}")
            toolbox.update_history("system", f"ERROR: {constants.KEY_ERROR_PROMPT}{e}", self.history)

        except Exception as e:
            chat.error(f"ERROR: {constants.SCRIPT_ERROR_PROMPT}{e}")
            toolbox.update_history("system", f"ERROR: {constants.SCRIPT_ERROR_PROMPT}{e}", self.history)

    def init_keys(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "system", "content": self.system_message},
                {"role": "system", "content": self.init_message}
            ]

        if "streaming" not in st.session_state:
            st.session_state.streaming = False

        if "upload_key" not in st.session_state:
            st.session_state.upload_key = 0

        if "max_tokens" not in st.session_state:
            st.session_state.max_tokens = constants.DEFAULT_MAX_TOKENS

        if "used_tokens" not in st.session_state:
            st.session_state.used_tokens = 0

        if "temperature" not in st.session_state:
            st.session_state.temperature = constants.DEFAULT_TEMPERATURE
        
        if "top_p" not in st.session_state:
            st.session_state.top_p = constants.DEFAULT_TOP_P

    def render_chat(self, loc):      
        with loc:
            chat = st.container(height=650)

            with chat:
                for message in self.history[2:]:
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

    def render_tools(self, loc):
        with loc:
            st.subheader("工具盒")

            with st.expander(constants.UPPER_EXPANDER_TITLE, expanded=False):
                upload_history = st.file_uploader(
                    constants.FILE_UPLOADER_PROMPT,
                    type="jsonl",
                    key=f"upload_history_{st.session_state.upload_key}"
                )

                if st.button(constants.FILE_UPLOADER_CONFIRMATION_PROMPT, use_container_width=True):
                    if upload_history is None:
                        st.warning(constants.FILE_UPLOADER_WARNING_PROMPT)
                        return

                    try:
                        history = [{"role": "system", "content": self.system_message},
                                    {"role": "system", "content": self.init_message}]

                        for line in upload_history.getvalue().decode("utf-8").splitlines():
                            line = line.strip()

                            if line:
                                history.append(ast.literal_eval(line))

                        self.history = history
                        st.session_state.chat_history = history
                        st.session_state.upload_key += 1

                        st.success(constants.FILE_UPLOADER_SUCCESS_PROMPT)
                        st.rerun()

                    except json.JSONDecodeError as e:
                        st.error(constants.FILE_UPLOADER_JSON_FORMAT_ERROR_PROMPT + f"{e}")

                    except Exception as e:
                        st.error(constants.FILE_UPLOADER_OTHER_ERROR_PROMPT + f"{e}")

                st.download_button(
                    constants.FILE_DOWNLOADER_PROMPT,
                    data=toolbox.package_data(self.history),
                    file_name="streamlit_chat_history.jsonl",
                    use_container_width=True,
                )

                if st.button(constants.FILE_PREVIEWER_PROMPT, use_container_width=True):
                    self.check_history()
 
        
            with st.expander(constants.LOWER_EXPANDER_TITLE, expanded = False):
                st.slider(constants.SLIDER_MAX_TOKENS_PROMPT + f"{st.session_state.max_tokens}", value=st.session_state.max_tokens, key="max_tokens", max_value=5000)
                st.write(constants.SLIDER_USED_TOKENS_PROMPT + f"{st.session_state.used_tokens} tokens")

                st.slider(constants.SLIDER_TEMPERATURE_PROMPT + f"{st.session_state.temperature}", value=st.session_state.temperature, key="temperature", max_value=2.00, min_value=0.01, step=0.01)
                st.slider(constants.SLIDER_TOP_P_PROMPT + f"{st.session_state.top_p}", value=st.session_state.top_p, key="top_p", min_value=0.01, max_value=1.00, step=0.01)
            
                st.toggle("Streaming", key="streaming")

                if st.button(constants.RESET_SESSION_PROMPT):
                    self.confirm_reset()

    def stream(self, selected_model):
        payload = {
                "model": selected_model,
                "stream": True,
                "messages": self.history,
                "temperature": 0,
                "max_tokens": st.session_state.max_tokens,
                "top_p": st.session_state.top_p,
                "temperature": st.session_state.temperature,
                "stream_options":{"include_usage":True}
                }
                
        resp = requests.post(self.url, json=payload, stream=True, timeout=constants.MAX_WAIT)

        for line in resp.iter_lines():
            if not line:
                continue             

            raw_line = line.decode("utf-8").strip()
            if not raw_line.startswith("data:"):
                continue

            json_str = raw_line[5:].strip()
            chunk = json.loads(json_str)

            if 'usage' in chunk:
                usage = chunk.get("usage")
                self.get_token_cost(usage)

                break

            if json_str == "[DONE]":
                break

            content = chunk["choices"][0]["delta"].get("content", "")
            yield content

    def get_token_cost(self, loc):
        self.tokens_used = loc.get("total_tokens")

        st.session_state.used_tokens += loc.get("total_tokens")

    @st.dialog(constants.FILE_PREVIEWER_DIALOGUE)
    def check_history(self):
        for entry in self.history[2:]:
            st.write(entry)

    @st.dialog("NYANCAT")
    def nyancat(self):
        try:
            st.video("https://www.youtube.com/watch?v=2yJgwwDcgV8")
        except Exception as e:
            st.exception(f"ERROR: {e}")

    def reset_session_state(self):
        for key in constants.VALUE_KEYS:
            del st.session_state[key]

    @st.dialog(constants.RESET_CONFIRMATION_DIALOGUE)
    def confirm_reset(self):
        if st.button(constants.RESET_CONFIRMATION_PROMPT):
            self.reset_session_state()
            st.rerun()


