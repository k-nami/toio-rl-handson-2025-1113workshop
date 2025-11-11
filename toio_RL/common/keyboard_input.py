import asyncio

import readchar
from enum import Enum
from typing import Dict, Any


class Key(Enum):
    UP = readchar.key.UP
    RIGHT = readchar.key.RIGHT
    DOWN = readchar.key.DOWN
    LEFT = readchar.key.LEFT


async def read_action_async(key_action_map: Dict[str, Any]):
    """
    ブロッキングなキー読みを別スレッドで実行して非同期化
    key_action_map = {
        readchar.key.UP:    Action.UP,
        readchar.key.RIGHT: Action.RIGHT,
        readchar.key.DOWN:  Action.DOWN,
        readchar.key.LEFT:  Action.LEFT,
    }
    """
    while True:
        k = await asyncio.to_thread(readchar.readkey)  # 別スレッドでブロッキングI/O
        if k.lower() == "q":
            return None  # 終了指示
        if k in key_action_map:
            return key_action_map[k]
        # 他キーは無視してループ


def read_action(key_action_map: Dict[str, Any]):
    """
    key_action_map = {
        readchar.key.UP:    Action.UP,
        readchar.key.RIGHT: Action.RIGHT,
        readchar.key.DOWN:  Action.DOWN,
        readchar.key.LEFT:  Action.LEFT,
    }
    """
    while True:
        k = readchar.readkey()
        if k.lower() == "q":
            return None  # 終了指示
        if k in key_action_map:
            return key_action_map[k]
        # 他キーは無視してループ
