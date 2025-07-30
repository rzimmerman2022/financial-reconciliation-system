from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="financial-reconciliation",
    version="1.0.0",
    author="Financial Reconciliation Team",
    author_email="team@example.com",
    description="A production-ready financial reconciliation system with double-entry bookkeeping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/financial-reconciliation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "reconcile=scripts.run_with_review:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.json", "*.db"],
    },
)