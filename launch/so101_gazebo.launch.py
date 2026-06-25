import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def _spawn_robot(package_name, entity_name, x, y, z):
    package_share = get_package_share_directory(package_name)
    urdf_path = os.path.join(package_share, 'urdf', 'so101.urdf')

    return Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-entity', entity_name,
            '-file', urdf_path,
            '-x', str(x), '-y', str(y), '-z', str(z),
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

    # Spawn at the world origin: the -0.55/0/0.7774 mounting offset now lives
    # in the world->base_link fixed joint inside the URDF, so applying it here
    # too would double it. robot_state_publisher publishes world->base_link
    # from that joint, so the old static_transform_publisher is removed
    # (two publishers for the same transform fight and cause TF jitter).
    spawn_follower = _spawn_robot('so101_gazebo', 'so101_follower', 0.0, 0.0, 0.0)

    return LaunchDescription([
        gazebo,
        rsp,
        TimerAction(period=5.0, actions=[spawn_follower]),
    ])