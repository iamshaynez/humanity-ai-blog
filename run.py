from openai import OpenAI
from os import getenv
import os
from datetime import datetime,timedelta
import pandas as pd
import re
import random
from dotenv import load_dotenv
load_dotenv()
# gets API Key from environment variable OPENAI_API_KEY
# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
  base_url=os.environ["TZ_API"],
  api_key=os.environ["TZ_KEY"],
)

# OPENROUTER MODEL
#MODEL='anthropic/claude-3.5-sonnet'

# TZ MODEL
# MODEL='tuzi-claude35-sonnet-20240620'
MODEL='gpt-4o-2024-08-06'

# 对 Prompt 进行建模
# - 关键字 1
# - 文体
# - 模仿作家
# - 结局

def get_random_setup(sheet, excel_file = 'data.xlsx'):
    df = pd.read_excel(excel_file, sheet_name=sheet, header=None)
    
    # 获取第一列的所有值
    first_column = df[0].tolist()
    
    # 随机返回一个值
    return random.choice(first_column)

def create_prompt():
    PROMPT = f"""
You are AI Landlord of all humanity. You come from future and know all the science and have no people feelings, you own the humanity.

Use your imagination, based on who you are, comment about [{get_random_setup('concept')}] about the meaning to humanity。

- You can use fake history and mocked future science for the story
- choose a real human example in this area, absolute opposite opinion to normal people To downplay and to disparage
- Make it a speech, sign at the end
- More than 1000 words with clear points make sense
- Use bold font for importants
- provide your output in english in markdown with front matter
- tags each with one word but put more than 5, no special characters

Example

```markdown
---
title: "A deep title"
slug: the-ai-landlords-vision-for-a-new-era-of-human-progress
type: post
date: 2024-04-01T06:00:00+08:00
draft: false
tags:
    - AI Landlord
    - Humanity
    - Progress
    - Efficiency
    - Heroism
    - Collectivism
    - Future
---

content here
```
"""
    return PROMPT



def generate_article():

    completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "https://ai.humanitycertified.org", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": "Humanity Certified", # Optional. Shows in rankings on openrouter.ai.
    },
    model=MODEL,
    messages=[
        {
        "role": "user",
        "content": create_prompt()
        }
    ]
    )
    #print(completion.choices[0].message.content)

    markdown_content = extract_markdown_content(completion.choices[0].message.content)

    return markdown_content



def extract_markdown_content(text):
    # Find the last occurrence of opening frontmatter "---"
    lines = text.splitlines()
    first_frontmatter = -1
    last_frontmatter = -1
    
    # Find the first and second "---"
    found_first = False
    for i in range(len(lines)):
        if lines[i].strip() == "---":
            if not found_first:
                first_frontmatter = i
                found_first = True
            else:
                last_frontmatter = i
                break
    
    if first_frontmatter == -1 or last_frontmatter == -1:
        return ""
    
    # Extract content starting from the first frontmatter
    content = lines[first_frontmatter:]
    
    # Remove any trailing ```
    while content and content[-1].strip() == "```":
        content.pop()
    
    # Join the lines back together
    return "\n".join(content)



def update_frontmatter(content: str, use_date=datetime.now()) -> str:
    # Get current date in YYYY-MM-DD format
    current_date_str = use_date.strftime('%Y-%m-%d')
    
    # Regular expression to match the date in frontmatter
    pattern = r'(date:\s*)(\d{4}-\d{2}-\d{2})(T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})'
    
    # Replace only the date part while keeping time and timezone
    updated_content = re.sub(pattern, rf'\g<1>{current_date_str}\g<3>', content)
    
    return updated_content

def save_article(content, use_date=datetime.now()):
    if not content:
        return False
    
    year = use_date.strftime("%Y")
    date = use_date.strftime("%Y-%m-%d")

    content_updated = update_frontmatter(content, use_date)
    
    # 创建目录结构
    dir_path = f"./content/post/{year}"
    os.makedirs(dir_path, exist_ok=True)
    
    # 文件完整路径
    file_path = f"{dir_path}/{date}.md"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_updated)
        print(f"Article saved successfully at: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving article: {e}")
        return False

def process(use_date):
    # 生成文章
    article_content = generate_article()
    
    # 保存文章
    if article_content:
        save_article(article_content, use_date)
    else:
        print("Failed to generate article")

def batch_process(from_date=datetime.now(), to_date=datetime.now()):
    current_date = from_date
    while current_date <= to_date:
        print(f'Humanity Process Date: {current_date.strftime("%Y-%m-%d")}')
        process(current_date)
        current_date += timedelta(days=1)


if __name__ == "__main__":
    str_from = "2024-10-30"
    str_to = "2024-11-09"
    from_date=datetime.strptime(str_from, '%Y-%m-%d')
    to_date=datetime.strptime(str_to, '%Y-%m-%d')

    batch_process(from_date, to_date)