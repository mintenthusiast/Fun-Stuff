import constants as constants
import requests
import time
import streamlit as st
import sqlite3

def prompt_and_check(models):
    if "model_input" not in st.session_state:
        st.session_state["model_input"] = models[0]

    model_input = st.selectbox(
        label="请选择一个模型",
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
            # 替换 new_history.append 为 update_history
            update_history("system", "INFO: 没有历史可总结", new_history)
            chat.info(f"INFO: 没有历史可总结")
            return 0, new_history

        summary_text = (
            "总结以下对话，提炼核心业务问答。"
            "提炼时不要丢失重要信息。"
        )

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
            "max_tokens": 1000
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
            update_history("system", f"ERROR: 总结失败{e}", new_history)
            return 3, new_history

    # ===== IPCONFIG =====
    elif cmd == "/ipconfig":
        # 替换 append
        update_history("system", f"INFO: 当前IP地址: {ip} 当前端口号: {port}", new_history)
        chat.info(f"当前IP地址: {ip} 当前端口号: {port}")
        return 3, new_history

    # ===== HELP =====
    elif cmd == "/help":
        help_text = (
            "INFO:\n/help       查看帮助\n/clear      清空历史\n/summarise  总结对话\n"
            "/ipconfig   查看配置\n/exit       退出\n/clean       清空所有历史（system在内）"
        )
        # 替换 append
        update_history("system", help_text, new_history)
        return 3, new_history
    
    elif cmd ==  "/clean":
        new_history = [new_history[0], new_history[1]]
        # 替换 append
        update_history("system", "INFO: 已清除所有信息", new_history)
        return 3, new_history

    # ===== UNKNOWN COMMAND =====
    elif cmd.startswith("/"):
        # 两条system提示统一调用update_history
        update_history("system", f"WARNING: 未知命令: {cmd}", new_history)
        update_history("system", f"INFO: 输入 /help 查看帮助", new_history)
        return 3, new_history

    # ===== NORMAL CHAT =====
    # 用户输入消息替换append
    update_history("user", user_input, new_history)
    return 2, new_history

def connection_check(url):
    with st.spinner("正在检测模型服务连通性...", show_time=True):
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
            st.error("REQUEST TIMEOUT")
            exit(1)

        st.success("连接成功！")

def update_history(role, content, history):
    history.append({"role":role, "content":content})

    conn = sqlite3.connect(f"AIHANDLER/sqlite_history/chat.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages(role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect("AIHANDLER/sqlite_history/chat.db")
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