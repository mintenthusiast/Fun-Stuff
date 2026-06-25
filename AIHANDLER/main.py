import requests
import toolbox
import constants as constants

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

        self.history = [
            {"role": "system", "content": self.system_message},
            {"role": "system", "content": self.init_message}
        ]

    def run(self):

        toolbox.connection_check(self.url)
        selected_model = toolbox.prompt_and_check(self.models)

        while True:
            try:
                user_input = input("你：").strip()

                if not user_input:
                    print("\n请输入有效内容\n")
                    continue

                cmd_status, new_history = toolbox.handle_input(
                    self.history,
                    user_input,
                    self.ip,
                    self.port
                )

                # 普通指令，继续循环
                if cmd_status == 0:
                    continue

                # 退出程序
                if cmd_status == 1:
                    print("会话结束，退出程序")
                    exit(0)

                # 正常对话请求
                if cmd_status == 2:
                    self.history = new_history
                    payload = {
                        "model": selected_model,
                        "stream": False,
                        "messages": self.history,
                        "temperature": 0,
                        "max_tokens": 200
                    }

                    print(f"\n{constants.YELLOW}AI正在思考，请稍候...{constants.RESET}")
                    resp = requests.post(self.url, json=payload, timeout=120)
                    resp.raise_for_status()
                    res_data = resp.json()

                    model_response = res_data["choices"][0]["message"]["content"]
                    self.history.append({"role": "assistant", "content": model_response})
                    print(f"\n{constants.GREEN}AI: {model_response}{constants.RESET}\n")

                if cmd_status == 3:
                    self.history = new_history
                    continue

            except requests.exceptions.RequestException as e:
                print(f"\n{constants.RED} :( 请求错误: {e}{constants.RESET}\n")
                self.history.append({"role": "system", "content": f"ERROR: {e}"})

            except KeyError as e:
                print(f"\n{constants.RED} :( 返回数据格式错误{constants.RESET}\n")
                self.history.append({"role": "system", "content": f"ERROR: {e}"})

            except Exception as e:
                print(f"\n{constants.RED} :( 程序异常: {e}{constants.RESET}\n")
                self.history.append({"role": "system", "content": f"ERROR: {e}"})


if __name__ == "__main__":
    port = input("请输入端口号：").strip()
    ip = input("请输入IP地址：").strip()
    system_message = input("请输入系统消息（可留空）：").strip() or "你是一个有帮助的AI助手。"

    aihandler = AIHandler(
        ip=ip,
        port=port,
        models=constants.MODELS,
        system_message=system_message
    )
    aihandler.run()