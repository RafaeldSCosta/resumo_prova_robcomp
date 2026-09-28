from setuptools import find_packages, setup


package_name = 'robo_com_desvio'


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
        'Robô comandado por tópico com desvio de obstáculos usando laser.'
    ),

    license='MIT',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'robo = robo_com_desvio.robo_com_desvio:main',
            'agente_teste = robo_com_desvio.agente_teste:main',
        ],
    },
)