import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    image_topic_arg = DeclareLaunchArgument(
        'image_topic', default_value='/camera/rgb/image_raw',
        description='RGB image topic')

    depth_topic_arg = DeclareLaunchArgument(
        'depth_topic', default_value='/camera/depth_raw/image',
        description='Depth image topic')

    camera_info_topic_arg = DeclareLaunchArgument(
        'camera_info_topic', default_value='/camera/depth_raw/camera_info',
        description='Camera info topic')

    laser_topic_arg = DeclareLaunchArgument(
        'laser_topic', default_value='/scan_filtered',
        description='Laser scan topic (sim: /scan_raw, real: /scan)')

    yolo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('yolo_bringup'),
                'launch', 'yolo.launch.py')),
        launch_arguments={
            'input_image_topic': LaunchConfiguration('image_topic'),
            'input_depth_topic': LaunchConfiguration('depth_topic'),
            'input_depth_info_topic': LaunchConfiguration('camera_info_topic'),
            'target_frame': 'camera_link',
            'use_3d': 'True',
        }.items()
    )

    yolo_detection_3d = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('camera'),
                'launch', 'yolo_detection3d.launch.py'))
    )

    attractive_node_cmd = Node(
        package='vff_control',
        executable='yolo_class_detector_node_3d',
        name='yolo_class_detector_node_3d',
        output='screen',
        parameters=[{
            'target_class': 'person',
            'base_frame': 'base_footprint'
        }],
        remappings=[
            ('/input_detection_3d', '/detections_3d')
        ]
    )

    obstacle_detector_cmd = Node(
        package='vff_control',
        executable='obstacle_detector_node',
        name='obstacle_detector_node',
        output='screen',
        parameters=[{
            'min_distance': 0.5,
            'base_frame': 'base_footprint'
        }],
        remappings=[
            ('/input_laser', LaunchConfiguration('laser_topic'))
        ]
    )

    vff_follow_cmd = Node(
        package='p6_vff_complete',
        executable='vff_follow_node',
        name='vff_follow_node',
        output='screen',
        parameters=[{
            'max_linear_speed': 0.3,
            'max_angular_speed': 1.0,
            'search_angular_speed': 0.5,
            'person_lost_timeout': 1.0,
            'repulsive_gain_factor': 0.3,
            'repulsive_influence_distance': 0.5,
            'stay_distance': 1.0,
        }]
    )

    return LaunchDescription([
        image_topic_arg,
        depth_topic_arg,
        camera_info_topic_arg,
        laser_topic_arg,
        yolo_launch,
        yolo_detection_3d,
        attractive_node_cmd,
        obstacle_detector_cmd,
        vff_follow_cmd,
    ])