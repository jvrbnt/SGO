"""
Nextcloud API integration module
Handles file uploads and downloads to Nextcloud
"""

import os
import logging
from typing import Optional
from urllib.parse import unquote, urljoin, urlparse
from xml.etree import ElementTree
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class NextcloudClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        remote_path: str = "/remote.php/dav/files"
    ):
        """
        Initialize Nextcloud client.

        Args:
            base_url: Nextcloud server URL (e.g., https://saco.csic.es)
            username: Nextcloud username
            password: Nextcloud password or app token
            remote_path: Path to the WebDAV endpoint
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.headers.update({"User-Agent": "SGO-Nextcloud-Client/1.0"})

    def _build_url(self, remote_file_path: str) -> str:
        """Build full WebDAV URL for a file."""
        # Ensure paths start with /
        if not remote_file_path.startswith("/"):
            remote_file_path = "/" + remote_file_path

        return urljoin(
            self.base_url,
            f"{self.remote_path}/{self.username}{remote_file_path}"
        )

    def upload_file(
        self,
        local_file_path: str,
        remote_file_path: str,
        overwrite: bool = True
    ) -> bool:
        """
        Upload a file to Nextcloud.

        Args:
            local_file_path: Path to local file
            remote_file_path: Target path in Nextcloud (e.g., /Documents/file.pdf)
            overwrite: Whether to overwrite existing file

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(local_file_path):
            logger.error(f"Local file not found: {local_file_path}")
            return False

        url = self._build_url(remote_file_path)

        try:
            with open(local_file_path, "rb") as f:
                response = self.session.put(url, data=f)

            if response.status_code in (201, 204):
                logger.info(f"File uploaded successfully: {remote_file_path}")
                return True
            else:
                logger.error(
                    f"Upload failed for {remote_file_path}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error uploading file {remote_file_path}: {str(e)}")
            return False

    def download_file(
        self,
        remote_file_path: str,
        local_file_path: str
    ) -> bool:
        """
        Download a file from Nextcloud.

        Args:
            remote_file_path: Path in Nextcloud (e.g., /Documents/file.pdf)
            local_file_path: Target local path

        Returns:
            True if successful, False otherwise
        """
        url = self._build_url(remote_file_path)

        try:
            response = self.session.get(url, stream=True)

            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                with open(local_file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"File downloaded successfully: {local_file_path}")
                return True
            else:
                logger.error(
                    f"Download failed for {remote_file_path}: "
                    f"{response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"Error downloading file {remote_file_path}: {str(e)}")
            return False

    def list_files(self, remote_dir_path: str = "/") -> Optional[list]:
        """
        List files in a Nextcloud directory.

        Args:
            remote_dir_path: Directory path in Nextcloud (e.g., /Documents/)

        Returns:
            List of file names or None if error
        """
        url = self._build_url(remote_dir_path)

        try:
            # Use PROPFIND method with custom header
            response = self.session.request("PROPFIND", url, headers={"Depth": "1"})

            if response.status_code in (207, 200):
                # Parse XML response and extract file names
                # For simplicity, we return the raw response
                logger.info(f"Listed files in {remote_dir_path}")
                return response.text
            else:
                logger.error(f"List failed for {remote_dir_path}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error listing files in {remote_dir_path}: {str(e)}")
            return None

    def list_names(self, remote_dir_path: str = "/") -> Optional[set]:
        """Return the set of entry names directly inside a remote directory.

        Returns None on error and an empty set if the directory does not exist.
        """
        url = self._build_url(remote_dir_path.rstrip("/") + "/")
        try:
            response = self.session.request("PROPFIND", url, headers={"Depth": "1"})
        except Exception as e:
            logger.error(f"Error listing {remote_dir_path}: {str(e)}")
            return None
        if response.status_code == 404:
            return set()
        if response.status_code not in (207, 200):
            logger.error(f"List failed for {remote_dir_path}: {response.status_code}")
            return None

        own_path = unquote(urlparse(url).path).rstrip("/")
        names = set()
        for element in ElementTree.fromstring(response.content).iter("{DAV:}href"):
            href = unquote(urlparse(element.text or "").path).rstrip("/")
            if href and href != own_path:
                names.add(href.rsplit("/", 1)[-1])
        return names

    def delete_file(self, remote_file_path: str) -> bool:
        """
        Delete a file from Nextcloud.

        Args:
            remote_file_path: Path in Nextcloud (e.g., /Documents/file.pdf)

        Returns:
            True if successful, False otherwise
        """
        url = self._build_url(remote_file_path)

        try:
            response = self.session.delete(url)

            if response.status_code in (200, 204):
                logger.info(f"File deleted successfully: {remote_file_path}")
                return True
            else:
                logger.error(
                    f"Delete failed for {remote_file_path}: {response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"Error deleting file {remote_file_path}: {str(e)}")
            return False

    def create_folder(self, remote_folder_path: str) -> bool:
        """
        Create a folder in Nextcloud.

        Args:
            remote_folder_path: Path for new folder (e.g., /Documents/NewFolder/)

        Returns:
            True if successful, False otherwise
        """
        url = self._build_url(remote_folder_path)

        try:
            response = self.session.request("MKCOL", url)

            if response.status_code in (201, 405):  # 405 = folder already exists
                logger.info(f"Folder created or exists: {remote_folder_path}")
                return True
            else:
                logger.error(
                    f"Folder creation failed for {remote_folder_path}: "
                    f"{response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"Error creating folder {remote_folder_path}: {str(e)}")
            return False


def get_nextcloud_client() -> NextcloudClient:
    """Factory function to create Nextcloud client from environment variables."""
    return NextcloudClient(
        base_url=os.getenv("NEXTCLOUD_URL", "https://saco.csic.es"),
        username=os.getenv("NEXTCLOUD_USERNAME", ""),
        password=os.getenv("NEXTCLOUD_PASSWORD", ""),
        remote_path=os.getenv("NEXTCLOUD_REMOTE_PATH", "/remote.php/dav/files")
    )
