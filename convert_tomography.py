import numpy as np
# from panel import widget
import uproot
import os
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import vtk
from vtk.util import numpy_support
from vtk.util import colors as vtk_colors
import matplotlib

def convert_tomography(input_file, input_folder):
    # Load the input file

    input_path = os.path.join(input_folder, input_file)
    print(input_path)
    if os.path.exists(input_path):
        print("File exists")
    else:
        print("File does not exist")
    f = uproot.open(input_path)

    # Get the keys
    keys = f.keys()

    # Print the keys
    print(keys)

    # Load the data
    data = f[keys[0]].to_numpy()

    print(data)

    for i, sub_item in enumerate(data):
        # print(i, sub_item)
        if isinstance(sub_item, np.ndarray):
            print("This is a numpy array")
            print(sub_item.shape)
            if np.ndim(sub_item) == 1:
                print("This is a 1D numpy array")
                print(sub_item)
            elif np.ndim(sub_item) == 2:
                print("This is a 2D numpy array")
                print(sub_item)
            elif np.ndim(sub_item) == 3:
                print("This is a 3D numpy array")
                print(sub_item)

                # plt.figure()
                # plt.imshow(sub_item[:,:,50])
                # plt.show()
                return sub_item


def add_volume(volume,
               renderer=None,
               spacing=(1, 1, 1),
               c_range=None,
               opacity_range=(0, 1),
               outline=False,
               colormap='viridis',
               clip_to_range=False,
               shade=False,
               blend_mode='composite',
               render_mode='smart',
               origin=(0, 0, 0),
               name='Field',
               verbose=False):
    """[Adds a volume to the current VTK renderer from a 3D Numpy array]

    Arguments:
        volume {[Numpy array (x,y,z)]} -- [the numpy volume you want to add]
        renderer {[VTK renderer]} -- [the current vtk renderer]

    Keyword Arguments:
        spacing {int} -- [grid spacing for volume] (default: {1})
        c_range {[type]} -- [range to evaluate scalar over] (default: {None})
        colormap {str} -- [the colormap of the volume] (default: {'viridis'})
        clip_to_range {bool} -- [allows you to clip the volume to the specified color range] (default: {False})
    """
    
    #print('numpy matrix shape:', volume.shape)


    if verbose:
        print('Adding volume')

    if clip_to_range and (c_range is not None):
        volume[volume > c_range[0]] = c_range[0]
        volume[volume > c_range[1]] = c_range[1]

    if c_range is None:
        c_range = (0, np.nanmax(volume))
        if verbose:
            print(c_range)
    im = vtk.vtkImageData()


    im.AllocateScalars(numpy_support.get_vtk_array_type(volume.dtype), 1)
    im.SetSpacing(spacing)
    im.SetOrigin(origin) 
    # im.SetOrigin(spacing[0]*(-volume.shape[0]/2)+origin[0], spacing[1]*(-volume.shape[1]/2)+origin[1], spacing[2]*(-volume.shape[2]/2) + origin[2])
    
    # im.SetDimensions(volume.shape[0]+1, volume.shape[1]+1, volume.shape[2]+1)
    # padded_volume = np.pad(volume, ((0, 1), (0, 1), (0, 1)), mode='constant', constant_values=0)
    # v_image = numpy_support.numpy_to_vtk(padded_volume.T.flat)
    
    im.SetDimensions(volume.shape[0], volume.shape[1], volume.shape[2])
    v_image = numpy_support.numpy_to_vtk(volume.T.flat)

    im.GetPointData().SetScalars(v_image)
    # im.GetCellData().SetScalars(v_image)
    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(c_range[0], opacity_range[0])
    # opacityTransferFunction.AddPoint(c_range[1]*0.9, 0.1)
    opacityTransferFunction.AddPoint(c_range[1], opacity_range[1])

    colormap = make_colormap(c_range=c_range, color=colormap)

    # Create transfer mapping scalar value to color
    colorTransferFunction = vtk.vtkColorTransferFunction()
    for color in colormap:
        colorTransferFunction.AddRGBPoint(color[0], color[1], color[2], color[3])

    if outline:
        outline = vtk.vtkOutlineFilter()
        vfilter = vtk.vtkImageDataGeometryFilter()
        vfilter.SetInputData(im)
        outline.SetInputConnection(vfilter.GetOutputPort())
        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputConnection(outline.GetOutputPort())
        outlineactor = vtk.vtkActor()
        outlineactor.GetProperty().SetColor(0, 0, 0)
        outlineactor.SetMapper(mapper2)

    # The property describes how the data will look
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)

    if shade:
        volumeProperty.ShadeOn()
    else:
        volumeProperty.ShadeOff()

    # volumeProperty.SetInterpolationTypeToLinear()
    volumeProperty.SetInterpolationTypeToNearest()

    if render_mode == 'smart':
        volumeMapper = vtk.vtkSmartVolumeMapper()
    elif render_mode == 'GPU':
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    elif render_mode == 'CPU':
        volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
        volumeMapper.AutoAdjustSampleDistancesOn()
    elif render_mode == 'openGL':
        volumeMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()

    if blend_mode == 'composite':
        volumeMapper.SetBlendModeToComposite()
    elif blend_mode == 'maximum':
        volumeMapper.SetBlendModeToMaximumIntensity()
    elif blend_mode == 'minimum':
        volumeMapper.SetBlendModeToMinimumIntensity()
    elif blend_mode == 'average':
        volumeMapper.SetBlendModeToAverageIntensity()
    elif blend_mode == 'Additive':
        volumeMapper.SetBlendModeToAdditive()
    elif blend_mode == 'iso':
        volumeMapper.SetBlendModeToIsoSurface()
    elif blend_mode == 'slice':
        volumeMapper.SetBlendModeToSlice()

    if verbose:
        print('Blend mode is:', volumeMapper.GetBlendMode())

    volumeMapper.SetInputData(im)

    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    volume.SetObjectName(name)

    volume.SetPickable(False)

    if renderer is None:
        if outline:
            return [volume, outlineactor]
        else:
            return volume
    else:
        renderer.AddVolume(volume)

        if outline:
            renderer.AddActor(outlineactor)

        if verbose:
            print('Volume added')

def add_stl(filename,
             renderer=None,
             opacity=1.0,
             specular=0.1,
             ambient=0.0,
             scale=(1, 1, 1),
             translate=(0, 0, 0),
             rotate=(0, 0, 0),
             mesh_color="blue",
             use_wireframe=False,
             scale_then_translate=False,
             smoothing_passes=0,
             max_subdivisions=0,
             name=None
             ):
    """[Used to load in standard STL files and translate them]

    Arguments:
        filename {[string]} -- [the filename of the STL]

    Keyword Arguments:
        opacity {float} -- [opacity of the object] (default: {1.0})
        scale {tuple} -- [x,y,z scale] (default: {(1, 1, 1)})
        translate {tuple} -- [x,y,z shift] (default: {(0, 0, 0)})
        rotate {tuple} -- [rotation in degrees] (default: {(0, 0, 0)})
        mesh_color {str} -- [color of the mesh, taken from VTK colors] (default: {"blue"})
        use_wireframe {bool} -- [renders the wireframe instead] (default: {False})
    """

    colors = vtk.vtkNamedColors()

    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()

    transform = vtk.vtkTransform()
    transform.RotateX(rotate[0])
    transform.RotateY(rotate[1])
    transform.RotateZ(rotate[2])

    if scale_then_translate:
        transform.Scale(scale)
        transform.Translate(translate)
    else:
        transform.Translate(translate)
        transform.Scale(scale)

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(reader.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    normals_filter = vtk.vtkPolyDataNormals()

    if max_subdivisions > 0:

        print('subdividing mesh, may take a while')

        subdivider = vtk.vtkAdaptiveSubdivisionFilter()
        subdivider.SetMaximumNumberOfPasses(max_subdivisions)
        subdivider.SetInputConnection(transformFilter.GetOutputPort())
        subdivider.Update()
        transformFilter = subdivider

    if smoothing_passes > 0:

        smooth_loop = vtk.vtkSmoothPolyDataFilter()
        smooth_loop.SetNumberOfIterations(smoothing_passes)
        smooth_loop.SetRelaxationFactor(0.1)
        smooth_loop.BoundarySmoothingOn()
        smooth_loop.SetInputConnection(transformFilter.GetOutputPort())
        smooth_loop.Update()
        # mapper = vtk.vtkPolyDataMapper()

        # mapper.SetInputConnection(smooth_loop.GetOutputPort())
        normals_filter.SetInputConnection(smooth_loop.GetOutputPort())
    else:
        normals_filter.SetInputConnection(transformFilter.GetOutputPort())

    normals_filter.ComputePointNormalsOn()
    normals_filter.ComputeCellNormalsOn()
    normals_filter.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals_filter.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    if mesh_color is not None:
        if isinstance(mesh_color, str):
            actor.GetProperty().SetColor(colors.GetColor3d(mesh_color))
        else:
            actor.GetProperty().SetColor(mesh_color[0], mesh_color[1], mesh_color[2])
    actor.GetProperty().SetOpacity(opacity)

    actor.GetProperty().SetSpecular(specular)
    actor.GetProperty().SetSpecularPower(80.0)
    actor.GetProperty().SetAmbient(ambient)

    actor.GetProperty().SetInterpolationToGouraud()

    if name is not None:
        actor.SetObjectName(name)
    else:
        actor.SetObjectName(filename)

    if use_wireframe:
        actor.GetProperty().SetRepresentationToWireframe()

    if renderer is None:
        return actor
    else:
        renderer.AddActor(actor)


def make_colormap(c_range=(0,1), color='viridis', total_colors=100, invert=False, verbose=False):

    total_colors = int(total_colors)

    # Possible values are: 

    # Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r,
    # BuGn, BuGn_r, BuPu, BuPu_r, CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu,
    # GnBu_r, Greens, Greens_r, Greys, Greys_r, OrRd, OrRd_r, Oranges, Oranges_r,
    # PRGn, PRGn_r, Paired, Paired_r, Pastel1, Pastel1_r, Pastel2, Pastel2_r,
    # PiYG, PiYG_r, PuBu, PuBuGn, PuBuGn_r, PuBu_r, PuOr, PuOr_r, PuRd, PuRd_r,
    # Purples, Purples_r, RdBu, RdBu_r, RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu,
    # RdYlBu_r, RdYlGn, RdYlGn_r, Reds, Reds_r, Set1, Set1_r, Set2, Set2_r,
    # Set3, Set3_r, Spectral, Spectral_r, Wistia, Wistia_r, YlGn, YlGnBu,
    # YlGnBu_r, YlGn_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r,
    # autumn, autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r,
    # cividis, cividis_r, cool, cool_r, coolwarm, coolwarm_r, copper, copper_r,
    # cubehelix, cubehelix_r, flag, flag_r, gist_earth, gist_earth_r, gist_gray,
    # gist_gray_r, gist_heat, gist_heat_r, gist_ncar, gist_ncar_r, gist_rainbow,
    # gist_rainbow_r, gist_stern, gist_stern_r, gist_yarg, gist_yarg_r, gnuplot,
    # gnuplot2, gnuplot2_r, gnuplot_r, gray, gray_r, hot, hot_r, hsv, hsv_r,
    # inferno, inferno_r, jet, jet_r, magma, magma_r, nipy_spectral,
    # nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma, plasma_r,
    # prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spring,
    # spring_r, summer, summer_r, tab10, tab10_r, tab20, tab20_r, tab20b,
    # tab20b_r, tab20c, tab20c_r, terrain, terrain_r, twilight, twilight_r,
    # twilight_shifted, twilight_shifted_r, viridis, viridis_r, winter, winter_r

    if verbose:
        if color is None:
            print('No colormap supplied, defaulting to Viridis')
        else:
            print('Making colormap:', color)

    if verbose:
        print('Using Matplotlib color tables')
    mpl_data = matplotlib.cm.get_cmap(color)
    cm_data = np.zeros([total_colors, 3])
    for i in range(total_colors):
        cm_data[i,:] = mpl_data(i/total_colors)[0:3]

    colormap = np.asarray(cm_data)

    if invert:
        if verbose:
            print('Using inverted direction')
        colormap = np.flip(colormap, axis=0)

    scale = np.linspace(c_range[0], c_range[1], num=colormap.shape[0])

    colormap = np.vstack([scale, colormap.T]).T

    if verbose:
        print('Colormap made')

    return colormap


def make_LUT(colormap='viridis', invert=False, verbose=False, c_range=(0,1), nan_color=(1,0,0,1), total_colors=100, scale_type='linear'):

    colormap = make_colormap(c_range=c_range, color=colormap, invert=invert, total_colors=total_colors, verbose=verbose)

    colorSeries = vtk.vtkColorSeries()
    colorSeries.SetNumberOfColors(colormap.shape[0])
    try:
        for total_colors, color in enumerate(colormap):
            color = (255*color[1:4]).astype(int) 
            vcolor = vtk.vtkColor3ub(color)
            colorSeries.SetColor(total_colors, vcolor)
        lut = vtk.vtkLookupTable()
        colorSeries.BuildLookupTable(lut, colorSeries.ORDINAL)
        lut.SetNanColor(nan_color)
    except TypeError:
        for total_colors, color in enumerate(colormap):
            color = (255*color[1:4]).astype(int) 
            vcolor = vtk.vtkColor3ub(color[0], color[1], color[2])
            colorSeries.SetColor(total_colors, vcolor)
        lut = vtk.vtkLookupTable()
        colorSeries.BuildLookupTable(lut, colorSeries.ORDINAL)
        lut.SetNanColor(nan_color)
        lut.SetRange(c_range)

    if scale_type == 'linear':

        lut.SetScaleToLinear()

    elif scale_type == 'logarithmic':

        lut.SetScaleToLog10()

    return lut


def volume_origin_from_front_center(shape, spacing=(1, 1, 1),
                                    front_center=(0, 0, 0)):
    """Place the center of a volume's maximum-Z bound at ``front_center``.

    VTK image bounds run from the origin to ``(dimension - 1) * spacing``.
    The data's detector front is its maximum-Z face, so the Z origin is shifted
    backwards by the full sampled depth. Using ``dimension - 1`` also centers
    the voxel bounds exactly without introducing a half-voxel offset.
    """
    if len(shape) != 3 or len(spacing) != 3 or len(front_center) != 3:
        raise ValueError("shape, spacing, and front_center must have three values")

    return (
        float(front_center[0]) - 0.5 * (shape[0] - 1) * spacing[0],
        float(front_center[1]) - 0.5 * (shape[1] - 1) * spacing[1],
        float(front_center[2]) - (shape[2] - 1) * spacing[2],
    )



def add_contours(input_data,
                 renderer=None,
                 c_number=10,
                 c_range=None,
                 spacing=(1, 1, 1),
                 opacity=1.0,
                 origin=None,
                 colormap='viridis',
                 name='Contour',
                 shade=False,
                 passthrough=False,
                 color_override=None,
                 pickable=False):
    """[Adds contours of a volume to the current renderer]

    Arguments:
        input_data {[NUmpy array (x,y,z)]} -- [the volume to contour]
        renderer {[VTK renderer]} -- [the current VTK renderer]

    Keyword Arguments:
        c_number {int} -- [description] (default: {10})
        c_range {[type]} -- [description] (default: {None})
        spacing {tuple} -- [description] (default: {(1,1,1)})
        opacity {float} -- [description] (default: {0.5})
        origin {[type]} -- [description] (default: {None})
    """

    # print('Adding contours')
    colors = vtk.vtkNamedColors()

    # print(type(input_data))

    if type(input_data) == type(vtk.vtkImageData()):

        # print('data is an vtk image data')

        im = input_data
        try:
            c_range = im.GetPointData().GetArray("ImageScalars").GetValueRange()
        except AttributeError:
           c_range = [0,1] 

        # image_shape = im.GetDimensions()
        passthrough = True

        # LUT = LUT_utils.make_LUT(colormap=colormap, c_range=(c_range))

    elif type(input_data) == type(vtk.vtkStructuredPoints()):

        # im = input_data

        # c_range = im.GetPointData().GetArray().GetValueRange()

        # image_shape = im.GetDimensions()

        # LUT = LUT_utils.make_LUT(colormap=colormap, c_range=(c_range))
        passthrough = True
        c_range = [0,1]


    elif type(input_data) == type(vtk.vtkVolume()):
        input_data = input_data.GetMapper().GetInput()

        # print(input_data)

        # LUT = aux_material.make_LUT(colormap=colormap, c_range=c_range)
        # LUT.SetSaturationRange(1.0, 1.0)
        # LUT.SetTableRange(0,1)
        passthrough = True

    else:

        # print('data is not vtk image data')

        # vol = vtk.vtkStructuredPoints()
        # vol.SetDimensions(input_data.shape[0], input_data.shape[1], input_data.shape[2])
        # if origin is None:
        #     vol.SetOrigin(spacing[0]*(-input_data.shape[0]/2), spacing[1]*(-input_data.shape[1]/2), (spacing[2]*(-input_data.shape[2]/2)))
        # else:
        #     vol.SetOrigin(origin)
        # vol.SetSpacing(spacing[0], spacing[1], spacing[2])

        scalars = vtk.vtkDoubleArray()
        scalars.SetNumberOfComponents(1)

        # ---------------------------------------------------------------------

        im = vtk.vtkImageData()
        im.SetDimensions(input_data.shape[0], input_data.shape[1], input_data.shape[2])

        im.AllocateScalars(numpy_support.get_vtk_array_type(input_data.dtype), 1)
        im.SetSpacing(spacing[0], spacing[1], spacing[2])

        if origin is None:
            im.SetOrigin((spacing[0]*(-input_data.shape[0]/2)), (spacing[1]*(-input_data.shape[1]/2)), 0)
        else:
            im.SetOrigin(origin)

        v_image = numpy_support.numpy_to_vtk(input_data.T.flat)

        im.GetPointData().SetScalars(v_image)

        if c_range is None:
            c_range = (0, np.max(input_data))

    # ---------------------------------------------------------------------

    contour = vtk.vtkContourFilter()
    if passthrough:
        contour.SetInputData(input_data)
    else:
        contour.SetInputData(im)
    if c_number == 1:
        contour.SetValue(0, c_range[0])
    else:
        contour.GenerateValues(c_number, c_range)
    contour.ComputeScalarsOn()
    contour.Update()

    lut = make_LUT(colormap, c_range=c_range)
    # lut.SetTableRange(c_range[0], c_range[1])

    volMapper = vtk.vtkPolyDataMapper()
    volActor = vtk.vtkActor()
    volMapper.SetInputConnection(contour.GetOutputPort())
    if color_override is not None:
        volActor.GetProperty().SetColor(colors.GetColor3d(color_override))
        volMapper.ScalarVisibilityOff()
    else:
        volMapper.ScalarVisibilityOn()
    volMapper.SetScalarRange(c_range)
    volMapper.SetLookupTable(lut)

    volActor.SetMapper(volMapper)
    volActor.GetProperty().EdgeVisibilityOff()
    volActor.GetProperty().SetOpacity(opacity)

    volActor.GetProperty().SetInterpolationToFlat()
    volActor.SetPickable(pickable)

    volActor.SetObjectName(name)

    volActor.Modified()

    if not shade:
        volActor.GetProperty().LightingOff()
    if renderer is None:
        return volActor
    else:
        renderer.AddActor(volActor)
        print('Contours added')


def _line_segment_in_bounds(center, direction, bounds):
    """Return the part of an infinite line that lies inside VTK bounds."""
    center = np.asarray(center, dtype=float)
    direction = np.asarray(direction, dtype=float)
    direction_norm = np.linalg.norm(direction)
    if direction_norm == 0:
        raise ValueError("A sampling direction cannot be the zero vector.")
    direction /= direction_norm

    lower = np.asarray(bounds[0::2], dtype=float)
    upper = np.asarray(bounds[1::2], dtype=float)
    if np.any(center < lower) or np.any(center > upper):
        raise ValueError("The profile center must lie inside the image bounds.")

    t_min = -np.inf
    t_max = np.inf
    for axis in range(3):
        if abs(direction[axis]) < 1e-12:
            continue
        axis_t = (
            (lower[axis] - center[axis]) / direction[axis],
            (upper[axis] - center[axis]) / direction[axis],
        )
        t_min = max(t_min, min(axis_t))
        t_max = min(t_max, max(axis_t))

    return center + t_min * direction, center + t_max * direction


def add_volume_profile_lines(image_data,
                             renderer=None,
                             center=None,
                             directions=None,
                             number_of_samples=500,
                             line_width=4.0):
    """Sample a VTK image along several lines and optionally draw the lines.

    The returned profiles contain signed physical distance, interpolated scalar
    values, and the same RGB color used by the corresponding 3D line actor.
    """
    if directions is None:
        directions = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
            "XY diagonal": (1, 1, 0),
            "XYZ diagonal": (1, 1, 1),
        }

    if number_of_samples < 2:
        raise ValueError("number_of_samples must be at least 2.")

    bounds = image_data.GetBounds()
    if center is None:
        center = tuple((bounds[2 * i] + bounds[2 * i + 1]) / 2 for i in range(3))

    color_map = plt.get_cmap("tab10")
    profiles = []
    line_actors = []

    for index, (label, direction) in enumerate(directions.items()):
        point_1, point_2 = _line_segment_in_bounds(center, direction, bounds)

        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(point_1)
        line_source.SetPoint2(point_2)
        line_source.SetResolution(number_of_samples - 1)

        probe = vtk.vtkProbeFilter()
        probe.SetInputConnection(line_source.GetOutputPort())
        probe.SetSourceData(image_data)
        probe.Update()

        sampled_scalars = probe.GetOutput().GetPointData().GetScalars()
        if sampled_scalars is None:
            raise RuntimeError("The volume probe did not produce scalar samples.")
        values = numpy_support.vtk_to_numpy(sampled_scalars).astype(float, copy=True)

        valid_array = probe.GetOutput().GetPointData().GetArray("vtkValidPointMask")
        if valid_array is not None:
            valid = numpy_support.vtk_to_numpy(valid_array).astype(bool)
            values[~valid] = np.nan

        unit_direction = np.asarray(direction, dtype=float)
        unit_direction /= np.linalg.norm(unit_direction)
        distance_1 = np.dot(point_1 - np.asarray(center), unit_direction)
        distance_2 = np.dot(point_2 - np.asarray(center), unit_direction)
        distances = np.linspace(distance_1, distance_2, number_of_samples)
        color = tuple(float(component) for component in color_map(index % 10)[:3])
        profiles.append({
            "label": label,
            "distance": distances,
            "value": values,
            "color": color,
            "point_1": point_1,
            "point_2": point_2,
        })

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line_source.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetObjectName("ProfileLine_" + label.replace(" ", "_"))
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetRenderLinesAsTubes(True)
        actor.GetProperty().LightingOff()
        line_actors.append(actor)

        if renderer is not None:
            renderer.AddActor(actor)

    return profiles, line_actors


def _threshold_crossings(distance, values, threshold):
    """Linearly estimate profile locations and slopes at threshold crossings."""
    distance = np.asarray(distance)
    values = np.asarray(values)
    finite_pair = np.isfinite(values[:-1]) & np.isfinite(values[1:])
    offset = values - threshold
    crossing_indices = np.flatnonzero(
        finite_pair
        & ((offset[:-1] == 0) | (offset[:-1] * offset[1:] < 0))
    )

    locations = []
    slopes = []
    for index in crossing_indices:
        x_0, x_1 = distance[index:index + 2]
        y_0, y_1 = values[index:index + 2]
        if x_1 == x_0:
            continue
        slope = (y_1 - y_0) / (x_1 - x_0)
        if y_1 == y_0:
            location = (x_0 + x_1) / 2
        else:
            location = x_0 + (threshold - y_0) / slope
        locations.append(location)
        slopes.append(abs(slope))

    return np.asarray(locations), np.asarray(slopes)


def plot_volume_profiles(profiles, threshold=0.45, show=True, output_file=None):
    """Plot sampled intensity and its spatial slope for each 3D profile line."""
    figure, (profile_axis, slope_axis) = plt.subplots(
        2, 1, figsize=(11, 8), sharex=True, constrained_layout=True
    )

    for profile in profiles:
        distance = profile["distance"]
        values = profile["value"]
        color = profile["color"]
        label = profile["label"]

        profile_axis.plot(distance, values, color=color, label=label)
        gradient = np.abs(np.gradient(values, distance))
        slope_axis.plot(distance, gradient, color=color, label=label)

        locations, slopes = _threshold_crossings(distance, values, threshold)
        profile_axis.scatter(locations, np.full(locations.shape, threshold),
                             color=color, edgecolor="black", s=35, zorder=3)
        slope_axis.scatter(locations, slopes, color=color, edgecolor="black",
                           s=35, zorder=3)

        if locations.size:
            crossing_summary = ", ".join(
                f"d={location:.2f} (|slope|={slope:.4f})"
                for location, slope in zip(locations, slopes)
            )
            print(f"{label} crossings at {threshold:.3f}: {crossing_summary}")
        else:
            print(f"{label}: no crossing at {threshold:.3f}")

    profile_axis.axhline(threshold, color="black", linestyle="--",
                         linewidth=1.2, label=f"threshold = {threshold:g}")
    profile_axis.set_ylabel("Normalized volume value")
    profile_axis.set_title("1D profiles through the reconstructed crystal")
    profile_axis.grid(alpha=0.25)
    profile_axis.legend(ncol=2)

    slope_axis.set_xlabel("Signed distance along line (volume units)")
    slope_axis.set_ylabel(r"$|dI/ds|$")
    slope_axis.set_title("Boundary sharpness at the threshold crossings")
    slope_axis.grid(alpha=0.25)

    if output_file is not None:
        figure.savefig(output_file, dpi=200)

    if show:
        plt.show(block=False)
        plt.pause(0.001)

    return figure, (profile_axis, slope_axis)


def add_world_origin_marker(renderer,
                            reference_data=None,
                            axis_length=None,
                            marker_radius=None):
    """Add a world-space origin marker and positive X/Y/Z direction arrows."""
    if axis_length is None or marker_radius is None:
        if reference_data is not None:
            bounds = reference_data.GetBounds()
            extents = np.asarray([
                bounds[1] - bounds[0],
                bounds[3] - bounds[2],
                bounds[5] - bounds[4],
            ])
            scale = np.linalg.norm(extents)
        else:
            scale = 100.0

        if axis_length is None:
            axis_length = 0.12 * scale
        if marker_radius is None:
            marker_radius = 0.012 * scale

    axes_actor = vtk.vtkAxesActor()
    axes_actor.SetObjectName("WorldAxes")
    axes_actor.SetPosition(0.0, 0.0, 0.0)
    axes_actor.SetTotalLength(axis_length, axis_length, axis_length)
    axes_actor.SetShaftTypeToCylinder()
    axes_actor.SetTipTypeToCone()
    axes_actor.SetCylinderRadius(0.025)
    axes_actor.SetConeRadius(0.10)
    axes_actor.SetCylinderResolution(24)
    axes_actor.SetConeResolution(24)
    axes_actor.SetXAxisLabelText("+X")
    axes_actor.SetYAxisLabelText("+Y")
    axes_actor.SetZAxisLabelText("+Z")
    axes_actor.SetPickable(False)

    origin_source = vtk.vtkSphereSource()
    origin_source.SetCenter(0.0, 0.0, 0.0)
    origin_source.SetRadius(marker_radius)
    origin_source.SetThetaResolution(32)
    origin_source.SetPhiResolution(24)

    origin_mapper = vtk.vtkPolyDataMapper()
    origin_mapper.SetInputConnection(origin_source.GetOutputPort())
    origin_actor = vtk.vtkActor()
    origin_actor.SetObjectName("WorldOrigin")
    origin_actor.SetMapper(origin_mapper)
    origin_actor.GetProperty().SetColor(1.0, 1.0, 1.0)
    origin_actor.GetProperty().LightingOff()
    origin_actor.SetPickable(False)

    renderer.AddActor(axes_actor)
    renderer.AddActor(origin_actor)
    return axes_actor, origin_actor


def create_vtk_renderer():
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.2, 0.4)
    renderer.SetUseDepthPeeling(1)
    renderer.SetOcclusionRatio(0.1)

    return renderer

def write_to_obj(render_window, output_file):
    writer = vtk.vtkOBJExporter()
    writer.SetInput(render_window)
    writer.SetFilePrefix(output_file)
    writer.Write()


def _actor_polydata_in_world_coordinates(actor):
    """Return a triangulated copy of an actor's surface in world coordinates."""
    actor.GetMapper().Update()

    transform = vtk.vtkTransform()
    transform.SetMatrix(actor.GetMatrix())

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(actor.GetMapper().GetInput())
    transform_filter.SetTransform(transform)

    triangulate = vtk.vtkTriangleFilter()
    triangulate.SetInputConnection(transform_filter.GetOutputPort())
    triangulate.PassLinesOff()
    triangulate.PassVertsOff()

    clean = vtk.vtkCleanPolyData()
    clean.SetInputConnection(triangulate.GetOutputPort())
    clean.Update()

    output = vtk.vtkPolyData()
    output.DeepCopy(clean.GetOutput())
    return output


def _indent_xml(element, level=0):
    """Indent an ElementTree in Python versions that predate ET.indent."""
    indentation = "\n" + level * "  "
    child_indentation = "\n" + (level + 1) * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = child_indentation
        for child in element:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indentation
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = indentation


def write_polydata_to_gdml(polydata, filename, length_unit="mm",
                           surface_name="Surface"):
    """Write triangular vtkPolyData as a standalone GDML tessellated solid."""
    if polydata.GetNumberOfPoints() == 0 or polydata.GetNumberOfPolys() == 0:
        raise ValueError("Cannot export an empty surface to GDML")

    root = ET.Element("gdml")
    define = ET.SubElement(root, "define")

    points = numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())
    for point_id, point in enumerate(points):
        ET.SubElement(define, "position", {
            "name": f"surface_v_{point_id}",
            "unit": length_unit,
            "x": f"{float(point[0]):.12g}",
            "y": f"{float(point[1]):.12g}",
            "z": f"{float(point[2]):.12g}",
        })

    materials = ET.SubElement(root, "materials")
    dummy_element = ET.SubElement(materials, "element", {
        "name": "GeometryElement",
        "formula": "H",
        "Z": "1",
    })
    ET.SubElement(dummy_element, "atom", {"value": "1.00794"})

    world_material = ET.SubElement(materials, "material", {
        "name": "WorldVacuum",
        "state": "gas",
    })
    ET.SubElement(world_material, "D", {
        "value": "1e-25",
        "unit": "g/cm3",
    })
    ET.SubElement(world_material, "fraction", {
        "n": "1.0",
        "ref": "GeometryElement",
    })

    surface_material = ET.SubElement(materials, "material", {
        "name": "TomographyMaterial",
        "state": "solid",
    })
    ET.SubElement(surface_material, "D", {
        "value": "1.0",
        "unit": "g/cm3",
    })
    ET.SubElement(surface_material, "fraction", {
        "n": "1.0",
        "ref": "GeometryElement",
    })

    solid_name = surface_name + "Solid"
    volume_name = surface_name + "Volume"
    position_name = surface_name + "Position"

    solids = ET.SubElement(root, "solids")
    tessellated = ET.SubElement(solids, "tessellated", {
        "name": solid_name,
    })

    cell_ids = vtk.vtkIdList()
    polygons = polydata.GetPolys()
    polygons.InitTraversal()
    triangle_count = 0
    while polygons.GetNextCell(cell_ids):
        if cell_ids.GetNumberOfIds() != 3:
            raise ValueError("GDML tessellated export requires triangular faces")
        ET.SubElement(tessellated, "triangular", {
            "vertex1": f"surface_v_{cell_ids.GetId(0)}",
            "vertex2": f"surface_v_{cell_ids.GetId(1)}",
            "vertex3": f"surface_v_{cell_ids.GetId(2)}",
            "type": "ABSOLUTE",
        })
        triangle_count += 1

    bounds = polydata.GetBounds()
    span = max(bounds[1] - bounds[0],
               bounds[3] - bounds[2],
               bounds[5] - bounds[4])
    margin = max(1.0, 0.1 * span)
    world_size = [
        2.0 * (max(abs(bounds[2 * axis]), abs(bounds[2 * axis + 1])) + margin)
        for axis in range(3)
    ]
    ET.SubElement(solids, "box", {
        "name": "WorldBox",
        "x": f"{world_size[0]:.12g}",
        "y": f"{world_size[1]:.12g}",
        "z": f"{world_size[2]:.12g}",
        "lunit": length_unit,
    })

    structure = ET.SubElement(root, "structure")
    surface_volume = ET.SubElement(structure, "volume", {
        "name": volume_name,
    })
    ET.SubElement(surface_volume, "materialref", {"ref": "TomographyMaterial"})
    ET.SubElement(surface_volume, "solidref", {"ref": solid_name})

    world_volume = ET.SubElement(structure, "volume", {"name": "WorldVolume"})
    ET.SubElement(world_volume, "materialref", {"ref": "WorldVacuum"})
    ET.SubElement(world_volume, "solidref", {"ref": "WorldBox"})
    physical_volume = ET.SubElement(world_volume, "physvol")
    ET.SubElement(physical_volume, "volumeref", {"ref": volume_name})
    ET.SubElement(physical_volume, "position", {
        "name": position_name,
        "unit": length_unit,
        "x": "0",
        "y": "0",
        "z": "0",
    })

    setup = ET.SubElement(root, "setup", {
        "name": "Default",
        "version": "1.0",
    })
    ET.SubElement(setup, "world", {"ref": "WorldVolume"})

    _indent_xml(root)
    ET.ElementTree(root).write(filename, encoding="utf-8", xml_declaration=True)
    return triangle_count


def export_surface(actor, output_prefix, length_unit="mm",
                   surface_name="Surface"):
    """Export one actor to matching OBJ and GDML surface files."""
    polydata = _actor_polydata_in_world_coordinates(actor)
    obj_filename = output_prefix + ".obj"
    gdml_filename = output_prefix + ".gdml"

    obj_writer = vtk.vtkOBJWriter()
    obj_writer.SetFileName(obj_filename)
    obj_writer.SetInputData(polydata)
    if obj_writer.Write() != 1:
        raise RuntimeError(f"Failed to write {obj_filename}")

    triangle_count = write_polydata_to_gdml(
        polydata,
        gdml_filename,
        length_unit=length_unit,
        surface_name=surface_name,
    )
    print(
        f"Exported {polydata.GetNumberOfPoints()} vertices and "
        f"{triangle_count} triangles to {obj_filename} and {gdml_filename}"
    )
    return obj_filename, gdml_filename


def add_surface_export_keypress(interactor, renderer,
                                output_base="B003",
                                key="g",
                                length_unit="mm"):
    """Bind a key to export the reduced surface, or the full one if unreduced."""
    export_key = key.lower()

    def on_key_press(obj, event):
        if obj.GetKeySym().lower() != export_key:
            return

        reduced_actor = None
        full_actor = None
        actors = renderer.GetActors()
        for index in range(actors.GetNumberOfItems()):
            actor = actors.GetItemAsObject(index)
            if actor.GetObjectName() == "SimplifiedContour":
                reduced_actor = actor
            elif actor.GetObjectName() == "LargestContour":
                full_actor = actor

        if reduced_actor is not None:
            export_actor = reduced_actor
            surface_kind = "reduced"
        elif full_actor is not None:
            export_actor = full_actor
            surface_kind = "full"
        else:
            print("No contour surface is available to export.")
            return

        try:
            export_surface(
                export_actor,
                f"{output_base}_{surface_kind}",
                length_unit=length_unit,
                surface_name=surface_kind.capitalize() + "Surface",
            )
        except Exception as error:
            print(f"Surface export failed: {error}")

    observer_id = interactor.AddObserver("KeyPressEvent", on_key_press)
    print(
        f"Press {key.upper()} to export {output_base}_reduced.* when simplified, "
        f"or {output_base}_full.* at full detail"
    )
    return observer_id


def extract_largest_contour(contour_actor):
    """Create an actor that tracks the largest connected contour region.

    Keeping the connectivity filter connected to the contour filter is important:
    when the slider changes the iso-value, the same pipeline and actor update in
    place.  A mapper fed with ``SetInputData`` would instead hold a snapshot of
    the polydata produced at the time this function was called.
    """
    contour_mapper = contour_actor.GetMapper()
    contour_mapper.Update()

    connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
    connectivity_filter.SetInputConnection(contour_mapper.GetInputConnection(0, 0))
    connectivity_filter.SetExtractionModeToLargestRegion()
    connectivity_filter.ColorRegionsOff()
    connectivity_filter.Update()

    # vtkPolyDataConnectivityFilter can retain points that are no longer used
    # by any output cell. Cleaning removes those points, which also makes the
    # actor bounds/center describe the selected region rather than all regions.
    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputConnection(connectivity_filter.GetOutputPort())

    largest_contour_mapper = vtk.vtkPolyDataMapper()
    largest_contour_mapper.SetInputConnection(clean_filter.GetOutputPort())
    largest_contour_mapper.SetScalarVisibility(contour_mapper.GetScalarVisibility())
    largest_contour_mapper.SetScalarRange(contour_mapper.GetScalarRange())
    largest_contour_mapper.SetLookupTable(contour_mapper.GetLookupTable())

    largest_contour_actor = vtk.vtkActor()
    largest_contour_actor.SetMapper(largest_contour_mapper)
    largest_contour_actor.GetProperty().SetColor(contour_actor.GetProperty().GetColor())
    largest_contour_actor.GetProperty().SetOpacity(contour_actor.GetProperty().GetOpacity())
    largest_contour_actor.SetObjectName("LargestContour")
    largest_contour_actor.GetProperty().SetInterpolationToFlat()
    largest_contour_actor.GetProperty().SetEdgeVisibility(1)

    return largest_contour_actor


def slider_callback(value, renderer):
    print("Slider value changed to:", value)


    actors = renderer.GetActors()
    contour_actor = None
    largest_contour = None
    decimated_contour = None
    for i in range(actors.GetNumberOfItems()):
        actor = actors.GetItemAsObject(i)
        if actor.GetObjectName() == "Contour":
            contour_actor = actor
        elif actor.GetObjectName() == "LargestContour":
            largest_contour = actor
        elif actor.GetObjectName() == "SimplifiedContour":
            decimated_contour = actor

    contour_filter = contour_actor.GetMapper().GetInputAlgorithm()
    contour_filter.SetValue(0, value)
    contour_filter.Modified()

    # The largest-contour actor has a live connection to contour_filter, so
    # updating its mapper reruns both the contour and connectivity filters.
    if largest_contour is not None:
        largest_contour.GetMapper().Update()
    else:
        contour_actor.GetMapper().Update()

    decimation_widget = renderer.widgets.get("Decimation Factor")
    current_decimation_factor = (
        decimation_widget.GetRepresentation().GetValue()
        if decimation_widget is not None else 1.0
    )

    simplification_source = (
        largest_contour if largest_contour is not None else contour_actor
    )
    decimated_actor = decimate_mesh(
        simplification_source,
        reduction_factor=current_decimation_factor,
    )

    if decimated_actor is not None:
        if decimated_contour is not None:
            renderer.RemoveActor(decimated_contour)
        renderer.AddActor(decimated_actor)
        if largest_contour is not None:
            largest_contour.SetVisibility(False)
        displayed_actor = decimated_actor
    else:
        if decimated_contour is not None:
            renderer.RemoveActor(decimated_contour)
        if largest_contour is not None:
            largest_contour.SetVisibility(True)
        elif contour_actor is not None:
            contour_actor.SetVisibility(True)
        displayed_actor = simplification_source

    displayed_actor.GetMapper().Update()
    displayed_vertices = displayed_actor.GetMapper().GetInput().GetNumberOfPoints()
    print(f"Displayed vertices after contour update: {displayed_vertices}")

    renderer.GetRenderWindow().Render()


def add_slider(renderer, min_value, max_value, initial_value, title, callback_function, position=[[0.1, 0.1], [0.9, 0.1]]):
    slider_rep = vtk.vtkSliderRepresentation2D()
    slider_rep.SetMinimumValue(min_value)
    slider_rep.SetMaximumValue(max_value)
    slider_rep.SetValue(initial_value)
    slider_rep.SetTitleText(title)
    slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider_rep.GetPoint1Coordinate().SetValue(position[0][0], position[0][1])
    slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider_rep.GetPoint2Coordinate().SetValue(position[1][0], position[1][1])

    slider_widget = vtk.vtkSliderWidget()
    slider_widget.SetInteractor(renderer.GetRenderWindow().GetInteractor())
    slider_widget.SetRepresentation(slider_rep)
    slider_widget.SetAnimationModeToAnimate()
    slider_widget.EnabledOn()

    slider_widget.SetObjectName(title)

    def on_slider_change(obj, event):
        value = obj.GetRepresentation().GetValue()
        callback_function(value, renderer)

    slider_widget.AddObserver("InteractionEvent", on_slider_change)

    if not hasattr(renderer, "widgets"):
        renderer.widgets = {}

    renderer.widgets[title] = slider_widget

    return slider_widget



def decimate_mesh(input_actor, reduction_factor=0.5):
    """Simplify a surface using a volume-preserving quadric error metric.

    Args:
        input_actor (vtkActor): The input actor whose mesh will be decimated.
        reduction_factor (float): Approximate fraction of faces to retain. A
            value of 1.0 returns ``None`` so the original actor can be shown.

    Returns:
        vtkActor or None: A new simplified actor, or ``None`` at full detail.
    """
    if input_actor is None:
        return None

    retained_fraction = float(np.clip(reduction_factor, 0.01, 1.0))
    if retained_fraction >= 0.999:
        print("Skipping reduction")
        return None

    input_mapper = input_actor.GetMapper()
    input_mapper.Update()
    polydata = input_mapper.GetInput()
    if polydata is None or polydata.GetNumberOfCells() == 0:
        print("Skipping reduction: the input mesh is empty")
        return None

    print(
        "Original mesh: "
        f"{polydata.GetNumberOfPoints()} points, "
        f"{polydata.GetNumberOfPolys()} faces"
    )

    # Remove unused/duplicate points and guarantee triangular input before
    # applying the same family of quadric error metric used by Blender's
    # collapse decimator.
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(polydata)

    triangulate = vtk.vtkTriangleFilter()
    triangulate.SetInputConnection(clean.GetOutputPort())
    triangulate.PassLinesOff()
    triangulate.PassVertsOff()

    decimate = vtk.vtkQuadricDecimation()
    decimate.SetInputConnection(triangulate.GetOutputPort())
    decimate.SetTargetReduction(1.0 - retained_fraction)
    decimate.VolumePreservationOn()
    decimate.WeighBoundaryConstraintsByLengthOn()
    decimate.SetBoundaryWeightFactor(10.0)
    decimate.AttributeErrorMetricOff()

    # Recompute coherent normals after the topology changes. Splitting is
    # disabled to avoid duplicating points along artificial feature edges.
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(decimate.GetOutputPort())
    normals.ComputePointNormalsOn()
    normals.ComputeCellNormalsOff()
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.SplittingOff()
    normals.Update()

    decimated_mapper = vtk.vtkPolyDataMapper()
    decimated_mapper.SetInputConnection(normals.GetOutputPort())
    decimated_mapper.SetScalarVisibility(input_mapper.GetScalarVisibility())
    decimated_mapper.SetScalarRange(input_mapper.GetScalarRange())
    decimated_mapper.SetLookupTable(input_mapper.GetLookupTable())

    decimated_actor = vtk.vtkActor()
    decimated_actor.SetMapper(decimated_mapper)
    decimated_actor.GetProperty().SetColor(input_actor.GetProperty().GetColor())
    decimated_actor.GetProperty().SetOpacity(input_actor.GetProperty().GetOpacity())
    decimated_actor.GetProperty().SetInterpolationToFlat()
    decimated_actor.GetProperty().EdgeVisibilityOff()
    decimated_actor.SetObjectName("SimplifiedContour")

    simplified = normals.GetOutput()
    print(
        "Simplified mesh: "
        f"{simplified.GetNumberOfPoints()} points, "
        f"{simplified.GetNumberOfPolys()} faces "
        f"({retained_fraction:.1%} requested)"
    )

    return decimated_actor


def decimation_callback(value, renderer):
    print("Decimation slider value changed to:", value)

    actors = renderer.GetActors()
    contour_actor = None
    largest_contour = None
    decimated_contour = None
    for i in range(actors.GetNumberOfItems()):
        actor = actors.GetItemAsObject(i)
        if actor.GetObjectName() == "Contour":
            contour_actor = actor
        elif actor.GetObjectName() == "LargestContour":
            largest_contour = actor
        elif actor.GetObjectName() == "SimplifiedContour":
            decimated_contour = actor

    # determine which actors are currently visible
    if contour_actor is not None and contour_actor.GetVisibility():
        print("Contour actor is visible")
    if largest_contour is not None and largest_contour.GetVisibility():
        print("Largest contour actor is visible")
    if decimated_contour is not None and decimated_contour.GetVisibility():
        print("Decimated contour actor is visible")

    simplification_source = (
        largest_contour if largest_contour is not None else contour_actor
    )
    decimated_actor = decimate_mesh(
        simplification_source,
        reduction_factor=value,
    )

    if decimated_actor is not None:
        if decimated_contour is not None:
            renderer.RemoveActor(decimated_contour)
        renderer.AddActor(decimated_actor)
        if largest_contour is not None:
            largest_contour.SetVisibility(False)
        if contour_actor is not None:
            contour_actor.SetVisibility(False)
        displayed_actor = decimated_actor
        print("Decimation applied, showing decimated contour")

    else:
        print("No decimation applied")

        if decimated_contour is not None:
            renderer.RemoveActor(decimated_contour)
        if largest_contour is not None:
            largest_contour.SetVisibility(True)
        else:
            contour_actor.SetVisibility(True)
        displayed_actor = simplification_source

    displayed_actor.GetMapper().Update()
    displayed_vertices = displayed_actor.GetMapper().GetInput().GetNumberOfPoints()
    print(f"Displayed vertices after decimation update: {displayed_vertices}")



    renderer.GetRenderWindow().Render()


if __name__ == "__main__":
    # tomography_matrix = convert_tomography("tomographie.root", "/home/grtdaq/Documents/PROJECTS/TOMOGRAPHY")

    tomography_matrix = convert_tomography("B003_tomography.root", "/home/grtdaq/Documents/PROJECTS/TOMOGRAPHY")




    print(tomography_matrix.shape, np.min(tomography_matrix), np.max(tomography_matrix))

    tomography_matrix = tomography_matrix - np.min(tomography_matrix)
    tomography_matrix = tomography_matrix / np.max(tomography_matrix)

    print(tomography_matrix.shape, np.min(tomography_matrix), np.max(tomography_matrix))

    volume_spacing = (1, 1, 1)
    detector_front_world = (0, 0, 0)
    volume_origin = volume_origin_from_front_center(
        tomography_matrix.shape,
        spacing=volume_spacing,
        front_center=detector_front_world,
    )

    renderer = create_vtk_renderer()
    # volume = add_volume(tomography_matrix, spacing=volume_spacing,
    #                     origin=volume_origin)
    # renderer.AddVolume(volume)

    contour_value = 0.45

    contour = add_contours(
        tomography_matrix,
        c_number=1,
        c_range=[contour_value, contour_value],
        shade=True,
        spacing=volume_spacing,
        origin=volume_origin,
    )
    decimated_contour = None

    largest_contour = extract_largest_contour(contour)

    renderer.AddActor(contour)
    renderer.AddActor(largest_contour)
    # Keep the source actor in the renderer so the callback can find its
    # contour filter, but render only the extracted largest region.
    contour.SetVisibility(False)

    # Sample the original normalized image (the contour filter's input), using
    # the extracted crystal center as the common point for all profile lines.
    largest_contour.GetMapper().Update()
    image_data = contour.GetMapper().GetInputAlgorithm().GetInput()
    print("Aligned volume bounds:", image_data.GetBounds())
    world_axes, world_origin = add_world_origin_marker(
        renderer,
        reference_data=image_data,
    )
    profiles, profile_line_actors = add_volume_profile_lines(
        image_data,
        renderer=renderer,
        center=largest_contour.GetCenter(),
        number_of_samples=500,
    )
    # profile_figure, profile_axes = plot_volume_profiles(
    #     profiles,
    #     threshold=contour_value,
    #     output_file="B003_profiles.png",
    # )

    print(contour.GetBounds())

    renderer_window = vtk.vtkRenderWindow()
    renderer_window.AddRenderer(renderer)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renderer_window)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())


    contour_slider = add_slider(renderer, min_value=0.1, max_value=0.9, initial_value=contour_value, title="Contour Value", callback_function=slider_callback, position=[[0.1, 0.2], [0.9, 0.2]])
    decimation_slider = add_slider(renderer, min_value=0.0, max_value=1.0, initial_value=1.0, title="Decimation Factor", callback_function=decimation_callback, position=[[0.1, 0.1], [0.9, 0.1]])
    export_observer = add_surface_export_keypress(
        iren,
        renderer,
        output_base="B003",
        key="g",
        length_unit="mm",
    )

    renderer.ResetCamera()

    renderer_window.Render()


    write_to_obj(renderer_window, "B003")

    iren.Start()
