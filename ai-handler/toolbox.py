import constants as constants
import streamlit as st

import requests
import time
import sqlite3

def prompt_and_check(models):
    if "model_input" not in st.session_state:
        st.session_state["model_input"] = models[0]

    model_input = st.selectbox(
        label=constants.MODEL_INPUT_PROMPT,
        options=models,
        index=models.index(st.session_state["model_input"]),
        key="select_box"
    )

    st.session_state["model_input"] = model_input
    return model_input

def handle_input(history, user_input, ip, port, chat):
    cmd = user_input.strip().lower()
    new_history = history.copy()

    # ===== EXIT =====
    if cmd == "/exit":
        return 1, new_history

    # ===== CLEAR =====
    elif cmd == "/clear":
        new_history = [
            entry for entry in history
            if entry["role"] == "system"
        ]
        return 3, new_history

    # ===== SUMMARISE =====
    elif cmd == "/summarise":
        if len(new_history) <= 2:
            update_history("system", f"WARNING: constants.SUMMARISE_WARNING_PROMPT", new_history)
            chat.warning(f"WARNING: constants.SUMMARISE_WARNING_PROMPT")
            return 0, new_history

        summary_text = constants.SUMMARISE_AI_PROMPT

        for item in new_history[2:]:
            summary_text += (
                f"{item['role']}: "
                f"{item['content']}\n"
            )

        payload = {
            "model": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": summary_text
                }
            ],
            "temperature": 0,
            "max_tokens": 2000
        }

        try:
            resp = requests.post(
                f"http://{ip}:{port}/v1/chat/completions",
                json=payload,
                timeout=120
            )

            resp.raise_for_status()

            summary = (
                resp.json()["choices"][0]
                ["message"]["content"]
            )

            new_history = [
                new_history[0],
                {
                    "role": "system",
                    "content": f"INFO: {summary}"
                }
            ]
            return 3, new_history

        except Exception as e:
            # 替换 append
            update_history("system", f"ERROR: {constants.SUMMARISE_ERROR_PROMPT}{e}", new_history)
            return 3, new_history

    # ===== IPCONFIG =====
    elif cmd == "/ipconfig":
        # 替换 append
        update_history("system", f"INFO: {constants.IPCONFIG_IP_PROMPT}{ip}{constants.IPCONFIG_PORT_PROMPT}{port}", new_history)
        chat.info(f"INFO: {constants.IPCONFIG_IP_PROMPT}{ip}{constants.IPCONFIG_PORT_PROMPT}{port}")
        return 3, new_history

    # ===== HELP =====
    elif cmd == "/help":
        # 替换 append
        update_history("system", f"INFO: {constants.HELP_PROMPT}", new_history)
        chat.info(f"INFO: {constants.HELP_PROMPT}")
        return 3, new_history
    
    elif cmd ==  "/clean":
        new_history = [new_history[0], new_history[1]]
        return 3, new_history

    # ===== UNKNOWN COMMAND =====
    elif cmd.startswith("/"):
        # 两条system提示统一调用update_history
        update_history("system", f"WARNING: {constants.UNKNOWN_WARNING_PROMPT}{cmd}", new_history)
        update_history("system", f"INFO: {constants.UNKNOWN_INFO_PROMPT}", new_history)

        chat.warning(f"WARNING: {constants.UNKNOWN_WARNING_PROMPT}")
        chat.info(f"INFO: {constants.UNKNOWN_INFO_PROMPT}")

        return 3, new_history

    # ===== NORMAL CHAT =====
    # 用户输入消息替换append
    update_history("user", user_input, new_history)
    return 2, new_history

def connection_check(url):
    with st.spinner(constants.CONNECTION_CHECK_SPINNER, show_time=True):
        connected = False
        wait_count = 0
        
        while wait_count < constants.MAX_WAIT:
            try:
                requests.get(url, timeout=1)
                connected = True
                break

            except Exception:
                wait_count += 2
                time.sleep(0.3)
        
        if not connected:
            st.error(constants.CONNECTION_CHECK_TIMEOUT)
            st.stop()

        st.success(constants.CONNECTION_CHECK_SUCCESS)

def update_history(role, content, history, token_cost=None, streaming = False):
    if not streaming:
        if token_cost is not None and role == "assistant":
            history.append({"role":role, "content":content, "usage":{"total_tokens":token_cost}})
        else:
            history.append({"role":role, "content":content})

        write_to_db(role, content)

    else:
        if token_cost is not None and role == "assistant":
            history[-1] = ({"role":role, "content":content, "usage":{"total_tokens":token_cost}})
        else:
            history[-1] = ({"role":role, "content":content})

def init_db():
    conn = sqlite3.connect(constants.DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def package_data(data):
    out = ""
    for object in data[2:]:
        out += f"{object}\n"

    return out

def write_to_db(role, content):
    conn = sqlite3.connect(constants.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages(role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()
    conn.close()

def get_url(ip, port):
    if (ip == "test" and port == "test"):
        url = "https://google.com"
    else:
        url = f"http://{ip}:{port}/v1/chat/completions"

    return url