from setuptools import find_packages, setup


package_name = 'robo_distancia'


setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],

    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='SEU_NOME',
    maintainer_email='SEU_EMAIL',

    description=(
        'Robô que percorre uma distância recebida por tópico usando Odom.'
    ),

    license='MIT',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'robo = robo_distancia.robo_distancia:main',
            'agente_teste = robo_distancia.agente_teste:main',
        ],
    },
)