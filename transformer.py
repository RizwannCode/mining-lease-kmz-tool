from pyproj import CRS, Transformer

def transform_coordinates(points):
    """
    Transforms Indian Zoned Grid Zone II-a coordinates to WGS 84 (EPSG:4326)
    using the official Proj4 definition provided in Appendix A of the OEL assignment.
    Points list format: [(point_id, northing_yds, easting_yds), ...]
    """
    # Official OEL Assignment Appendix A Proj4 string for India Zone II-a
    proj4_string = (
        "+proj=lcc +lat_1=26 +lat_0=26 +lon_0=74 +k_0=0.99878641 "
        "+x_0=2743195.592 +y_0=914398.531 "
        "+a=6377299.36559538 +b=6356098.35900516 "
        "+to_meter=0.9143985307 "
        "+towgs84=282,726,254,0,0,0,0 +no_defs"
    )
    
    source_crs = CRS.from_proj4(proj4_string)
    target_crs = CRS.from_epsg(4326)
    
    # always_xy=True ensures transformer expects (easting, northing)
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    
    transformed_results = []
    for pt_id, northing_yds, easting_yds in points:
        easting_val = float(easting_yds)
        northing_val = float(northing_yds)
        
        lon, lat = transformer.transform(easting_val, northing_val)
        transformed_results.append((pt_id, float(lon), float(lat)))
        
    return transformed_results