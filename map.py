
import os
import html
from pathlib import Path

import requests
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from shapely.ops import polylabel
from shapely.geometry import MultiPolygon


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data/input/neighbourhoods.geojson"
OUTPUT_FILE = BASE_DIR / "regions_map.html"

# Load API key from .env
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "Google Maps API key not found. Check your .env file."
    )

# Your GeoJSON neighbourhood column
NAME_COLUMN = "neighbourhood"

# Polygon settings
FILL_OPACITY = 0.48
BORDER_COLOR = "white"
BORDER_WEIGHT = 1.5

# Label settings
LABEL_FONT_SIZE = 12


# ==========================================
# 2. LOAD GEOJSON
# ==========================================

gdf = gpd.read_file(INPUT_FILE)

print("Available columns:", gdf.columns.tolist())
print("Total regions:", len(gdf))

if gdf.empty:
    raise ValueError("GeoJSON contains no regions.")

if NAME_COLUMN not in gdf.columns:
    raise ValueError(
        f"Missing column '{NAME_COLUMN}'. "
        f"Available columns: {gdf.columns.tolist()}"
    )

# Ensure WGS84 coordinates
if gdf.crs is None:
    gdf = gdf.set_crs("EPSG:4326")

gdf = gdf.to_crs("EPSG:4326")

print("Neighbourhood name column:", NAME_COLUMN)


# ==========================================
# 3. GENERATE REGION COLOURS
# ==========================================

num_regions = len(gdf)

cmap = plt.get_cmap("gist_ncar", num_regions)

colors = [
    "#%02x%02x%02x" % tuple(
        int(v * 255) for v in cmap(i)[:3]
    )
    for i in range(num_regions)
]


# ==========================================
# 4. CREATE GOOGLE SATELLITE SESSION
# ==========================================

print("\nConnecting to Google Maps...")

try:
    response = requests.post(
        "https://tile.googleapis.com/v1/createSession",
        params={
            "key": GOOGLE_API_KEY
        },
        json={
            "mapType": "satellite",
            "language": "en-US",
            "region": "CA"
        },
        timeout=30
    )

except requests.exceptions.RequestException as e:
    print("\nNetwork error connecting to Google Maps.")
    print("Error type:", type(e).__name__)
    raise SystemExit(1)


# ==========================================
# 5. HANDLE GOOGLE API ERRORS
# ==========================================

if not response.ok:

    print("\n====================================")
    print("GOOGLE MAPS API ERROR")
    print("====================================")

    print("HTTP Status:", response.status_code)

    try:
        error_data = response.json()
        error = error_data.get("error", {})

        print("Status:", error.get("status", "Unknown"))
        print("Message:", error.get("message", "Unknown"))

    except ValueError:
        print("Google returned a non-JSON error response.")

    print("\nPossible causes:")
    print("1. Map Tiles API is not enabled.")
    print("2. Billing is not enabled.")
    print("3. API key restrictions prevent access.")
    print("4. API key is invalid or revoked.")

    print("====================================")

    raise SystemExit(1)


session_data = response.json()
session_token = session_data["session"]

print("Google satellite session created successfully!")


# ==========================================
# 6. INITIALIZE FOLIUM MAP
# ==========================================

m = folium.Map(
    location=[49.25, -123.12],
    zoom_start=12,
    tiles=None,
    control_scale=True,
    zoom_control=True
)


# ==========================================
# 7. ADD GOOGLE SATELLITE IMAGERY
# ==========================================

google_tiles = (
    "https://tile.googleapis.com/v1/2dtiles/"
    "{z}/{x}/{y}"
    f"?session={session_token}&key={GOOGLE_API_KEY}"
)

folium.TileLayer(
    tiles=google_tiles,
    attr="Google Maps",
    name="Google Satellite",
    overlay=False,
    control=True,
    max_zoom=20
).add_to(m)


# ==========================================
# 8. CREATE MAP LAYERS
# ==========================================

regions_layer = folium.FeatureGroup(
    name="Neighbourhood Regions",
    show=True
)

labels_layer = folium.FeatureGroup(
    name="Neighbourhood Names",
    show=True
)


# ==========================================
# 9. DRAW ALL NEIGHBOURHOODS
# ==========================================

for i, (_, row) in enumerate(gdf.iterrows()):

    geometry = row.geometry

    if geometry is None or geometry.is_empty:
        continue

    color = colors[i]

    name = str(row[NAME_COLUMN])

    print(f"Adding region {i + 1}: {name}")

    # --------------------------------------
    # Draw coloured polygon
    # --------------------------------------

    folium.GeoJson(
        geometry.__geo_interface__,

        style_function=lambda feature, c=color: {
            "fillColor": c,
            "fillOpacity": FILL_OPACITY,
            "color": BORDER_COLOR,
            "weight": BORDER_WEIGHT,
            "opacity": 0.9
        },

        highlight_function=lambda feature, c=color: {
            "fillColor": c,
            "fillOpacity": 0.7,
            "color": "yellow",
            "weight": 2.5
        },

        tooltip=folium.Tooltip(
            html.escape(name),
            sticky=True
        )

    ).add_to(regions_layer)

    # --------------------------------------
    # Calculate label position
    # --------------------------------------

    # Choose the largest polygon for MultiPolygon regions
    if isinstance(geometry, MultiPolygon):
        label_polygon = max(
            geometry.geoms,
            key=lambda polygon: polygon.area
        )
    else:
        label_polygon = geometry

    # Project to a local metric CRS for label placement
    label_series = gpd.GeoSeries(
        [label_polygon],
        crs="EPSG:4326"
    ).to_crs("EPSG:26910")

    # Find the most interior point
    center_projected = polylabel(
        label_series.iloc[0],
        tolerance=10
    )

    # Convert back to latitude/longitude
    center = gpd.GeoSeries(
        [center_projected],
        crs="EPSG:26910"
    ).to_crs("EPSG:4326").iloc[0]

    latitude = center.y
    longitude = center.x

    # --------------------------------------
    # Add neighbourhood name
    # --------------------------------------
    
    label_html = f"""
    <div style="
        transform: translate(-50%, -50%);
        font-family: Arial, sans-serif;
        font-size: {LABEL_FONT_SIZE}px;
        font-weight: bold;
        color: white;
        text-align: center;
        white-space: normal;
        width: 100px;
        line-height: 1.2;
        pointer-events: none;
        text-shadow:
            -1px -1px 2px black,
            1px -1px 2px black,
            -1px  1px 2px black,
            1px  1px 2px black;
    ">
        {html.escape(name)}
    </div>
    """

    folium.Marker(
        location=[latitude, longitude],
        icon=folium.DivIcon(
            icon_size=(0, 0),
            icon_anchor=(0, 0),
            html=label_html
        )
    ).add_to(labels_layer)


# ==========================================
# 10. ADD LAYERS TO MAP
# ==========================================

regions_layer.add_to(m)
labels_layer.add_to(m)


# ==========================================
# 11. FIT MAP TO ALL NEIGHBOURHOODS
# ==========================================

minx, miny, maxx, maxy = gdf.total_bounds

m.fit_bounds([
    [miny, minx],
    [maxy, maxx]
])


# ==========================================
# 12. ADD LAYER CONTROL
# ==========================================

folium.LayerControl(
    collapsed=False
).add_to(m)


# ==========================================
# 13. SAVE HTML MAP
# ==========================================

m.save(str(OUTPUT_FILE))

print()
print("====================================")
print("MAP GENERATED SUCCESSFULLY")
print("====================================")
print(f"Total regions: {num_regions}")
print(f"Output: {OUTPUT_FILE}")
print("====================================")
