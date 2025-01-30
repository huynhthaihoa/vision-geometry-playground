import math

from loguru import logger

def get_rotation(start_point, center_point, rad):
    """Find the point T(x_T, y_T) that was made by rotating the point start_point(x_S, y_S) around the center point center_point(x_C, y_C)

    Args:
        start_point: start point as format (x, y)
        center_point: center point as format (x, y)
        rad: rotation angle in radian unit, counterclockwise order
        
    Returns:
        T as shape [x_T, y_T]    
    """    
    
    T = [0, 0]
    T[0] = (start_point[0] - center_point[0]) * math.cos(rad) - (start_point[1] - center_point[1]) * math.sin(rad) + center_point[0]
    T[1] = (start_point[0] - center_point[0]) * math.sin(rad) + (start_point[1] - center_point[1]) * math.cos(rad) + center_point[1]
    
    return T

def find_angle(start_point, end_point):
    """Find the angle of the vector start_point->end_point (with respect to Ox axis, in clockwise order)

    Args:
        start_point: start point of the vector as format (x, y)
        end_point: "end" point of the vector as format (x, y)

    Returns: 
        angle in radian
    """    
    return math.atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])

def is_anglerange_in_fovrange(fov_min, fov_max, angle_1, angle_2):
    """Check if the angle range [min(angle_1, angle_2), max(angle_1, angle_2)] is inside/overlaps with the FOV range [fov_min, fov_max]

    Args:
        fov_min (float): lower bound of the fov range (in radian unit, -pi <= range_min <= pi)
        fov_max (float): upper bound of the fov range (in radian unit, -pi <= range_max <= pi)
        angle_1 (float): first bound of the angle range  (in radian unit, -pi <= angle_1 <= pi)
        angle_2 (float): second bound of the angle range  (in radian unit, -pi <= angle_1 <= pi)
        
    Constraint:
        0 <= fov <= math.pi / 2 (90 degree)
        0 <= angle <= math.pi (180 degree)
        fov_min <= fov_max
    Returns:
        True if angle range the FOV range, False otherwise
    """    
    
    angle_min = min(angle_1, angle_2)
    angle_max = max(angle_1, angle_2)

    if fov_min <= 0 and fov_max >= 0:
        if fov_min >= -math.pi / 2:                                 ## -math.pi / 2 <= fov_min <= 0 && 0 <= fov_max <= math.pi / 2
            logger.info("case 1")
            if angle_max < fov_min:                                 # -math.pi <= angle_max < fov_min
                return False
            elif angle_max <= fov_max:                              # fov_min <= angle_max <= fov_max
                return True
            elif angle_max <= fov_min + math.pi:                    # fov_max < angle_max <= fov_min + math.pi
                return angle_max - math.pi <= angle_min <= fov_max
            else:                                                   # fov_min + math.pi < angle_max <= math.pi
                return fov_min <= angle_min <= fov_max
        else:                                                       ## -math.pi <= fov_min <= -math.pi / 2 && math.pi / 2 <= fov_max <= 0
            logger.info("case 2")
            if angle_max <= fov_min:                                # -math.pi <= fov_min <= -math.pi / 2
                return True
            elif angle_max <= 0:                                    # fov_min < angle_max <= 0
                return angle_min <= fov_min
            elif angle_max < fov_max:                               # 0 < angle_max < fov_max
                return angle_min <= angle_max - math.pi   
            else:                                                   # fov_max <= angle_max <= math.pi 
                return True      
    else: 
        if fov_max <= 0:     
            logger.info("case 3")
            ## fov_min <= fov_max <= 0
            if angle_max < fov_min:                                 # -math.pi <= angle_max < fov_min
                return False
            elif angle_max <= fov_max:                              # fov_min <= angle_max <= fov_max
                return True
            elif angle_max <= fov_max + math.pi:                    # fov_max < angle_max <= fov_max + math.pi
                return angle_max - math.pi <= angle_min <= fov_max
            else:                                                   # fov_max + math.pi < angle_max <= math.pi
                return fov_min <= angle_min <= angle_max - math.pi
        else:                                               ## 0 <= fov_min <= fov_max
            logger.info("case 4")
            if angle_max < 0:                               # -math.pi <= angle_max < 0
                return False
            elif angle_max < fov_min:                       # 0 <= angle_max < fov_min
                return angle_min <= angle_max - math.pi
            elif angle_max <= fov_max:                      # fov_min <= angle_max <= fov_max
                return True
            else:                                           # fov_max < angle_max <= math.pi
                return angle_max - math.pi <= angle_min <= fov_max

def is_overlapped(bbox1, bbox2):
    """Check if the 2 bounding boxes are overlapped with/contains each other (True) or not (False)

    Args:
        bbox1: the first bounding box as format [xmin, ymin, xmax, ymax(, conf)]
        bbox2: the second bounding box as format [xmin, ymin, xmax, ymax(, conf)]

    Returns:
        True if bbox1 is overlappedoverlapp with/contains/is contained by bbox2, False otherwise
    """
    horizontalValid = False
    verticalValid = False
    
    if (bbox1[0] <= bbox2[2] and bbox1[0] >= bbox2[0]):
        horizontalValid = True
    elif (bbox2[0] <= bbox1[2] and bbox2[0] >= bbox1[0]):
        horizontalValid = True

    if (bbox1[1] <= bbox2[3] and bbox1[1] >= bbox2[1]):
        verticalValid = True
    elif (bbox2[1] <= bbox1[3] and bbox2[1] >= bbox1[1]):
        verticalValid = True

    return (horizontalValid and verticalValid)