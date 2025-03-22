'''
Script to compute a new ECEF given measured location and known location


'''

import click
import osgeo.osr
import pygeotools.lib.geolib

FT2M = 0.3048
MSL_OFFSET = 34.7842

epsg_2893 = osgeo.osr.SpatialReference()
epsg_2893.ImportFromEPSG(2983)

def md28932ll(x,y,z):
    # z is provided in ft MSL
    z = (z*FT2M) - MSL_OFFSET
    res = pygeotools.lib.geolib.cT_helper(x, y, z, epsg_2893, pygeotools.lib.geolib.wgs_srs)
    print(res)


def ll2md2893(longitude, latitude, msl_ft):
    x = longitude
    y = latitude
    z = (msl_ft*FT2M) - MSL_OFFSET
    res = pygeotools.lib.geolib.cT_helper(x, y, z, pygeotools.lib.geolib.wgs_srs, epsg_2893)
    return res


def delta2893(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    dz = p1[2] - p0[2]
    return (dx, dy, dz)

def deltaXYZ(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    dz = p1[2] - p0[2]
    return (dx**2 + dy**2 + dz**2)**0.5

@click.group()
def main():
    pass

@main.command()
@click.argument('data', nargs=-1)
def delta(data):
    assert len(data) == 6
    data = [float(v) for v in data]
    p0 = data[:3]
    p1 = data[3:]
    print(deltaXYZ(p0,p1))

if __name__ == "__main__":
    main()

