import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chimera_visualizer_project",
    version="1.0.0",
    author="Anish Prakriya",
    author_email="aprakriya201@gmail.com",
    description="TODO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Buddyboy201/chimera_visualizer_project",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=[],
    install_requires=["argparse", "sqlalchemy", "pathlib"],
    python_requires='>=3.6',
    license="MIT"
)
