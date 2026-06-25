def is_model_supported(input_str, models):
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
        if not is_model_supported(model_input, models):
            print(f"暂未支持 '{model_input}'。")
            # 打印带序号列表
            show_list = [f'{i}: {model}' for i, model in enumerate(models)]
            print(f"当前支持的模型有: {', '.join(show_list)}")
            continue
        
        if model_input.isdigit():
            select_idx = int(model_input)
            return models[select_idx]
        else:
            return model_input