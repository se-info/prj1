from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()
                    and not line.startswith("#")]

setup(
    name="crypto-order-block-detector",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A sophisticated web application that automatically detects and visualizes Order Blocks on cryptocurrency price charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crypto-order-block-detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/*", "*.md", "*.txt"],
    },
    entry_points={
        "console_scripts": [
            "crypto-ob-detector=app:main",
        ],
    },
    keywords="cryptocurrency, trading, order-blocks, smart-money-concepts, technical-analysis, flask, web-app",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crypto-order-block-detector/issues",
        "Source": "https://github.com/yourusername/crypto-order-block-detector",
        "Documentation": "https://github.com/yourusername/crypto-order-block-detector#readme",
    },
)
