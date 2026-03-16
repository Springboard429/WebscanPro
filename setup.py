from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="webscanpro",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced Web Application Security Scanner",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/WebScanPro",
    packages=find_packages(include=['core', 'core.*', 'utils', 'utils.*']),
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'webscanpro=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)