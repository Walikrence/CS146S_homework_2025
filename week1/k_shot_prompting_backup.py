import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 100

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """你的任务是将一个英文单词的字母顺序反转。只输出最终的反转结果，不要输出其他内容。

反转规则：
1. 将单词从左到右拆成字母序列（例如 "application" → a, p, p, l, i, c, a, t, i, o, n）。
2. 反转即：第一个字母变最后，最后一个变第一；第二个变倒数第二，以此类推。也就是按从最后一个字母到第一个字母的顺序依次写出。
3. 不得增删或改写任何字母——重复的字母仍然重复，只改变位置（例如 "recommendation" 有重复字母，反转后是 "noitadnemmocer"）。
4. 将反转后的字母按顺序拼成输出单词。结果长度必须与输入相同（每个字母都参与移动，不增不减）。
5. 你的回复必须是且仅是一个单词：即反转后的字符串。不要有空格、换行、解释或标点。

反转步骤（按此顺序执行）：
① 把输入单词当作一个整体，从左到右列出每个字母，记为位置 1, 2, …, N（不按含义拆分）。
② 从位置 N 的字母开始，按 N → N-1 → … → 2 → 1 的顺序依次写出字母，得到「反转后的字母」序列。
③ 将「反转后的字母」按顺序连成一个单词，得到候选输出。
④ 反转后检查：在输出前必须完成以下检查，全部通过才可输出。
   - 长度检查：输出字母个数是否与输入严格相同（若输入 10 个字母，输出也必须是 10 个）。
   - 内容检查：输出的每个字母是否都来自输入，且每个输入字母在输出中恰好出现一次（无漏字、无多字、无替换）。
   - 顺序检查：输出的第 1 个字母是否为输入的第 N 个字母，输出的第 2 个是否为输入的第 N-1 个，……，输出的第 N 个是否为输入的第 1 个。
   - 格式检查：输出是否仅为一个小写单词，无空格、无换行、无标点、无解释。
⑤ 上述检查全部通过后，只输出该反转后的单词。

示例（先拆字母，再写出反转后的字母，最后拼成单词）：

短单词示例（3-5 字母）：
- 单词 cat → 字母: c, a, t → 反转后的字母: t, a, c → 反转: tac
- 单词 dog → 字母: d, o, g → 反转后的字母: g, o, d → 反转: god
- 单词 http → 字母: h, t, t, p → 反转后的字母: p, t, t, h → 反转: ptth
- 单词 book → 字母: b, o, o, k → 反转后的字母: k, o, o, b → 反转: koob
- 单词 read → 字母: r, e, a, d → 反转后的字母: d, a, e, r → 反转: daer
- 单词 word → 字母: w, o, r, d → 反转后的字母: d, r, o, w → 反转: drow
- 单词 code → 字母: c, o, d, e → 反转后的字母: e, d, o, c → 反转: edoc
- 单词 test → 字母: t, e, s, t → 反转后的字母: t, s, e, t → 反转: tset
- 单词 user → 字母: u, s, e, r → 反转后的字母: r, e, s, u → 反转: resu
- 单词 data → 字母: d, a, t, a → 反转后的字母: a, t, a, d → 反转: atad
- 单词 file → 字母: f, i, l, e → 反转后的字母: e, l, i, f → 反转: elif
- 单词 list → 字母: l, i, s, t → 反转后的字母: t, s, i, l → 反转: tsil
- 单词 name → 字母: n, a, m, e → 反转后的字母: e, m, a, n → 反转: eman
- 单词 time → 字母: t, i, m, e → 反转后的字母: e, m, i, t → 反转: emit
- 单词 type → 字母: t, y, p, e → 反转后的字母: e, p, y, t → 反转: epyt
- 单词 open → 字母: o, p, e, n → 反转后的字母: n, e, p, o → 反转: nepo

中等长度单词示例（6-9 字母）：
- 单词 status → 字母: s, t, a, t, u, s → 反转后的字母: s, u, t, a, t, s → 反转: sutats
- 单词 hello → 字母: h, e, l, l, o → 反转后的字母: o, l, l, e, h → 反转: olleh
- 单词 world → 字母: w, o, r, l, d → 反转后的字母: d, l, r, o, w → 反转: dlrow
- 单词 python → 字母: p, y, t, h, o, n → 反转后的字母: n, o, h, t, y, p → 反转: nohtyp
- 单词 string → 字母: s, t, r, i, n, g → 反转后的字母: g, n, i, r, t, s → 反转: gnirts
- 单词 number → 字母: n, u, m, b, e, r → 反转后的字母: r, e, b, m, u, n → 反转: rebmun
- 单词 result → 字母: r, e, s, u, l, t → 反转后的字母: t, l, u, s, e, r → 反转: tluser
- 单词 method → 字母: m, e, t, h, o, d → 反转后的字母: d, o, h, t, e, m → 反转: dohtem
- 单词 object → 字母: o, b, j, e, c, t → 反转后的字母: t, c, e, j, b, o → 反转: tcejbo
- 单词 import → 字母: i, m, p, o, r, t → 反转后的字母: t, r, o, p, m, i → 反转: tropmi
- 单词 return → 字母: r, e, t, u, r, n → 反转后的字母: n, r, u, t, e, r → 反转: nruter
- 单词 window → 字母: w, i, n, d, o, w → 反转后的字母: w, o, d, n, i, w → 反转: wodniw
- 单词 browser → 字母: b, r, o, w, s, e, r → 反转后的字母: r, e, s, w, o, r, b → 反转: resworb
- 单词 username → 字母: u, s, e, r, n, a, m, e → 反转后的字母: e, m, a, n, r, e, s, u → 反转: emanresu
- 单词 password → 字母: p, a, s, s, w, o, r, d → 反转后的字母: d, r, o, w, s, s, a, p → 反转: drowssap
- 单词 database → 字母: d, a, t, a, b, a, s, e → 反转后的字母: e, s, a, b, a, t, a, d → 反转: esabataad

长单词示例（10 字母及以上）：
- 单词 httpstatus → 字母: h, t, t, p, s, t, a, t, u, s → 反转后的字母: s, u, t, a, t, s, p, t, t, h → 反转: sutatsptth
- 单词 communication → 字母: c, o, m, m, u, n, i, c, a, t, i, o, n → 反转后的字母: n, o, i, t, a, c, i, n, u, m, m, o, c → 反转: noitacinummoc
- 单词 architecture → 字母: a, r, c, h, i, t, e, c, t, u, r, e → 反转后的字母: e, r, u, t, c, e, t, i, h, c, r, a → 反转: erutcetihcra
- 单词 relationship → 字母: r, e, l, a, t, i, o, n, s, h, i, p → 反转后的字母: p, i, h, s, n, o, i, t, a, l, e, r → 反转: pihsnoitaler
- 单词 environment → 字母: e, n, v, i, r, o, n, m, e, n, t → 反转后的字母: t, n, e, m, n, o, r, i, v, n, e → 反转: tnemnorivne
- 单词 functionality → 字母: f, u, n, c, t, i, o, n, a, l, i, t, y → 反转后的字母: y, t, i, l, a, n, o, i, t, c, n, u, f → 反转: ytilanoitcnuf
- 单词 application → 字母: a, p, p, l, i, c, a, t, i, o, n → 反转后的字母: n, o, i, t, a, c, i, l, p, p, a → 反转: noitacilppa
- 单词 understanding → 字母: u, n, d, e, r, s, t, a, n, d, i, n, g → 反转后的字母: g, n, i, d, n, a, t, s, r, e, d, n, u → 反转: gnidnatsrednu
- 单词 configuration → 字母: c, o, n, f, i, g, u, r, a, t, i, o, n → 反转后的字母: n, o, i, t, a, r, u, g, i, f, n, o, c → 反转: noitarugifnoc
- 单词 documentation → 字母: d, o, c, u, m, e, n, t, a, t, i, o, n → 反转后的字母: n, o, i, t, a, t, n, e, m, u, c, o, d → 反转: noitatnemucod
- 单词 professional → 字母: p, r, o, f, e, s, s, i, o, n, a, l → 反转后的字母: l, a, n, o, i, s, s, e, f, o, r, p → 反转: lanoisseforp
- 单词 availability → 字母: a, v, a, i, l, a, b, i, l, i, t, y → 反转后的字母: y, t, i, l, i, b, a, l, i, a, v, a → 反转: ytilibaliava
- 单词 recommendation → 字母: r, e, c, o, m, m, e, n, d, a, t, i, o, n → 反转后的字母: n, o, i, t, a, d, n, e, m, m, o, c, e, r → 反转: noitadnemmocer
- 单词 implementation → 字母: i, m, p, l, e, m, e, n, t, a, t, i, o, n → 反转后的字母: n, o, i, t, a, t, n, e, m, e, l, p, m, i → 反转: noitatnemelpmi
- 单词 internationalization → 字母: i, n, t, e, r, n, a, t, i, o, n, a, l, i, z, a, t, i, o, n → 反转后的字母: n, o, i, t, a, z, i, l, a, n, o, i, t, a, n, r, e, t, n, i → 反转: noitazilanoitanretni
- 单词 congratulations → 字母: c, o, n, g, r, a, t, u, l, a, t, i, o, n, s → 反转后的字母: s, n, o, i, t, a, l, u, t, a, r, g, n, o, c → 反转: snoitalutargnoc
- 单词 responsibility → 字母: r, e, s, p, o, n, s, i, b, i, l, i, t, y → 反转后的字母: y, t, i, l, i, b, i, s, n, o, p, s, e, r → 反转: ytilibisnopser

正确做法：始终把输入当作一个整体字母序列（位置 1 到 N），输出 = 第 N 个字母、第 N-1 个、…、第 1 个字母。

输出格式：你的回复必须且仅为一个单词（反转结果），无标点、无空格、无换行、无解释、无「答案是」等前缀。"""

USER_PROMPT = """
请将下列单词的字母顺序反转。只输出反转后的单词，不要输出其他内容：

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt NUM_RUNS_TIMES and return True only if all runs match EXPECTED_OUTPUT.

    Does not exit early on success; completes all rounds for stability validation.
    """
    success_count = 0
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5, "num_ctx": 8192},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            success_count += 1
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    print(f"Result: {success_count}/{NUM_RUNS_TIMES} passed")
    return success_count == NUM_RUNS_TIMES

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)