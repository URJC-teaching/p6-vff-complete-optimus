import os
from glob import glob
from setuptools import setup

package_name = 'p6_vff_complete'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Angel Ruiz',
    maintainer_email='a.ruizf.2022@alumnos.urjc.es',
    description='P6: VFF complete — follow person (3D) with obstacle avoidance and FSM',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'vff_follow_node = p6_vff_complete.vff_follow_node:main',
        ],
    },
)
