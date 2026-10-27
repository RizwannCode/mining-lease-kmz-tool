import os
import simplekml

def validate_and_export_kmz(transformed_points):
    """
    Takes transformed WGS84 points: [(point_id, lon, lat), ...]
    Generates a KMZ file with a closed polygon and styled point markers.
    """
    kml = simplekml.Kml()
    
    # Extract longitude and latitude for boundary polygon
    polygon_coords = [(lon, lat) for pt_id, lon, lat in transformed_points]
    
    # Ensure polygon loop is closed
    if polygon_coords[0] != polygon_coords[-1]:
        polygon_coords.append(polygon_coords[0])
        
    # Create Polygon geometry
    pol = kml.newpolygon(name="Mining Lease Boundary")
    pol.outerboundaryis = polygon_coords
    pol.style.linestyle.color = simplekml.Color.red
    pol.style.linestyle.width = 3
    pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.green)
    
    # Add labeled vertices/points
    for pt_id, lon, lat in transformed_points:
        pnt = kml.newpoint(name=f"Point {pt_id}", coords=[(lon, lat)])
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
        
    # Export KMZ to output directory
    os.makedirs("output", exist_ok=True)
    kmz_path = "output/mining_lease.kmz"
    kml.savekmz(kmz_path)
    
    return kmz_path