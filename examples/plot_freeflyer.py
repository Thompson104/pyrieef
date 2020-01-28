#!/usr/bin/env python

# Copyright (c) 2020, University of Stuttgart
# All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for any purpose
# with or without   fee is hereby granted, provided   that the above  copyright
# notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS  SOFTWARE INCLUDING ALL  IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR  BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR  ANY DAMAGES WHATSOEVER RESULTING  FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION,   ARISING OUT OF OR IN    CONNECTION WITH THE USE   OR
# PERFORMANCE OF THIS SOFTWARE.
#
#                                      Jim Mainprice on Monday January 27 2020

import demos_common_imports
from pyrieef.geometry.workspace import *
from pyrieef.geometry.rotations import *
from pyrieef.kinematics.robot import *
from pyrieef.rendering.workspace_renderer import WorkspaceDrawer


robot = create_robot_from_file(scale=.02)
workspace = Workspace()
body = Polygon(origin=np.array([0, 0]), verticies=robot.shape)
workspace.obstacles.append(body)
sdf = SignedDistanceWorkspaceMap(workspace)
body.nb_points = 20
points = body.sampled_points()
viewer = WorkspaceDrawer(workspace, wait_for_keyboard=True)
q = np.array([.1, .1, -.5])
viewer.draw_ws_polygon(robot.shape, q[:2], q[2])
# for name, i in robot.keypoint_names.items():
#     p = robot.keypoint_map(i)(q)
#     viewer.draw_ws_point(p, color='b', shape='o')

R = rotation_matrix_2d_radian(q[2])
print(len(points))
for p in points:
    viewer.draw_ws_point(np.dot(R, p) + q[:2], color='b', shape='o')
viewer.background_matrix_eval = True
viewer.draw_ws_background(sdf, nb_points=200)
viewer.show_once()