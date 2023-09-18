import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-iss-telemetry", # Replace with your own username
    version="1.2",
    author="Ben Appleby",
    author_email="ben.appleby@sky.com",
    description="Stream live International Space Station Telemetry.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BApplB/py-iss-telemetry",
    packages=setuptools.find_packages(),
	include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
