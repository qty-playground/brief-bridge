from setuptools import setup, find_packages

setup(
    name="brief-bridge",
    version="0.1.0",
    description="A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi[standard]==0.116.1",
        "uvicorn==0.35.0",
        "pydantic==2.9.2",
        "openai>=1.0.0",
        "python-multipart",
        "aiofiles",
    ],
    extras_require={
        "test": [
            "pytest==8.4.1",
            "pytest-asyncio==1.1.0",
            "pytest-bdd==8.1.0",
            "httpx==0.28.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "brief-bridge=uvicorn:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)