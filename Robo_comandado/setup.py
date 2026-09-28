from setuptools import find_packages, setup


package_name = 'robo_comandado'


setup(
    name=package_name,
    version='0.0.0',

    # Localiza a pasta Python chamada robo_comandado.
    packages=find_packages(exclude=['test']),

    # Instala os arquivos necessários para a ROS reconhecer o pacote.
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

    description='Robô simulado controlado por comandos recebidos por tópico.',
    license='MIT',

    tests_require=['pytest'],

    # Cria os comandos usados com ros2 run.
    entry_points={
        'console_scripts': [
            # ros2 run robo_comandado robo
            'robo = robo_comandado.robo_comandado:main',

            # ros2 run robo_comandado agente_teste
            'agente_teste = robo_comandado.agente_teste:main',
        ],
    },
)