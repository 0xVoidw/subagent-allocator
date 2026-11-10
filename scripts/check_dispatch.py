#!/usr/bin/env python3
"""检查 plan.dispatch.md 是否符合技能的输出约定。

用法：python3 scripts/check_dispatch.py <dispatch 文件> <对应的 plan 文件>
全部通过退出码为 0，否则逐条打印失败原因并退出码 1。
"""

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = ("总览", "执行阶段", "角色卡", "假设与注意事项", "预计节省")
REQUIRED_TABLE_COLUMNS = ("任务", "档位", "模型", "effort")
REQUIRED_CARD_FIELDS = ("角色", "目标", "输入", "约束", "完成标准", "返回格式", "升级阶梯")
VALID_TIERS = ("T0", "T1", "T2", "T3")
PLATFORM_RE = re.compile(
    r"^来源[：:].*?平台[：:]\s*(claude|codex|both)(?=\s|$)",
    re.MULTILINE | re.IGNORECASE,
)
REFERENCE_DIR = Path(__file__).resolve().parent.parent / "skills" / "subagent-allocator" / "references"


def split_section(lines, title):
    """返回指定二级标题下的行列表（不含标题本身）。找不到返回 None。"""
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^##\s+%s\s*$" % re.escape(title), line):
            start = index + 1
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        if re.match(r"^##\s+", lines[index]):
            end = index
            break
    return lines[start:end]


def parse_table(section_lines):
    """从总览小节里解析第一张表，返回 (表头, 数据行列表)。"""
    header = None
    rows = []
    for line in section_lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header is not None:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell):
            continue
        rows.append(cells)
    return header, rows


def normalize_model(value):
    value = value.replace("`", "").replace("*", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value.casefold()


def parse_documented_models(path):
    """从参考文件的“档位 → 模型”表中提取模型名。"""
    names = set()
    header = None
    model_indexes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = None
            model_indexes = []
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if header is None:
            if "模型" in cells:
                header = cells
                model_indexes = [
                    index for index, cell in enumerate(cells) if cell in ("模型", "模型 ID")
                ]
                if not model_indexes:
                    header = None
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell):
            continue
        for index in model_indexes:
            if index >= len(cells):
                continue
            cleaned = cells[index].replace("`", "").replace("*", "").strip()
            if cleaned and cleaned not in ("—", "-", "无"):
                names.add(normalize_model(cleaned))
    return names


def load_documented_models(platform, errors):
    if platform == "both":
        paths = [REFERENCE_DIR / "claude.md", REFERENCE_DIR / "codex.md"]
    elif platform == "claude":
        paths = [REFERENCE_DIR / "claude.md"]
    else:
        paths = [REFERENCE_DIR / "codex.md"]

    names = set()
    for path in paths:
        if not path.is_file():
            errors.append("找不到参考文件：%s" % path)
            continue
        names |= parse_documented_models(path)
    if not names:
        errors.append("无法从参考文件中解析出任何模型名")
    return names


def main(argv):
    if len(argv) < 3:
        print("用法：python3 scripts/check_dispatch.py <dispatch 文件> <plan 文件>")
        return 2

    dispatch_path = Path(argv[1])
    plan_path = Path(argv[2])
    errors = []

    if not dispatch_path.is_file():
        print("FAIL 找不到 dispatch 文件：%s" % dispatch_path)
        return 1
    if not plan_path.is_file():
        errors.append("找不到对应的 plan 文件：%s" % plan_path)

    text = dispatch_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    for section in REQUIRED_SECTIONS:
        if split_section(lines, section) is None:
            errors.append("缺少二级标题：## %s" % section)

    overview = split_section(lines, "总览")
    header = None
    rows = []
    if overview is not None:
        header, rows = parse_table(overview)
        if header is None:
            errors.append("总览下没有表格")
        else:
            for column in REQUIRED_TABLE_COLUMNS:
                if not any(
                    cell == column or (column == "effort" and cell.lower() == "effort")
                    for cell in header
                ):
                    errors.append("总览表头缺少列：%s" % column)

    total_tasks = 0
    t3_tasks = 0
    if header is not None:
        tier_index = header.index("档位") if "档位" in header else None
        model_index = header.index("模型") if "模型" in header else None

        platform_match = PLATFORM_RE.search(text)
        documented_models = set()
        if platform_match is None:
            errors.append("找不到合法的平台声明（应在“来源”行写明 平台：claude / codex / both）")
        else:
            platform = platform_match.group(1).lower()
            documented_models = load_documented_models(platform, errors)

        for row_number, cells in enumerate(rows, start=1):
            if len(cells) != len(header):
                errors.append("总览表第 %d 行数据列的个数与表头不一致" % row_number)
                continue
            total_tasks += 1

            if tier_index is not None:
                tier = cells[tier_index]
                if tier not in VALID_TIERS:
                    errors.append(
                        "总览表第 %d 行的档位取值非法：%r（只允许 T0/T1/T2/T3）"
                        % (row_number, tier)
                    )
                if tier == "T3":
                    t3_tasks += 1

            if model_index is None:
                continue
            model_cell = cells[model_index]
            if model_cell in ("", "—", "-", "无"):
                continue
            for model in re.split(r"\s*[/、，,]\s*", model_cell):
                model = model.strip()
                if not model:
                    continue
                if documented_models and normalize_model(model) not in documented_models:
                    errors.append(
                        "总览表第 %d 行的模型名 %r 不是参考文件中记录的模型名"
                        % (row_number, model)
                    )

    if total_tasks == 0:
        errors.append("总览表没有数据行")
    elif t3_tasks * 3 > total_tasks:
        errors.append("T3 任务为 %d 个，超过任务总数 %d 的三分之一" % (t3_tasks, total_tasks))

    cards = split_section(lines, "角色卡")
    if cards is not None:
        card_starts = [i for i, line in enumerate(cards) if re.match(r"^###\s+", line)]
        if not card_starts:
            errors.append("角色卡小节里没有任何角色卡")
        for position, start in enumerate(card_starts):
            end = card_starts[position + 1] if position + 1 < len(card_starts) else len(cards)
            block = "\n".join(cards[start:end])
            title = cards[start].strip()
            for field in REQUIRED_CARD_FIELDS:
                if not re.search(r"^\s*-\s*\*\*%s\*\*" % re.escape(field), block, re.MULTILINE):
                    errors.append("角色卡「%s」缺少字段：%s" % (title, field))

    if errors:
        for message in errors:
            print("FAIL %s" % message)
        return 1

    print("PASS dispatch 检查通过：%d 个任务，T3 ×%d" % (total_tasks, t3_tasks))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
