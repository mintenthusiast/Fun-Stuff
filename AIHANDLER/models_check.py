def is_model_supported(model, models):
    return model in models

def prompt_and_check(models):
    while True:
        model_input = input("\n请输入模型名称: ").strip()
        if model_input == "/exit":
            print("退出程序。")
            exit(0)
        if is_model_supported(model_input, models):
            return model_input
        print(f"暂未支持 '{model_input}'。")
        print(f"当前支持的模型有: {', '.join(models)}")