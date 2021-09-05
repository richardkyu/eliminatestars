from __future__ import print_function
import image_slicer, binascii, struct, os, cv2, glob, math, shutil
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster

def find_dominant_color(image_path):
    NUM_CLUSTERS = 10
    #print('reading image')
    im = Image.open(image_path)
    im = im.resize((150, 150))      # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

    #print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    #print('cluster centres:\n', codes)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = np.histogram(vecs, len(codes))    # count occurrences

    index_max = np.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    colour = ''.join([hex(int(c))[2:].zfill(2) for c in peak])
    #print('most frequent is %s (#%s)' % (peak, colour[:6]))
    return colour[:6]


def check_images_from_folder(folder):
    image_colors = []
    filenames = [img for img in glob.glob(folder+"/*.png")]
    filenames.sort()

    for filename in filenames:
        img = Image.open(filename)
        dominant_color = find_dominant_color(filename)
        if img is not None:
            image_colors.append(dominant_color)
    return image_colors

def check_color_similarity(color_list):
    different_colors = [color_list[0]]
    
    #Iterate through all the colors in the list.
    for element in color_list[1:]:
        r2 = int(element[:2], 16)
        g2= int(element[2:4], 16)
        b2 = int(element[4:6], 16)
        euclidean_distances = []
        color_difference_check = []

        #Compare each color in the list to the list of unique colors to see if this color matches any of those unique colors.
        #If there is no match, append this new color to the list.
        for color in different_colors:
            r1 = int(color[:2], 16)
            g1= int(color[2:4], 16)
            b1 = int(color[4:6], 16)
            
            euclidean_distance = math.sqrt(math.pow((r2-r1),2) + math.pow((g2-g1),2) + math.pow((b2-b1),2))
            euclidean_distances.append(euclidean_distance)
        
        
        for distance in euclidean_distances:
            if distance <= 40:
                color_difference_check.append(False)
            else:
                color_difference_check.append(True)

        add_color = all(color_difference_check)
        if(add_color):
            different_colors.append(element)
        
        #print(different_colors)
    return different_colors



def create_color_grid(color_list, unique_colors):
    grid = []
    for element in color_list:
        minimum = float("inf")
        element_index = -1

        r2 = int(element[:2], 16)
        g2= int(element[2:4], 16)
        b2 = int(element[4:6], 16)

        #Generate euclidean distances, find minimum and associate index of minimum to color.
        for index in range(len(unique_colors)):
            r1 = int(unique_colors[index][:2], 16)
            g1= int(unique_colors[index][2:4], 16)
            b1 = int(unique_colors[index][4:6], 16)
            
            euclidean_distance = math.sqrt(math.pow((r2-r1),2) + math.pow((g2-g1),2) + math.pow((b2-b1),2))

            if euclidean_distance < minimum:
                element_index = index
                minimum = euclidean_distance
        
        grid.append(element_index+1)
        
    
    return grid

def nested_grid(grid):
    nested_grid = []
    
    for index in range(0,len(grid),9):
        nested_grid.append(grid[index:index+9])


    return nested_grid


def slice_and_read_image(folder, file):
    image_slicer.slice(folder + file, 81)
    os.remove(folder + file)
    images_list = check_images_from_folder(folder)
    unique_colors = check_color_similarity(images_list)

    grid = create_color_grid(images_list, unique_colors)
    output = nested_grid(grid)

    shutil.rmtree(folder)
    os.makedirs(folder)

    return output



#
# Caching System
def check_for_image_in_cache(image_name):
    '''
    returns None if this image is not cached, or if the cached data
    is invalid. It does NOT check that the cached file matches 
    the image (incorrect data).

    If returning None, the cache file will be deleted.

    image_name is expected to be in the form 'asdsad.png'
    '''
    cache_file_name = image_name.split('.')[0] + '.txt'
    cache_file_path = './cache/' + cache_file_name

    if not os.path.exists(cache_file_path):
        print("Image isn't cached")
        return None

    try:
        with open(cache_file_path, 'r') as cached_content:
            # first row = "5 6" meaning "rows cols"
            dim_info = cached_content.readline()
            rows, cols = [int(x) for x in dim_info.split(" ")]

            img_grid = []
            for row in range(rows):
                img_grid += [[int(x) for x in cached_content.readline().split(" ")]]
        
        return img_grid

    except Exception:
        print("Cache file is invalid")
        os.remove(cache_file_path)
        return None

    

def write_image_grid_to_cache(image_name, grid):
    rows = len(grid)
    cols = len(grid[0])

    print("Rows and cols")
    print(rows)
    print(cols)
    print()

    cache_file_name = image_name.split('.')[0] + '.txt'
    cache_file_path = './cache/' + cache_file_name

    with open(cache_file_path, 'w') as cache_file:
        # first row = "5 6" meaning "rows cols"
        cache_file.write(str(rows) + " " + str(cols) + "\n")

        for row in range(rows):
            row_str = ""
            for value in grid[row]:
                row_str += str(value) + " "
            row_str = row_str[:-1] + "\n"

            cache_file.write(row_str)
    









def main_process():
    print("Processing game image.")

    selected_image = 'sample10.png'

    output = check_for_image_in_cache(selected_image)

    if output == None:
        print("Processing the image")

        # values based on directory structure
        img_file = '/' + selected_image
        os.mkdir('./tmp')
        shutil.copy('./imgs' + img_file, './tmp' + img_file)

        output = slice_and_read_image('./tmp', img_file)
        os.removedirs('./tmp')

        # write to cache for next time
        write_image_grid_to_cache(selected_image, output)

    return output

