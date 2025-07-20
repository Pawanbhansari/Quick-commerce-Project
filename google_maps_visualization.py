import folium
import pandas as pd
import numpy as np
from datetime import datetime
import json
import webbrowser
import os
from typing import List, Dict, Tuple

class GoogleMapsVisualization:
    """
    Create interactive Google Maps visualization for MFU vs Traditional delivery comparison
    """
    
    def __init__(self):
        self.map_center = [40.7128, -74.0060]  # NYC center
        self.zoom_level = 12
        
    def create_delivery_comparison_map(self, orders: List, warehouse_locations: List[Tuple[float, float]], 
                                     mfu_locations: List[Tuple[float, float]], simulation_results: Dict):
        """
        Create interactive map showing MFU vs Traditional delivery routes
        """
        print("Creating Google Maps visualization...")
        
        # Create base map
        m = folium.Map(
            location=self.map_center,
            zoom_start=self.zoom_level,
            tiles='OpenStreetMap'
        )
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Create feature groups for different elements
        traditional_group = folium.FeatureGroup(name="Traditional Delivery", overlay=True)
        mfu_group = folium.FeatureGroup(name="MFU Delivery", overlay=True)
        warehouses_group = folium.FeatureGroup(name="Warehouses", overlay=True)
        mfu_stations_group = folium.FeatureGroup(name="MFU Stations", overlay=True)
        orders_group = folium.FeatureGroup(name="Customer Orders", overlay=True)
        
        # Add traditional delivery routes
        self._add_traditional_routes(m, traditional_group, orders, warehouse_locations, simulation_results)
        
        # Add MFU delivery routes
        self._add_mfu_routes(m, mfu_group, orders, mfu_locations, simulation_results)
        
        # Add warehouses
        self._add_warehouses(m, warehouses_group, warehouse_locations)
        
        # Add MFU stations
        self._add_mfu_stations(m, mfu_stations_group, mfu_locations)
        
        # Add customer orders
        self._add_customer_orders(m, orders_group, orders)
        
        # Add performance comparison popup
        self._add_performance_popup(m, simulation_results)
        
        # Add all feature groups to map
        traditional_group.add_to(m)
        mfu_group.add_to(m)
        warehouses_group.add_to(m)
        mfu_stations_group.add_to(m)
        orders_group.add_to(m)
        
        return m
    
    def _add_traditional_routes(self, m, group, orders: List, warehouse_locations: List[Tuple[float, float]], 
                               simulation_results: Dict):
        """Add traditional delivery routes to map"""
        
        # Assign orders to nearest warehouses
        warehouse_assignments = self._assign_orders_to_warehouses(orders, warehouse_locations)
        
        colors = ['red', 'darkred', 'crimson', 'firebrick']
        
        for warehouse_idx, warehouse_orders in warehouse_assignments.items():
            warehouse_location = warehouse_locations[warehouse_idx]
            color = colors[warehouse_idx % len(colors)]
            
            # Create route from warehouse to each order
            for i, order in enumerate(warehouse_orders):
                # Route from warehouse to customer
                route_coords = [warehouse_location, (order.latitude, order.longitude)]
                
                # Calculate distance and time
                distance = self._haversine_distance(warehouse_location, (order.latitude, order.longitude))
                time_minutes = distance * 2  # 30 km/h average
                
                # Create route line
                folium.PolyLine(
                    locations=route_coords,
                    color=color,
                    weight=3,
                    opacity=0.7,
                    popup=f"Traditional Route {i+1}<br>Distance: {distance:.2f} km<br>Time: {time_minutes:.1f} min"
                ).add_to(group)
                
                # Add direction arrow
                self._add_direction_arrow(route_coords, color, group)
    
    def _add_mfu_routes(self, m, group, orders: List, mfu_locations: List[Tuple[float, float]], 
                       simulation_results: Dict):
        """Add MFU delivery routes to map"""
        
        # Import delivery engine to get optimized routes
        from delivery_engine import DeliveryEngine
        
        engine = DeliveryEngine()
        mfu_result = engine.process_orders(orders, mfu_locations)
        
        colors = ['blue', 'darkblue', 'navy', 'royalblue']
        
        for i, route in enumerate(mfu_result['routes']):
            color = colors[i % len(colors)]
            
            # Create route coordinates
            route_coords = []
            
            # Start from MFU location
            mfu_location = mfu_locations[i % len(mfu_locations)]
            route_coords.append(mfu_location)
            
            # Add order locations
            for order in route.orders:
                route_coords.append((order.latitude, order.longitude))
            
            # Create route line
            folium.PolyLine(
                locations=route_coords,
                color=color,
                weight=4,
                opacity=0.8,
                popup=f"MFU Route {i+1}<br>Orders: {len(route.orders)}<br>Distance: {route.total_distance:.2f} km<br>Time: {route.total_time:.1f} min"
            ).add_to(group)
            
            # Add direction arrows
            for j in range(len(route_coords) - 1):
                segment_coords = [route_coords[j], route_coords[j+1]]
                self._add_direction_arrow(segment_coords, color, group)
    
    def _add_warehouses(self, m, group, warehouse_locations: List[Tuple[float, float]]):
        """Add warehouse markers to map"""
        
        for i, location in enumerate(warehouse_locations):
            folium.Marker(
                location=location,
                popup=f"Warehouse {i+1}<br>Traditional Model Base",
                icon=folium.Icon(color='red', icon='building', prefix='fa'),
                tooltip=f"Warehouse {i+1}"
            ).add_to(group)
    
    def _add_mfu_stations(self, m, group, mfu_locations: List[Tuple[float, float]]):
        """Add MFU station markers to map"""
        
        for i, location in enumerate(mfu_locations):
            folium.Marker(
                location=location,
                popup=f"MFU Station {i+1}<br>Mobile Fulfillment Unit Base",
                icon=folium.Icon(color='blue', icon='truck', prefix='fa'),
                tooltip=f"MFU Station {i+1}"
            ).add_to(group)
    
    def _add_customer_orders(self, m, group, orders: List):
        """Add customer order markers to map"""
        
        for i, order in enumerate(orders):
            folium.Marker(
                location=(order.latitude, order.longitude),
                popup=f"Order {order.order_id}<br>Products: {len(order.products)}<br>Priority: {order.priority}",
                icon=folium.Icon(color='green', icon='shopping-cart', prefix='fa'),
                tooltip=f"Order {order.order_id}"
            ).add_to(group)
    
    def _add_performance_popup(self, m, simulation_results: Dict):
        """Add performance comparison popup to map"""
        
        comparison = simulation_results.get('comparison_metrics', {})
        
        if comparison:
            cost_savings = comparison.get('cost_comparison', {}).get('cost_savings', 0)
            time_improvement = comparison.get('efficiency_comparison', {}).get('delivery_time_improvement', 0)
            carbon_reduction = comparison.get('environmental_impact', {}).get('carbon_reduction_percent', 0)
            
            html = f"""
            <div style="width: 300px; padding: 10px;">
                <h3>MFU vs Traditional Delivery</h3>
                <h4>Performance Comparison</h4>
                <p><strong>Cost Savings:</strong> ${cost_savings:.2f}/day</p>
                <p><strong>Time Improvement:</strong> {time_improvement:.1f}%</p>
                <p><strong>Carbon Reduction:</strong> {carbon_reduction:.1f}%</p>
                <hr>
                <p><small>Red lines = Traditional routes<br>Blue lines = MFU routes</small></p>
            </div>
            """
            
            folium.Marker(
                location=[40.7128, -74.0060],
                popup=folium.Popup(html, max_width=350),
                icon=folium.Icon(color='purple', icon='info-sign'),
                tooltip="Performance Comparison"
            ).add_to(m)
    
    def _add_direction_arrow(self, coords: List[Tuple[float, float]], color: str, group):
        """Add direction arrow to route"""
        
        if len(coords) < 2:
            return
        
        # Calculate midpoint for arrow
        mid_lat = (coords[0][0] + coords[1][0]) / 2
        mid_lng = (coords[0][1] + coords[1][1]) / 2
        
        # Calculate direction
        lat_diff = coords[1][0] - coords[0][0]
        lng_diff = coords[1][1] - coords[0][1]
        
        # Add small arrow marker
        folium.RegularPolygonMarker(
            location=[mid_lat, mid_lng],
            number_of_sides=3,
            radius=3,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            rotation=45  # Adjust based on direction
        ).add_to(group)
    
    def _assign_orders_to_warehouses(self, orders: List, warehouse_locations: List[Tuple[float, float]]) -> Dict:
        """Assign orders to nearest warehouses"""
        assignments = {i: [] for i in range(len(warehouse_locations))}
        
        for order in orders:
            distances = [
                self._haversine_distance((order.latitude, order.longitude), warehouse)
                for warehouse in warehouse_locations
            ]
            nearest_warehouse = distances.index(min(distances))
            assignments[nearest_warehouse].append(order)
        
        return assignments
    
    def _haversine_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate haversine distance between two points"""
        import math
        
        lat1, lng1 = point1
        lat2, lng2 = point2
        
        R = 6371  # Earth's radius in km
        
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def create_heatmap_comparison(self, orders: List, simulation_results: Dict):
        """Create heatmap showing delivery density and efficiency"""
        
        # Create base map
        m = folium.Map(
            location=self.map_center,
            zoom_start=self.zoom_level,
            tiles='OpenStreetMap'
        )
        
        # Create feature groups for different delivery types
        traditional_group = folium.FeatureGroup(name="Traditional Delivery Density")
        mfu_group = folium.FeatureGroup(name="MFU Delivery Density")
        
        # Add markers with different colors for density visualization
        for order in orders:
            # Traditional delivery marker (red)
            folium.CircleMarker(
                location=(order.latitude, order.longitude),
                radius=8,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.7,
                popup=f"Traditional: Order {order.order_id}",
                tooltip="Traditional Delivery"
            ).add_to(traditional_group)
            
            # MFU delivery marker (blue)
            folium.CircleMarker(
                location=(order.latitude, order.longitude),
                radius=6,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.8,
                popup=f"MFU: Order {order.order_id}",
                tooltip="MFU Delivery"
            ).add_to(mfu_group)
        
        # Add groups to map
        traditional_group.add_to(m)
        mfu_group.add_to(m)
        folium.LayerControl().add_to(m)
        
        return m
    
    def save_and_open_map(self, m, filename: str = "delivery_comparison_map.html"):
        """Save map and open in browser"""
        
        # Save map
        m.save(filename)
        print(f"Map saved as {filename}")
        
        # Open in browser
        try:
            webbrowser.open(f'file://{os.path.abspath(filename)}')
            print("Map opened in browser")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print(f"Please open {filename} manually in your browser")

def create_sample_orders():
    """Create sample orders for visualization"""
    from delivery_engine import Order
    from datetime import datetime, timedelta
    
    orders = []
    
    # Sample NYC addresses with realistic coordinates
    addresses = [
        ("123 Main St, New York, NY", 40.7128, -74.0060),
        ("456 Broadway, New York, NY", 40.7505, -73.9934),
        ("789 5th Ave, New York, NY", 40.7589, -73.9851),
        ("321 Park Ave, New York, NY", 40.7455, -73.9744),
        ("654 Madison Ave, New York, NY", 40.7605, -73.9744),
        ("987 Lexington Ave, New York, NY", 40.7625, -73.9674),
        ("147 3rd Ave, New York, NY", 40.7325, -73.9874),
        ("258 2nd Ave, New York, NY", 40.7305, -73.9844),
        ("369 1st Ave, New York, NY", 40.7285, -73.9814),
        ("741 6th Ave, New York, NY", 40.7505, -73.9914)
    ]
    
    for i, (address, lat, lng) in enumerate(addresses):
        order = Order(
            order_id=f"ORDER_{i+1}",
            customer_address=address,
            latitude=lat,
            longitude=lng,
            products=[f"Product_{j+1}" for j in range(3)],
            priority=1,
            order_time=datetime.now(),
            delivery_deadline=datetime.now() + timedelta(hours=2)
        )
        orders.append(order)
    
    return orders

def main():
    """Main function to create and display the map"""
    print("=== Creating Google Maps Delivery Comparison Visualization ===")
    
    # Create sample data
    orders = create_sample_orders()
    
    # Define locations
    warehouse_locations = [
        (40.7128, -74.0060),  # Manhattan center
        (40.7505, -73.9934),  # Midtown
    ]
    
    mfu_locations = [
        (40.7128, -74.0060),  # Manhattan center
        (40.7505, -73.9934),  # Midtown
        (40.7589, -73.9851)   # Times Square
    ]
    
    # Run simulation to get results
    from delivery_simulation_engine import DeliverySimulationEngine
    
    simulation = DeliverySimulationEngine()
    traditional_results = simulation.simulate_traditional_delivery(orders, warehouse_locations)
    mfu_results = simulation.simulate_mfu_delivery(orders, mfu_locations)
    comparison = simulation.compare_models()
    
    simulation_results = {
        'traditional_results': traditional_results,
        'mfu_results': mfu_results,
        'comparison_metrics': comparison
    }
    
    # Create visualization
    viz = GoogleMapsVisualization()
    
    # Create main comparison map
    comparison_map = viz.create_delivery_comparison_map(
        orders, warehouse_locations, mfu_locations, simulation_results
    )
    
    # Save and open map
    viz.save_and_open_map(comparison_map, "mfu_vs_traditional_delivery_map.html")
    
    # Create heatmap comparison
    heatmap = viz.create_heatmap_comparison(orders, simulation_results)
    viz.save_and_open_map(heatmap, "delivery_heatmap_comparison.html")
    
    print("\n=== Visualization Complete ===")
    print("Two maps have been created:")
    print("1. mfu_vs_traditional_delivery_map.html - Route comparison")
    print("2. delivery_heatmap_comparison.html - Heatmap comparison")
    print("\nThe maps should open automatically in your browser!")

if __name__ == "__main__":
    main() 