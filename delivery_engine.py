import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import os
from dataclasses import dataclass
from collections import defaultdict
import math

@dataclass
class Order:
    """Order data structure"""
    order_id: str
    customer_address: str
    latitude: float
    longitude: float
    products: List[str]
    priority: int = 1
    order_time: datetime = None
    delivery_deadline: datetime = None

@dataclass
class MFU:
    """Mobile Fulfillment Unit data structure"""
    mfu_id: str
    current_lat: float
    current_lng: float
    capacity: int
    current_load: int = 0
    route: List[Order] = None
    eta: datetime = None

@dataclass
class Route:
    """Route data structure"""
    route_id: str
    orders: List[Order]
    total_distance: float
    total_time: float
    mfu_id: str
    waypoints: List[Tuple[float, float]] = None

class GoogleMapsAPI:
    """Google Maps API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        if not self.api_key:
            print("Warning: No Google Maps API key provided. Using simulated data.")
    
    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Convert address to coordinates"""
        if not self.api_key:
            # Simulate geocoding for testing
            return self._simulate_geocoding(address)
        
        url = f"{self.base_url}/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                print(f"Geocoding failed: {data['status']}")
                return None, None
                
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None, None
    
    def _simulate_geocoding(self, address: str) -> Tuple[float, float]:
        """Simulate geocoding for testing"""
        # Generate realistic NYC coordinates
        base_lat, base_lng = 40.7128, -74.0060  # NYC center
        
        # Add some randomness based on address
        lat_offset = hash(address) % 1000 / 10000  # ±0.1 degrees
        lng_offset = (hash(address) // 1000) % 1000 / 10000
        
        return base_lat + lat_offset, base_lng + lng_offset
    
    def get_distance_matrix(self, origins: List[Tuple[float, float]], 
                           destinations: List[Tuple[float, float]]) -> Dict:
        """Get distance matrix between multiple points"""
        if not self.api_key:
            return self._simulate_distance_matrix(origins, destinations)
        
        url = f"{self.base_url}/distancematrix/json"
        
        # Convert coordinates to strings
        origins_str = "|".join([f"{lat},{lng}" for lat, lng in origins])
        destinations_str = "|".join([f"{lat},{lng}" for lat, lng in destinations])
        
        params = {
            'origins': origins_str,
            'destinations': destinations_str,
            'mode': 'driving',
            'traffic_model': 'best_guess',
            'departure_time': 'now',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Distance matrix error: {e}")
            return self._simulate_distance_matrix(origins, destinations)
    
    def _simulate_distance_matrix(self, origins: List[Tuple[float, float]], 
                                 destinations: List[Tuple[float, float]]) -> Dict:
        """Simulate distance matrix for testing"""
        matrix = {
            'rows': []
        }
        
        for origin in origins:
            row = {'elements': []}
            for dest in destinations:
                # Calculate haversine distance
                distance = self._haversine_distance(origin, dest)
                duration = distance * 2  # Assume 30 km/h average speed
                
                row['elements'].append({
                    'distance': {'text': f"{distance:.1f} km", 'value': distance * 1000},
                    'duration': {'text': f"{duration:.0f} mins", 'value': duration * 60},
                    'status': 'OK'
                })
            matrix['rows'].append(row)
        
        return matrix
    
    def _haversine_distance(self, point1: Tuple[float, float], 
                           point2: Tuple[float, float]) -> float:
        """Calculate haversine distance between two points"""
        lat1, lng1 = point1
        lat2, lng2 = point2
        
        R = 6371  # Earth's radius in km
        
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_route(self, origin: Tuple[float, float], 
                  destination: Tuple[float, float], 
                  waypoints: List[Tuple[float, float]] = None) -> Dict:
        """Get optimized route with waypoints"""
        if not self.api_key:
            return self._simulate_route(origin, destination, waypoints)
        
        url = f"{self.base_url}/directions/json"
        
        params = {
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'mode': 'driving',
            'traffic_model': 'best_guess',
            'departure_time': 'now',
            'key': self.api_key
        }
        
        if waypoints:
            waypoints_str = "|".join([f"{lat},{lng}" for lat, lng in waypoints])
            params['waypoints'] = waypoints_str
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Route error: {e}")
            return self._simulate_route(origin, destination, waypoints)
    
    def _simulate_route(self, origin: Tuple[float, float], 
                       destination: Tuple[float, float], 
                       waypoints: List[Tuple[float, float]] = None) -> Dict:
        """Simulate route for testing"""
        total_distance = self._haversine_distance(origin, destination)
        total_duration = total_distance * 2  # 30 km/h average
        
        if waypoints:
            # Add distance for waypoints
            for i, waypoint in enumerate(waypoints):
                if i == 0:
                    total_distance += self._haversine_distance(origin, waypoint)
                else:
                    total_distance += self._haversine_distance(waypoints[i-1], waypoint)
                total_duration += self._haversine_distance(waypoints[i-1], waypoint) * 2
        
        return {
            'routes': [{
                'legs': [{
                    'distance': {'text': f"{total_distance:.1f} km", 'value': total_distance * 1000},
                    'duration': {'text': f"{total_duration:.0f} mins", 'value': total_duration * 60}
                }],
                'overview_polyline': {'points': ''}
            }],
            'status': 'OK'
        }

class OrderBatchingEngine:
    """Order batching and clustering engine"""
    
    def __init__(self, google_maps: GoogleMapsAPI):
        self.google_maps = google_maps
        self.max_batch_size = 10
        self.max_batch_distance = 5.0  # km
        self.max_batch_time = 30  # minutes
    
    def batch_orders(self, orders: List[Order]) -> List[List[Order]]:
        """Group orders into batches for efficient delivery"""
        if not orders:
            return []
        
        # Sort orders by priority and time
        sorted_orders = sorted(orders, key=lambda x: (x.priority, x.order_time))
        
        batches = []
        current_batch = []
        
        for order in sorted_orders:
            if len(current_batch) == 0:
                current_batch.append(order)
            elif self._can_add_to_batch(current_batch, order):
                current_batch.append(order)
            else:
                batches.append(current_batch)
                current_batch = [order]
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _can_add_to_batch(self, batch: List[Order], new_order: Order) -> bool:
        """Check if new order can be added to existing batch"""
        if len(batch) >= self.max_batch_size:
            return False
        
        # Check distance constraints
        batch_coords = [(order.latitude, order.longitude) for order in batch]
        new_coord = (new_order.latitude, new_order.longitude)
        
        # Calculate maximum distance from batch center
        center_lat = sum(coord[0] for coord in batch_coords) / len(batch_coords)
        center_lng = sum(coord[1] for coord in batch_coords) / len(batch_coords)
        
        max_distance = max([
            self.google_maps._haversine_distance((center_lat, center_lng), coord)
            for coord in batch_coords
        ])
        
        new_distance = self.google_maps._haversine_distance((center_lat, center_lng), new_coord)
        
        if max_distance + new_distance > self.max_batch_distance:
            return False
        
        # Check time constraints
        if new_order.delivery_deadline:
            earliest_deadline = min(order.delivery_deadline for order in batch if order.delivery_deadline)
            if new_order.delivery_deadline < earliest_deadline:
                return False
        
        return True

class RouteOptimizationEngine:
    """Route optimization using TSP and Google Maps"""
    
    def __init__(self, google_maps: GoogleMapsAPI):
        self.google_maps = google_maps
    
    def optimize_route(self, orders: List[Order], mfu_location: Tuple[float, float]) -> Route:
        """Optimize route for a batch of orders"""
        if not orders:
            return None
        
        # Simple nearest neighbor algorithm for TSP
        unvisited = orders.copy()
        route_orders = []
        current_location = mfu_location
        
        while unvisited:
            # Find nearest unvisited order
            nearest = min(unvisited, key=lambda order: 
                         self.google_maps._haversine_distance(current_location, 
                                                            (order.latitude, order.longitude)))
            
            route_orders.append(nearest)
            current_location = (nearest.latitude, nearest.longitude)
            unvisited.remove(nearest)
        
        # Calculate route metrics
        total_distance = 0
        total_time = 0
        waypoints = []
        
        current_location = mfu_location
        for order in route_orders:
            distance = self.google_maps._haversine_distance(current_location, 
                                                          (order.latitude, order.longitude))
            total_distance += distance
            total_time += distance * 2  # 30 km/h average speed
            waypoints.append((order.latitude, order.longitude))
            current_location = (order.latitude, order.longitude)
        
        return Route(
            route_id=f"route_{len(route_orders)}_{int(time.time())}",
            orders=route_orders,
            total_distance=total_distance,
            total_time=total_time,
            mfu_id="",  # Will be assigned later
            waypoints=waypoints
        )

class MFUFleetManager:
    """MFU fleet management and allocation"""
    
    def __init__(self, google_maps: GoogleMapsAPI):
        self.google_maps = google_maps
        self.mfus = {}
        self.routes = {}
    
    def add_mfu(self, mfu: MFU):
        """Add MFU to fleet"""
        self.mfus[mfu.mfu_id] = mfu
    
    def assign_routes(self, routes: List[Route]) -> Dict[str, Route]:
        """Assign routes to available MFUs"""
        assignments = {}
        
        # Sort routes by priority (total time)
        sorted_routes = sorted(routes, key=lambda x: x.total_time)
        
        # Sort MFUs by current load
        available_mfus = sorted(self.mfus.values(), key=lambda x: x.current_load)
        
        for route in sorted_routes:
            # Find best available MFU
            best_mfu = None
            best_score = float('inf')
            
            for mfu in available_mfus:
                if mfu.current_load + len(route.orders) <= mfu.capacity:
                    # Calculate score based on distance to route start
                    distance_to_start = self.google_maps._haversine_distance(
                        (mfu.current_lat, mfu.current_lng),
                        (route.orders[0].latitude, route.orders[0].longitude)
                    )
                    
                    score = distance_to_start + mfu.current_load * 10  # Penalize loaded MFUs
                    
                    if score < best_score:
                        best_score = score
                        best_mfu = mfu
            
            if best_mfu:
                assignments[best_mfu.mfu_id] = route
                best_mfu.current_load += len(route.orders)
                best_mfu.route = route
                route.mfu_id = best_mfu.mfu_id
        
        return assignments
    
    def update_mfu_positions(self):
        """Update MFU positions based on current routes"""
        for mfu in self.mfus.values():
            if mfu.route and mfu.route.orders:
                # Move MFU to next order location
                next_order = mfu.route.orders[0]
                mfu.current_lat = next_order.latitude
                mfu.current_lng = next_order.longitude

class DeliveryEngine:
    """Main delivery engine orchestrating all components"""
    
    def __init__(self, google_maps_api_key: str = None):
        self.google_maps = GoogleMapsAPI(google_maps_api_key)
        self.batching_engine = OrderBatchingEngine(self.google_maps)
        self.route_optimizer = RouteOptimizationEngine(self.google_maps)
        self.fleet_manager = MFUFleetManager(self.google_maps)
    
    def process_orders(self, orders: List[Order], mfu_locations: List[Tuple[float, float]]) -> Dict:
        """Process orders through the complete delivery pipeline"""
        print(f"Processing {len(orders)} orders...")
        
        # Step 1: Batch orders
        batches = self.batching_engine.batch_orders(orders)
        print(f"Created {len(batches)} order batches")
        
        # Step 2: Optimize routes for each batch
        routes = []
        for i, batch in enumerate(batches):
            # Use first MFU location as starting point (simplified)
            start_location = mfu_locations[i % len(mfu_locations)]
            route = self.route_optimizer.optimize_route(batch, start_location)
            if route:
                routes.append(route)
        
        print(f"Optimized {len(routes)} routes")
        
        # Step 3: Initialize MFU fleet
        for i, location in enumerate(mfu_locations):
            mfu = MFU(
                mfu_id=f"MFU_{i+1}",
                current_lat=location[0],
                current_lng=location[1],
                capacity=20
            )
            self.fleet_manager.add_mfu(mfu)
        
        # Step 4: Assign routes to MFUs
        assignments = self.fleet_manager.assign_routes(routes)
        print(f"Assigned {len(assignments)} routes to MFUs")
        
        # Step 5: Calculate performance metrics
        metrics = self._calculate_metrics(routes, assignments)
        
        return {
            'batches': batches,
            'routes': routes,
            'assignments': assignments,
            'metrics': metrics
        }
    
    def _calculate_metrics(self, routes: List[Route], assignments: Dict[str, Route]) -> Dict:
        """Calculate delivery performance metrics"""
        total_distance = sum(route.total_distance for route in routes)
        total_time = sum(route.total_time for route in routes)
        total_orders = sum(len(route.orders) for route in routes)
        
        return {
            'total_distance_km': total_distance,
            'total_time_minutes': total_time,
            'total_orders': total_orders,
            'avg_distance_per_order': total_distance / total_orders if total_orders > 0 else 0,
            'avg_time_per_order': total_time / total_orders if total_orders > 0 else 0,
            'mfu_utilization': len(assignments) / len(self.fleet_manager.mfus) if self.fleet_manager.mfus else 0
        }

def create_sample_orders() -> List[Order]:
    """Create sample orders for testing"""
    orders = []
    
    # Sample NYC addresses
    addresses = [
        "123 Main St, New York, NY",
        "456 Broadway, New York, NY", 
        "789 5th Ave, New York, NY",
        "321 Park Ave, New York, NY",
        "654 Madison Ave, New York, NY",
        "987 Lexington Ave, New York, NY",
        "147 3rd Ave, New York, NY",
        "258 2nd Ave, New York, NY",
        "369 1st Ave, New York, NY",
        "741 6th Ave, New York, NY"
    ]
    
    for i, address in enumerate(addresses):
        order = Order(
            order_id=f"ORDER_{i+1}",
            customer_address=address,
            latitude=40.7128 + (i * 0.01),  # Spread out
            longitude=-74.0060 + (i * 0.01),
            products=[f"Product_{j+1}" for j in range(3)],
            priority=1,
            order_time=datetime.now(),
            delivery_deadline=datetime.now() + timedelta(hours=2)
        )
        orders.append(order)
    
    return orders

def main():
    """Main function to demonstrate delivery engine"""
    print("=== MFU Delivery Engine Demo ===")
    
    # Initialize delivery engine
    engine = DeliveryEngine()
    
    # Create sample orders
    orders = create_sample_orders()
    
    # Sample MFU locations (NYC area)
    mfu_locations = [
        (40.7128, -74.0060),  # Manhattan center
        (40.7505, -73.9934),  # Midtown
        (40.7589, -73.9851)   # Times Square
    ]
    
    # Process orders
    result = engine.process_orders(orders, mfu_locations)
    
    # Display results
    print("\n=== Delivery Results ===")
    print(f"Orders processed: {result['metrics']['total_orders']}")
    print(f"Total distance: {result['metrics']['total_distance_km']:.2f} km")
    print(f"Total time: {result['metrics']['total_time_minutes']:.2f} minutes")
    print(f"Average distance per order: {result['metrics']['avg_distance_per_order']:.2f} km")
    print(f"Average time per order: {result['metrics']['avg_time_per_order']:.2f} minutes")
    print(f"MFU utilization: {result['metrics']['mfu_utilization']:.1%}")
    
    print(f"\nRoutes created: {len(result['routes'])}")
    for route in result['routes']:
        print(f"- Route {route.route_id}: {len(route.orders)} orders, {route.total_distance:.2f} km, {route.total_time:.2f} min")
    
    print(f"\nMFU assignments: {len(result['assignments'])}")
    for mfu_id, route in result['assignments'].items():
        print(f"- {mfu_id}: {len(route.orders)} orders")

if __name__ == "__main__":
    main() 