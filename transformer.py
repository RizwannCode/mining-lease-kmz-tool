from pyproj import Transformer

def transform_coordinates(points_list):
    """
    Transforms coordinates from Indian Zone II-a (Everest 1830, Indian yards)
    to WGS 84 (Latitude, Longitude).
    Input points_list: List of tuples (point_id, northing, easting)
    """
    # Official Proj definition for India Zone II-a / Indian Everest 1830 in yards
    src_crs = "+proj=tmerc +lat_0=24 +lon_0=80.15 +k=0.9999 +x_0=300000 +y_0=0 +ellps=evrst30 +units=yard +no_defs"
    dst_crs = "EPSG:4326"
    
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    
    transformed_points = []
    for pt_id, northing, easting in points_list:
        # pyproj expects (easting, northing)
        lon, lat = transformer.transform(float(easting), float(northing))
        transformed_points.append((pt_id, lon, lat))
        
    return transformed_points
