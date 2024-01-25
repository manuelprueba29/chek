from setuptools import setup, find_packages

setup(
    name='checklistexperiencia',
    version='0.1',
    packages=find_packages(where='cheklistexperiencia/src'),
    include_package_data=True,
    install_requires=[
        'Flask',
        'mysql-connector-python',
        'reportlab',
        # Agrega cualquier otra dependencia que tu aplicación necesite
    ],

    entry_points={
        'console_scripts': [
            'guardar = src.guardar:main',  # Ajusta esto según tu script principal
        ],
    },
    package_data={
        '': ['src/static/*', 'src/static/css/*', 'src/templates/*', 'src/database.py'],
    },

)
