from setuptools import setup, find_packages

setup(
    name="csharp-transpile",
    version="0.1.0",
    description="Minimal C# subset to JS/Python transpiler",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "c2t=c2t.__main__:main"
        ]
    },
    install_requires=[],
    python_requires=">=3.8",
)
