import os
import json
import streamlit as st
import pandas as pd
from shapely.geometry import Polygon
from transformer import transform_coordinates
from exporter import validate_and_export_kmz

st.set_page_config(page_title="Mining Lease to KMZ Converter", page_icon="🗺️", layout="wide")

st.title("🗺️ Automated Mining Lease Plan to KMZ Conversion Tool")
st.markdown("**Course CAMI-21MN** | Open-Ended Laboratory Assignment Pipeline")

uploaded_file = st.file_uploader("F1: Upload Scanned Lease Plan (JPEG, PNG, PDF)", type=["jpg", "png", "jpeg", "pdf"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Lease Document", use_container_width=True)
    
st.subheader("F3 & F4: Survey Data Table (Northing First, Easting Second)")
st.info("Yahan aap apne naye lease document ke mutabiq points add ya edit kar sakte hain.")

# Initialize session state for dataframe so edits are safely preserved across reruns
if "lease_df" not in st.session_state:
    st.session_state.lease_df = pd.DataFrame({
        "Point": ["A", "B", "C", "D"],
        "Northing (yd)": [0.0, 0.0, 0.0, 0.0],
        "Easting (yd)": [0.0, 0.0, 0.0, 0.0]
    })

# Use session state in data_editor and keep it updated
edited_df = st.data_editor(st.session_state.lease_df, num_rows="dynamic", key="lease_table_editor")
st.session_state.lease_df = edited_df

declared_area = st.number_input("F7: Declared Total Area on Document (Acres)", value=100.0, step=0.01)

if st.button("🚀 Process and Generate KMZ"):
    try:
        points_list = []
        for index, row in edited_df.iterrows():
            if str(row["Point"]).strip() != "":
                points_list.append((str(row["Point"]), float(row["Northing (yd)"]), float(row["Easting (yd)"])))
        
        if len(points_list) < 3:
            st.error("❌ Kam az kam 3 valid points enter karna lazmi hain polygon banane ke liye!")
        else:
            # 1. Coordinate Transformation
            transformed = transform_coordinates(points_list)
            
            st.subheader("🌐 Transformed WGS 84 Coordinates (Latitude & Longitude)")
            trans_df_data = []
            for pt_id, lon, lat in transformed:
                trans_df_data.append({
                    "Point": pt_id,
                    "Latitude (N)": round(lat, 6),
                    "Longitude (E)": round(lon, 6)
                })
            trans_df = pd.DataFrame(trans_df_data)
            st.dataframe(trans_df, use_container_width=True)
            
            # 2. Polygon Topology Validation & Area Calculation
            poly_coords = []
            for pt_id, northing_val, easting_val in points_list:
                poly_coords.append((float(easting_val), float(northing_val)))
                
            poly = Polygon(poly_coords)
            
            if not poly.is_simple:
                st.error("❌ F5 Validation Error: Polygon self-intersecting hai! Coordinates check karein.")
            else:
                st.success("✅ F5 Polygon Topology Validated: Simple closed polygon confirmed.")
                
                area_sq_yards = poly.area
                area_acres = area_sq_yards / 4840.0
                area_hectares = area_acres / 2.47105
                
                st.info(f"📊 **Computed Area:** {area_acres:.2f} Acres ({area_hectares:.2f} Hectares)")
                
                warnings_list = []
                discrepancy_pct = abs(area_acres - declared_area) / declared_area * 100 if declared_area > 0 else 0
                if discrepancy_pct > 1.0:
                    warning_msg = (
                        f"⚠️ F7 Warning: Computed area ({area_acres:.2f} acres) aur declared area "
                        f"({declared_area:.2f} acres) mein {discrepancy_pct:.1f}% ka fark hai."
                    )
                    st.warning(warning_msg)
                    warnings_list.append(warning_msg)
                else:
                    st.success("✅ F7 Area check passed within tolerance limits.")

                # 3. Export KMZ File
                kmz_file = validate_and_export_kmz(transformed)
                st.success("🎉 KMZ file successfully generate ho gayi hai!")
                
                # 4. Generate Machine-Readable JSON Summary (F9)
                summary_data = {
                    "extracted_grid_points": [{"point": p, "northing_yd": n, "easting_yd": e} for p, n, e in points_list],
                    "transformed_wgs84_points": [{"point": p, "latitude": lat, "longitude": lon} for p, lon, lat in transformed],
                    "computed_area_acres": round(area_acres, 4),
                    "computed_area_hectares": round(area_hectares, 4),
                    "declared_area_acres": declared_area,
                    "discrepancy_percentage": round(discrepancy_pct, 2),
                    "warnings": warnings_list
                }
                json_summary = json.dumps(summary_data, indent=4)

                col1, col2 = st.columns(2)
                with col1:
                    with open(kmz_file, "rb") as f:
                        st.download_button("📥 Download KMZ File (F8)", f, file_name="mining_lease.kmz")
                with col2:
                    st.download_button("📄 Download JSON Summary (F9)", json_summary, file_name="lease_summary.json", mime="application/json")
                
                st.markdown("---")
                st.markdown("### 🌍 Open in Google Earth")
                st.markdown(
                    "Click below to launch Google Earth Web, then go to **Projects > Import KML/KMZ file** and upload your KMZ file:",
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<a href="https://earth.google.com/web/" target="_blank"><button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">Launch Google Earth Web 🚀</button></a>',
                    unsafe_allow_html=True
                )
                
    except Exception as e:
        st.error(f"❌ Error during processing: {e}")
