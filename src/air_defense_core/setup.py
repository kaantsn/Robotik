import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'air_defense_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    description='Air Defense C2 System',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'rviz_military_sim = air_defense_core.rviz_military_sim:main',
            'c2_dashboard = air_defense_core.c2_dashboard:main'  # YENİ ARAYÜZÜMÜZ EKLENDİ
        ],
    },
)
