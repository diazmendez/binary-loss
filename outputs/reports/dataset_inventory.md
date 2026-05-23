# Dataset Inventory

Generated: 2026-05-05 08:55 UTC

## choices13k

### Files

| File | Size | Rows | Columns |
|------|------|------|---------|
| c13k_selections.csv | 1.1 MB | 14568 | 16 |
| c13k_problems.json | 1.6 MB | 14568 entries | — |

### Column Names (c13k_selections.csv)

`['Problem', 'Feedback', 'n', 'Block', 'Ha', 'pHa', 'La', 'Hb', 'pHb', 'Lb', 'LotShapeB', 'LotNumB', 'Amb', 'Corr', 'bRate', 'bRate_std']`

### JSON Structure (c13k_problems.json)

- Number of problems: 14568
- Keys per problem: `['B', 'A']`
- Example (first entry):
```json
{
  "B": [
    [
      0.95,
      21.0
    ],
    [
      0.05,
      23.0
    ]
  ],
  "A": [
    [
      0.95,
      26.0
    ],
    [
      0.050000000000000044,
      -1.0
    ]
  ]
}
```

### First rows (c13k_selections.csv)

```
   Problem  Feedback   n  Block  Ha   pHa  La  Hb   pHb  Lb  LotShapeB  LotNumB    Amb  Corr     bRate  bRate_std
0        1      True  15      2  26  0.95  -1  23  0.05  21          0        1  False     0  0.626667   0.384460
1        2      True  15      4  14  0.60 -18   8  0.25  -5          0        1   True    -1  0.493333   0.413118
2        3      True  17      4   2  0.50   0   1  1.00   1          0        1  False     0  0.611765   0.432843
```

## CPC15

### Files

| File | Size | Rows | Columns |
|------|------|------|---------|
| RawDataExperiment1sorted.csv | 7.2 MB | 93750 | 26 |
| RawDataExperiment2sorted.csv | 10.0 MB | 120750 | 26 |
| RawDataExperiment3.csv | 10.0 MB | 120000 | 26 |

### Column Names

- **exp1**: `['SubjID', 'Location', 'Gender', 'Age', 'set', 'Condition', 'GameID', 'Ha', 'pHa', 'La', 'Hb', 'pHb', 'Lb', 'Manipulation', 'Amb', 'LotShape', 'LotNum', 'Corr', 'Order', 'Trial', 'Button', 'Risk', 'Payoff', 'Forgone', 'RiskPay', 'Feedback']`

- **exp2**: `['SubjID', 'Location', 'Gender', 'Age', 'set', 'Condition', 'GameID', 'Ha', 'pHa', 'La', 'Hb', 'pHb', 'Lb', 'Manipulation', 'Amb', 'LotShape', 'LotNum', 'Corr', 'Order', 'Trial', 'Button', 'Risk', 'Payoff', 'Forgone', 'RiskPay', 'Feedback']`

- **exp3**: `['SubjID', 'Location', 'Gender', 'Age', 'set', 'Condition', 'GameID', 'Ha', 'pHa', 'La', 'Hb', 'pHb', 'Lb', 'Manipulation', 'Amb', 'LotShape', 'LotNum', 'Corr', 'Order', 'Trial', 'Button', 'Risk', 'Payoff', 'Forgone', 'RiskPay', 'Feedback']`

### First rows (exp1)

```
   SubjID  Location Gender  Age  set Condition  GameID  Ha  pHa  La  Hb   pHb  Lb Manipulation  Amb LotShape  LotNum  Corr  Order  Trial Button  Risk  Payoff  Forgone  RiskPay  Feedback
0       1  Technion      M   27    1    ByProb       8   1  1.0   1  20  0.05   0     Abstract    0        -       1     0      1      1      L     0       1        0        0         0
1       1  Technion      M   27    1    ByProb       8   1  1.0   1  20  0.05   0     Abstract    0        -       1     0      1      2      L     0       1        0        0         0
2       1  Technion      M   27    1    ByProb       8   1  1.0   1  20  0.05   0     Abstract    0        -       1     0      1      3      L     0       1        0        0         0
```

## CPC18

### Files

| File | Size | Rows | Columns |
|------|------|------|---------|
| all_CPC18_raw_data.csv | 62.3 MB | 694500 | 30 |
| CPC18_dictionary.pdf | 194.1 KB | — (PDF) | — |

### Column Names

`['SubjID', 'Location', 'Gender', 'Age', 'Set', 'Condition', 'GameID', 'Ha', 'pHa', 'La', 'LotShapeA', 'LotNumA', 'Hb', 'pHb', 'Lb', 'LotShapeB', 'LotNumB', 'Amb', 'Corr', 'Order', 'Trial', 'Button', 'B', 'Payoff', 'Forgone', 'RT', 'Apay', 'Bpay', 'Feedback', 'block']`

### First rows

```
   SubjID Location Gender  Age  Set Condition  GameID  Ha  pHa  La LotShapeA  LotNumA  Hb  pHb  Lb LotShapeB  LotNumB  Amb  Corr  Order  Trial Button  B  Payoff  Forgone  RT  Apay  Bpay  Feedback  block
0   10100  Rehovot      M   28    1    ByProb      13   0  1.0   0         -        1  50  0.5 -50         -        1    0     0      1      1      L  1      50        0 NaN     0    50         0      1
1   10100  Rehovot      M   28    1    ByProb      13   0  1.0   0         -        1  50  0.5 -50         -        1    0     0      1      2      L  1      50        0 NaN     0    50         0      1
2   10100  Rehovot      M   28    1    ByProb      13   0  1.0   0         -        1  50  0.5 -50         -        1    0     0      1      3      L  1     -50        0 NaN     0   -50         0      1
```
