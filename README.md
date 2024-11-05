# CodeCoR

This repository contains the implementation and supplementary resources for the CodeCoR framework, as described in our paper.

The framework, CodeCoR, aims to a self-reflective multi-agent framework that evaluates the effectiveness of each agent and their collaborations. Below is an overview of the directory structure and contents, organized to facilitate replication and further experimentation.

### Directory Structure

**CodeCoR_agent**

This directory contains the core implementation of the agents in the CodeCoR framework. Each agent is responsible for a distinct phase in the code generation process, such as prompt generation, testing, and code repair. The modular structure allows for easy modification and experimentation with individual agent behaviors.

**dataset**

The dataset directory houses all the datasets used in the experiments. These datasets are integral to evaluating the performance and robustness of the CodeCoR framework. Each file in this directory has been preprocessed to conform to the framework’s requirements, ensuring consistency and repeatability of experimental results.

**experiments**

This directory includes the experimental code and configurations. 

**image**

The image directory contains visual representations, such as diagrams and flowcharts, illustrating the principles and workflow of the CodeCoR framework. These images provide insight into the system architecture and the interaction between the agents, supplementing the explanations provided in the paper.

**utils**

This directory provides utility scripts and helper functions essential for the CodeCoR framework's operation. These scripts support data preprocessing, performance logging, and result visualization, ensuring smooth execution and facilitating further development.