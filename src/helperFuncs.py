import math
from geometry import *

def circle_from_three_points(A, B, C):
    """
    Given three points A, B, C, returns Point(x,y), radius
    """
    # Extract coordinates
    x1, y1 = A.x, A.y
    x2, y2 = B.x, B.y
    x3, y3 = C.x, C.y

    # Calculate the determinants
    temp = x2**2 + y2**2
    bc = (x1**2 + y1**2 - temp) / 2.0
    cd = (temp - x3**2 - y3**2) / 2.0
    det = (x1 - x2)*(y2 - y3) - (x2 - x3)*(y1 - y2)

    if abs(det) < 1e-10:
        raise ValueError("Points are collinear or too close together")

    # Center coordinates
    cx = (bc*(y2 - y3) - cd*(y1 - y2)) / det
    cy = ((x1 - x2)*cd - (x2 - x3)*bc) / det

    # Radius
    r = math.hypot(cx - x1, cy - y1)

    return cx, cy, r

def angle_from_three_points(A, B, C):
    """
    Return the angle at point B between AB and CB in radians.
    """
    ax, ay = A.x - B.x, A.y - B.y
    cx, cy = C.x - B.x, C.y - B.y

    dot = ax*cx + ay*cy
    mag_a = math.hypot(ax, ay)
    mag_c = math.hypot(cx, cy)

    if mag_a == 0 or mag_c == 0:
        raise ValueError("Cannot calculate angle with zero-length side")

    cos_theta = dot / (mag_a * mag_c)
    cos_theta = max(-1, min(1, cos_theta))  # clamp for safety
    return math.acos(cos_theta)

# Standalone function to check if a list of Points are colinear
def are_points_colinear(points, tol=1e-9):
    """
    Returns True if all defined points in the list are colinear.
    Fewer than 3 points are trivially colinear.
    Only considers defined points.
    """
    defined_points = [p for p in points if getattr(p, 'isDefined', lambda: False)() ]
    if len(defined_points) < 3:
        return True
    p1, p2 = defined_points[0], defined_points[1]
    # Use the same logic as Line.pointOnLine for each remaining point
    # Handle vertical line
    if abs(p2.x - p1.x) < tol:
        for p in defined_points[2:]:
            if abs(p.x - p1.x) >= tol:
                return False
        return True
    else:
        m = (p2.y - p1.y) / (p2.x - p1.x)
        for p in defined_points[2:]:
            expected_y = m * (p.x - p1.x) + p1.y
            if abs(p.y - expected_y) >= tol:
                return False
        return True
