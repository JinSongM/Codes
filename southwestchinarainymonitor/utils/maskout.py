import shapefile
import cartopy.crs as ccrs
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def shp2clip(originfig, ax, shpfile, region, proj=None):
    sf = shapefile.Reader(shpfile)
    vertices = []
    codes = []
    for shape_rec in sf.shapeRecords():

        if shape_rec.record[3] == region:

            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    if proj:
                        vertices.append(proj.transform_point(pts[j][0], pts[j][1], ccrs.Geodetic()))
                    else:
                        vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            clip = Path(vertices, codes)
            clip = PathPatch(clip, transform=ax.transData)

    for contour in originfig.collections:
        contour.set_clip_path(clip)
    return clip

