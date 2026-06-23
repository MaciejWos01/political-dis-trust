# GPT annotation classification reports

Generated: 2026-06-23 17:15
N (complete cases): 690

## Summary (F1-scores)

| regime | f1_D | f1_NA | f1_T | macro_avg |
| --- | --- | --- | --- | --- |
| gpt_instruction_short_no_ex | 0.573 | 0.769 | **0.583** | **0.642** |
| gpt_instruction_CoT | 0.573 | 0.776 | 0.522 | 0.624 |
| gpt_instruction_detailed_no_ex | **0.625** | **0.836** | 0.333 | 0.598 |
| gpt_instruction_short_with_examples | 0.585 | 0.790 | 0.410 | 0.595 |
| gpt_instruction_detailed_with_examples | 0.531 | 0.697 | 0.542 | 0.590 |

---

## gpt_instruction_short_no_ex

```text
              precision    recall  f1-score   support

           D      0.408     0.962     0.573       132
          NA      0.974     0.636     0.769       538
           T      0.500     0.700     0.583        20

    accuracy                          0.700       690
   macro avg      0.628     0.766     0.642       690
weighted avg      0.852     0.700     0.727       690
```

## gpt_instruction_short_with_examples

```text
              precision    recall  f1-score   support

           D      0.429     0.917     0.585       132
          NA      0.941     0.680     0.790       538
           T      0.421     0.400     0.410        20

    accuracy                          0.717       690
   macro avg      0.597     0.666     0.595       690
weighted avg      0.828     0.717     0.739       690
```

## gpt_instruction_detailed_no_ex

```text
              precision    recall  f1-score   support

           D      0.475     0.917     0.625       132
          NA      0.940     0.753     0.836       538
           T      1.000     0.200     0.333        20

    accuracy                          0.768       690
   macro avg      0.805     0.623     0.598       690
weighted avg      0.852     0.768     0.781       690
```

## gpt_instruction_detailed_with_examples

```text
              precision    recall  f1-score   support

           D      0.364     0.977     0.531       132
          NA      0.980     0.541     0.697       538
           T      0.410     0.800     0.542        20

    accuracy                          0.632       690
   macro avg      0.585     0.773     0.590       690
weighted avg      0.846     0.632     0.661       690
```

## gpt_instruction_CoT

```text
              precision    recall  f1-score   support

           D      0.414     0.932     0.573       132
          NA      0.956     0.652     0.776       538
           T      0.462     0.600     0.522        20

    accuracy                          0.704       690
   macro avg      0.611     0.728     0.624       690
weighted avg      0.838     0.704     0.730       690
```
## Summary figure

![F1-scores by instruction regime](figures/Figure_Classification%20Report%20GPT5.4_Different%20Instructions.png)