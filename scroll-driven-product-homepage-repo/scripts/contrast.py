#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WCAG 2.2 对比度实算器。

为什么必须实算：凭感觉估的色值经常不达标。
实测教训 —— #6b7f77 实算 4.26:1、#9aa8a2 实算 2.47:1（均低于 AA 的 4.5:1）。

用法：
    python contrast.py                      # 跑内置默认色板
    python contrast.py "#12211b" "#ffffff"  # 自定义：前置色... + 末尾为背景色
"""
import sys


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    # WCAG 相对亮度：sRGB 线性化
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg: str, bg: str) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    l1, l2 = max(l1, l2), min(l1, l2)
    return (l1 + 0.05) / (l2 + 0.05)


def verdict(ratio: float) -> str:
    """AA: 正文 >=4.5，大字/UI 元件 >=3"""
    if ratio >= 7:
        return 'PASS  AAA'
    if ratio >= 4.5:
        return 'PASS  AA'
    if ratio >= 3:
        return 'WARN  AA-large/UI only'
    return 'FAIL'


# 一套经过实算达标的浅色官网色板（可直接复用为设计 token）
DEFAULT_TOKENS = [
    ('--ink',        '#12211b'),
    ('--ink-2',      '#374b43'),
    ('--ink-3',      '#5c6f68'),
    ('--ink-4',      '#67766f'),
    ('--brand-700',  '#0b6e4f'),
    ('--brand-600',  '#008c43'),
    ('--up   涨',    '#c2372f'),
    ('--down 跌',    '#0e7d47'),
    ('chart-amber',  '#a8641a'),
]
BACKGROUNDS = [('#ffffff', 'card'), ('#f7faf9', 'sunk')]


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) >= 3:
        bg = argv[-1]
        pairs = [(c, c) for c in argv[:-1]]
        print(f'背景 {bg}')
        for name, c in pairs:
            r = contrast(c, bg)
            print(f'  {c:9s} {r:5.2f}:1  {verdict(r)}')
        return 0

    print('=== 对比度实算（WCAG 2.2）===')
    worst = 99.0
    for bg, bg_name in BACKGROUNDS:
        print(f'\n背景 {bg} ({bg_name})')
        for name, c in DEFAULT_TOKENS:
            r = contrast(c, bg)
            if bg_name == 'card':
                worst = min(worst, r)
            print(f'  {name:14s} {c:9s} {r:5.2f}:1  {verdict(r)}')
    print(f'\n最差（card 底）：{worst:.2f}:1')
    if worst < 4.5:
        print('!! 存在低于 AA 4.5:1 的正文色，必须调深后全量替换')
        return 1
    print('全部正文色达标 AA')
    return 0


if __name__ == '__main__':
    sys.exit(main())
