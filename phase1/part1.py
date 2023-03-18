import cv2
import pickle
import pyautogui
from time import sleep
import numpy as np
import os
import random

def get_game(img):
    # turn gray to black
    mask = cv2.inRange(img, (0, 0, 0), (100, 180, 100))

    # get each square contour
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # order by vertical and horizontal position
    contours = sorted(contours, key=lambda x: (cv2.boundingRect(x)[1], cv2.boundingRect(x)[0]))

    min_contour = contours[0]
    for i in range(1, len(contours)):
        # draw the contour on the image
        x, y, w, h = cv2.boundingRect(contours[i])
        if cv2.boundingRect(contours[i])[2] < cv2.boundingRect(min_contour)[2] and w>40 and h>40:
            min_contour = contours[i]
    
    # cv2.drawContours(img, [min_contour], -1, (0, 0, 255), 3)
    # return None, None

    # remove small contours
    contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[2] > 65 and cv2.boundingRect(cnt)[3] > 65]

    # remove colisions
    for i in range(len(contours)-1):
        for j in range(i+1, len(contours)):
            x1, y1, w1, h1 = cv2.boundingRect(contours[i])
            x2, y2, w2, h2 = cv2.boundingRect(contours[j])
            if x1 < x2 < x1+w1 and y1 < y2 < y1+h1:
                contours[j] = None
    contours = [cnt for cnt in contours if cnt is not None]

    # coord of min contour
    mx, my, mw, mh = cv2.boundingRect(min_contour)
    maze = []
    for pos,cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        count_non_zero = cv2.countNonZero(mask[y:y+h, x:x+w])
        if count_non_zero > 2000:
            maze.append('1')
        else:
            maze.append('0')

        # if min contour is in the middle
        if x < mx < x+w and y < my < y+h:
            pos_min = pos

    # split in 8 elements
    maze = [maze[i:i+8] for i in range(0, len(maze), 8)]
    pos = (pos_min % 8, pos_min // 8)

    if len(maze) < 7:
        raise Exception("Maze not found")
    for i in range(7):
        if len(maze[i]) < 8:
            raise Exception("Maze not found")
    

    return pos, maze

def maze_screenshot():
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # cut the image
    img = img[240:900, 2280:3080]

    return img

def move(direction,pos=(0,0)):
    if direction == "up":
        pyautogui.press("up")
        pos = (pos[0], pos[1]-1)
    elif direction == "down":
        pyautogui.press("down")
        pos = (pos[0], pos[1]+1)
    elif direction == "left":
        pyautogui.press("left")
        pos = (pos[0]-1, pos[1])
    elif direction == "right":
        pyautogui.press("right")
        pos = (pos[0]+1, pos[1])

    sleep(0.2)
    return pos
    
def runner_maze(path):
    pos = (0, 0)
    for direction in path:
        pos = move(direction, pos)
    return pos

def empty_direction(pos, maze):
    if pos[0]+1 < 7 and maze[pos[0]+1][pos[1]] == "0":
        return "right"
    elif pos[1]+1 < 7 and maze[pos[0]][pos[1]+1] == "0":
        return "down"
    elif pos[0]-1 > 0 and maze[pos[0]-1][pos[1]] == "0":
        return "left"
    elif pos[1]-1 > 0 and maze[pos[0]][pos[1]-1] == "0":
        return "up"

def opposite_direction(direction):
    if direction == "up":
        return "down"
    elif direction == "down":
        return "up"
    elif direction == "left":
        return "right"
    elif direction == "right":
        return "left"

def dfs(mazes, pos=(0,0), path=[], i=1):
    if pos[0]==7 and pos[1]==6:
        return path
    
    if len(mazes) == 0:
        return []
    
    if i == len(mazes):
        return path
    
    directions = ["right", "down", "left", "up"]
    positions = [(pos[0]+1, pos[1]), (pos[0], pos[1]+1), (pos[0]-1, pos[1]), (pos[0], pos[1]-1)]
    for pos, direction in zip(positions, directions):
        if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 6:
            continue
        if mazes[i][pos[1]][pos[0]] == "0":
            final_path = dfs(mazes, pos, path+[direction], i+1)
            if final_path is not None:
                return final_path

def bfs(mazes):
    min_steps = 150
    max_steps = 400
    for i in range(min_steps, max_steps):
        pos = (0, 0)
        path = []
        dist = 0
        queue = [(pos, dist, path)]
        while len(queue) > 0 and dist < i:
            pos, dist, path = queue.pop(0)
            print(f"> pos: {pos}, dist: {dist}, path: {path}")
            print(f"> queue size: {len(queue)}")
            if dist == len(mazes)-1:
                break
            if pos[0] == 7 and pos[1] == 6:
                return path
            directions = ["right", "down", "left", "up"]
            positions = [((pos[0]+1, pos[1])), ((pos[0], pos[1]+1)), ((pos[0]-1, pos[1])), ((pos[0], pos[1]-1))]

            for pos, direction in zip(positions, directions):
                if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 6:
                    continue
                print(dist, pos, len(mazes))
                try:
                    if mazes[dist+1][pos[1]][pos[0]] == "0" and dist+(7-pos[0])+(6-pos[1]) <= i:
                        queue.append((pos, dist+1, path+[direction]))
                except:
                    breakpoint()
    return queue[0][2]


def random_direction(pos):
    directions = ["up", "down", "left", "right"]
    random.shuffle(directions)
    for direction in directions:
        if direction == "up" and pos[1]-1 > 0:
            return direction
        elif direction == "down" and pos[1]+1 < 7:
            return direction
        elif direction == "left" and pos[0]-1 > 0:
            return direction
        elif direction == "right" and pos[0]+1 < 7:
            return direction

def load_mazes():
    # get all filenames
    files = os.listdir("mazes")
    files = [f for f in files if f.endswith(".pickle")]
    files.sort()

    try:
        filename = f"mazes/{files[-1]}"
        with open(filename, "rb") as f:
            mazes = pickle.load(f)
    except:
        mazes = []
    return mazes

def save_mazes(mazes):
    filename = f"mazes/{str(len(mazes)).zfill(8)}.pickle"
    with open(filename, "wb") as f:
        pickle.dump(mazes, f)
    print(f"Saved {filename}")

def find_path():

    mazes = load_mazes()
    while True:
        sleep(0.2)
        pyautogui.click(2880, 892)
        sleep(0.5)


        path = bfs(mazes)
        print(f"Profundidade: {len(mazes)}")
        print(path)
        pos = runner_maze(path)
        
        while not (pos[0] == 7 and pos[1] == 6):
            direction = random_direction(pos)
            print(direction)
            move(direction)

            screenshot = maze_screenshot()
            pos, maze = get_game(screenshot)

            mazes.append(maze)
            if mazes[-1][pos[1]][pos[0]] == "1":
                direction = opposite_direction(direction)
                move(direction)
                break
        print()

        if pos[0] == 7 and pos[1] == 6:
            break

        save_mazes(mazes)

def debug():
    screenshot = maze_screenshot()
    pos, maze = get_game(screenshot)
    print(pos)
    print('\n'.join([''.join(row) for row in maze]))

    cv2.imshow("maze", screenshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    find_path()
    # debug()
