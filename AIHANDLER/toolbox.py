import constants as constants
import requests
import time

def is_model_supported(models, input_str):
    if input_str.isdigit():
        idx = int(input_str)
        return 0 <= idx < len(models)
    else:
        return input_str in models


def prompt_and_check(models):
    while True:
        model_input = input("\n请输入模型名称/序号: ").strip()
        if model_input == "/exit":
            print("退出程序。")
            exit(0)

        if not is_model_supported(models, model_input):
            print(f"暂未支持 '{model_input}'。")
            # 打印带序号列表
            show_list = [f"{i}: {model}" for i, model in enumerate(models)]
            print(f"当前支持的模型有:\n\n{'\n'.join(show_list)}")
            continue

        if model_input.isdigit():
            select_idx = int(model_input)
            selected_model = models[select_idx]
            print(f"当前使用模型：{selected_model}\n输入 /help 查看全部指令\n")
            return selected_model
        else:
            selected_model = model_input
            print(f"当前使用模型：{selected_model}\n输入 /help 查看全部指令\n")
            return selected_model


def handle_input(history, user_input, ip, port):
    cmd = user_input.lower().strip()
    new_history = history.copy()

    if cmd == "/exit":
        # 返回状态1：退出循环
        return 1, new_history

    if cmd == "/clear":
        new_history = [entry for entry in history if entry['role'] == 'system']
        print("\n已清空全部对话历史\n")
        return 3, new_history

    elif cmd == "/history":
        print("\n=====对话历史记录=====")
        for i in range(2, len(new_history)):
            print(f"{new_history[i]['role']}: {new_history[i]['content']}")
        print("======================\n")
        return 0, new_history

    elif cmd == "/summarise":
        if len(new_history) <= 1:
            print("\n暂无对话内容可总结\n")
            return 0, new_history

        summary_text = "总结以下对话，提炼核心业务问答。提炼时不要丢失重要信息（如，你回答的答案）。\n"
        for item in new_history[2:]:
            summary_text += f"{item['role']}: {item['content']}\n"

        import requests
        payload = {
            "model": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
            "stream": False,
            "messages": [{"role": "system", "content": summary_text}],
            "temperature": 0,
            "max_tokens": 1000
        }
        resp = requests.post(
            f"http://{ip}:{port}/v1/chat/completions",
            json=payload,
            timeout=120
        )
        summary = resp.json()["choices"][0]["message"]["content"]

        # 精简历史：仅保留system+总结
        new_history = [
            new_history[0],
            {"role": "system", "content": f"【对话总结】{summary}"}
        ]
        print(f"对话总结：\n{summary}\n")
        return 0, new_history

    elif cmd == "/ipconfig":
        print(f"\n当前IP地址: {ip}\n当前端口号: {port}\n")
        return 0, new_history

    elif cmd == "/help" or cmd.startswith("/"):
        print("\n=====可用控制指令=====")
        print("/exit      退出程序")
        print("/clear     清空对话历史")
        print("/history   查看完整对话")
        print("/summarise 总结对话并精简上下文")
        print("/ipconfig  查看IP配置")
        print("======================\n")
        return 0, new_history

    # 普通提问，状态2
    new_history.append({"role": "user", "content": user_input})
    return 2, new_history

def connection_check(url):
    print(f"\n{constants.YELLOW}正在检测模型服务{constants.RESET}", end="", flush=True)

    connected = False
    dots = ["   ", ".  ", ".. ", "..."]
    dot_idx = 0
    wait_count = 0

    while not connected and wait_count < constants.MAX_WAIT:
        try:
            requests.get(f"{url}", timeout=1)
            connected = True

        except Exception:
            dot_id = (dot_idx) % len(dots)
            print(f"\r{constants.YELLOW}正在检测模型服务{dots[dot_id]}{constants.RESET}", end="", flush=True)

            wait_count += 0.5
            dot_idx += 1

            time.sleep(0.5)

    if not connected:
        print(f"\n{constants.RED}连接超时，服务未启动，程序退出{constants.RESET}")
        exit(1)

    print(f"\n{constants.GREEN}服务连接成功。{constants.RESET}\n")