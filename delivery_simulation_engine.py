import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import os

class DeliverySimulationEngine:
    """
    Comprehensive simulation engine to compare traditional vs MFU delivery models
    """
    
    def __init__(self):
        self.traditional_results = {}
        self.mfu_results = {}
        self.comparison_metrics = {}
        
        # Cost parameters
        self.cost_params = {
            'traditional': {
                'rider_hourly_cost': 25,  # $/hour per rider
                'fuel_cost_per_km': 0.15,  # $/km
                'warehouse_rental_cost': 5000,  # $/month per warehouse
                'vehicle_maintenance': 0.05,  # $/km
                'insurance_per_rider': 200,  # $/month
                'average_orders_per_rider_hour': 3
            },
            'mfu': {
                'mfu_hourly_cost': 40,  # $/hour per MFU (3-person team)
                'fuel_cost_per_km': 0.20,  # $/km (larger vehicle)
                'mfu_rental_cost': 8000,  # $/month per MFU
                'vehicle_maintenance': 0.08,  # $/km
                'insurance_per_mfu': 500,  # $/month
                'average_orders_per_mfu_hour': 8
            }
        }
    
    def simulate_traditional_delivery(self, orders: List, warehouse_locations: List[Tuple[float, float]]) -> Dict:
        """
        Simulate traditional delivery model (riders from warehouses)
        """
        print("=== Simulating Traditional Delivery Model ===")
        
        # Parameters for traditional model
        riders_per_warehouse = 10
        max_orders_per_rider = 5
        average_speed_kmh = 25  # Urban traffic speed
        
        results = {
            'total_orders': len(orders),
            'warehouses_used': len(warehouse_locations),
            'total_riders': len(warehouse_locations) * riders_per_warehouse,
            'delivery_times': [],
            'distances': [],
            'costs': {},
            'efficiency_metrics': {}
        }
        
        # Assign orders to nearest warehouses
        warehouse_assignments = self._assign_orders_to_warehouses(orders, warehouse_locations)
        
        total_distance = 0
        total_time = 0
        
        for warehouse_idx, warehouse_orders in warehouse_assignments.items():
            warehouse_location = warehouse_locations[warehouse_idx]
            
            # Calculate distances and times for each order
            for order in warehouse_orders:
                # Distance from warehouse to customer
                distance = self._haversine_distance(warehouse_location, (order.latitude, order.longitude))
                time_minutes = (distance / average_speed_kmh) * 60
                
                total_distance += distance
                total_time += time_minutes
                
                results['distances'].append(distance)
                results['delivery_times'].append(time_minutes)
        
        # Calculate costs
        results['costs'] = self._calculate_traditional_costs(
            total_distance, total_time, len(warehouse_locations), riders_per_warehouse
        )
        
        # Calculate efficiency metrics
        results['efficiency_metrics'] = {
            'avg_delivery_time': np.mean(results['delivery_times']),
            'avg_distance': np.mean(results['distances']),
            'orders_per_rider_hour': len(orders) / (total_time / 60) / (riders_per_warehouse * len(warehouse_locations)),
            'fuel_efficiency': total_distance / (total_time / 60),  # km per hour
            'cost_per_order': results['costs']['total_cost'] / len(orders)
        }
        
        self.traditional_results = results
        return results
    
    def simulate_mfu_delivery(self, orders: List, mfu_locations: List[Tuple[float, float]]) -> Dict:
        """
        Simulate MFU-based delivery model
        """
        print("=== Simulating MFU Delivery Model ===")
        
        # Import delivery engine
        from delivery_engine import DeliveryEngine, create_sample_orders
        
        # Initialize delivery engine
        engine = DeliveryEngine()
        
        # Process orders through MFU system
        mfu_result = engine.process_orders(orders, mfu_locations)
        
        results = {
            'total_orders': len(orders),
            'mfus_used': len(mfu_locations),
            'total_distance': mfu_result['metrics']['total_distance_km'],
            'total_time': mfu_result['metrics']['total_time_minutes'],
            'routes_created': len(mfu_result['routes']),
            'mfu_utilization': mfu_result['metrics']['mfu_utilization'],
            'costs': {},
            'efficiency_metrics': {}
        }
        
        # Calculate costs
        results['costs'] = self._calculate_mfu_costs(
            results['total_distance'], results['total_time'], len(mfu_locations)
        )
        
        # Calculate efficiency metrics
        results['efficiency_metrics'] = {
            'avg_delivery_time': mfu_result['metrics']['avg_time_per_order'],
            'avg_distance': mfu_result['metrics']['avg_distance_per_order'],
            'orders_per_mfu_hour': len(orders) / (results['total_time'] / 60) / len(mfu_locations),
            'fuel_efficiency': results['total_distance'] / (results['total_time'] / 60),
            'cost_per_order': results['costs']['total_cost'] / len(orders),
            'route_efficiency': results['total_distance'] / len(mfu_result['routes'])
        }
        
        self.mfu_results = results
        return results
    
    def _assign_orders_to_warehouses(self, orders: List, warehouse_locations: List[Tuple[float, float]]) -> Dict:
        """Assign orders to nearest warehouses"""
        assignments = {i: [] for i in range(len(warehouse_locations))}
        
        for order in orders:
            # Find nearest warehouse
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
    
    def _calculate_traditional_costs(self, total_distance: float, total_time: float, 
                                   warehouses: int, riders_per_warehouse: int) -> Dict:
        """Calculate costs for traditional delivery model"""
        params = self.cost_params['traditional']
        
        total_riders = warehouses * riders_per_warehouse
        total_hours = total_time / 60
        
        costs = {
            'labor_cost': total_hours * total_riders * params['rider_hourly_cost'],
            'fuel_cost': total_distance * params['fuel_cost_per_km'],
            'warehouse_cost': warehouses * params['warehouse_rental_cost'] / 30,  # Daily cost
            'maintenance_cost': total_distance * params['vehicle_maintenance'],
            'insurance_cost': total_riders * params['insurance_per_rider'] / 30,  # Daily cost
        }
        
        costs['total_cost'] = sum(costs.values())
        return costs
    
    def _calculate_mfu_costs(self, total_distance: float, total_time: float, mfus: int) -> Dict:
        """Calculate costs for MFU delivery model"""
        params = self.cost_params['mfu']
        
        total_hours = total_time / 60
        
        costs = {
            'labor_cost': total_hours * mfus * params['mfu_hourly_cost'],
            'fuel_cost': total_distance * params['fuel_cost_per_km'],
            'mfu_rental_cost': mfus * params['mfu_rental_cost'] / 30,  # Daily cost
            'maintenance_cost': total_distance * params['vehicle_maintenance'],
            'insurance_cost': mfus * params['insurance_per_mfu'] / 30,  # Daily cost
        }
        
        costs['total_cost'] = sum(costs.values())
        return costs
    
    def compare_models(self) -> Dict:
        """Compare traditional vs MFU delivery models"""
        print("=== Comparing Delivery Models ===")
        
        if not self.traditional_results or not self.mfu_results:
            print("Error: Both models must be simulated first")
            return {}
        
        comparison = {
            'cost_comparison': {},
            'efficiency_comparison': {},
            'environmental_impact': {},
            'recommendations': []
        }
        
        # Cost comparison
        trad_costs = self.traditional_results['costs']
        mfu_costs = self.mfu_results['costs']
        
        comparison['cost_comparison'] = {
            'traditional_total': trad_costs['total_cost'],
            'mfu_total': mfu_costs['total_cost'],
            'cost_savings': trad_costs['total_cost'] - mfu_costs['total_cost'],
            'cost_savings_percent': ((trad_costs['total_cost'] - mfu_costs['total_cost']) / trad_costs['total_cost']) * 100,
            'cost_per_order_traditional': trad_costs['total_cost'] / self.traditional_results['total_orders'],
            'cost_per_order_mfu': mfu_costs['total_cost'] / self.mfu_results['total_orders']
        }
        
        # Efficiency comparison
        trad_eff = self.traditional_results['efficiency_metrics']
        mfu_eff = self.mfu_results['efficiency_metrics']
        
        comparison['efficiency_comparison'] = {
            'delivery_time_improvement': ((trad_eff['avg_delivery_time'] - mfu_eff['avg_delivery_time']) / trad_eff['avg_delivery_time']) * 100,
            'distance_optimization': ((trad_eff['avg_distance'] - mfu_eff['avg_distance']) / trad_eff['avg_distance']) * 100,
            'orders_per_hour_improvement': ((mfu_eff['orders_per_mfu_hour'] - trad_eff['orders_per_rider_hour']) / trad_eff['orders_per_rider_hour']) * 100,
            'fuel_efficiency_improvement': ((mfu_eff['fuel_efficiency'] - trad_eff['fuel_efficiency']) / trad_eff['fuel_efficiency']) * 100
        }
        
        # Environmental impact
        traditional_total_distance = sum(self.traditional_results['distances'])
        mfu_total_distance = self.mfu_results['total_distance']
        
        comparison['environmental_impact'] = {
            'carbon_footprint_traditional': traditional_total_distance * 0.2,  # kg CO2/km
            'carbon_footprint_mfu': mfu_total_distance * 0.15,  # kg CO2/km (more efficient)
            'carbon_reduction': (traditional_total_distance * 0.2) - (mfu_total_distance * 0.15),
            'carbon_reduction_percent': ((traditional_total_distance * 0.2) - (mfu_total_distance * 0.15)) / (traditional_total_distance * 0.2) * 100
        }
        
        # Generate recommendations
        recommendations = []
        
        if comparison['cost_comparison']['cost_savings'] > 0:
            recommendations.append(f"MFU model saves ${comparison['cost_comparison']['cost_savings']:.2f} per day")
        
        if comparison['efficiency_comparison']['delivery_time_improvement'] > 0:
            recommendations.append(f"MFU model improves delivery time by {comparison['efficiency_comparison']['delivery_time_improvement']:.1f}%")
        
        if comparison['environmental_impact']['carbon_reduction'] > 0:
            recommendations.append(f"MFU model reduces carbon footprint by {comparison['environmental_impact']['carbon_reduction_percent']:.1f}%")
        
        comparison['recommendations'] = recommendations
        
        self.comparison_metrics = comparison
        return comparison
    
    def generate_visualizations(self, save_path: str = "delivery_simulation_results"):
        """Generate comprehensive visualizations of simulation results"""
        print("=== Generating Visualizations ===")
        
        # Create plots directory
        os.makedirs('plots', exist_ok=True)
        
        # 1. Cost Comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Total cost comparison
        costs = ['Traditional', 'MFU']
        total_costs = [
            self.traditional_results['costs']['total_cost'],
            self.mfu_results['costs']['total_cost']
        ]
        
        bars1 = ax1.bar(costs, total_costs, color=['#ff6b6b', '#4ecdc4'])
        ax1.set_title('Total Daily Cost Comparison')
        ax1.set_ylabel('Cost ($)')
        ax1.set_ylim(0, max(total_costs) * 1.1)
        
        # Add value labels on bars
        for bar, cost in zip(bars1, total_costs):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_costs)*0.01,
                    f'${cost:.0f}', ha='center', va='bottom')
        
        # Cost per order comparison
        cost_per_order = [
            self.comparison_metrics['cost_comparison']['cost_per_order_traditional'],
            self.comparison_metrics['cost_comparison']['cost_per_order_mfu']
        ]
        
        bars2 = ax2.bar(costs, cost_per_order, color=['#ff6b6b', '#4ecdc4'])
        ax2.set_title('Cost per Order Comparison')
        ax2.set_ylabel('Cost per Order ($)')
        ax2.set_ylim(0, max(cost_per_order) * 1.1)
        
        for bar, cost in zip(bars2, cost_per_order):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cost_per_order)*0.01,
                    f'${cost:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('plots/cost_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Efficiency Metrics
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        metrics = ['Delivery Time\n(minutes)', 'Distance\n(km)', 'Orders per Hour', 'Fuel Efficiency\n(km/h)']
        traditional_values = [
            self.traditional_results['efficiency_metrics']['avg_delivery_time'],
            self.traditional_results['efficiency_metrics']['avg_distance'],
            self.traditional_results['efficiency_metrics']['orders_per_rider_hour'],
            self.traditional_results['efficiency_metrics']['fuel_efficiency']
        ]
        mfu_values = [
            self.mfu_results['efficiency_metrics']['avg_delivery_time'],
            self.mfu_results['efficiency_metrics']['avg_distance'],
            self.mfu_results['efficiency_metrics']['orders_per_mfu_hour'],
            self.mfu_results['efficiency_metrics']['fuel_efficiency']
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        ax1.bar(x - width/2, traditional_values, width, label='Traditional', color='#ff6b6b')
        ax1.bar(x + width/2, mfu_values, width, label='MFU', color='#4ecdc4')
        ax1.set_title('Efficiency Metrics Comparison')
        ax1.set_ylabel('Value')
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics, rotation=45)
        ax1.legend()
        
        # 3. Environmental Impact
        carbon_data = [
            self.comparison_metrics['environmental_impact']['carbon_footprint_traditional'],
            self.comparison_metrics['environmental_impact']['carbon_footprint_mfu']
        ]
        
        bars3 = ax2.bar(costs, carbon_data, color=['#ff6b6b', '#4ecdc4'])
        ax2.set_title('Carbon Footprint Comparison')
        ax2.set_ylabel('CO2 Emissions (kg)')
        
        for bar, carbon in zip(bars3, carbon_data):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(carbon_data)*0.01,
                    f'{carbon:.1f} kg', ha='center', va='bottom')
        
        # 4. Improvement Percentages
        improvements = [
            self.comparison_metrics['efficiency_comparison']['delivery_time_improvement'],
            self.comparison_metrics['efficiency_comparison']['distance_optimization'],
            self.comparison_metrics['efficiency_comparison']['orders_per_hour_improvement'],
            self.comparison_metrics['environmental_impact']['carbon_reduction_percent']
        ]
        
        improvement_labels = ['Delivery Time\nImprovement (%)', 'Distance\nOptimization (%)', 
                            'Orders per Hour\nImprovement (%)', 'Carbon\nReduction (%)']
        
        bars4 = ax3.bar(improvement_labels, improvements, color=['#4ecdc4' if x > 0 else '#ff6b6b' for x in improvements])
        ax3.set_title('MFU Model Improvements')
        ax3.set_ylabel('Improvement (%)')
        ax3.tick_params(axis='x', rotation=45)
        
        for bar, improvement in zip(bars4, improvements):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (1 if improvement > 0 else -1),
                    f'{improvement:.1f}%', ha='center', va='bottom' if improvement > 0 else 'top')
        
        # 5. Resource Utilization
        utilization_data = {
            'Traditional': self.traditional_results['total_riders'],
            'MFU': self.mfu_results['mfus_used']
        }
        
        ax4.pie(utilization_data.values(), labels=utilization_data.keys(), autopct='%1.1f%%',
                colors=['#ff6b6b', '#4ecdc4'])
        ax4.set_title('Resource Utilization')
        
        plt.tight_layout()
        plt.savefig('plots/efficiency_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to plots/ directory")
    
    def generate_report(self, save_path: str = "delivery_simulation_report.md"):
        """Generate comprehensive simulation report"""
        print("=== Generating Simulation Report ===")
        
        report = []
        report.append("# MFU vs Traditional Delivery Simulation Report\n")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Executive Summary
        report.append("## Executive Summary\n")
        cost_savings = self.comparison_metrics['cost_comparison']['cost_savings']
        time_improvement = self.comparison_metrics['efficiency_comparison']['delivery_time_improvement']
        carbon_reduction = self.comparison_metrics['environmental_impact']['carbon_reduction_percent']
        
        report.append(f"- **Cost Savings**: ${cost_savings:.2f} per day ({self.comparison_metrics['cost_comparison']['cost_savings_percent']:.1f}% reduction)")
        report.append(f"- **Delivery Time Improvement**: {time_improvement:.1f}% faster")
        report.append(f"- **Environmental Impact**: {carbon_reduction:.1f}% reduction in carbon footprint")
        report.append(f"- **Resource Efficiency**: {self.mfu_results['mfus_used']} MFUs vs {self.traditional_results['total_riders']} riders\n")
        
        # Detailed Results
        report.append("## Detailed Results\n")
        
        # Traditional Model
        report.append("### Traditional Delivery Model\n")
        report.append(f"- Total Orders: {self.traditional_results['total_orders']}")
        report.append(f"- Warehouses Used: {self.traditional_results['warehouses_used']}")
        report.append(f"- Total Riders: {self.traditional_results['total_riders']}")
        report.append(f"- Average Delivery Time: {self.traditional_results['efficiency_metrics']['avg_delivery_time']:.2f} minutes")
        report.append(f"- Average Distance: {self.traditional_results['efficiency_metrics']['avg_distance']:.2f} km")
        report.append(f"- Cost per Order: ${self.comparison_metrics['cost_comparison']['cost_per_order_traditional']:.2f}\n")
        
        # MFU Model
        report.append("### MFU Delivery Model\n")
        report.append(f"- Total Orders: {self.mfu_results['total_orders']}")
        report.append(f"- MFUs Used: {self.mfu_results['mfus_used']}")
        report.append(f"- Routes Created: {self.mfu_results['routes_created']}")
        report.append(f"- MFU Utilization: {self.mfu_results['mfu_utilization']:.1%}")
        report.append(f"- Average Delivery Time: {self.mfu_results['efficiency_metrics']['avg_delivery_time']:.2f} minutes")
        report.append(f"- Average Distance: {self.mfu_results['efficiency_metrics']['avg_distance']:.2f} km")
        report.append(f"- Cost per Order: ${self.comparison_metrics['cost_comparison']['cost_per_order_mfu']:.2f}\n")
        
        # Cost Breakdown
        report.append("## Cost Breakdown\n")
        report.append("### Traditional Model Costs\n")
        for cost_type, amount in self.traditional_results['costs'].items():
            if cost_type != 'total_cost':
                report.append(f"- {cost_type.replace('_', ' ').title()}: ${amount:.2f}")
        report.append(f"- **Total Daily Cost**: ${self.traditional_results['costs']['total_cost']:.2f}\n")
        
        report.append("### MFU Model Costs\n")
        for cost_type, amount in self.mfu_results['costs'].items():
            if cost_type != 'total_cost':
                report.append(f"- {cost_type.replace('_', ' ').title()}: ${amount:.2f}")
        report.append(f"- **Total Daily Cost**: ${self.mfu_results['costs']['total_cost']:.2f}\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        for recommendation in self.comparison_metrics['recommendations']:
            report.append(f"- {recommendation}")
        
        # Save report
        with open(save_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Report saved to {save_path}")

def main():
    """Main function to run complete delivery simulation"""
    print("=== MFU vs Traditional Delivery Simulation ===")
    
    # Import sample orders
    from delivery_engine import create_sample_orders
    
    # Create sample orders
    orders = create_sample_orders()
    
    # Initialize simulation engine
    simulation = DeliverySimulationEngine()
    
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
    
    # Run simulations
    traditional_results = simulation.simulate_traditional_delivery(orders, warehouse_locations)
    mfu_results = simulation.simulate_mfu_delivery(orders, mfu_locations)
    
    # Compare models
    comparison = simulation.compare_models()
    
    # Generate visualizations and report
    simulation.generate_visualizations()
    simulation.generate_report()
    
    # Display summary
    print("\n=== Simulation Summary ===")
    print(f"Cost Savings: ${comparison['cost_comparison']['cost_savings']:.2f} per day")
    print(f"Delivery Time Improvement: {comparison['efficiency_comparison']['delivery_time_improvement']:.1f}%")
    print(f"Carbon Reduction: {comparison['environmental_impact']['carbon_reduction_percent']:.1f}%")
    print(f"Resource Efficiency: {mfu_results['mfus_used']} MFUs vs {traditional_results['total_riders']} riders")
    
    print("\nCheck 'plots/' directory for visualizations and 'delivery_simulation_report.md' for detailed report.")

if __name__ == "__main__":
    main() 