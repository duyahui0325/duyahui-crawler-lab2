# -*- coding: utf-8 -*-
"""
spider_utils.py —— 网页解析实验的通用工具函数（可复用）

设计思路：把与具体业务无关的逻辑（构造请求头、创建目录）抽成通用函数，
案例1、案例2 只保留各自的“请求信息、解析规则、存储位置”，便于复用与维护。
"""

from pathlib import Path


def default_headers() -> dict:
    """构造默认请求头：伪装成浏览器，降低被网站反爬拦截的概率。"""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }


def ensure_dir(dir_path) -> Path:
    """创建目录（已存在也不会报错），返回 Path 对象。"""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path
