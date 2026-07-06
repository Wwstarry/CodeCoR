from setuptools import setup, find_packages

setup(
    name="codecor",
    version="1.0.0",
    description=(
        "CodeCoR: An LLM-Based Self-Reflective Multi-Agent Framework for Code Generation"
    ),
    author="Ruwei Pan, Hongyu Zhang, Chao Liu",
    author_email="panruwei@cqu.edu.cn",
    url="https://arxiv.org/abs/2501.07811",
    packages=find_packages(exclude=["tests*", "evaluate*", "examples*"]),
    python_requires=">=3.9",
    install_requires=[
        "anthropic>=0.60.0",
        "openai>=1.0.0",
        "evalplus>=0.3.0",
        "editdistance>=0.6.3",
        "nltk>=3.8",
        "pyyaml>=6.0",
        "tqdm>=4.65",
    ],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="code generation, LLM, multi-agent, self-reflective, HumanEval, MBPP",
)
