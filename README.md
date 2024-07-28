# CodeCoR

**:relaxed:This is CodeCoR’s review reference code. A new version will be compiled and open sourced on github later.**

:bear:Below is our directory structure.

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

:panda_face:Below is a description of each folder.

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



:sunny:**Because the code is written a lot and is very complicated, it may be a bit messy after sorting it out. You can select the key parts to reproduce, and then get the results for evaluation. Thank you very much for reading this and wish you a happy life.**

