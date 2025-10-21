#!/usr/bin/env python3
"""
用法：
    python overlap.py your_log_file.log
输出（stdout）：
0 Agent=0 Hit=53 Hit0=0 Activate=92 HitRate=57.61%
1 Agent=68 Hit=44 Hit0=48 Activate=76 HitRate=57.89%
...
"""
import re
import sys
from pathlib import Path

GPU_NUM = 2

WARN_RE = re.compile(
    r".*?\[pf = 0\] agent_ids: \[(?P<agents>[^\]]+)\].*?lora_names: \[(?P<loras>[^\]]+)\]"
)
CRIT_RE = re.compile(
    r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?"
    r"Activate Agent: (?P<act>\{[^}]*\}),.*?Prefetch LoRA: (?P<pre>\{[^}]*\})"
)

def parse_agent_set(line: str) -> set[int] | None:
    m = WARN_RE.search(line)
    if not m:
        return None
    return {int(x.strip().strip("'")) for x in m["agents"].split(",") if x.strip()}

def parse_critical(line: str) -> tuple | None:
    m = CRIT_RE.search(line)
    if not m:
        return None
    act_set = {int(x) for x in eval(m["act"])}
    pre_set = {int(p.strip().replace("'", "").replace("lora", ""))
               for p in m["pre"].strip("{}").split(",") if p.strip()}
    hit = len(act_set & pre_set)
    hr = hit / len(act_set) * 100 if act_set else 0.0
    return act_set, hit, hr

def main(file_name: str):
    path = Path(file_name)
    if not path.exists():
        print(f"文件不存在：{file_name}", file=sys.stderr)
        sys.exit(1)

    lines = path.read_text(encoding="utf-8").splitlines()

    # --------- 阶段 1：开头连续 CRITICAL（无 WARNING） ---------
    phase1_crit = []
    for line in lines:
        if parse_critical(line) is None:
            break
        phase1_crit.append(line)

    # 打印阶段 1（Agent=0，Hit0=0）
    for g in range((len(phase1_crit) + GPU_NUM - 1) // GPU_NUM):
        round_id = g
        first_line = phase1_crit[g * GPU_NUM]
        act_set, hit, hr = parse_critical(first_line)
        print(f"{round_id} Agent=0 Hit={hit} Hit0=0 Activate={len(act_set)} HitRate={hr:.2f}%")

    # --------- 阶段 2：剩余“GPU_NUM 行 WARN + GPU_NUM 行 CRIT”成对 ---------
    warns, crits = [], []
    for line in lines[len(phase1_crit):]:
        if parse_agent_set(line) is not None:
            warns.append(line)
        elif parse_critical(line) is not None:
            crits.append(line)

    if len(warns) != len(crits) or len(warns) % GPU_NUM != 0:
        print("ERROR: 剩余段 WARNING/CRITICAL 行数不匹配或不是 GPU_NUM 倍数", file=sys.stderr)
        sys.exit(1)

    groups = len(warns) // GPU_NUM
    base_round = (len(phase1_crit) + GPU_NUM - 1) // GPU_NUM
    prev_agent_set = set()          # 初始为空
    for g in range(groups):
        round_id = base_round + g
        # 取组内第一行即可
        w_line = warns[g * GPU_NUM]
        c_line = crits[g * GPU_NUM]
        agent_set = parse_agent_set(w_line)
        act_set, hit, hr = parse_critical(c_line)
        if agent_set is None or act_set is None:
            continue
        hit0 = len(prev_agent_set & act_set)   # 上一组 agent_ids 与当前 Activate 交集
        print(f"{round_id} Agent={len(agent_set)} Hit={hit} Hit0={hit0} Activate={len(act_set)} HitRate={hr:.2f}%")
        prev_agent_set = agent_set             # 更新为当前组，供下一组使用

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python overlap.py <log_file>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])