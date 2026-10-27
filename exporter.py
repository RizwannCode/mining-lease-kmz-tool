import simplekml

def validate_and_export_kmz(transformed_points, filename="mining_lease.kmz"):
    """
    Generates a clean KMZ file from transformed WGS84 points (lon, lat) without warnings.
    """
    kml = simplekml.Kml()
    
    poly_coords = []
    for pt_id, lon, lat in transformed_points:
        poly_coords.append((lon, lat, 0))
        
    # Close polygon loop if not already closed
    if poly_coords and poly_coords[0] != poly_coords[-1]:
        poly_coords.append(poly_coords[0])
        
    # Add polygon boundary and styling
    pol = kml.newpolygon(name="Mining Lease Boundary", outerboundaryis=poly_coords)
    pol.style.linestyle.color = simplekml.Color.red
    pol.style.linestyle.width = 3
    pol.style.polystyle.color = "6400ff00"
    
    # Add point markers for vertices (using clean default styles)
    unique_points = transformed_points[:-1] if len(poly_coords) > 1 and poly_coords[0] == poly_coords[-1] else transformed_points
    for pt_id, lon, lat in unique_points:
        pnt = kml.newpoint(name=f"Point {pt_id}", coords=[(lon, lat, 0)])
        
    kml.save(filename)
    return filename
