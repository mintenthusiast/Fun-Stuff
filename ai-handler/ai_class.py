import requests
import streamlit as st
import json
from app_render import app

import toolbox
import constants as constants

class ai_handler:
    def __init__(self, ip, port, selected_model, system_message, user_input, chat, settings, render: app):
        self.ip = ip
        self.port = port    
        self.selected_model = selected_model
        self.system_message = system_message
        self.user_input = user_input
        self.chat = chat
        self.settings = settings
        self.render = render
        self.url = toolbox.get_url(ip, port)

        self.tokens_used = 0

        self.history = []

    def run(self):
        self.history = st.session_state.chat_history
        self.chat, self.user_input, self.selected_model, self.settings = self.render.render(self.history)

        if self.user_input:
            model_response = self.process_requests(streaming=st.session_state.streaming)
            toolbox.update_history("assistant", model_response, self.history, self.tokens_used)
            st.session_state.chat_history = self.history

            st.rerun()
            
    def process_requests(self, streaming=False):
        try:
            cmd_status, new_history = toolbox.handle_input(
                self.history,
                self.user_input,
                self.ip,
                self.port,
                self.chat
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
                        "model": self.selected_model,
                        "stream": False,
                        "messages": self.history,
                        "max_tokens": st.session_state.max_tokens,
                        "top_p": st.session_state.top_p,
                        "temperature": st.session_state.temperature
                    }

                    with self.chat.spinner(constants.CHAT_OUTPUT_THINKING_PROMPT, show_time=True):
                        resp = requests.post(self.url, json=payload, timeout=constants.MAX_WAIT)
                        resp.raise_for_status()
                        res_data = resp.json()

                        model_response = res_data["choices"][0]["message"]["content"]
                        usage = res_data.get("usage")
                        self.get_token_cost(usage)

                        return model_response
                
                if streaming:
                    with self.chat.spinner(constants.CHAT_OUTPUT_THINKING_PROMPT, show_time=True):   
                        with self.chat.chat_message("assistant"):
                            model_response = st.write_stream(self.stream())

                    return model_response

            if cmd_status == 3:
                self.history = new_history

        except requests.exceptions.RequestException as e:
            self.chat.error(f"ERROR: {constants.REQUEST_ERROR_PROMPT}{e}")
            toolbox.update_history("system", f"ERROR: {constants.REQUEST_ERROR_PROMPT}{e}", self.history)

        except KeyError as e:
            self.chat.error(f"ERROR: {constants.KEY_ERROR_PROMPT}{e}")
            toolbox.update_history("system", f"ERROR: {constants.KEY_ERROR_PROMPT}{e}", self.history)

        except Exception as e:
            self.chat.error(f"ERROR: {constants.SCRIPT_ERROR_PROMPT}{e}")
            toolbox.update_history("system", f"ERROR: {constants.SCRIPT_ERROR_PROMPT}{e}", self.history)

    def stream(self):
        payload = {
                "model": self.selected_model,
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
