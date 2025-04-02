from wand.image import Image

def get_bytes_per_channel(img):
    """
    Dynamically determines the number of channels from a Wand Image object.

    Args:
        img (wand.image.Image): The Wand Image object.

    Returns:
        int or None: The number of channels, or None if it cannot be determined.
    """
    format_lower = img.format.lower()
    colorspace_lower = str(img.colorspace).lower()
    has_alpha = img.alpha_channel

    num_channels = 0

    if format_lower == 'png':
        if colorspace_lower in ('rgb', 'srgb') and has_alpha:
            num_channels = 4
        elif colorspace_lower in ('rgb', 'srgb') and not has_alpha:
            num_channels = 3
        elif colorspace_lower in ('grayscale') and has_alpha:
            num_channels = 2
        elif colorspace_lower in ('grayscale') and not has_alpha:
            num_channels = 1
        elif colorspace_lower in ('rgba', 'srgba'):
            num_channels = 4
        elif colorspace_lower == 'transparent':
            num_channels = 1
        else:
            num_channels = 4 if has_alpha else 3 # Default for PNG

    elif format_lower in ('jpeg', 'jpg', 'webp'):
        num_channels = 3 # Typically RGB

    elif format_lower in ('gif'):
        num_channels = 4 if has_alpha else 3 # Often treated as RGBA with palette

    elif format_lower in ('bmp', 'dib'):
        if colorspace_lower in ('grayscale', 'gray'):
            num_channels = 1
        else:
            num_channels = 3

    elif format_lower in ('tiff', 'tif'):
        if colorspace_lower in ('rgb', 'srgb'):
            num_channels = 3
        elif colorspace_lower in ('rgba', 'srgba'):
            num_channels = 4
        elif colorspace_lower in ('grayscale', 'gray'):
            num_channels = 1
        elif colorspace_lower == 'cmyk':
            num_channels = 4
        else:
            num_channels = None

    elif format_lower in ('exr', 'hdr'):
        if colorspace_lower in ('rgb', 'srgb'):
            num_channels = 3
        elif colorspace_lower in ('rgba', 'srgba'):
            num_channels = 4
        elif colorspace_lower in ('grayscale', 'gray'):
            num_channels = 1
        else:
            num_channels = None

    elif format_lower in ('ico', 'icns'):
        num_channels = None

    elif colorspace_lower in ('rgb', 'srgb', 'hsv', 'hsl', 'hwb', 'lab', 'luv', 'yiq', 'yuv', 'xyz', 'ohta', 'rec601ycbcr', 'rec709ycbcr'):
        num_channels = 3
    elif colorspace_lower in ('rgba', 'srgba', 'cmyk'):
        num_channels = 4
    elif colorspace_lower == 'cmyka':
        num_channels = 5
    elif colorspace_lower in ('grayscale', 'gray', 'transparent', 'rec601luma', 'rec709luma'):
        num_channels = 1
    elif colorspace_lower in ('dng', 'null', 'undefined'):
        num_channels = None
    else:
        print(f"Warning: Unrecognized format '{format_lower}' or colorspace '{colorspace_lower}'. Cannot reliably determine the number of channels.")
        num_channels = None
    
    return int(round(img.depth * num_channels / 8))
