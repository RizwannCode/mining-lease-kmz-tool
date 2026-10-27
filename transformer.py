from pyproj import Transformer

def transform_coordinates(points_list):
    """
    Transforms coordinates from Indian Zone II-a (Everest 1830)
    to WGS 84 (Latitude, Longitude).
    Input points_list: List of tuples (point_id, northing, easting in yards)
    """
    # Modernized Proj definition converting Indian yards to meters internally 
    # (1 Indian yard = 0.9143953 meters roughly, or using standard scaling)
    src_crs = "+proj=tmerc +lat_0=24 +lon_0=80.15 +k=0.9999 +x_0=274318.59 +y_0=0 +ellps=evrst30 +units=m +no_defs"
    dst_crs = "EPSG:4326"
    
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    
    transformed_points = []
    for pt_id, northing, easting in points_list:
        # Convert yards to meters for pyproj compatibility (1 yard = 0.9143953 m)
        easting_m = float(easting) * 0.9143953
        northing_m = float(northing) * 0.9143953
        
        lon, lat = transformer.transform(easting_m, northing_m)
        transformed_points.append((pt_id, lon, lat))
        
    return transformed_points
