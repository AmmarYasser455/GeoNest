"""
GeoNest - Core Map Module.

A lightweight wrapper around ipyleaflet for GIS workflows.

Author: Ammar Yasser Abdalazim
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import ipyleaflet
import ipywidgets as widgets

if TYPE_CHECKING:
    import geopandas as gpd

# Type aliases
Position = Literal["topleft", "topright", "bottomleft", "bottomright"]
GoogleMapType = Literal["ROADMAP", "SATELLITE", "HYBRID", "TERRAIN"]


class Map(ipyleaflet.Map):
    """
    An extended ipyleaflet Map with simplified methods for GIS workflows.

    This class provides convenient methods for adding basemaps, vector data,
    raster layers, and interactive widgets to a Leaflet map in Jupyter.

    Args:
        center: Initial map center as (lat, lon). Defaults to (20, 0).
        zoom: Initial zoom level. Defaults to 2.
        height: Map height as CSS string. Defaults to "600px".
        **kwargs: Additional arguments passed to ipyleaflet.Map.

    Example:
        >>> from geonest import Map
        >>> m = Map(center=[30.0, 31.0], zoom=6)
        >>> m.add_basemap("OpenTopoMap")
        >>> m
    """

    def __init__(
        self,
        center: tuple[float, float] = (20, 0),
        zoom: int = 2,
        height: str = "600px",
        **kwargs: Any,
    ) -> None:
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    # -------------------------------------------------------------------------
    # Basemaps
    # -------------------------------------------------------------------------

    def add_basemap(self, basemap: str = "OpenTopoMap") -> None:
        """
        Add a basemap tile layer by name.

        Args:
            basemap: Name of the basemap from ipyleaflet.basemaps.
                Common options: "OpenStreetMap.Mapnik", "OpenTopoMap",
                "Esri.WorldImagery", "CartoDB.DarkMatter".

        Raises:
            ValueError: If the basemap name is not found.

        Example:
            >>> m = Map()
            >>> m.add_basemap("Esri.WorldImagery")
        """
        basemaps = ipyleaflet.basemaps
        
        # Handle nested basemap names like "Esri.WorldImagery"
        try:
            provider = basemaps
            for part in basemap.split("."):
                provider = getattr(provider, part)
        except AttributeError:
            raise ValueError(f"Basemap '{basemap}' not found in ipyleaflet.basemaps")

        layer = ipyleaflet.TileLayer(
            url=provider.build_url(),
            name=basemap,
        )
        self.add(layer)

    def add_basemap_gui(
        self,
        options: list[str] | None = None,
        position: Position = "topright",
    ) -> None:
        """
        Add an interactive basemap selector widget.

        Args:
            options: List of basemap names to include in the dropdown.
            position: Widget position on the map.

        Example:
            >>> m = Map()
            >>> m.add_basemap_gui()
        """
        if options is None:
            options = [
                "OpenStreetMap.Mapnik",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "CartoDB.DarkMatter",
            ]

        toggle = widgets.ToggleButton(
            icon="map",
            layout=widgets.Layout(width="38px"),
        )
        dropdown = widgets.Dropdown(
            options=options,
            value=options[0],
            description="Basemap:",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="250px"),
        )
        close_btn = widgets.Button(
            icon="times",
            layout=widgets.Layout(width="38px"),
        )

        container = widgets.HBox([toggle, dropdown, close_btn])

        def on_toggle(change: dict) -> None:
            if change["new"]:
                container.children = [toggle, dropdown, close_btn]
            else:
                container.children = [toggle]

        def on_close(_: Any) -> None:
            container.close()

        def on_change(change: dict) -> None:
            new_basemap = change["new"]
            if new_basemap:
                # Remove the last added basemap layer (not the default base)
                if len(self.layers) > 1:
                    self.remove(self.layers[-1])
                self.add_basemap(new_basemap)

        toggle.observe(on_toggle, names="value")
        close_btn.on_click(on_close)
        dropdown.observe(on_change, names="value")

        self.add(ipyleaflet.WidgetControl(widget=container, position=position))

    # -------------------------------------------------------------------------
    # Widgets
    # -------------------------------------------------------------------------

    def add_widget(
        self,
        widget: widgets.Widget,
        position: Position = "topright",
        **kwargs: Any,
    ) -> None:
        """
        Add a custom ipywidgets widget to the map.

        Args:
            widget: Any ipywidgets widget instance.
            position: Widget position on the map.
            **kwargs: Additional arguments for WidgetControl.
        """
        control = ipyleaflet.WidgetControl(
            widget=widget,
            position=position,
            **kwargs,
        )
        self.add(control)

    # -------------------------------------------------------------------------
    # Google Maps
    # -------------------------------------------------------------------------

    def add_google_map(self, map_type: GoogleMapType = "ROADMAP") -> None:
        """
        Add a Google Maps tile layer.

        Note: Use of Google Maps tiles may be subject to Google's Terms of Service.

        Args:
            map_type: Type of Google map - "ROADMAP", "SATELLITE", "HYBRID", or "TERRAIN".

        Raises:
            ValueError: If map_type is not valid.

        Example:
            >>> m = Map()
            >>> m.add_google_map("SATELLITE")
        """
        types = {
            "ROADMAP": "m",
            "SATELLITE": "s",
            "HYBRID": "y",
            "TERRAIN": "p",
        }
        key = map_type.upper()
        if key not in types:
            valid = ", ".join(types.keys())
            raise ValueError(f"Invalid Google map type. Must be one of: {valid}")

        url = f"https://mt1.google.com/vt/lyrs={types[key]}&x={{x}}&y={{y}}&z={{z}}"
        self.add(ipyleaflet.TileLayer(url=url, name=f"Google {map_type.title()}"))

    # -------------------------------------------------------------------------
    # Vector Data
    # -------------------------------------------------------------------------

    def add_geojson(
        self,
        data: str | dict,
        zoom_to_layer: bool = True,
        hover_style: dict | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Add GeoJSON data to the map.

        Args:
            data: Either a file path (str) to a GeoJSON/Shapefile or a GeoJSON dict.
            zoom_to_layer: If True, zoom the map to fit the layer bounds.
            hover_style: Style applied on hover. Defaults to yellow highlight.
            **kwargs: Additional arguments for ipyleaflet.GeoJSON.

        Raises:
            ValueError: If data is not a valid file path or dict.

        Example:
            >>> m = Map()
            >>> m.add_geojson("/path/to/data.geojson")
        """
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

    def add_gdf(self, gdf: "gpd.GeoDataFrame", **kwargs: Any) -> None:
        """
        Add a GeoDataFrame to the map.

        The GeoDataFrame will be reprojected to EPSG:4326 (WGS84) if necessary.

        Args:
            gdf: A geopandas GeoDataFrame.
            **kwargs: Additional arguments passed to add_geojson.

        Example:
            >>> import geopandas as gpd
            >>> gdf = gpd.read_file("/path/to/data.shp")
            >>> m = Map()
            >>> m.add_gdf(gdf)
        """
        gdf = gdf.to_crs(epsg=4326)
        self.add_geojson(gdf.__geo_interface__, **kwargs)

    def add_vector(
        self,
        data: str | dict | "gpd.GeoDataFrame",
        **kwargs: Any,
    ) -> None:
        """
        Add vector data from various sources.

        This is a convenience method that dispatches to the appropriate
        method based on the data type.

        Args:
            data: File path, GeoDataFrame, or GeoJSON dict.
            **kwargs: Additional arguments passed to the underlying method.

        Raises:
            ValueError: If data type is not supported.
        """
        import geopandas as gpd

        if isinstance(data, str):
            self.add_geojson(data, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            self.add_gdf(data, **kwargs)
        elif isinstance(data, dict):
            self.add_geojson(data, **kwargs)
        else:
            raise ValueError("Unsupported vector data type")

    # -------------------------------------------------------------------------
    # Raster & Media
    # -------------------------------------------------------------------------

    def add_raster(self, filepath: str, **kwargs: Any) -> None:
        """
        Add a raster layer using localtileserver.

        This method uses localtileserver to serve raster tiles locally,
        enabling visualization of large raster files.

        Args:
            filepath: Path to a raster file (GeoTIFF, etc.) or URL.
            **kwargs: Additional arguments for the tile layer.

        Example:
            >>> m = Map()
            >>> m.add_raster("/path/to/landsat.tif", indexes=[4, 3, 2])
        """
        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(filepath)
        layer = get_leaflet_tile_layer(client, **kwargs)
        self.add(layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(
        self,
        image: str,
        bounds: list[list[float]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Add an image overlay to the map.

        Args:
            image: URL to the image.
            bounds: Geographic bounds as [[south, west], [north, east]].
                Defaults to world extent.
            **kwargs: Additional arguments for ImageOverlay.
        """
        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        self.add(ipyleaflet.ImageOverlay(url=image, bounds=bounds, **kwargs))

    def add_video(
        self,
        video: str,
        bounds: list[list[float]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Add a video overlay to the map.

        Args:
            video: URL to the video.
            bounds: Geographic bounds as [[south, west], [north, east]].
                Defaults to world extent.
            **kwargs: Additional arguments for VideoOverlay.
        """
        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        self.add(ipyleaflet.VideoOverlay(url=video, bounds=bounds, **kwargs))

    # -------------------------------------------------------------------------
    # Services
    # -------------------------------------------------------------------------

    def add_wms_layer(
        self,
        url: str,
        layers: str,
        format: str = "image/png",
        transparent: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Add a WMS (Web Map Service) layer.

        Args:
            url: WMS service URL.
            layers: Comma-separated layer names.
            format: Image format. Defaults to "image/png".
            transparent: Request transparent background. Defaults to True.
            **kwargs: Additional WMS parameters.

        Example:
            >>> m = Map()
            >>> m.add_wms_layer(
            ...     url="https://example.com/wms",
            ...     layers="layer_name",
            ... )
        """
        self.add(
            ipyleaflet.WMSLayer(
                url=url,
                layers=layers,
                format=format,
                transparent=transparent,
                **kwargs,
            )
        )

    def add_layer_control(self, position: Position = "topright") -> None:
        """
        Add a layer control widget for toggling layer visibility.

        Args:
            position: Control position on the map.
        """
        self.add(ipyleaflet.LayersControl(position=position))
