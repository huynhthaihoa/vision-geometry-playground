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
        if fov_min >= -math.pi / 2:                                 ## fov_min >= -math.pi / 2 && fov_max <= math.pi / 2
            logger.info("case 1")
            if angle_max < fov_min:                                 # -math.pi <= angle_max < fov_min
                return False
            elif angle_max <= fov_max:                              # fov_min <= angle_max <= fov_max
                return True
            elif angle_max <= fov_min + math.pi:                    # fov_max < angle_max <= fov_min + math.pi
                return angle_max - math.pi <= angle_min <= fov_max
            else:                                                   # fov_min + math.pi < angle_max <= math.pi
                return fov_min <= angle_min <= fov_max
        else:                                                       ## fov_min <= -math.pi / 2 && fov_max >= math.pi / 2:
            logger.info("case 2")
            if angle_max <= fov_min:                                # -math.pi <= angle_max <= fov_min
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
    return False

def is_overlapped(bbox1, bbox2):
    """Check if the 2 bounding boxes are overlapped with each other (True) or not (False)

    Args:
        bbox1: the first bounding box as format [xmin, ymin, xmax, ymax(, conf)]
        bbox2: the second bounding box as format [xmin, ymin, xmax, ymax(, conf)]

    Returns:
        True if bbox1 is overlapped with bbox2, False otherwise
    """
    if ((bbox1[0] <= bbox2[2] and bbox1[0] >= bbox2[0]) or (bbox1[2] >= bbox2[0] and bbox1[0] <= bbox2[0])) and ((bbox1[1] <= bbox2[3] and bbox1[1] >= bbox2[1]) or (bbox1[3] >= bbox2[1] and bbox1[1] <= bbox2[1])):
        return True
    return False

def find_intersect_obj_indices(gaze_start, gaze_end, objects, bbox, fov_degree=30, conf_thres=0.5, count_thres=1):
    """Check if any object intersects with the "fov" that starts from "gaze_start" and receives gaze vector as the angle bisector

    Args:
        - gaze_start: start point of the gaze vector as format (x, y)
        - gaze_end: "end" point of the gaze vector as format (x, y)
        - objects: list of objects, each object has format [xmin, ymin, xmax, ymax, conf] (xmin, ymin, xmax, ymax is bounding box, conf is confidence score)
        - bbox: only use objects which are overlapped with the bounding box bbox [xmin, ymin, xmax, ymax(, conf)]
        - fov_degree (int, optional): the absolute value of the "fov" in Degree unit. Defaults to 30 (this is a configuration value, and must be >= 0 and < 90)
        - count_thres (int, optional): the minimum number of corners that lie within "gaze angle" to be considered as "intersect". Default to 1 (this is a configuration value, and must be >= 1 and <= 4)
        - conf_thres (float, optional): confidence threshold as many false positive "Phone" detection may appear. Default to 0.5 (this is a configuration value, and must be > 0 and < 1)
    Returns:
        - fov_p1: the point to represent the first vector of the "fov" as format (x, y)
        - fov_p2: the point to represent the second vector of the "fov" as format (x, y)
        - intersect_obj_indices: indices of intersect objects (if any)
        - outside_obj_indices: indices of object outside of the bbox (if any)
        - unseen_obj_indices: indices of object inside of the bbox but is not looked at (if any)
    """    
    
    # convert angle to radian unit
    rad = math.pi * fov_degree / 360
    
    #find 2 points represent 2 vectors of the "gaze angle"
    fov_p1 = get_rotation(gaze_end, gaze_start, rad)
    fov_p2 = get_rotation(gaze_end, gaze_start, -rad) 
    
    fov_a1 = find_angle(gaze_start, fov_p1) 
    fov_a2 = find_angle(gaze_start, fov_p2)   
    
    fov_amin = min(fov_a1, fov_a2)
    fov_amax = max(fov_a1, fov_a2)

    logger.info("fov_amin: {}".format(fov_amin * 180 / math.pi))
    logger.info("fov_amax: {}".format(fov_amax * 180 / math.pi))

    intersect_obj_indices = list()
    outside_obj_indices = list()
    unseen_obj_indices = list()
    
    for idx, obj in enumerate(objects):

        if is_overlapped(obj, bbox) is False:
            outside_obj_indices.append(idx)
            continue
        
        # make sure object's confidence score satisfies the confidence threshold
        if obj[4] >= conf_thres:
            logger.info("object {}".format(idx))
            count = 0
        
            # 4 corners of the object bounding box, in order is top-left, top-right, bottom-left, bottom-right
            corner_pts = [(obj[0], obj[1]), (obj[0], obj[3]), (obj[2], obj[1]), (obj[2], obj[3])]
            
            # the angle from "gaze_start" to each corner
            corner_angles = list()
            for corner_pt in corner_pts:
                corner_angle = find_angle(gaze_start, corner_pt)
                logger.info("corner: {}".format(corner_angle * 180 / math.pi))
                corner_angles.append(corner_angle)#find_angle(gaze_start, corner_pt))
                            
            # check if the FOV intersects with the top edge (from top-left corner to top-right corner)
            if is_anglerange_in_fovrange(fov_amin, fov_amax, corner_angles[0], corner_angles[1]):
                count += 1
            
            # check if the FOV intersects with the bottom edge (from bottom-left corner to bottom-right corner)
            if is_anglerange_in_fovrange(fov_amin, fov_amax, corner_angles[2], corner_angles[3]):
                count += 1
            
            # check if the FOV intersects with the left edge (from top-left corner to bottom-left corner)
            if is_anglerange_in_fovrange(fov_amin, fov_amax, corner_angles[0], corner_angles[2]):
                count += 1            

            # check if the FOV intersects with the right edge (from top-right corner to bottom-right corner)
            if is_anglerange_in_fovrange(fov_amin, fov_amax, corner_angles[1], corner_angles[3]):
                count += 1   
            
            # object's bounding box intersects with the FOV
            if count >= count_thres:
                logger.warning("INSIDE!")
                intersect_obj_indices.append(idx)
            else:
                logger.warning("OUTSIDE!")
                unseen_obj_indices.append(idx)
    # print("fov angle range:", fov_amin * 180 / math.pi, fov_amax * 180 / math.pi)
    
    return fov_p1, fov_p2, intersect_obj_indices, outside_obj_indices, unseen_obj_indices