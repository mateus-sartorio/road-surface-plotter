import folium
import csv
import os
import sys

# Map center (used for initial view)
center = [-20.27684329445295, -40.3013367945867]
m = folium.Map(location=center, zoom_start=16)

csv_path = "data.csv"
points = []

def _to_float(v):
    try:
        return float(v)
    except Exception:
        return None

if os.path.exists(csv_path):
    try:
        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                # keep original strings so we can show the full (unrounded) values in the tooltip
                lat_str = row.get('location_latitude')
                lon_str = row.get('location_logitude')
                lat = _to_float(lat_str)
                lon = _to_float(lon_str)
                # prefer the explicit rating_value (if present and numeric), otherwise use predicted_probability
                rating_val_str = row.get('rating_value')
                # try to parse rating_value first
                rating = _to_float(rating_val_str) if rating_val_str is not None else None
                # fallback to predicted_rating_probability if rating_value missing or not numeric
                if rating is None:
                    rating = _to_float(row.get('predicted_rating_probability'))
                if lat is not None and lon is not None and rating is not None:
                    # store original strings alongside floats
                    points.append((lat, lon, rating, lat_str, lon_str))
    except Exception as e:
        print(f"Warning reading CSV: {e}", file=sys.stderr)

print(f"Using {len(points)} points")

for lat, lon, rating, lat_str, lon_str in points:
    # Color rules: <0.5 red, 0.5-0.7 grey, >0.7 green
    if rating < 0.5:
        color = "red"
    elif rating <= 0.7:
        color = "grey"
    else:
        color = "green"

    # tooltip shows full (unrounded) latitude and longitude strings from the CSV
    tooltip_html = f"<div>rating: {rating:.3f}<br>latitude: {lat_str}<br>longitude: {lon_str}</div>"
    popup_txt = f"rating: {rating:.3f}"
    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        tooltip=folium.Tooltip(tooltip_html),
        popup=folium.Popup(popup_txt, parse_html=True)
    ).add_to(m)

m.save("map.html")
print("Saved map.html")