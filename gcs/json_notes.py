"""
    Get parameters from json file :
    prefix: string
        Folder name to store the results
    with_graphes: bool
        true if all the graphes are shown and saved in png files,
        false otherwise
    seed: integer
        Random seed which can be used to reproduce a random selection
        if >0
    For each domain :
    |    name: string
    |        Domain name
    |    background: string
    |        Image file used as background
    |    px: float
    |        Pixel size in meters (also called space step)
    |    width: integer
    |        Domain width (equal to the width of the background image)
    |    height: integer
    |        Domain height (equal to the height of the background image)
    |    wall_colors: list
    |        rgb colors for walls
    |        [ [r,g,b],[r,g,b],... ]
    |    shape_lines: list
    |        Used to define the Matplotlib Polyline shapes,
    |        [
    |          {
    |             "xx": [x0,x1,x2,...],
    |             "yy": [y0,y1,y2,...],
    |             "linewidth": float,
    |             "outline_color": [r,g,b],
    |             "fill_color": [r,g,b]
    |          },...
    |        ]
    |    shape_circles: list
    |        Used to define the Matplotlib Circle shapes,
    |        [
    |           {
    |             "center_x": float,
    |             "center_y": float,
    |             "radius": float,
    |             "outline_color": [r,g,b],
    |             "fill_color": [r,g,b]
    |            },...
    |        ]
    |    shape_ellipses: list
    |        Used to define the Matplotlib Ellipse shapes,
    |        [
    |           {
    |             "center_x": float,
    |             "center_y": float,
    |             "width": float,
    |             "height": float,
    |             "angle_in_degrees_anti-clockwise": float (degre),
    |             "outline_color": [r,g,b],
    |             "fill_color": [r,g,b]
    |            },...
    |        ]
    |    shape_rectangles: list
    |        Used to define the Matplotlib Rectangle shapes,
    |        [
    |           {
    |             "bottom_left_x": float,
    |             "bottom_left_y": float,
    |             "width": float,
    |             "height": float,
    |             "angle_in_degrees_anti-clockwise": float (degre),
    |             "outline_color": [r,g,b],
    |             "fill_color": [r,g,b]
    |            },...
    |        ]
    |    shape_polygons: list
    |        Used to define the Matplotlib Polygon shapes,
    |        [
    |           {
    |             "xy": float,
    |             "outline_color": [r,g,b],
    |             "fill_color": [r,g,b]
    |            },...
    |        ]
    |    destinations: list
    |        Used to define the Destination objects,
    |        [
    |           {
    |             "name": string,
    |             "colors": [[r,g,b],...],
    |             "excluded_colors": [[r,g,b],...],
    |             "desired_velocity_from_color": [] or
    |             [
    |                {
    |                   "color": [r,g,b],
    |                   "desired_velocity": [ex,ey]
    |                },...
    |             ],
    |             "velocity_scale": float,
    |             "next_destination": null or string,
    |             "next_domain": null or string,
    |             "next_transit_box": null or [[x0,y0],...,[x3,y3]]
    |            },...
    |        ]
    |--------------------
    For each group of persons, required for the initialization process:
    |    nb:
    |        Number of people in the group
    |    domain:
    |        Name of the domain where people are located
    |    radius_distribution:
    |        Radius distribution used to create people
    |        ["uniform",min,max] or ["normal",mean,sigma]
    |    velocity_distribution:
    |        Velocity distribution used to create people
    |        ["uniform",min,max] or ["normal",mean,sigma]
    |    box:
    |        Boxe to randomly position people at initialization
    |        [ [x0,y0],[x1,y1],...]
    |    destination:
    |        Initial destination for the group
    |--------------------
    For each sensor:
    |    domain:
    |        Name of the domain where the sensor is located
    |    line:
    |        Segment through which incoming and outgoing flows are measured
    |        [x0,y0,x1,y1]
    |--------------------
    Tf: float
        Final time
    dt: float
        Time step
    drawper: integer
        The results will be displayed every "drawper" iterations
    mass: float
        Mass of one person (typically 80 kg)
    tau: float
        (typically 0.5 s)
    F: float
        Coefficient for the repulsion force between individuals
        (typically 2000 N)
    kappa: float
        Stiffness constant to handle overlapping (typically
        120000 kg s^-2)
    delta: float
        To maintain a certain distance from neighbors (typically 0.08 m)
    Fwall: float
        Coefficient for the repulsion force between individual and
        walls (typically 2000 N, like for F)
    lambda: float
        Directional dependence (between 0 and 1 = fully isotropic case)
    eta: float
        Friction coefficient (typically 240000 kg m^-1 s^-1)
    projection_method: string
        Name of the projection method : cvxopt(default),
        mosek(a licence is needed) or uzawa
    dmax: float
        Maximum distance used to detect neighbors
    dmin_people: float
        Minimum distance allowed between individuals
    dmin_walls: float
        Minimum distance allowed between an individual and a wall
    plot_people: boolean
        If true, people are drawn
    plot_contacts: boolean
        If true, active contacts between people are drawn
    plot_desired_velocities: boolean
        If true, people desired velocities are drawn
    plot_velocities: boolean
        If true, people velocities are drawn
    plot_sensors: boolean
        If true, plot sensor lines on people graph and sensor data graph
    plot_paths: boolean
        If true, people paths are drawn
"""