import cv2
import numpy as np

from loguru import logger

from utils import find_intersect_obj_indices

def generate_object(image_size):
    """Generate a random object

    Args:
        image_size (int): input image size (width = height = image_size)

    Returns:
        object as format [xmin, ymin, xmax, ymax, conf] (xmin, ymin, xmax, ymax is bounding box, conf is confidence score)
    """    
    xmax = np.random.randint(1, image_size)
    xmin = np.random.randint(xmax)
    
    ymax = np.random.randint(1, image_size)
    ymin = np.random.randint(ymax)
    
    # confidence score
    conf = np.random.rand()
    
    return [xmin, ymin, xmax, ymax, conf]

def generate_gaze(bbox):
    """Generate a "gaze vector" that starts from gaze_start and goes toward "gaze_end"

    Args:
        image_size (int): input image size (width = height = image_size)

    Returns:
        gaze_start as format (x, y)
        gaze_end as format (x, y)
    """    
    while True:
        gaze_start_x = np.random.randint(bbox[0], bbox[2])
        gaze_start_y = np.random.randint(bbox[1], bbox[3])
        
        gaze_end_x = np.random.randint(bbox[0], bbox[2])
        gaze_end_y = np.random.randint(bbox[1], bbox[3])

        # gaze_start = np.random.randint(image_size, size=2)
        # gaze_end = np.random.randint(image_size, size=2)
        
        # # to make sure "gaze_start" and "gaze_end" are not the same point
        if gaze_start_x != gaze_end_x or gaze_start_y != gaze_end_y:
            break
    
    return (gaze_start_x, gaze_start_y), (gaze_end_x, gaze_end_y)

if __name__ == "__main__":
    
    #configuration
    fov_degree = np.random.randint(30, 91) #90
    logger.info("fov degree: {}".format(fov_degree))
    conf_threshold = 0.5
    count_threshold = 1
    
    # image size
    image_size = 700
    
    # number of objects
    num_objects = 10
    
    # generate objects
    objects = list()
    for i in range(num_objects):
        obj = generate_object(image_size)
        objects.append(obj)
        
    # generate human bouding box
    human = generate_object(image_size)
        
    #generate gaze vector
    gaze_start, gaze_end = generate_gaze(human)
    
    # find the list of object inside "fov"
    fov_p1, fov_p2, intersect_obj_indices, outside_obj_indices, unseen_obj_indices = find_intersect_obj_indices(gaze_start, gaze_end, objects, human, fov_degree=fov_degree, conf_thres=conf_threshold)#, count_thres=count_threshold)
    
    # image    
    image = np.zeros((image_size, image_size, 3), dtype=np.uint8)

    # visualize human bounding box
    cv2.rectangle(image, (human[0], human[1]), (human[2], human[3]), (255, 0, 0))
    
    # visualize fov (green)
    fov_color = (0, 255, 0)
    cv2.arrowedLine(image, gaze_start, (int(fov_p1[0]), int(fov_p1[1])), fov_color, 3)
    cv2.arrowedLine(image, gaze_start, (int(fov_p2[0]), int(fov_p2[1])), fov_color, 3)
    
    # visualize gaze vector (sky blue)
    gaze_color = (255, 255, 0)
    cv2.arrowedLine(image, gaze_start, gaze_end, gaze_color, 1)
    
    # visualize object
    for idx, obj in enumerate(objects):
        
        if idx in intersect_obj_indices: # object in fov, color in red
            color = (0, 0, 255)
        elif idx in outside_obj_indices: #object outside human bounding box, color in white
            color = (255, 255, 255)
        elif idx in unseen_obj_indices: # object out of fov and inside human bounding box, color in yellow
            color = (0, 255, 255)  
        else:
            continue
        # if obj[4] >= conf_threshold:    
        cv2.rectangle(image, (obj[0], obj[1]), (obj[2], obj[3]), color)
    
    # the driver is looking at at least 1 phone => distracted
    if len(intersect_obj_indices) > 0:
        text = "DISTRACTED"
    else:
        text = "FOCUS!"
    cv2.putText(image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255))
        
    cv2.imshow("preview", image)
    cv2.waitKey()
    
    cv2.imwrite("example.png", image)