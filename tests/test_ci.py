import os
import sys

# To allow importing modules from the main workspace
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_environment_setup():
    """
    Check if basic directory structures exist.
    """
    assert os.path.isdir("tutorials"), "tutorials directory should exist"
    assert os.path.isdir("models"), "models directory should exist"


def test_dockerfile_exists():
    """
    Ensure Dockerfile exists for ROS 2 container building.
    """
    assert os.path.isfile("Dockerfile"), "Dockerfile must exist at root"
    assert os.path.isfile("docker-compose.yml"), "docker-compose.yml must exist at root"


def test_dummy_math():
    """
    Sanity check for pytest.
    """
    assert 1 + 1 == 2
