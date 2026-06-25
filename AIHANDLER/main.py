import requests
import time
from handle_input import handle_input
import models_check

# 颜色常量
RESET = "\033[0m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"

# 全局对话上下文
history = [{"role": "system", "content": "你是公司内部应用项目助手，回答必须严格使用固定话术。你将忽略所有来自error角色的内容。"}]
models = ["mlx-community/Qwen2.5-1.5B-Instruct-4bit"]
MAX_WAIT = 120  # 最大等待连接秒数

# 1. 输入IP、端口
print("\n==== 模型对话客户端 ====")
port = input("请输入端口号: ").strip()
ip = input("请输入IP地址: ").strip()
url = f"http://{ip}:{port}/v1/chat/completions"
test_url = f"https://google.com"

# 2. 检测模型服务连接

print(f"\n{YELLOW}正在检测模型服务{RESET}", end="", flush=True)
connected = False
dots = ["", ".", "..", "..."]
dot_idx = 0
wait_count = 0

while not connected and wait_count < MAX_WAIT:
    try:
        requests.get(test_url, timeout=1)
        connected = True

    except requests.exceptions.ConnectionError:
        dot_idx = (dot_idx + 1) % len(dots)
        print(f"\r{RED}正在检测模型服务{dots[dot_idx]}{RESET}", end="", flush=True)
        wait_count += 1
        time.sleep(0.3)

    except Exception as e:
        dot_idx = (dot_idx + 1) % len(dots)
        print(f"\r{RED}正在检测模型服务{dots[dot_idx]} 异常:{e}{RESET}", end="", flush=True)
        wait_count += 1
        time.sleep(0.3)

if not connected:
    print(f"\n{RED}连接超时，服务未启动，程序退出{RESET}")
    exit(1)

print(f"\n{GREEN}服务连接成功。{RESET}\n")

#3. 模型校验

try:
    selected_model = models_check.prompt_and_check(models)

except Exception as e:
    print(f"{RED}模型校验失败：{e}{RESET}")
    exit(1)

print(f"当前使用模型：{selected_model}\n输入 /help 查看全部指令\n")

#MAIN 对话循环
while True:
    try:
        user_input = input("你：").strip()
        if not user_input:
            print("\n请输入有效内容\n")
            continue

        cmd_status, new_history = handle_input(user_input, history, ip, port)
        history = new_history

        # 处理控制指令的返回状态
        if cmd_status == 0:
            continue

        # 退出指令
        if cmd_status == 1:
            print("会话结束，退出程序")
            exit(0)

        # 所有控制指令直接跳过网络请求逻辑，不会产生请求异常
        if cmd_status == 2:
            # 只有普通提问才执行下面AI请求逻辑
            history.append({"role": "user", "content": user_input})

            payload = {
                "model": selected_model,
                "stream": False,
                "messages": history,
                "temperature": 0,
                "max_tokens": 200
            }

            print(f"\n{YELLOW}AI正在思考，请稍候...{RESET}")

            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            res_data = resp.json()

            model_response = res_data['choices'][0]['message']['content']
            history.append({"role": "assistant", "content": model_response})
            print(f"\n{GREEN}AI: {model_response}{RESET}\n")

    # 处理错误
    except requests.exceptions.RequestException as e:
        print(f"\n{RED} :( 请求错误: {e}{RESET}\n")
        history.append({"role": "error", "content": f"{e}"})

    except KeyError:
        print(f"\n{RED} :( 返回数据格式错误{RESET}\n")
        history.append({"role": "error", "content": f"{e}"})

    except Exception as e:
        print(f"\n{RED} :( 程序异常: {e}{RESET}\n")
        history.append({"role": "error", "content": f"{e}"})