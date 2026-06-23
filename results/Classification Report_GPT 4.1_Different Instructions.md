# GPT annotation classification reports

Generated: 2026-06-23 17:09
N (complete cases): 690

## Summary (F1-scores)

| regime | f1_D | f1_NA | f1_T | macro_avg |
| --- | --- | --- | --- | --- |
| gpt_instruction_short_with_examples | 0.572 | 0.765 | **0.600** | **0.646** |
| gpt_instruction_CoT | 0.578 | 0.785 | 0.565 | 0.643 |
| gpt_instruction_detailed_with_examples | 0.579 | 0.789 | 0.462 | 0.610 |
| gpt_instruction_detailed_no_ex | 0.536 | 0.706 | 0.567 | 0.603 |
| gpt_instruction_short_no_ex | **0.636** | **0.839** | 0.320 | 0.598 |

---

## gpt_instruction_short_no_ex

```text
              precision    recall  f1-score   support

           D      0.482     0.932     0.636       132
          NA      0.944     0.755     0.839       538
           T      0.800     0.200     0.320        20

    accuracy                          0.772       690
   macro avg      0.742     0.629     0.598       690
weighted avg      0.852     0.772     0.785       690
```

## gpt_instruction_short_with_examples

```text
              precision    recall  f1-score   support

           D      0.407     0.962     0.572       132
          NA      0.974     0.630     0.765       538
           T      0.500     0.750     0.600        20

    accuracy                          0.697       690
   macro avg      0.627     0.781     0.646       690
weighted avg      0.852     0.697     0.723       690
```

## gpt_instruction_detailed_no_ex

```text
              precision    recall  f1-score   support

           D      0.370     0.977     0.536       132
          NA      0.983     0.550     0.706       538
           T      0.425     0.850     0.567        20

    accuracy                          0.641       690
   macro avg      0.593     0.792     0.603       690
weighted avg      0.850     0.641     0.669       690
```

## gpt_instruction_detailed_with_examples

```text
              precision    recall  f1-score   support

           D      0.423     0.917     0.579       132
          NA      0.945     0.677     0.789       538
           T      0.474     0.450     0.462        20

    accuracy                          0.716       690
   macro avg      0.614     0.681     0.610       690
weighted avg      0.832     0.716     0.739       690
```

## gpt_instruction_CoT

```text
              precision    recall  f1-score   support

           D      0.421     0.924     0.578       132
          NA      0.957     0.665     0.785       538
           T      0.500     0.650     0.565        20

    accuracy                          0.714       690
   macro avg      0.626     0.747     0.643       690
weighted avg      0.841     0.714     0.739       690
```
## Summary figure

![F1-scores by instruction regime](figures/Figure_Classification%20Report%20GPT4.1_Different%20Instructions.png)