#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编译滚动时间轴 -> timeline.json

唯一事实源：本脚本输出的 timeline.json 是页面控制器读取的唯一时间常量来源。
页面内不得维护第二份时间常量。

语义对齐 oil-motion references/runtime.md：
  - start <= hold < endExclusive
  - states 顺序与 segments 的 from -> to 一致
  - 所有时间由编译结果生成，不手工抄写

本脚本面向 page-owned 背景 + 程序驱动滚动动画（无生成视频/图集），
因此时间单位为「归一化滚动进度 0..1」，fps 仅记录程序动画目标帧率。

用法：
    # 1) 用章节配置文件（推荐）
    python compile_timeline.py --chapters chapters.json --out build/timeline.json

    # 2) 命令行直接给章节（id:标签:权重，权重可省略默认 1.0）
    python compile_timeline.py \
        --section hero:首页:1.0 \
        --section overview:产品总览:0.85 \
        --section detail:详情:1.35 \
        --out build/timeline.json

chapters.json 格式（数组即顺序）：
    [
      {"id": "hero",     "label": "首页",     "sub": "品牌露出",  "weight": 1.0},
      {"id": "overview", "label": "产品总览", "sub": "三大模块",  "weight": 0.85},
      {"id": "detail",   "label": "详情",     "sub": "数据看板",  "weight": 1.35}
    ]
"""
import argparse
import json
import os
import sys

FPS_DEFAULT = 60.0
# 章节内：前占比为转场推进，其余为稳定停留（停帧）
ADVANCE_RATIO = 0.45


def parse_section(spec: str) -> dict:
    """解析 'id:标签:权重' 形式的章节定义。"""
    parts = spec.split(':')
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            f"--section 需要 'id:标签[:权重]' 形式，收到：{spec}"
        )
    cid, label = parts[0].strip(), parts[1].strip()
    weight = float(parts[2]) if len(parts) > 2 and parts[2].strip() else 1.0
    return {"id": cid, "label": label, "sub": "", "weight": weight}


def load_chapters(args) -> list:
    if args.chapters:
        with open(args.chapters, encoding='utf-8') as f:
            raw = json.load(f)
        if not isinstance(raw, list) or not raw:
            sys.exit("[err] chapters 文件必须是非空数组")
        out = []
        for i, c in enumerate(raw):
            cid = c.get('id')
            if not cid:
                sys.exit(f"[err] chapters[{i}] 缺少 id")
            out.append({
                "id": cid,
                "label": c.get('label', cid),
                "sub": c.get('sub', ''),
                "weight": float(c.get('weight', 1.0)),
            })
        return out
    if args.section:
        return args.section
    sys.exit("[err] 需要 --chapters 或至少一个 --section")


def build(chapters: list, fps: float) -> dict:
    ids = [c["id"] for c in chapters]
    if len(ids) != len(set(ids)):
        dup = sorted({x for x in ids if ids.count(x) > 1})
        sys.exit(f"[err] 章节 id 重复：{dup}")
    for c in chapters:
        if c["weight"] <= 0:
            sys.exit(f"[err] 章节 {c['id']} 权重必须为正数")

    total_weight = sum(c["weight"] for c in chapters)
    segments, states = [], []
    cursor = 0.0

    for i, c in enumerate(chapters):
        span = c["weight"] / total_weight
        start = round(cursor, 6)
        hold = round(cursor + span * ADVANCE_RATIO, 6)
        end_ex = round(cursor + span, 6)

        if i == 0:
            states.append({"id": c["id"], "label": c["label"], "hold": start})

        segments.append({
            "id": f"seg-{c['id']}",
            "from": chapters[i - 1]["id"] if i > 0 else None,
            "to": c["id"],
            "start": start,
            "hold": hold,
            "endExclusive": end_ex,
            "curve": {"type": "edge-mid-edge", "edgeRate": 1.6, "midRate": 0.85},
        })
        if i > 0:
            states.append({"id": c["id"], "label": c["label"], "hold": hold})
        cursor = end_ex

    # 末段收尾：把总进度归一到 1.0（浮点累积误差修正）
    if segments:
        last = segments[-1]
        scale = 1.0 / last["endExclusive"] if last["endExclusive"] else 1.0
        if abs(scale - 1.0) > 1e-9:
            for s in segments:
                s["start"] = round(s["start"] * scale, 6)
                s["hold"] = round(s["hold"] * scale, 6)
                s["endExclusive"] = round(s["endExclusive"] * scale, 6)
            for s in states:
                s["hold"] = round(s["hold"] * scale, 6)
        segments[-1]["endExclusive"] = 1.0

    hold_of = {s["id"]: s["hold"] for s in states}
    return {
        "schemaVersion": 1,
        "fps": fps,
        "frameDuration": round(1.0 / fps, 8),
        "initialState": chapters[0]["id"],
        "progressUnit": "normalized-scroll-progress",
        "totalProgress": 1.0,
        "states": states,
        "segments": segments,
        "chapters": [
            {"id": c["id"], "label": c["label"], "sub": c["sub"],
             "hold": hold_of[c["id"]]}
            for c in chapters
        ],
        "generatedFrom": "chapters 配置",
        "backgroundOwner": "page",
        "controller": "frame-scrub",
    }


def validate(tl: dict) -> None:
    """硬性语义校验，任一失败即拒绝写出。"""
    states, segments = tl["states"], tl["segments"]
    assert states, "states 不能为空"
    assert segments, "segments 不能为空"
    assert len(states) == len(segments), \
        "states 数量必须等于 segments 数量（首段 start 即 state0）"
    assert states[0]["hold"] == segments[0]["start"], \
        "初始 state hold 必须对应第一段 start"

    for idx, seg in enumerate(segments):
        assert seg["start"] <= seg["hold"] < seg["endExclusive"], \
            f"segment {idx} 违反 start<=hold<endExclusive"
        if idx > 0:
            prev = segments[idx - 1]
            assert seg["start"] >= prev["endExclusive"] - 1e-9, \
                f"segment {idx} 与上一段重叠"
            assert abs(seg["start"] - prev["endExclusive"]) < 1e-5, \
                f"segment {idx} 与上一段之间存在空隙"
            assert seg["from"] == prev["to"], \
                f"segment {idx} 的 from 与上段 to 不连续"
    ids = [s["id"] for s in states]
    assert len(ids) == len(set(ids)), "state id 必须唯一"
    assert all(s["id"] for s in states), "state id 不能为空"
    assert abs(segments[-1]["endExclusive"] - 1.0) < 1e-5, \
        "末段 endExclusive 必须收敛到 1.0"


def main() -> int:
    ap = argparse.ArgumentParser(
        description='编译滚动驱动主页的 timeline.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--chapters', help='章节配置文件（JSON 数组）')
    ap.add_argument('--section', action='append', type=parse_section,
                    help="章节，形式 'id:标签[:权重]'，可重复；顺序即章节顺序")
    ap.add_argument('--out', default='timeline.json', help='输出路径')
    ap.add_argument('--fps', type=float, default=FPS_DEFAULT,
                    help=f'程序动画目标帧率（默认 {FPS_DEFAULT:g}）')
    args = ap.parse_args()

    chapters = load_chapters(args)
    tl = build(chapters, args.fps)

    try:
        validate(tl)
    except AssertionError as e:
        sys.exit(f"[err] 时间轴语义校验失败，拒绝写出：{e}")

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(tl, f, ensure_ascii=False, indent=2)

    print(f"[ok] {args.out} 写出：{len(tl['states'])} states / "
          f"{len(tl['segments'])} segments")
    for s in tl["segments"]:
        print(f"     {s['id']:<18} start={s['start']:.6f}  "
              f"hold={s['hold']:.6f}  endEx={s['endExclusive']:.6f}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
