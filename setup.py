from setuptools import setup, find_packages

setup(
    name='zebra-code-diff-editor',
    version='0.1.0',
    description='Desktop Code Diff Editor with Syntax Highlighting and Inline Editing',
    author='Alexander Buchelnikov',
    packages=find_packages(),
    install_requires=[
        'PySide6',
    ],
    include_package_data=True,
    package_data={
        'app': [
            'resources/icons/*.svg',
            'resources/images/*.jpg',
            'resources/images/*.png',
        ],
    },
    entry_points={
        'console_scripts': [
            'zebra-diff=app.core.main:main',
        ],
    },
    python_requires='>=3.10,<4.0',
)
