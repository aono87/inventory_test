import yaml
import csv
import argparse

# Load inventory from a local CSV file
def load_inventory_from_csv(inventory_file):
    inventory = {}
    with open(inventory_file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = row['Item'].strip()
            inventory[item] = {
                'unit': row['Unit'].strip(),
                'stock': float(row['Stock Quantity']),
                'threshold': float(row['Reorder Threshold'])
            }
    return inventory

# Load protocol from YAML
def load_protocol(protocol_file):
    with open(protocol_file, 'r') as f:
        return yaml.safe_load(f)

# Calculate total needs
def calculate_needs(protocol_data, sample_count):
    return {
        item: qty * sample_count
        for item, qty in protocol_data['supplies_per_sample'].items()
    }

# Compare needs with inventory
def generate_report(needs, inventory, unit_label):
    print(f"\n{'Item':30} | {'Need':>8} | {'Stock':>8} | {'Status':>6} | {'Reorder'}")
    print("-" * 70)
    for item, required in needs.items():
        inv = inventory.get(item)
        if not inv:
            print(f"{item:30} | {required:8.2f} | {'?':>8} | {'MISSING':>6} | {'⚠️'}")
            continue
        stock = inv['stock']
        threshold = inv['threshold']
        unit = inv['unit']
        status = "OK" if stock >= required else "LOW"
        reorder_flag = "YES" if (stock - required) < threshold else "NO"
        print(f"{item:30} | {required:8.2f} | {stock:8.2f} | {status:>6} | {reorder_flag}")

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate lab supply needs from protocol and inventory.")
    parser.add_argument("--samples", type=int, required=True, help="Number of samples to process")
    parser.add_argument("--inventory", default="inventory/inventory.csv", help="Path to inventory CSV file")
    parser.add_argument("--protocol", default="protocols/dna_extraction_mn.yaml", help="Path to protocol YAML file")

    args = parser.parse_args()

    inventory = load_inventory_from_csv(args.inventory)
    protocol = load_protocol(args.protocol)
    needs = calculate_needs(protocol, args.samples)
    unit_label = protocol.get("unit", "")
    generate_report(needs, inventory, unit_label)
