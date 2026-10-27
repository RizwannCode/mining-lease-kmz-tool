import simplekml

def validate_and_export_kmz(transformed_points, filename="mining_lease.kmz"):
    """
    Generates a KMZ file ensuring all vertices (A, B, C, D, etc.) are explicitly shown.
    """
    kml = simplekml.Kml()
    
    poly_coords = []
    for pt_id, lon, lat in transformed_points:
        poly_coords.append((lon, lat, 0))
        
    # Close polygon loop for boundary rendering
    if poly_coords and poly_coords[0] != poly_coords[-1]:
        poly_coords.append(poly_coords[0])
        
    # Add polygon boundary and styling
    pol = kml.newpolygon(name="Mining Lease Boundary", outerboundaryis=poly_coords)
    pol.style.linestyle.color = simplekml.Color.red
    pol.style.linestyle.width = 3
    pol.style.polystyle.color = "6400ff00"
    
    # Add ALL individual point markers for every vertex without missing any
    for pt_id, lon, lat in transformed_points:
        pnt = kml.newpoint(name=f"Point {pt_id}", coords=[(lon, lat, 0)])
        pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
        
    kml.save(filename)
    return filename
