'''Find the minimum enclosing circle for a polygon'''

# Standard modules
import sys
import math
import random
import argparse

# Additional permitted modules
import cvxpy as cp
from scipy.spatial import ConvexHull


def get_convex_hull(vertices_set):
    '''
    Compute the convex hull of the polygon.

    The convex hull of a set of points is the smallest convex set that
    contains all of the points.  The convex hull of a concave polygon contains
    fewer vertices than the original polygon.  This should reduce cvxpy
    constraints and run time for concave polygons with many vertices.

    Uses scipy.ConvexHull.

    :param vertices_set: Set of (x, y) tuples representing the polygon vertices
    :return: hull_vertices Set of (x, y) tuples representing the convex hull
                           of the polygon vertices
    '''

    # Convert set to list for ConvexHull function.
    vertices = list(vertices_set)
    vertices_len = len(vertices)

    # Compute the convex hull of the polygon.
    hull = ConvexHull(vertices)

    # Extract convex hull vertices.
    hull_vertices = [vertices[hull_vertex] for hull_vertex in hull.vertices]
    hull_vertices_set = set(hull_vertices)
    hull_vertices_len = len(hull_vertices_set)
    print_v('Convex hull vertices:', hull_vertices_set)

    # Warn about vertex removal.
    if hull_vertices_len < vertices_len:
        vertices_diff = vertices_len - hull_vertices_len
        print(f'Warning - convex hull calculation removes {vertices_diff} vertices:')
        print('\t', vertices_set - hull_vertices_set)

    return hull_vertices_set


def check_vertices(vertices):
    '''
    Check vertices for problems.

    Must be at least 3 vertices.
    Vertices must all be tuples.
    Vertices must all be 2 dimensional.

    :param vertices: Set of (x, y) tuples representing the polygon vertices
    '''

    # Must be at least 3 vertices.
    if len(vertices) < 3:
        print('Must be at least 3 vertices:', vertices)
        sys.exit()

    # Vertices must all be tuples.
    if not all(isinstance(vertex, tuple) for vertex in vertices):
        print('Vertices must all be tuples:', vertices)
        sys.exit()

    # Vertices must all be 2 dimensional.
    vertex_sizes = [len(p) for p in vertices]

    if not all(vertex_size == 2 for vertex_size in vertex_sizes):
        vertex_size_min = min(vertex_sizes)
        vertex_size_max = max(vertex_sizes)
        print('Vertices must be 2 dimensional:', vertices)
        print('Vertex sizes:', vertex_sizes)
        print(f'Vertex size - min, max: {vertex_size_min}, {vertex_size_max}')
        sys.exit()


def minimum_enclosing_circle(vertices):
    '''
    Find minimum enclosing circle for a polygon.

    Uses cvxpy with Euclidean distance constraints.
    Euclidean distance from each vertex to the circle center should be
    less than or equal to circle radius.
    The cvxpy objective is to minimise the enclosing circle radius.

    :param vertices: Set of (x, y) tuples representing the polygon vertices
    :return: Center (x, y) and radius of the minimal enclosing circle
    '''

    # Variables for the center of the circle (c_x, c_y) and the radius.
    center = cp.Variable(2)
    radius = cp.Variable(nonneg=True)

    # Objective: Minimize the radius.
    objective = cp.Minimize(radius)

    # Constraints:
    # Euclidean distance from each vertex to the center should be <= radius
    # cp.hstack - Horizontal concatenation of arguments
    # cp.norm - Euclidean distance
    constraints = [cp.norm(cp.hstack(vertex - center), 2) <= radius
                   for vertex in vertices]

    # Formulate the problem.
    problem = cp.Problem(objective, constraints)

    # Solve the problem.
    problem.solve()

    # Check problem status.
    if problem.status != cp.OPTIMAL:
        print('Solver failed to find a solution')
        sys.exit()

    # Return the center coordinates and the radius.
    return center.value, radius.value


def describe_circle(center, radius):
    '''
    Print circle position and radius.

    :param center: Center (x, y) coordinates of the minimal enclosing circle
    :param radius: Radius of the minimal enclosing circle
    '''

    (c_x, c_y) = center
    print(f'Circle center: ({c_x:.4f}, {c_y:.4f})')
    print(f'Circle radius: {radius:.4f}')


def get_vertices(args):
    '''
    Either generate regular polygon, generate random points are use hardcoded
    polygon.

    A polygon is defined as a set of coordinates that map the vertices
    inside a 2D plane.

    :param args: argparse arguments
    :return: Set of tuples containing 2D coordinates
    '''

    if args.radius is not None:
        # Generate regular polygon.
        vertices = generate_regular_polygon(args)
    elif args.min_coord is not None and args.max_coord is not None:
        # Generate set of random 2D tuples.
        vertices = generate_random_points(args)
    else:
        # Use hardcoded vertices.
        # Triangle
        # vertices = {(0, 0), (2, 0), (2, 2)}
        # Square
        # vertices = {(0, 0), (0, 2), (2, 0), (2, 2)}
        # Irregular pentagon
        # vertices = {(0, 0), (0, 2), (2, 0), (2, 2), (1, 3)}
        # Bow tie - concave
        # vertices = {(0, 0), (1, 1), (2, 2), (2, 4), (1, 3), (0, 4)}
        # 5-sided star
        vertices = {(0, 100), (59, 81), (95, 31), (36, -12), (59, -81),
                    (-59, -81), (-36, -12), (-95, 31), (-59, 81)}
        print('Hardcoded polygon:', vertices)

    return vertices


def main(args):
    '''
    Standard main function.

    Get hardcoded vertices or generate a polygon or random points on 2D plane.
    Check for problems with points/vertices.
    Calculate convex hull of points/vertices.
    Find the minimal enclosing circle of the convex hull.
    Describe the minimal enclosing circle.

    :param args: Argparse command line arguments
    '''

    # Get hardcoded vertices or generate a polygon or
    # generate random points on 2D plane.
    vertices = get_vertices(args)

    # Check for problems with points/vertices.
    check_vertices(vertices)

    # Calculate convex hull of the points/vertices with scipy.
    convex_hull = get_convex_hull(vertices)

    # Find the minimal enclosing circle of the convex hull with cvxpy.
    cen, rad = minimum_enclosing_circle(convex_hull)

    # Print description of minimal enclosing circle.
    describe_circle(cen, rad)


def generate_regular_polygon(args):
    '''
    Generates coordinates of a regular polygon.

    :param args: argparse arguments
    :return: Set of tuples containing 2D coordinates of regular polygon
    '''

    # Extract parameters from args.
    radius = args.radius
    num_points = args.num_points

    # Sanity check parameters.
    assert isinstance(radius, int)
    assert isinstance(num_points, int)
    assert radius > 0
    assert num_points >= 3

    # Generate regular polygon.
    regular_coords = []
    angle = 2 * math.pi / num_points
    for i in range(num_points):
        # coords or tuples containing x, y coordinates
        coords = (radius * math.cos(i * angle), radius * math.sin(i * angle))
        regular_coords.append(coords)

    # Convert list to set.
    regular_coords_set = set(regular_coords)
    print('Generated regular polygon:', regular_coords_set)

    return regular_coords_set


def generate_random_points(args):
    '''
    Generates at least 3 random 2D points for testing.

    A set of n random points may not result in an n-sided polygon.

    :param args: argparse arguments
    :return: Set of tuples containing random integer 2D coordinates
    '''

    # Extract parameters from args.
    min_coord = args.min_coord
    max_coord = args.max_coord
    num_points = args.num_points

    # Sanity check parameters.
    assert isinstance(min_coord, int)
    assert isinstance(max_coord, int)
    assert isinstance(num_points, int)
    assert num_points >= 3
    assert min_coord < max_coord

    # Generate random 2D integer points.
    random_coords = []
    for _ in range(num_points):
        # coords or tuples containing random integer coordinates
        coords = (random.randint(min_coord, max_coord),
                  random.randint(min_coord, max_coord))
        random_coords.append(coords)

    # Convert list to set.
    random_coords_set = set(random_coords)
    print('Generated random 2D integer points:', random_coords_set)

    return random_coords_set


def _int_range(int_min=None, int_max=None):
    '''
    Create function to check integer argument is within acceptable range.

    :param int_min: Minimum integer of acceptable range
    :param int_max: Maximum integer of acceptable range
    :return: check_range function for use by argparse
    '''

    # Function to check integer argument is within acceptable range.
    def check_range(int_arg):
        int_arg = int(int_arg)

        if int_arg < int_min and int_min is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]"
                    % (int_arg, int_min, int_max))

        if int_arg > int_max and int_max is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]"
                    % (int_arg, int_min, int_max))

        return int_arg

    return check_range


if __name__ == "__main__":
    # Command line argument handling with argparse.
    parser = argparse.ArgumentParser(
            description='Find the minimum enclosing circle for a polygon')

    # Verbose option
    parser.add_argument('-v',  '--verbose',
            help='Print additional information - default=%(default)s',
            default=False, action="store_true")

    # Number of points/vertices to generate.
    # For use with both regular polygon and random point generation.
    gen_points = parser.add_argument_group(
            'Optional argument for generate regular polygon and random points',
            'Has no effect if only argument. Use with -rd or -mi & -mx options.')
    gen_points.add_argument('-np', '--num_points',
            help='Number of points/vertices to generate', default=3,
            type=_int_range(3, 10), metavar="[3, 10]")

    # Radius to use with regular polygon generation.
    # radius is mutually exclusive with min_coord and max_coord
    gen_reg_poly = parser.add_argument_group(
            'Required argument for generate regular polygon',
            'Mutually exclusive with min_coord and max_coord')
    arg_radius = gen_reg_poly.add_argument('-rd', '--radius',
            help='Radius of regular polygon', default=None,
            type=_int_range(1, 10), metavar="[1, 10]")

    # Minimum and maximum values to use for random point generation.
    # min_coord and max_coord are mutually exclusive with radius
    gen_rand_points = parser.add_argument_group(
            'Required arguments for generate random points',
            'Mutually exclusive with radius')
    arg_min = gen_rand_points.add_argument('-mi', '--min_coord',
            help='Minimum value for random point generation',
            default=None, type=_int_range(-10, 10), metavar="[-10, 10]")
    arg_max = gen_rand_points.add_argument('-mx', '--max_coord',
            help='Maximum value for random point generation',
            default=None, type=_int_range(-10, 10), metavar="[-10, 10]")

    # Enforce mutual exclusion betweeen radius and min_coord.
    g1 = parser.add_mutually_exclusive_group()
    g1._group_actions.append(arg_radius)
    g1._group_actions.append(arg_min)

    # Enforce mutual exclusion betweeen radius and max_coord.
    g2 = parser.add_mutually_exclusive_group()
    g2._group_actions.append(arg_radius)
    g2._group_actions.append(arg_max)

    # Parse argparse arguments.
    cliargs = parser.parse_args()

    # Ensure both min_coord and max_coord are specified.
    if (cliargs.min_coord is None and cliargs.max_coord is not None) or \
       (cliargs.min_coord is not None and cliargs.max_coord is None):
        parser.error("Both -mi/--min_coord and -mx/--max_coord are required")

    # Verbose print function - used in get_convex_hull function.
    print_v = print if cliargs.verbose else lambda *a, **k: None

    # Call main function.
    main(cliargs)
