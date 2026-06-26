import requests
import toolbox
import constants as constants
import streamlit as st

class AIHandler:
    def __init__(self, ip, port, models, system_message):
        self.ip = ip
        self.port = port    
        self.models = models
        self.system_message = system_message

        if (self.ip == "test" and self.port == "test"):
            self.url = "https://google.com"
        else:
            self.url = f"http://{self.ip}:{self.port}/v1/chat/completions"

        with open("AIHANDLER/init_message.txt", "r", encoding="utf-8") as f:
            self.init_message = f.read()

        self.history = []

    def run(self):
        toolbox.connection_check(self.url)
        selected_model = toolbox.prompt_and_check(self.models)
        st.write(self.history)

        chat = st.container(height=400)
        user = st.container()

        if "user_text" not in st.session_state:
            st.session_state["user_text"] = ""

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = [
                {"role": "system", "content": self.system_message},
                {"role": "system", "content": self.init_message}
            ]

        self.history = st.session_state.chat_history

        with chat:
            for message in self.history[2:]:
                if message['role'] == 'user':
                    st.chat_message("你").write(message['content'])
                elif message['role'] == 'assistant':
                    st.chat_message("AI").write(message['content'])
                elif message['role'] == 'system':
                    if message['content'].startswith('E'):
                        st.error(message['content'])
                    elif message['content'].startswith('I'):
                        st.info(message['content'])
                    elif message['content'].startswith('W'):
                        st.warning(message['content'])

        with user:
            user_input = st.chat_input("输入消息...")
        
        if user_input:
            self.process_requests(user_input, chat, selected_model)
            st.session_state.chat_history = self.history
            st.rerun()
        
        else:
            pass

    def process_requests(self, user_input, chat, selected_model):
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

            if cmd_status == 1:
                st.success("会话结束，退出程序")
                exit(0)

            if cmd_status == 2:
                self.history = new_history
                payload = {
                    "model": selected_model,
                    "stream": False,
                    "messages": self.history,
                    "temperature": 0,
                    "max_tokens": 200
                }

                with chat.spinner("AI思考中...", show_time=True):
                    resp = requests.post(self.url, json=payload, timeout=120)
                    resp.raise_for_status()
                    res_data = resp.json()

                    model_response = res_data["choices"][0]["message"]["content"]
                    toolbox.update_history("assistant", model_response, self.history)
                    return model_response
                            
            if cmd_status == 3:
                self.history = new_history

        except requests.exceptions.RequestException as e:
            err_msg = f"ERROR: {e}"
            chat.error(f"请求错误: {e}")
            toolbox.update_history("system", err_msg, self.history)

        except KeyError as e:
            err_msg = f"ERROR: 返回数据格式错误{e}"
            chat.error(err_msg)
            toolbox.update_history("system", err_msg, self.history)

        except Exception as e:
            err_msg = f"ERROR: 程序异常: {e}"
            chat.error(err_msg)
            toolbox.update_history("system", err_msg, self.history)