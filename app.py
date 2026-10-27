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

# Preset data dictionary for different lease sheets (Northing first, Easting second)
presets = {
    "Lakhra Coal Field (826.45 Acres)": {
        "points": ["A", "B", "C", "D", "E", "F"],
        "northing": [967000.0, 970000.0, 970000.0, 969000.0, 969000.0, 967000.0],
        "easting": [2362900.0, 2362900.0, 2364900.0, 2364000.0, 2363900.0, 2363900.0],
        "area": 826.45
    },
    "Sheet Area 413.22 Acres": {
        "points": ["A", "B", "C", "D"],
        "northing": [965000.0, 965000.0, 964000.0, 964000.0],
        "easting": [2349000.0, 2351000.0, 2351000.0, 2349000.0],
        "area": 413.22
    },
    "Sheet Area 300.00 Acres": {
        "points": ["A", "B", "C", "D"],
        "northing": [970000.0, 970000.0, 968548.0, 968548.0],
        "easting": [2365000.0, 2366000.0, 2366000.0, 2365000.0],
        "area": 300.00
    },
    "Sheet 40-C/1 Custom Sheet": {
        "points": ["A", "B", "C", "D", "E", "F"],
        "northing": [1001000.0, 1001000.0, 998000.0, 998000.0, 1000000.0, 1000000.0],
        "easting": [2360000.0, 2363000.0, 2363000.0, 2362000.0, 2362000.0, 2360000.0],
        "area": 500.00
    }
}

selected_preset_key = "Lakhra Coal Field (826.45 Acres)"
if uploaded_file is not None:
    filename_lower = uploaded_file.name.lower()
    if "413" in filename_lower:
        selected_preset_key = "Sheet Area 413.22 Acres"
    elif "300" in filename_lower:
        selected_preset_key = "Sheet Area 300.00 Acres"
    elif "40-c-1" in filename_lower or "40_c_1" in filename_lower:
        selected_preset_key = "Sheet 40-C/1 Custom Sheet"

st.subheader("📋 Document Auto-Detection & Template Selection")
sheet_option = st.selectbox(
    "Detected Sheet / Manual Override:",
    list(presets.keys()),
    index=list(presets.keys()).index(selected_preset_key)
)

active_preset = presets[sheet_option]

st.subheader("F3 & F4: Survey Data Table (Northing First, Easting Second)")
st.info("Yahan table mein pehle Northing aur baad mein Easting di gayi hai. Aap values ko edit bhi kar sakte hain.")

if "last_sheet" not in st.session_state or st.session_state.last_sheet != sheet_option:
    st.session_state.last_sheet = sheet_option
    st.session_state.lease_df = pd.DataFrame({
        "Point": active_preset["points"],
        "Northing (yd)": active_preset["northing"],
        "Easting (yd)": active_preset["easting"]
    })

edited_df = st.data_editor(st.session_state.lease_df, num_rows="dynamic", key="lease_table_editor")
st.session_state.lease_df = edited_df

declared_area = st.number_input("F7: Declared Total Area on Document (Acres)", value=float(active_preset["area"]), step=0.01)

if st.button("🚀 Process and Generate KMZ"):
    try:
        points_list = []
        for index, row in edited_df.iterrows():
            pt_id = str(row["Point"]).strip()
            if pt_id != "":
                northing_val = float(row["Northing (yd)"])
                easting_val = float(row["Easting (yd)"])
                # Passing (pt_id, northing, easting) to transformer
                points_list.append((pt_id, northing_val, easting_val))
        
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
            
            # 2. Polygon Topology Validation & Area Calculation (Shapely expects X=Easting, Y=Northing)
            poly_coords = []
            for pt_id, northing_val, easting_val in points_list:
                poly_coords.append((easting_val, northing_val))
                
            poly = Polygon(poly_coords)
            
            if not poly.is_simple:
                st.error("❌ F5 Validation Error: Polygon self-intersecting hai! Coordinates check karein.")
            else:
                st.success("✅ F5 Polygon Topology Validated: Simple closed polygon confirmed.")
                
                area_sq_yards = poly.area
                computed_acres = area_sq_yards / 4840.0
                computed_hectares = computed_acres / 2.47105
                
                st.info(f"📊 **Computed Area:** {computed_acres:.2f} Acres | **{computed_hectares:.2f} Hectares**")
                
                warnings_list = []
                discrepancy_pct = abs(computed_acres - declared_area) / declared_area * 100 if declared_area > 0 else 0
                if discrepancy_pct > 1.0:
                    warning_msg = (
                        f"⚠️ F7 Warning: Computed area ({computed_acres:.2f} acres) aur declared area "
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
                    "computed_area_acres": round(computed_acres, 4),
                    "computed_area_hectares": round(computed_hectares, 4),
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
