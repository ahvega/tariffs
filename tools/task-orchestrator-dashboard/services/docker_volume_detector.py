"""
Docker Volume Detector Service

Automatically detects and provides access to task-orchestrator Docker volumes.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class DockerVolumeDetector:
    """Automatically detect and access task-orchestrator Docker volumes"""

    VOLUME_NAME = "mcp-task-data"
    DB_FILENAME = "tasks.db"

    def __init__(self):
        self.docker_client = None
        self._init_docker_client()

    def _init_docker_client(self):
        """Initialize Docker client if available"""
        try:
            import docker
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except ImportError:
            logger.warning("Docker Python SDK not installed. Install with: pip install docker")
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")

    def detect_volume(self) -> Optional[Tuple[str, str]]:
        """
        Detect Docker volume and return path information.

        Returns:
            Tuple of (db_path, access_method) or None if not found
            access_method: 'direct' | 'copy' | 'wsl'
        """
        if not self.docker_client:
            logger.info("Docker client not available, cannot detect volumes")
            return None

        try:
            volume = self.docker_client.volumes.get(self.VOLUME_NAME)
            mountpoint = volume.attrs['Mountpoint']
            logger.info(f"Found Docker volume '{self.VOLUME_NAME}' at: {mountpoint}")

            # Platform-specific detection
            if os.name == 'nt':  # Windows
                return self._detect_windows_path(mountpoint)
            else:  # Linux/macOS
                return self._detect_unix_path(mountpoint)

        except Exception as e:
            logger.info(f"Docker volume '{self.VOLUME_NAME}' not found: {e}")
            return None

    def _detect_windows_path(self, mountpoint: str) -> Optional[Tuple[str, str]]:
        """
        Detect database path on Windows (handles WSL2 Docker).

        Returns:
            Tuple of (db_path, access_method)
        """
        # WSL2 paths
        wsl_paths = [
            f"\\\\wsl.localhost\\docker-desktop-data\\data\\docker\\volumes\\{self.VOLUME_NAME}\\_data\\{self.DB_FILENAME}",
            f"\\\\wsl$\\docker-desktop-data\\data\\docker\\volumes\\{self.VOLUME_NAME}\\_data\\{self.DB_FILENAME}",
        ]

        for path in wsl_paths:
            if os.path.exists(path):
                logger.info(f"WSL path accessible: {path}")
                return (path, 'wsl')

        # If WSL paths don't work, recommend copy method
        logger.info("WSL paths not accessible, using copy method")
        return (None, 'copy')

    def _detect_unix_path(self, mountpoint: str) -> Optional[Tuple[str, str]]:
        """
        Detect database path on Unix systems (Linux/macOS).

        Returns:
            Tuple of (db_path, access_method)
        """
        db_path = os.path.join(mountpoint, self.DB_FILENAME)

        if os.path.exists(db_path):
            logger.info(f"Direct access available: {db_path}")
            return (db_path, 'direct')
        else:
            logger.warning(f"Database not found at {db_path}")
            return (None, 'copy')

    def get_recommended_path(self, fallback_path: str = "data/tasks.db") -> str:
        """
        Get recommended database path with fallback.

        Args:
            fallback_path: Default path if Docker volume not found

        Returns:
            Database path to use
        """
        detection = self.detect_volume()

        if detection:
            db_path, method = detection

            if method == 'copy':
                logger.info("Using copy method - you may need to run sync manually")
                logger.info(f"Recommended: docker cp <container>:/app/data/{self.DB_FILENAME} {fallback_path}")
                return fallback_path
            elif db_path:
                return db_path

        # Check if fallback exists
        if os.path.exists(fallback_path):
            logger.info(f"Using fallback database path: {fallback_path}")
            return fallback_path

        logger.warning(f"No database found. Please ensure task-orchestrator is running and database exists.")
        return fallback_path

    def sync_from_container(self, container_name: str = "mcp-task-orchestrator",
                           dest_path: str = "data/tasks.db") -> bool:
        """
        Copy database from Docker container to local path.

        Args:
            container_name: Name of the task-orchestrator container
            dest_path: Destination path for the database copy

        Returns:
            True if successful, False otherwise
        """
        if not self.docker_client:
            logger.error("Docker client not available")
            return False

        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest_path)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Get container
            container = self.docker_client.containers.get(container_name)

            # Get file from container
            bits, stat = container.get_archive(f'/app/data/{self.DB_FILENAME}')

            # Write to destination
            import tarfile
            import io

            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)

            with tarfile.open(fileobj=tar_stream) as tar:
                member = tar.getmember(self.DB_FILENAME)
                with tar.extractfile(member) as source:
                    with open(dest_path, 'wb') as dest:
                        dest.write(source.read())

            logger.info(f"Successfully synced database to {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to sync database from container: {e}")
            return False


if __name__ == "__main__":
    # Test the detector
    logging.basicConfig(level=logging.INFO)
    detector = DockerVolumeDetector()

    result = detector.detect_volume()
    if result:
        path, method = result
        print(f"Detected: {path} (method: {method})")
    else:
        print("Volume not detected")

    recommended = detector.get_recommended_path()
    print(f"Recommended path: {recommended}")
