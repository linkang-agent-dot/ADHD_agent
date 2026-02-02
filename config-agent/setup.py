"""
Git 配置变更检查工具 - 安装脚本
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取 requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="git-config-checker",
    version="1.0.0",
    author="ADHD Agent Team",
    author_email="",
    description="检查 Git 仓库中配置文件的变更记录",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/git-config-checker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "git-config-check=main:main",
        ],
    },
    keywords="git config checker version-control analysis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/git-config-checker/issues",
        "Source": "https://github.com/yourusername/git-config-checker",
    },
)
