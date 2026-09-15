# lamini-earnings-calls sample (transcripts 2018-Q4 to 2023-Q1)

Head-of-file sample of https://github.com/lamini-ai/lamini-earnings-calls (archived 13 Jun 2024, no LICENSE file).
`earnings-transcripts.head.jsonl`: first 100 full earnings-call transcripts (99 tickers, calls Jul 2019 to Feb 2023; HLT is the only lodging name seen; ABNB not in the head).
`answers.head.jsonl`: first 334 LLM-generated QA pairs over 4,096-char transcript chunks (6 tickers, 2019-Q2 to 2020-Q3).
`transcripts_head_index.csv`: ticker/exchange/quarter/date/length index of the sampled transcripts. `main.py`, `generate-qa.sh`, `README.upstream.md`: the pipeline, kept for the method record, not run (needs a Lamini API key).
Pulled 2026-09-14 with `curl -r 0-5000000` / `curl -r 0-3000000` range requests on raw.githubusercontent.com; the final truncated line of each head was dropped. Total written 8.0 MB (cap 25 MB).
Full dataset: `curl -L -o earnings-transcripts.jsonl https://raw.githubusercontent.com/lamini-ai/lamini-earnings-calls/main/data/earnings-transcripts.jsonl` (49.3 MB) and the same for `data/answers.jsonl` (25.1 MB), or `git clone --depth 1 https://github.com/lamini-ai/lamini-earnings-calls`.
Licence caution: transcript text is Motley Fool call-page text; the HF mirror lamini/earnings-calls-qa says CC-BY-4.0 but the repo itself carries no licence. Do not republish without a human decision.
