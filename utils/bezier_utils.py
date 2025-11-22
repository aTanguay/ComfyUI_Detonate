"""
Bezier curve utilities for ComfyUI_Detonate.

Implements de Casteljau's algorithm and curve evaluation for rotoscoping.
Based on Natron's Bezier implementation.
"""

import numpy as np
from typing import List, Tuple


def de_casteljau(t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Evaluate Bezier curve at parameter t using de Casteljau's algorithm.

    This is the most numerically stable method for Bezier evaluation.

    Args:
        t: Parameter value (0.0 to 1.0)
        points: Control points [(x0,y0), (x1,y1), (x2,y2), (x3,y3)]
                For cubic Bezier: [P0, P1, P2, P3]

    Returns:
        (x, y) position on curve at parameter t

    Algorithm:
        Recursive linear interpolation between points
        More stable than direct polynomial evaluation
    """
    if len(points) == 1:
        return points[0]

    # Linear interpolation between consecutive points
    new_points = []
    for i in range(len(points) - 1):
        x = (1 - t) * points[i][0] + t * points[i + 1][0]
        y = (1 - t) * points[i][1] + t * points[i + 1][1]
        new_points.append((x, y))

    return de_casteljau(t, new_points)


def evaluate_cubic_bezier(p0: Tuple[float, float],
                          p1: Tuple[float, float],
                          p2: Tuple[float, float],
                          p3: Tuple[float, float],
                          t: float) -> Tuple[float, float]:
    """
    Evaluate cubic Bezier curve at parameter t.

    Uses de Casteljau's algorithm for numerical stability.

    Args:
        p0: Start point (x, y)
        p1: First control point (x, y)
        p2: Second control point (x, y)
        p3: End point (x, y)
        t: Parameter (0.0 to 1.0)

    Returns:
        (x, y) position on curve
    """
    return de_casteljau(t, [p0, p1, p2, p3])


def discretize_bezier_segment(p0: Tuple[float, float],
                              p1: Tuple[float, float],
                              p2: Tuple[float, float],
                              p3: Tuple[float, float],
                              num_samples: int = 20) -> List[Tuple[float, float]]:
    """
    Discretize cubic Bezier segment into line segments.

    Args:
        p0, p1, p2, p3: Cubic Bezier control points
        num_samples: Number of samples along curve

    Returns:
        List of (x, y) points along curve
    """
    points = []
    for i in range(num_samples + 1):
        t = i / num_samples
        point = evaluate_cubic_bezier(p0, p1, p2, p3, t)
        points.append(point)
    return points


def discretize_spline(spline_points: List[dict],
                     closed: bool = True,
                     samples_per_segment: int = 20) -> np.ndarray:
    """
    Discretize entire Bezier spline into points.

    Args:
        spline_points: List of point dicts with:
                       - x, y: point position
                       - handleIn: {x, y} incoming tangent offset
                       - handleOut: {x, y} outgoing tangent offset
        closed: Whether spline is closed
        samples_per_segment: Samples per Bezier segment

    Returns:
        Numpy array of shape (N, 2) with discretized points
    """
    if len(spline_points) < 2:
        return np.array([])

    all_points = []

    # Process each segment
    num_segments = len(spline_points) if closed else len(spline_points) - 1

    for i in range(num_segments):
        p0_data = spline_points[i]
        p1_data = spline_points[(i + 1) % len(spline_points)]

        # Construct cubic Bezier control points
        p0 = (p0_data['x'], p0_data['y'])
        # Control point 1: start point + out handle
        p1 = (p0_data['x'] + p0_data['handleOut']['x'],
              p0_data['y'] + p0_data['handleOut']['y'])
        # Control point 2: end point + in handle
        p2 = (p1_data['x'] + p1_data['handleIn']['x'],
              p1_data['y'] + p1_data['handleIn']['y'])
        p3 = (p1_data['x'], p1_data['y'])

        # Discretize this segment
        segment_points = discretize_bezier_segment(p0, p1, p2, p3, samples_per_segment)

        # Avoid duplicate points at segment boundaries
        if i > 0:
            segment_points = segment_points[1:]

        all_points.extend(segment_points)

    return np.array(all_points, dtype=np.float32)


def compute_curve_tangent(p0: Tuple[float, float],
                         p1: Tuple[float, float],
                         p2: Tuple[float, float],
                         p3: Tuple[float, float],
                         t: float) -> Tuple[float, float]:
    """
    Compute tangent (derivative) of cubic Bezier at parameter t.

    Used for computing normals for feathering.

    Args:
        p0, p1, p2, p3: Cubic Bezier control points
        t: Parameter (0.0 to 1.0)

    Returns:
        (dx, dy) tangent vector (unnormalized)
    """
    # Derivative of cubic Bezier curve
    # B'(t) = 3(1-t)²(P1-P0) + 6(1-t)t(P2-P1) + 3t²(P3-P2)

    one_minus_t = 1.0 - t

    dx = (3 * one_minus_t ** 2 * (p1[0] - p0[0]) +
          6 * one_minus_t * t * (p2[0] - p1[0]) +
          3 * t ** 2 * (p3[0] - p2[0]))

    dy = (3 * one_minus_t ** 2 * (p1[1] - p0[1]) +
          6 * one_minus_t * t * (p2[1] - p1[1]) +
          3 * t ** 2 * (p3[1] - p2[1]))

    return (dx, dy)


def normalize_vector(v: Tuple[float, float]) -> Tuple[float, float]:
    """
    Normalize a 2D vector.

    Args:
        v: (x, y) vector

    Returns:
        Normalized vector (length = 1)
    """
    length = np.sqrt(v[0] ** 2 + v[1] ** 2)
    if length < 1e-10:
        return (0.0, 0.0)
    return (v[0] / length, v[1] / length)


def perpendicular(v: Tuple[float, float]) -> Tuple[float, float]:
    """
    Get perpendicular vector (90° rotation).

    Args:
        v: (x, y) vector

    Returns:
        Perpendicular vector (-y, x)
    """
    return (-v[1], v[0])


def adaptive_sampling(p0: Tuple[float, float],
                     p1: Tuple[float, float],
                     p2: Tuple[float, float],
                     p3: Tuple[float, float],
                     flatness_threshold: float = 0.5) -> List[Tuple[float, float]]:
    """
    Adaptive sampling of Bezier curve based on curvature.

    More samples where curve is more curved, fewer on flat sections.
    Better quality than uniform sampling.

    Args:
        p0, p1, p2, p3: Cubic Bezier control points
        flatness_threshold: Maximum allowed deviation (pixels)

    Returns:
        List of (x, y) points
    """
    # Check if curve is flat enough
    # Flatness criterion: distance from control points to line P0-P3

    def point_to_line_distance(point, line_start, line_end):
        """Distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end

        line_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if line_len_sq < 1e-10:
            return np.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # Perpendicular distance
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len_sq))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        return np.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)

    max_dist = max(
        point_to_line_distance(p1, p0, p3),
        point_to_line_distance(p2, p0, p3)
    )

    if max_dist < flatness_threshold:
        # Curve is flat enough, return endpoints
        return [p0, p3]
    else:
        # Subdivide curve at t=0.5
        # De Casteljau subdivision
        mid_01 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        mid_12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        mid_23 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)

        mid_012 = ((mid_01[0] + mid_12[0]) / 2, (mid_01[1] + mid_12[1]) / 2)
        mid_123 = ((mid_12[0] + mid_23[0]) / 2, (mid_12[1] + mid_23[1]) / 2)

        mid_point = ((mid_012[0] + mid_123[0]) / 2, (mid_012[1] + mid_123[1]) / 2)

        # Recurse on both halves
        left_points = adaptive_sampling(p0, mid_01, mid_012, mid_point, flatness_threshold)
        right_points = adaptive_sampling(mid_point, mid_123, mid_23, p3, flatness_threshold)

        # Combine (avoid duplicate mid_point)
        return left_points[:-1] + right_points
