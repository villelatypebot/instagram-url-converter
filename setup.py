from setuptools import setup, find_packages

setup(
    name="instagram-url-converter",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "flask>=2.0.0",
        "gunicorn>=20.0.4",
        "Pillow>=8.0.0",
    ],
    author="Instagram URL Converter",
    author_email="",
    description="Extrai URLs diretas de imagens de perfil do Instagram",
    keywords="instagram, url, converter, api",
    url="https://github.com/seu-usuario/instagram-url-converter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 