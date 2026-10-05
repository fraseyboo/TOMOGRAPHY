import numpy as np
import uproot
import os
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



def add_contours(input_data,
                 renderer=None,
                 c_number=10,
                 c_range=None,
                 spacing=(1, 1, 1),
                 opacity=1.0,
                 origin=None,
                 colormap='viridis',
                 name='contour',
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

    volActor.SetPickable(pickable)

    volActor.SetObjectName(name)

    if not shade:
        volActor.GetProperty().LightingOff()
    if renderer is None:
        return volActor
    else:
        renderer.AddActor(volActor)
        print('Contours added')



    # print(data.shape)



    # print(dir(data))

    # Save the data
    # np.save(output_file, data)
    # print(data)

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


if __name__ == "__main__":
    tomography_matrix = convert_tomography("tomographie.root", "/home/grtdaq/Documents/PROJECTS/TOMOGRAPHY")

    renderer = create_vtk_renderer()
    # volume = add_volume(tomography_matrix)
    # renderer.AddVolume(volume)
    contour = add_contours(tomography_matrix, c_number=1, c_range=[100, 100], shade=True, spacing=(1, 1, 1))
    renderer.AddActor(contour)

    print(contour.GetBounds())

    renderer_window = vtk.vtkRenderWindow()
    renderer_window.AddRenderer(renderer)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renderer_window)



    renderer_window.Render()


    write_to_obj(renderer_window, "A005")

    iren.Start()
