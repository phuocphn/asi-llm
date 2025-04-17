4.10.2025
---
- [x] python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=false (report-1)
- [x] python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=true (report-2)
- [x] python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=true rule_provided=true (report-3)
- [x] python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=false 
- [x] python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=true (report-4)
- [x] python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=true rule_provided=true -> python main.py 'benchmark_subsets=[small]' eval_llms='small' break_hl2_prompt=true rule_provided=true 'categories=[pair]'
- [x] python main.py eval_llms='all'  break_hl2_prompt=false rule_provided=true && python main.py eval_llms='all'  break_hl2_prompt=false rule_provided=false
- [x] python main.py eval_llms='all'  break_hl2_prompt=false rule_provided=true rule_src=data/gen_rules/gen-rules-deepseek-04.md 'categories=[pair]' && python main.py eval_llms='all'  break_hl2_prompt=false rule_provided=false rule_src=data/gen_rules/gen-rules-deepseek-04.md 'categories=[pair]'
- [x] python main.py eval_llms='medium' 'medium_llms=[llama3.3:70b]' break_hl2_prompt=false rule_provided=true rule_src=data/gen_rules/llama-rules-0-out.md 'categories=[pair]'
- [x] python main.py eval_llms='medium' 'medium_llms=[llama3:70b]' break_hl2_prompt=false rule_provided=true rule_src=data/gen_rules/llama3.70b-rules-2-out.md 'categories=[pair]'
- [x] python main.py eval_llms='all' 'categories=[pair]' break_hl2_prompt=false rule_provided=true && python main.py eval_llms='all'  break_hl2_prompt=false rule_provided=false 'categories=[pair]'

-----

DeepSeek API
- [ ] python main.py break_hl2_prompt=false rule_provided=false 'categories=[pair]' eval_llms='proprietary' && python main.py  break_hl2_prompt=false rule_provided=true 'categories=[pair]' eval_llms='proprietary' 