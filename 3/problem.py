from dataclasses import dataclass
from functools import reduce
from typing import Tuple


@dataclass
class Point:
    coords: Tuple[int, int]
    dist: int


def acc_points(point_list, instr):
    last_point = point_list[-1]
    next_coords = next_point(last_point.coords, instr)
    point_list.append(
        Point(
            next_coords,
            last_point.dist + abs(last_point.coords[0] - next_coords[0] + last_point.coords[1] - next_coords[1])
        )
    )
    return point_list


def next_point(from_point, instr):
    if instr[0] == "U":
        return (from_point[0], from_point[1] + int(instr[1]))
    if instr[0] == "D":
        return (from_point[0], from_point[1] - int(instr[1]))
    if instr[0] == "L":
        return (from_point[0] - int(instr[1]), from_point[1])
    if instr[0] == "R":
        return (from_point[0] + int(instr[1]), from_point[1])


def is_vertical(segment):
    return segment[0].coords[0] == segment[1].coords[0]


def get_intersections(point_list1, point_list2):
    intersections = []

    for p1_idx in range(len(point_list1) - 1):
        segment1 = (point_list1[p1_idx], point_list1[p1_idx + 1])

        segment1_min_y = min(segment1[0].coords[1], segment1[1].coords[1])
        segment1_max_y = max(segment1[0].coords[1], segment1[1].coords[1])
        segment1_min_x = min(segment1[0].coords[0], segment1[1].coords[0])
        segment1_max_x = max(segment1[0].coords[0], segment1[1].coords[0])

        for p2_idx in range(len(point_list2) - 1):
            segment2 = (point_list2[p2_idx], point_list2[p2_idx + 1])

            segment2_min_y = min(segment2[0].coords[1], segment2[1].coords[1])
            segment2_max_y = max(segment2[0].coords[1], segment2[1].coords[1])
            segment2_min_x = min(segment2[0].coords[0], segment2[1].coords[0])
            segment2_max_x = max(segment2[0].coords[0], segment2[1].coords[0])

            if is_vertical(segment1) and not is_vertical(segment2):

                if (
                    segment2_min_y <= segment1_max_y and segment2_min_y >= segment1_min_y and
                    segment2_min_x <= segment1_min_x and segment2_max_x >= segment1_min_x
                ):
                    int_x = segment1[0].coords[0]
                    int_y = segment2[0].coords[1]
                    dst1 = segment2[0].dist + abs(int_x - segment2[0].coords[0])
                    dst2 = segment1[0].dist + abs(int_y - segment1[0].coords[1])

                    intersections.append(
                        Point(
                            (int_x, int_y),
                            dst1 + dst2
                        )
                    )

            if not is_vertical(segment1) and is_vertical(segment2):

                if (
                    segment1_min_y <= segment2_max_y and segment1_min_y >= segment2_min_y and
                    segment1_min_x <= segment2_min_x and segment1_max_x >= segment2_min_x
                ):
                    int_x = segment2[0].coords[0]
                    int_y = segment1[0].coords[1]
                    dst1 = segment1[0].dist + abs(int_x - segment1[0].coords[0])
                    dst2 = segment2[0].dist + abs(int_y - segment2[0].coords[1])

                    intersections.append(
                        Point(
                            (int_x, int_y),
                            dst1 + dst2
                        )
                    )

    try:
        intersections.remove(Point((0,0), 0))
    except Exception:
        pass

    return intersections


def get_inputs():
    with open("input.csv") as f:
        return f.read()

# input = """R8,U5,L5,D3
# U7,R6,D4,L4"""
# input = """R75,D30,R83,U83,L12,D49,R71,U7,L72
# U62,R66,U55,R34,D71,R55,D58,R83"""
input = get_inputs()

cable1 = input.split('\n')[0]
cable2 = input.split('\n')[1]

cable1 = list(map(lambda x: (x[0], x[1:]), cable1.split(',')))
cable2 = list(map(lambda x: (x[0], x[1:]), cable2.split(',')))

cable1_vertices = reduce(
    acc_points,
    cable1,
    [Point((0, 0), 0)]
)

cable2_vertices = reduce(
    acc_points,
    cable2,
    [Point((0, 0), 0)]
)

print("Cables")
print(cable1_vertices)
print(cable2_vertices)

intersections = get_intersections(cable1_vertices, cable2_vertices)

print("Intersections")
print(intersections)

min_distance = reduce(lambda x, y: x if min(x.dist, y.dist) == x.dist else y, intersections)
print(min_distance)
