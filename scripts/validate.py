#!/usr/bin/env python3
"""校验 subagent-allocator 技能目录的结构与格式。

用法：python3 scripts/validate.py [技能目录]
默认技能目录为 skills/subagent-allocator。
全部通过退出码为 0，否则逐条打印失败原因并退出码 1。
"""

import re
import sys
from pathlib import Path

DEFAULT_SKILL_DIR = Path("skills/subagent-allocator")
FRONTMATTER_NAME_RE = re.compile(r"^[a-z0-9-]+$")
REFERENCE_PATH_RE = re.compile(r"references/[A-Za-z0-9._/-]+\.md")
REFERENCE_TOKEN_RE = re.compile(r"references/[A-Za-z0-9._/-]+")
TRAILING_PUNCTUATION = ".,;:!?，。；：！？"
UPGRADE_HEADING_RE = re.compile(r"^#{1,6}\s*升级阶梯\s*$", re.MULTILINE)
REQUIRED_KEYS = ("name", "description")
REQUIRED_TIERS = ("T0", "T1", "T2", "T3")


def parse_frontmatter(text):
    """返回 (frontmatter 字典, 正文行列表)。格式不完整时返回 (None, None)。"""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None, None
    closing = None
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            closing = index
            break
    if closing is None:
        return None, None

    frontmatter = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace():
            # 缩进行是嵌套键，不属于顶层 frontmatter
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        frontmatter[key] = value
    return frontmatter, lines[closing + 1:]


def mentioned_reference_paths(text):
    """从 SKILL.md 中提取被提及的 references 路径，去掉行尾标点。"""
    paths = set()
    for token in REFERENCE_TOKEN_RE.findall(text):
        paths.add(token.rstrip(TRAILING_PUNCTUATION))
    return paths


def check_frontmatter(skill_dir, text, errors):
    frontmatter, body = parse_frontmatter(text)
    if frontmatter is None:
        errors.append("SKILL.md 缺少完整的 YAML frontmatter（需以 --- 开头并以第二个 --- 结束）")
        return

    for key in REQUIRED_KEYS:
        if key not in frontmatter:
            errors.append("frontmatter 缺少必需的键：%s" % key)
        elif not frontmatter[key]:
            errors.append("frontmatter 的 %s 值为空" % key)

    name = frontmatter.get("name", "")
    if name and not FRONTMATTER_NAME_RE.fullmatch(name):
        errors.append("frontmatter 的 name 只能包含小写字母、数字和连字符：%r" % name)
    if name and name != skill_dir.name:
        errors.append("frontmatter 的 name（%r）与技能目录名（%r）不一致" % (name, skill_dir.name))

    description = frontmatter.get("description", "")
    if len(description) > 1024:
        errors.append("description 长度为 %d，超过 1024 个字符" % len(description))

    body_line_count = len(body)
    if body_line_count > 500:
        errors.append("SKILL.md 正文为 %d 行，超过 500 行" % body_line_count)


def check_references(skill_dir, text, errors):
    references_dir = skill_dir / "references"

    for relative in sorted(set(REFERENCE_PATH_RE.findall(text))):
        if not (skill_dir / relative).is_file():
            errors.append("SKILL.md 引用了不存在的文件：%s" % relative)

    if not references_dir.is_dir():
        errors.append("缺少 references/ 目录")
        return

    reference_files = sorted(
        path for path in references_dir.rglob("*") if path.is_file()
    )
    if not reference_files:
        errors.append("references/ 目录为空")
    mentioned = mentioned_reference_paths(text)
    for path in reference_files:
        relative = path.relative_to(skill_dir).as_posix()
        if relative not in mentioned:
            errors.append("references/ 下的文件未在 SKILL.md 中提及：%s" % relative)


def check_code_fences(skill_dir, errors):
    for path in sorted(skill_dir.rglob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            errors.append("无法读取 %s：%s" % (path, exc))
            continue
        fence_count = sum(1 for line in lines if line.strip().startswith("```"))
        if fence_count % 2 != 0:
            relative = path.relative_to(skill_dir).as_posix()
            errors.append("%s 的围栏代码块标记数量为奇数（%d），存在未闭合代码块" % (relative, fence_count))


def check_tier_references(skill_dir, errors):
    for filename in ("claude.md", "codex.md"):
        path = skill_dir / "references" / filename
        if not path.is_file():
            errors.append("缺少 references/%s" % filename)
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append("无法读取 %s：%s" % (path, exc))
            continue
        for tier in REQUIRED_TIERS:
            if tier not in text:
                errors.append("references/%s 缺少档位 %s" % (filename, tier))
        if not UPGRADE_HEADING_RE.search(text):
            errors.append("references/%s 缺少“升级阶梯”小节" % filename)


def main(argv):
    skill_dir = Path(argv[1]) if len(argv) > 1 else DEFAULT_SKILL_DIR
    errors = []

    if not skill_dir.is_dir():
        print("FAIL 技能目录不存在：%s" % skill_dir)
        return 1
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print("FAIL 缺少 SKILL.md：%s" % skill_md)
        return 1

    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print("FAIL 无法读取 SKILL.md：%s" % exc)
        return 1

    check_frontmatter(skill_dir, text, errors)
    check_references(skill_dir, text, errors)
    check_code_fences(skill_dir, errors)
    check_tier_references(skill_dir, errors)

    if errors:
        for message in errors:
            print("FAIL %s" % message)
        return 1

    print("PASS 技能结构校验通过：%s" % skill_dir.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
