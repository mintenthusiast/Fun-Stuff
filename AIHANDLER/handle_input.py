# handle_input.py
def handle_input(user_input, history, ip, port):
    typos = ["/hepl", "/hlep", "/hel", "/helo"]
    cmd = user_input.lower().strip()
    new_history = history.copy()

    if cmd == "/exit":
        # 返回状态1：退出循环
        return 1, new_history

    if cmd == "/clear":
        new_history = [new_history[0]]
        print("\n✅ 已清空全部对话历史\n")
        return 0, new_history

    elif cmd == "/history":
        print("\n=====对话历史记录=====")
        for item in new_history:
            print(f"{item['role']}: {item['content']}")
        print("======================\n")
        return 0, new_history

    elif cmd == "/summarise":
        if len(new_history) <= 1:
            print("暂无对话内容可总结\n")
            return 0, new_history
        
        summary_text = "总结以下对话，提炼核心业务问答：\n"
        for item in new_history[1:]:
            summary_text += f"{item['role']}: {item['content']}\n"
        
        import requests
        payload = {
            "model": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
            "stream": False,
            "messages": [{"role": "system", "content": summary_text}],
            "temperature": 0,
            "max_tokens": 1000
        }
        resp = requests.post(f"http://{ip}:{port}/v1/chat/completions", json=payload, timeout=120)
        summary = resp.json()["choices"][0]["message"]["content"]
        
        # 精简历史：仅保留system+总结
        new_history = [new_history[0], {"role":"system", "content":f"【对话总结】{summary}"}]
        print(f"对话总结：\n{summary}\n")
        return 0, new_history
    
    elif cmd == "/ipconfig":
        print(f"\n当前IP地址: {ip}\n当前端口号: {port}\n")
        return 0, new_history

    elif cmd in typos:
        print(
            "\n•.,¸,.•*`•.,¸¸,.•*¯ ╭━━━━━━━━━━━╮\n"
            "•.,¸,.•*¯`•.,¸,.•*¯.|:::::::: /___/\n"
            "•.,¸,.•*¯`•.,¸,.•* <|:::::::(｡ ●ω●｡)\n"
            "•.,¸,.•¯•.,¸,.•╰ * >し------し---Ｊ\n"
        )
        return 0, new_history
    
    elif cmd == "/help" or cmd[0] == "/":
        print("\n=====可用控制指令=====")
        print("/exit      退出程序")
        print("/clear     清空对话历史")
        print("/history   查看完整对话")
        print("/summarise 总结对话并精简上下文")
        print("/ipconfig  查看IP配置")
        print("======================\n")
        return 0, new_history

    # 普通提问，状态0
    new_history.append({"role": "user", "content": user_input})
    return 0, new_history

