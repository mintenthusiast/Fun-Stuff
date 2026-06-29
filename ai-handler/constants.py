# DEFAULT

DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.5
DEFAULT_TOP_P = 0.5

MODELS = ["mlx-community/Qwen2.5-1.5B-Instruct-4bit", "mlx-community/Tmax-9B-MLX-bf16", "mlx-community/Qwen3-8B-4bit", "Qwen/Qwen1.5-0.5B-Chat"] # 模型
MAX_WAIT = 10 # 最大等待连接秒数
INIT_MESSAGE_PATH = "ai-handler/init_message.md"
DATABASE_PATH = "ai-handler/database/chat.db"

ROLES = {
            "user": "你：",
            "assistant": "AI: "
        }

VALUE_KEYS = ["max_tokens", "used_tokens", "temperature", "top_p", "chat_history", "upload_key"]

# PAGE

PAGE_TITLE = "AI HANDLER"
HEADING = "AI HANDLER V0.4"
SUBHEADING = "聊天"
SUBHEADING_CAPTION = "模型："

UPPER_EXPANDER_TITLE = "历史"
LOWER_EXPANDER_TITLE = "模型参数"

# HISTORY

FILE_UPLOADER_PROMPT = "上传聊天历史(JSONL)"
FILE_UPLOADER_CONFIRMATION_PROMPT = "导入历史"
FILE_UPLOADER_WARNING_PROMPT = "请选择一个聊天记录文件。"
FILE_UPLOADER_SUCCESS_PROMPT = "聊天记录导入成功！"

FILE_UPLOADER_JSON_FORMAT_ERROR_PROMPT = "JSON格式错误: "
FILE_UPLOADER_OTHER_ERROR_PROMPT = "导入失败："

FILE_DOWNLOADER_PROMPT = "下载聊天历史"
FILE_PREVIEWER_PROMPT = "预览JSONL"
FILE_PREVIEWER_DIALOGUE = "JSONL PREVIEW"

# AI VARIABLES

SLIDER_MAX_TOKENS_PROMPT = "最大token输出: "
SLIDER_USED_TOKENS_PROMPT = "此对话已使用："
SLIDER_TEMPERATURE_PROMPT = "temperature: "
SLIDER_TOP_P_PROMPT = "top_p: "

RESET_SESSION_PROMPT = "重置此次会话"
RESET_CONFIRMATION_PROMPT = "确认"
RESET_CONFIRMATION_DIALOGUE = "请确认"

# CHAT

CHAT_INPUT_PROMPT = "输入消息..."
CHAT_OUTPUT_THINKING_PROMPT = "AI思考中..."
TOKENS_USED_PROMPT = "Tokens花费: "

REQUEST_ERROR_PROMPT = "请求错误: "
KEY_ERROR_PROMPT = "返回数据格式错误: "
SCRIPT_ERROR_PROMPT = "程序异常: "

# INITIALISATION

PORT_PROMPT = "请输入端口号："
IP_PROMPT = "请输入IP地址: "
SYSTEM_MESSAGE_PROMPT = "请输入系统消息（可留空）："
SYSTEM_MESSAGE_DEFAULT = "你是一个有帮助的AI助手。"

IP_PORT_WARNING_PROMPT = "IP地址和端口号不能为空! "
SESSION_START_SPINNER = "正在启动控制台对话程序，请稍等..."

CONNECTION_CHECK_SPINNER = "正在检测模型服务连通性..."
CONNECTION_CHECK_TIMEOUT = "REQUEST TIMEOUT!"
CONNECTION_CHECK_SUCCESS = "连接成功！"

RENDER_START_SPINNER = "加载中..."

MODEL_INPUT_PROMPT = "请选择一个模型"

# CMDS

SUMMARISE_WARNING_PROMPT = "没有历史可总结"
SUMMARISE_ERROR_PROMPT = "总结失败"

SUMMARISE_AI_PROMPT = ("总结以下对话，提炼核心业务问答。提炼时不要丢失重要信息。")

IPCONFIG_IP_PROMPT = "当前IP地址: "
IPCONFIG_PORT_PROMPT = "当前端口号: "

HELP_PROMPT = ("\n/help       查看帮助\n/clear      清空历史\n/summarise  总结对话\n"
            "/ipconfig   查看配置\n/exit       退出\n/clean       清空所有system在内历史")

UNKNOWN_WARNING_PROMPT = "未知命令: "
UNKNOWN_INFO_PROMPT = "输入 /help 查看帮助"

SESSION_EXIT_PROMPT = "会话结束，退出程序"
