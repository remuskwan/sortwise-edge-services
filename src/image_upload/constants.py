from typing import Final

# Max file size is 2MB
SUPPORTED_FILE_SIZE: Final[int] = 3 * 1024 * 1024
SUPPORTED_FILE_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
}
