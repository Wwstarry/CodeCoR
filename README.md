# CodeCoR

**This is CodeCoR’s review reference code. A new version will be compiled and open sourced on github later.**

Below is our directory structure.

```
CODECOR_FOR_REVIEW
├── codellama
├── evaluate
├── gallary
├── gpt
├── results 
├── tool 
└── README.md
```

Below is a description of each folder.

- **codellama**

  Key code and files for CodeLlama experiments.

- **evaluate**

  Data sets for evaluation and some evaluation-related code.

- **gallary**

  

- **gpt**

  The key code for calling gpt to conduct experiments includes the implementation of CodeCoR.
  The most important one is the CodeCoR.py .(It includes the whole frame work of CodeCoR.)

- **results**

  This folder saves some of our experimental results. Due to the long experimental period, there may be confusion in the naming of some data, but we have accurately named the key data, such as CodeCoR_results_gpt3.jsonl and CodeCoR_results_gpt4.jsonl.

- **tool**

  This folder saves some of the tools we used for data processing during the experiment, such as cleaning the complete MBPP data set into a test data set.



# Code Generation Model Comparison

The table below compares various code generation models for the HumanEval, HumanEval-ET, MBPP, and MBPP-ET datasets based on Pass@1 scores. The best approach is highlighted in bold. The baseline results are obtained from their paper reports.

| Models                  | Human-Eval | Human-Eval-ET | MBPP  | MBPP-ET |
|-------------------------|------------|---------------|-------|---------|
| Code LLMs               |            |               |       |         |
| Incoder (6.7B)          | 15.2       | 11.6          | 17.6  | 14.3    |
| CodeGeeX (1.3B)         | 18.9       | 15.2          | 26.9  | 20.4    |
| StarCoder (15.5B)       | 34.1       | 25.6          | 43.6  | 33.4    |
| CodeGen-Mono (16.1B)    | 32.9       | 23.5          | 46.0  | 29.6    |
| CodeX (175B)            | 47.0       | 36.0          | 57.0  | 45.0    |
| CodeX (175B)+CodeT      | 65.8       | 51.7          | 67.7  | 57.1    |
| GPT-3.5-turbo           | 67.4       | 50.2          | 52.7  | 42.7    |
| GPT-4                   | 67.6       | 50.6          | 68.0  | 52.3    |
| PaLM Coder              | 43.9       | 36.6          | 32.3  | 27.2    |
| Claude-instant-1        | 31.1       | 28.1          | 26.7  | 22.7    |
| GPT-4-turbo             | 57.9       | 48.8          | 63.4  | 47.5    |
|                         |            |               |       |         |
| GPT-3.5-turbo-0613 with |            |               |       |         |
| Few-Shot                | 67.7       | 54.9          | 65.8  | 48.3    |
| ReAct                   | 56.9       | 49.4          | 67.6  | 45.9    |
| Reflexion               | 68.1       | 50.6          | 70.4  | 48.4    |
| ToT                     | 54.4       | 47.2          | 65.0  | 48.3    |
| RAP                     | 63.1       | 52.4          | 71.4  | 48.5    |
| Self-Edit               | 64.1       | 48.8          | 67.1  | 51.4    |
| Self-Planning           | 65.2       | 48.8          | 68.8  | 50.6    |
| Self-Debugging          | 61.6       | 45.8          | 68.1  | 52.3    |
| Self-Collaboration      | 71.4       | 56.1          | 66.1  | 52.5    |
| INTERVENOR              | 75.6       | 54.8          | 69.0  | 55.2    |
| SCOT                    | 73.5       | 54.3          | 68.4  | 52.7    |
| CodeChain               | 62.8       | 54.3          | 69.3  | 51.0    |
| Vanilla CodeCoT         | 64.5       | 48.3          | 68.8  | 50.6    |
| CodeCoT                 | 79.3       | 69.5          | 67.7  | 53.1    |
| **CodeCoR**             | **81.1**   | **80.5**      | **76.2**| **65.2**|

## Comparison of models on the HumanEval and MBPP datasets based on Average Edit Distance and Average BLEU score
The table below compares models on the HumanEval and MBPP datasets based on Average Edit Distance and Average BLEU score, including the mean values across both datasets.

| Method         | HumanEval Avg. Edit Dist. | HumanEval Avg. BLEU Score | MBPP Avg. Edit Dist. | MBPP Avg. BLEU Score | Mean Avg. Edit Dist. | Mean Avg. BLEU Score |
|----------------|----------------------------|---------------------------|----------------------|----------------------|----------------------|----------------------|
| CodeCoR        | 378.79                     | 0.276                     | 166.61               | 0.351                | 272.70               | 0.314                |
| Self-Planning  | 387.53                     | 0.249                     | 538.52               | 0.127                | 463.03               | 0.188                |
| SCOT           | 334.97                     | 0.263                     | 538.52               | 0.127                | 436.75               | 0.195                |
| CodeChain      | 357.20                     | 0.263                     | 301.81               | 0.259                | 329.51               | 0.261                |
| CodeCoT        | 387.53                     | 0.249                     | 167.18               | 0.360                | 277.36               | 0.305                |

##  The impact of major components of CodeCoR on HumanEval and MBPP datasets (Pass@1)
The table below shows the impact of major components of CodeCoR on HumanEval and MBPP datasets based on Pass@1 scores.

| Variant                   | HumanEval | HumanEval-ET | MBPP | MBPP-ET |
|---------------------------|-----------|--------------|------|---------|
| w/o Self-examination      | 45.1      | 43.3         | 52.1 | 40.6    |
| w/o Repair Agent          | 75.6      | 75.6         | 67.7 | 48.6    |
| w/o Control Module        | 77.4      | 76.2         | 67.7 | 57.1    |
| CodeCoR                   | 81.1      | 80.5         | 76.2 | 65.2    |

## Cost comparison of code generation models
The table below compares the cost of code generation models based on run time, CPU usage, memory increments, disk read/write, and network send/receive.

| Method         | Run Time (s) | CPU Usage (%) | Memory Increments (GB) | Disk Read (MB) | Disk Write (MB) | Net Send (MB) | Net Receive (MB) |
|----------------|--------------|---------------|-------------------------|----------------|-----------------|---------------|------------------|
| CodeCoR        | 123.69       | 0.08          | 0.01                    | 0.36           | 11.49           | 0.14          | 0.30             |
| CodeCoT        | 156.38       | 0.08          | -0.02                   | 0.43           | 12.24           | 0.19          | 0.32             |
| CodeChain      | 121.80       | 0.04          | 0.01                    | 1.25           | 16.21           | 0.12          | 0.22             |
| SCOT           | 251.79       | 0.53          | 0.00                    | 55.32          | 16.96           | 0.63          | 1.50             |
| Self-Planning  | 242.92       | 0.02          | -0.02                   | 31.16          | 0.35            | 0.74          | 0.65             |

## Comparison of different methods on HumanEval and HumanEval-ET datasets
The table below compares different methods on the HumanEval and HumanEval-ET datasets using GPT-4 and CodeLlama (34B).

| Method         | GPT-4 Human-Eval | GPT-4 HumanEval-ET | CodeLlama (34B) Human-Eval | CodeLlama (34B) HumanEval-ET |
|----------------|-------------------|---------------------|----------------------------|-------------------------------|
| CodeChain      | 89.0              | 61.6                | 15.9                       | 14.0                          |
| SCOT           | 78.9              | 69.5                | 17.4                       | 14.9                          |
| Self-Planning  | 83.5              | 76.8                | 22.6                       | 20.1                          |
| CodeCoT        | 86.6              | 77.4                | 34.1                       | 29.9                          |
| CodeCoR        | **94.5**          | **83.5**            | **43.9**                   | **37.8**                      |

