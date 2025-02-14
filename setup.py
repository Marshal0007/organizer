import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="organizer",  # Replace with your tool's name
    version="0.1.0",  # Initial version number
    author="Your Name",  # Replace with your name
    author_email="your.email@example.com",  # Replace with your email
    description="A tool to organize and manage project resources",  # Short description
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/organizer",  # Replace with your GitHub repo URL
    packages=setuptools.find_packages(),  # Automatically find packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
    entry_points={
        "console_scripts": [
            "organizer = organizer.organizer:cli"  # Make 'organizer' command available
        ]
    },
    install_requires=[
        "requests",  # List any dependencies here
        "fuzzywuzzy",
        "colorama",
        "click",  # Added Click as a dependency
        "pyfiglet",  # Added pyfiglet
    ],
)
