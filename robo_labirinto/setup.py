from setuptools import find_packages, setup


package_name = 'robo_labirinto'


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
        'Robô que utiliza Laser e Odom para sair de um labirinto.'
    ),

    license='MIT',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'labirinto = robo_labirinto.robo_labirinto:main',
        ],
    },
)