from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
)
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from llm import llm


# 普通聊天历史
_chat_histories: dict[
    str,
    InMemoryChatMessageHistory,
] = {}


def get_chat_history(
    session_id: str,
) -> InMemoryChatMessageHistory:
    """根据 session_id 获取对应的聊天历史。"""

    if session_id not in _chat_histories:
        _chat_histories[
            session_id
        ] = InMemoryChatMessageHistory()

    return _chat_histories[
        session_id
    ]


def content_to_text(content) -> str:
    """把不同格式的消息内容转换为文本。"""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, str):
                parts.append(block)

            elif isinstance(block, dict):
                block_text = block.get("text")

                if block_text:
                    parts.append(block_text)

        return "".join(parts)

    return str(content) if content else ""


def message_to_text(
    message: BaseMessage,
) -> str:
    """把历史消息转换为摘要文本。"""

    role_names = {
        "human": "用户",
        "ai": "助手",
        "system": "系统摘要",
        "tool": "工具",
    }

    role = role_names.get(
        message.type,
        message.type,
    )

    content = content_to_text(
        message.content
    )

    return f"{role}：{content}"


def summarize_chat_history(
    session_id: str,
    max_messages: int = 16,
    keep_messages: int = 6,
) -> None:
    """
    普通聊天历史摘要压缩。

    当历史超过 max_messages 条时：
    1. 较早消息生成摘要；
    2. 最近 keep_messages 条保留原文；
    3. 用摘要替换较早消息。
    """

    history = get_chat_history(
        session_id
    )

    messages = list(
        history.messages
    )

    if len(messages) <= max_messages:
        return

    old_messages = messages[
        :-keep_messages
    ]

    recent_messages = messages[
        -keep_messages:
    ]

    old_history_text = "\n".join(
        message_to_text(message)
        for message in old_messages
    )

    response = llm.invoke([
        SystemMessage(
            content=(
                "你负责压缩聊天历史。"
                "不要回答历史中的问题，"
                "只生成供后续对话参考的摘要。"
            )
        ),
        HumanMessage(
            content=f"""
请将下面的聊天历史压缩成一份简洁、准确的中文摘要。

必须保留：

1. 用户正在完成的任务；
2. 用户已经明确提出的要求；
3. 已经得到的结论；
4. 重要的文件名、技术名词和参数；
5. 用户的稳定偏好；
6. 尚未解决的问题；
7. 后续对话需要参考的上下文。

聊天历史：

{old_history_text}
"""
        ),
    ])

    summary_text = content_to_text(
        response.content
    )

    history.clear()

    history.add_message(
        SystemMessage(
            content=(
                "下面是较早聊天内容的摘要，"
                "请在后续回答中参考：\n"
                f"{summary_text}"
            )
        )
    )

    history.add_messages(
        recent_messages
    )


def clear_chat_history(
    session_id: str,
) -> None:
    """清除普通聊天历史。"""

    history = _chat_histories.pop(
        session_id,
        None,
    )

    if history is not None:
        history.clear()