from setuptools import setup


if __name__ == '__main__':
    setup(
        setup_requires=['setuptools>=34.0', 'setuptools-gitver'],
        gitver=True,
    )
