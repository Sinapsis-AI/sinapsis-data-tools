# -*- coding: utf-8 -*-
import os

import requests
from sinapsis_core.utils.logging_utils import sinapsis_logger


def download_file(url: str, output_path: str, description: str | None = None) -> None:
    """General-purpose function to download a file from a URL.

    Args:
        url (str): The URL of the file to download.
        output_path (str): The path to save the downloaded file.
        description (Optional[str]): Description for logging purposes.
    """
    if os.path.exists(output_path):
        return

    sinapsis_logger.info(f"Downloading {description or 'file'} from {url} to {output_path}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        sinapsis_logger.info(f"{description or 'File'} download completed successfully.")
    else:
        raise RuntimeError(f"Failed to download {description or 'file'}. HTTP status code: {response.status_code}")
