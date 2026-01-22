"""
Author:"Ammar Yasser Abdalazim"
geonest - Core Map Module
A lightweight wrapper around ipyleaflet for GIS workflows.
"""

import ipyleaflet
import ipywidgets as widgets


class Map(ipyleaflet.Map):
    def __init__(self, center=(20, 0), zoom=2, height="600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    # ------------------------------------------------------------------
    # Basemaps
    # ------------------------------------------------------------------

    def add_basemap(self, basemap="OpenTopoMap"):
        """Add a basemap by name."""
        basemaps = ipyleaflet.basemaps
        if not hasattr(basemaps, basemap):
            raise ValueError(f"Basemap '{basemap}' not found in ipyleaflet.basemaps")

        provider = getattr(basemaps, basemap)
        layer = ipyleaflet.TileLayer(
            url=provider.build_url(),
            name=basemap,
        )
        self.add(layer)

    def add_basemap_gui(self, options=None, position="topright"):
        """Add a basemap selector GUI."""
        if options is None:
            options = [
                "OpenStreetMap.Mapnik",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "CartoDB.DarkMatter",
            ]

        toggle = widgets.ToggleButton(icon="map", layout=widgets.Layout(width="38px"))
        dropdown = widgets.Dropdown(
            options=options,
            value=options[0],
            description="Basemap:",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="250px"),
        )
        close_btn = widgets.Button(icon="times", layout=widgets.Layout(width="38px"))

        container = widgets.HBox([toggle, dropdown, close_btn])

        def on_toggle(change):
            container.children = [toggle, dropdown, close_btn] if change["new"] else [toggle]

        def on_close(_):
            container.close()

        def on_change(change):
            if change["new"]:
                self.layers = self.layers[:-1]
                self.add_basemap(change["new"])

        toggle.observe(on_toggle, names="value")
        close_btn.on_click(on_close)
        dropdown.observe(on_change, names="value")

        self.add(ipyleaflet.WidgetControl(widget=container, position=position))

    # ------------------------------------------------------------------
    # Widgets
    # ------------------------------------------------------------------

    def add_widget(self, widget, position="topright", **kwargs):
        control = ipyleaflet.WidgetControl(widget=widget, position=position, **kwargs)
        self.add(control)

    # ------------------------------------------------------------------
    # Google Maps
    # ------------------------------------------------------------------

    def add_google_map(self, map_type="ROADMAP"):
        types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "HYBRID": "y",
            "TERRAIN": "p",
        }
        key = map_type.upper()
        if key not in types:
            raise ValueError("Invalid Google map type")

        url = f"https://mt1.google.com/vt/lyrs={types[key]}&x={{x}}&y={{y}}&z={{z}}"
        self.add(ipyleaflet.TileLayer(url=url, name=f"Google {map_type.title()}"))

    # ------------------------------------------------------------------
    # Vector Data
    # ------------------------------------------------------------------

    def add_geojson(self, data, zoom_to_layer=True, hover_style=None, **kwargs):
        """Add GeoJSON from file path or dict."""
        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.3}

        gdf = None

        if isinstance(data, str):
            gdf = gpd.read_file(data).to_crs(epsg=4326)
            geojson = gdf.__geo_interface__
        elif isinstance(data, dict):
            geojson = data
        else:
            raise ValueError("GeoJSON data must be a file path or dict")

        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add(layer)

        if zoom_to_layer and gdf is not None:
            minx, miny, maxx, maxy = gdf.total_bounds
            self.fit_bounds([[miny, minx], [maxy, maxx]])

    def add_gdf(self, gdf, **kwargs):
        """Add a GeoDataFrame."""
        gdf = gdf.to_crs(epsg=4326)
        self.add_geojson(gdf.__geo_interface__, **kwargs)

    def add_vector(self, data, **kwargs):
        """Add vector data from path, GeoDataFrame, or GeoJSON dict."""
        import geopandas as gpd

        if isinstance(data, str):
            self.add_geojson(data, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Unsupported vector data type")

    # ------------------------------------------------------------------
    # Raster & Media
    # ------------------------------------------------------------------

    def add_raster(self, filepath, **kwargs):
        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(filepath)
        layer = get_leaflet_tile_layer(client, **kwargs)
        self.add(layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds=None, **kwargs):
        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        self.add(ipyleaflet.ImageOverlay(url=image, bounds=bounds, **kwargs))

    def add_video(self, video, bounds=None, **kwargs):
        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        self.add(ipyleaflet.VideoOverlay(url=video, bounds=bounds, **kwargs))

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------

    def add_wms_layer(self, url, layers, format="image/png", transparent=True, **kwargs):
        self.add(
            ipyleaflet.WMSLayer(
                url=url,
                layers=layers,
                format=format,
                transparent=transparent,
                **kwargs,
            )
        )

    def add_layer_control(self):
        self.add(ipyleaflet.LayersControl(position="topright"))
