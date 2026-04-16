@echo off
echo ==========================================
echo    Starting ROS 2 Docker Environment
echo ==========================================

docker info 1>nul 2>nul
if not %errorlevel%==0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop!
    pause
    exit /b 1
)

docker inspect groupwork_ros2 1>nul 2>nul
if %errorlevel%==0 (
    echo [INFO] Container already exists. Attaching new terminal...
    docker start groupwork_ros2 1>nul 2>nul
    docker exec -it groupwork_ros2 bash -c "source /opt/ros/humble/setup.bash && bash"
    exit /b 0
)

echo Starting container...
docker-compose up -d
timeout /t 2 /nobreak 1>nul
echo [INFO] Attaching terminal...
docker exec -it groupwork_ros2 bash -c "source /opt/ros/humble/setup.bash && bash"
