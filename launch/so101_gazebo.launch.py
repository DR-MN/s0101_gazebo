import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def _spawn_robot(package_name, entity_name, x_position, y_position, z_position, yaw):
    package_share = get_package_share_directory(package_name)
    urdf_path = os.path.join(package_share, 'urdf', 'so101.urdf')

    return Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-entity', entity_name,
            '-file', urdf_path,
            '-x', str(x_position),
            '-y', str(y_position),
            '-z', str(z_position),
            '-Y', str(yaw),
            '-timeout', '30',
        ],
    )


def _robot_state_publisher(package_name):
    package_share = get_package_share_directory(package_name)
    urdf_path = os.path.join(package_share, 'urdf', 'so101.urdf')
    with open(urdf_path, 'r', encoding='utf-8') as f:
        urdf_content = f.read()

    return Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': urdf_content,
            'use_sim_time': True,
        }],
        output='screen',
    )


def generate_launch_description():
    gazebo_share = get_package_share_directory('so101_gazebo')
    gazebo_ros_share = get_package_share_directory('gazebo_ros')
    world_path = os.path.join(gazebo_share, 'worlds', 'empty_world.world')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_path,
            'verbose': 'false',
        }.items(),
    )

    rsp = _robot_state_publisher('so101_gazebo')

    tf_follower = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_world_follower',
        arguments=[
            '--x', '-0.55', '--y', '0.0', '--z', '0.7774',
            '--roll', '0.0', '--pitch', '0.0', '--yaw', '0.0',
            '--frame-id', 'world',
            '--child-frame-id', 'base_link',
        ],
        output='screen',
    )

    spawn_follower = _spawn_robot(
        package_name='so101_gazebo',
        entity_name='so101_follower',
        x_position=-0.55,
        y_position=0.0,
        z_position=0.7774,
        yaw=0.0,
    )

    return LaunchDescription([
        gazebo,
        rsp,
        tf_follower,
        TimerAction(period=5.0, actions=[spawn_follower]),
    ])
