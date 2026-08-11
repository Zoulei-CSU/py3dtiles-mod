import numpy as np
import math
import traceback
import laspy
import struct
from pickle import dumps as pdumps

from py3dtiles.utils import SrsInMissingException


def init(files, color_scale=None, srs_in=None, srs_out=None, fraction=100):
    aabb = None
    total_point_count = 0
    pointcloud_file_portions = []
    avg_min = np.array([0., 0., 0.])

    for filename in files:
        try:
            reader = laspy.open(filename)
        except Exception as e:
            print('Error opening {filename}. Skipping.'.format(**locals()))
            print(e)
            continue
        with reader:
            header = reader.header
            avg_min += (np.asarray(header.mins) / len(files))

            if aabb is None:
                aabb = np.array([header.mins, header.maxs])
            else:
                bb = np.array([header.mins, header.maxs])
                aabb[0] = np.minimum(aabb[0], bb[0])
                aabb[1] = np.maximum(aabb[1], bb[1])

            count = int(header.point_count * fraction / 100)
            total_point_count += count

            # Read a small sample to determine whether 16-bit colors need scaling.
            if color_scale is None:
                dimension_names = set(header.point_format.dimension_names)
                color_test_field = 'red' if 'red' in dimension_names else 'intensity'
                if color_test_field == 'intensity':
                    color_scale = 1.0 / 255
                elif header.point_count:
                    sample = reader.read_points(min(10000, header.point_count))
                    if np.max(sample[color_test_field]) > 255:
                        color_scale = 1.0 / 255

        _1M = min(count, 1000000)
        steps = math.ceil(count / _1M)
        portions = [(i * _1M, min(count, (i + 1) * _1M)) for i in range(steps)]
        for p in portions:
            pointcloud_file_portions += [(filename, p)]

        if (srs_out is not None and srs_in is None):
            embedded_crs = header.parse_crs()
            if embedded_crs is None:
                raise SrsInMissingException('\'{}\' file doesn\'t contain srs information. Please use the --srs_in option to declare it.'.format(filename))
            srs_in = embedded_crs.to_wkt()

    return {
        'portions': pointcloud_file_portions,
        'aabb': aabb,
        'color_scale': color_scale,
        'srs_in': srs_in,
        'point_count': total_point_count,
        'avg_min': avg_min
    }


def run(_id, filename, offset_scale, portion, queue, transformer, verbose):
    '''
    Reads points from a las file
    '''
    try:
        with laspy.open(filename) as reader:
            header = reader.header
            point_count = portion[1] - portion[0]
            step = min(point_count, max(point_count // 10, 100000))
            indices = range(math.ceil(point_count / step))
            color_scale = offset_scale[3]
            dimension_names = set(header.point_format.dimension_names)
            has_rgb = 'red' in dimension_names
            reader.seek(portion[0])

            for index in indices:
                num = min(step, point_count - index * step)
                file_points = reader.read_points(num)
                X = file_points['X']
                Y = file_points['Y']
                Z = file_points['Z']

                # Read scaled values and apply the tileset offset.
                x = X * header.scales[0] + header.offsets[0]
                y = Y * header.scales[1] + header.offsets[1]
                z = Z * header.scales[2] + header.offsets[2]

                if transformer:
                    x, y, z = transformer.transform(x, y, z)

                x = (x + offset_scale[0][0]) * offset_scale[1][0]
                y = (y + offset_scale[0][1]) * offset_scale[1][1]
                z = (z + offset_scale[0][2]) * offset_scale[1][2]

                coords = np.vstack((x, y, z)).transpose()

                if offset_scale[2] is not None:
                    # Apply transformation matrix (because the tile's transform will contain
                    # the inverse of this matrix)
                    coords = np.dot(coords, offset_scale[2])

                coords = np.ascontiguousarray(coords.astype(np.float32))

                # Read RGB when present; otherwise use intensity as grayscale.
                if has_rgb:
                    red = file_points['red']
                    green = file_points['green']
                    blue = file_points['blue']
                else:
                    red = file_points['intensity']
                    green = file_points['intensity']
                    blue = file_points['intensity']

                if color_scale is None:
                    red = red.astype(np.uint8)
                    green = green.astype(np.uint8)
                    blue = blue.astype(np.uint8)
                else:
                    red = (red * color_scale).astype(np.uint8)
                    green = (green * color_scale).astype(np.uint8)
                    blue = (blue * color_scale).astype(np.uint8)

                colors = np.vstack((red, green, blue)).transpose()

                queue.send_multipart([
                    ''.encode('ascii'),
                    pdumps({'xyz': coords, 'rgb': colors}),
                    struct.pack('>I', len(coords))], copy=False)

        queue.send_multipart([pdumps({'name': _id, 'total': 0})])
        # notify we're idle
        queue.send_multipart([b''])
    except Exception as e:
        print('Exception while reading points from las file')
        print(e)
        traceback.print_exc()
