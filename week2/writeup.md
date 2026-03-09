# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
# 任务
实现extract_action_items_llm

## 描述
你的任务是实现一个由 LLM 驱动的替代方案， extract_action_items_llm() ，该方案利用 Ollama 通过大型语言模型执行行动项提取。

## 关键点

1. 只提取待办事项或下一步行动。
2. 不要输出背景信息、解释或总结。
3. 每条任务尽量简短清楚。
4. 去掉重复内容。
5. 如果没有待办事项，返回空数组。
6. 只返回 JSON 字符串数组，例如：
["更新 README", "编写单元测试"]


## 调用大模型的
我们使用python调用ollama实现，相关的调用方式为：

Using the Ollama Python library, pass in the schema as a JSON object to the format parameter as either dict or use Pydantic (recommended) to serialize the schema using model_json_schema().

<function_call_example>
from ollama import chat
from pydantic import BaseModel

class Country(BaseModel):
  name: str
  capital: str
  languages: list[str]

response = chat(
  messages=[
    {
      'role': 'user',
      'content': 'Tell me about Canada.',
    }
  ],
  model='llama3.1',
  format=Country.model_json_schema(),
)

country = Country.model_validate_json(response.message.content)
print(country)
<function_call_example>

<function_output>
name='Canada' capital='Ottawa' languages=['English', 'French']
<function_output>

## 原始实现
<origin_code>
def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique
<origin_code>
请根据上述内容，实现llm版本的抽取函数:

``` 

Generated Code Snippets:
```
def extract_action_items_llm(text: str, model: str = DEFAULT_OLLAMA_MODEL) -> List[str]:
    text = text.strip()
    if not text:
        return []
    if chat is None:
        raise RuntimeError("ollama is not installed. Install it before using extract_action_items_llm.")

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract action items from notes. Return only a JSON array of strings."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Read the note and extract all action items or next steps. "
                    "Only include tasks that someone still needs to do. "
                    "Do not include background information, explanations, or summaries. "
                    "Keep each task short and clear. Remove duplicates. "
                    "If there are no action items, return [].\n\n"
                    f"Note:\n{text}"
                ),
            },
        ],
        format=ActionItemsResponse.model_json_schema(),
    )

    parsed = ActionItemsResponse.model_validate_json(response.message.content)
    return _normalize_action_items(parsed.root)

```

### Exercise 2: Add Unit Tests
Prompt: 
```
在 test_extract.py 增加LLM 版测试，覆盖结构化输出、前缀清理、空输入不调用模型。
``` 

Generated Code Snippets:
```

def test_extract_action_items_llm_returns_structured_items(monkeypatch):
    def fake_chat(*, model, messages, format):
        assert model == "test-model"
        assert messages[1]["content"].endswith("Note:\n- [ ] Set up database\n- Write tests")
        assert format == extract.ActionItemsResponse.model_json_schema()
        return SimpleNamespace(
            message=SimpleNamespace(
                content='["Set up database", "Write tests", "Set up database"]'
            )
        )

    monkeypatch.setattr(extract, "chat", fake_chat)

    items = extract_action_items_llm("- [ ] Set up database\n- Write tests", model="test-model")

    assert items == ["Set up database", "Write tests"]


def test_extract_action_items_llm_cleans_prefixes(monkeypatch):
    def fake_chat(*, model, messages, format):
        return SimpleNamespace(
            message=SimpleNamespace(content='["- [ ] Update README", "1. Write tests"]')
        )

    monkeypatch.setattr(extract, "chat", fake_chat)

    items = extract_action_items_llm("todo: update follow-up tasks")

    assert items == ["Update README", "Write tests"]


def test_extract_action_items_llm_skips_empty_input(monkeypatch):
    def fake_chat(*, model, messages, format):
        raise AssertionError("chat should not be called for empty input")

    monkeypatch.setattr(extract, "chat", fake_chat)

    assert extract_action_items_llm("   ") == []

```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
# Task
refactor existing code for clarity.

## rule:
MUST focusing in particular on these points:
- well-defined API contracts/schemas 
- database layer cleanup
- app lifecycle
- configuration
- error handling

REFACTOR CODE:
``` 

Generated/Modified Code Snippets:
```
8 files changed
+387
-177

week2/app/config.py
week2/app/db.py
week2/app/main.py
week2/app/routers/action_items.py
week2/app/routers/notes.py
week2/app/schemas.py
week2/app/services/extract.py
week2/tests/test_api.py


```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
把llm的版本替换掉原有的extract，并做到能在前端测试
``` 

Generated Code Snippets:
```
4 files changed +46 -7

week2/app/main.py +5 -0
week2/app/routers/action_items.py +4 -4
week2/frontend/index.html +10 -3
week2/tests/test_api.py +27 -0

```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
生成一个完整的README.md文档，介绍这个项目的背景、目的、启动方式
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 