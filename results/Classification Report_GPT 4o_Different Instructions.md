# GPT annotation classification reports

Generated: 2026-06-22 13:34
N (complete cases): 690

## Summary (F1-scores)

| regime | f1_D | f1_NA | f1_T | macro_avg |
| --- | --- | --- | --- | --- |
| gpt_instruction_detailed_with_examples | 0.573 | 0.769 | **0.600** | **0.647** |
| gpt_instruction_detailed_no_ex | 0.577 | 0.780 | 0.511 | 0.623 |
| gpt_instruction_short_with_examples | 0.578 | 0.792 | 0.444 | 0.605 |
| gpt_instruction_CoT | **0.629** | **0.837** | 0.333 | 0.600 |
| gpt_instruction_short_no_ex | 0.533 | 0.699 | 0.483 | 0.572 |

*CoT = Chain of Thought
---

## gpt_instruction_short_no_ex

```text
              precision    recall  f1-score   support

           D      0.366     0.977     0.533       132
          NA      0.977     0.545     0.699       538
           T      0.368     0.700     0.483        20

    accuracy                          0.632       690
   macro avg      0.571     0.741     0.572       690
weighted avg      0.842     0.632     0.661       690
```

## gpt_instruction_CoT

```text
              precision    recall  f1-score   support

           D      0.477     0.924     0.629       132
          NA      0.942     0.753     0.837       538
           T      1.000     0.200     0.333        20

    accuracy                          0.770       690
   macro avg      0.806     0.626     0.600       690
weighted avg      0.855     0.770     0.782       690
```

## gpt_instruction_detailed_with_examples

```text
              precision    recall  f1-score   support

           D      0.408     0.962     0.573       132
          NA      0.977     0.634     0.769       538
           T      0.500     0.750     0.600        20

    accuracy                          0.700       690
   macro avg      0.628     0.782     0.647       690
weighted avg      0.854     0.700     0.727       690
```

## gpt_instruction_short_with_examples

```text
              precision    recall  f1-score   support

           D      0.424     0.909     0.578       132
          NA      0.941     0.684     0.792       538
           T      0.500     0.400     0.444        20

    accuracy                          0.719       690
   macro avg      0.622     0.664     0.605       690
weighted avg      0.829     0.719     0.741       690
```

## gpt_instruction_detailed_no_ex

```text
              precision    recall  f1-score   support

           D      0.419     0.924     0.577       132
          NA      0.954     0.660     0.780       538
           T      0.444     0.600     0.511        20

    accuracy                          0.709       690
   macro avg      0.606     0.728     0.623       690
weighted avg      0.837     0.709     0.733       690
```
