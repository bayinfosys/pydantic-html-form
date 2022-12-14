import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydform",
    version="0.0.1",
    author="ed",
    author_email="ed@bayis.co.uk",
    description="pydantic.basemodel to html form conversion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bayinfosys/pydform",
    packages=["pydform"],
    package_data={
        "pydform": ["js/*.js"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
      "pydantic",
    ],
    extras_require={
      "tests": [
        "hypothesis",
        "mock",
        "pytest",
      ],
      "examples": [
        "fastapi",
        "jinja2",
        "uvicorn[standard]"
      ]
    },
    test_suite="tests",
)
