import csv
import json
import logging
import codecs

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_csv_to_jsonl(csv_file_path, jsonl_file_path):
    """Convert a CSV file containing mobile data to the JSONL format needed by the chatbot.
    
    Args:
        csv_file_path (str): Path to the input CSV file
        jsonl_file_path (str): Path to the output JSONL file
    
    Returns:
        int: Number of entries created
    """
    try:
        entries = []
        
        # Try different encodings
        encodings = ['utf-8-sig', 'latin-1', 'iso-8859-1', 'windows-1252']
        
        for encoding in encodings:
            try:
                logger.info(f"Trying encoding: {encoding}")
                # Try to read with this encoding
                with open(csv_file_path, 'r', encoding=encoding) as csv_file:
                    reader = csv.DictReader(csv_file)
                    # Test if we can read a row
                    test_row = next(reader)
                    
                    # If we got here, the encoding works
                    # Reopen the file and process it
                    csv_file.seek(0)
                    reader = csv.DictReader(csv_file)
                    
                    # Process each row
                    for row in reader:
                        # Create product details entry
                        product_entry = {
                            "instruction": "Get product details for this mobile phone",
                            "input": f"Product Name: {row['Company Name']} {row['Model Name']}",
                            "output": generate_product_description(row)
                        }
                        entries.append(product_entry)
                        
                        # Create price comparison entry
                        price_entry = {
                            "instruction": "Compare prices of this mobile in different countries",
                            "input": f"Product Name: {row['Company Name']} {row['Model Name']}",
                            "output": generate_price_comparison(row)
                        }
                        entries.append(price_entry)
                        
                        # Create technical specs entry
                        specs_entry = {
                            "instruction": "Tell me the technical specifications of this phone",
                            "input": f"Product Name: {row['Company Name']} {row['Model Name']}",
                            "output": generate_technical_specs(row)
                        }
                        entries.append(specs_entry)
                    
                    # If we processed the file successfully, break the loop
                    logger.info(f"Successfully read CSV with encoding: {encoding}")
                    break
            except Exception as e:
                logger.warning(f"Failed with encoding {encoding}: {str(e)}")
                continue
        
        # Write the entries to the JSONL file
        with open(jsonl_file_path, 'w', encoding='utf-8') as jsonl_file:
            for entry in entries:
                jsonl_file.write(json.dumps(entry) + '\n')
        
        logger.info(f"Successfully converted CSV to JSONL format with {len(entries)} entries")
        return len(entries)
    
    except Exception as e:
        logger.error(f"Error converting CSV to JSONL: {str(e)}")
        return 0

def generate_product_description(row):
    """Generate a descriptive product output from a CSV row"""
    return f"The {row['Company Name']} {row['Model Name']} is a mobile phone launched in {row['Launched Year']}. " + \
           f"It features a {row['Screen Size']} display, {row['RAM']} of RAM, and is powered by the {row['Processor']} processor. " + \
           f"The phone comes with a {row['Back Camera']} rear camera and a {row['Front Camera']} front camera for selfies. " + \
           f"It has a battery capacity of {row['Battery Capacity']} and weighs {row['Mobile Weight']}."

def generate_price_comparison(row):
    """Generate a price comparison output from a CSV row"""
    return f"The {row['Company Name']} {row['Model Name']} is priced at:\n" + \
           f"- Pakistan: {row['Launched Price (Pakistan)']}\n" + \
           f"- India: {row['Launched Price (India)']}\n" + \
           f"- China: {row['Launched Price (China)']}\n" + \
           f"- USA: {row['Launched Price (USA)']}\n" + \
           f"- Dubai: {row['Launched Price (Dubai)']}"

def generate_technical_specs(row):
    """Generate technical specifications output from a CSV row"""
    return f"Technical specifications for {row['Company Name']} {row['Model Name']}:\n" + \
           f"- Processor: {row['Processor']}\n" + \
           f"- RAM: {row['RAM']}\n" + \
           f"- Screen Size: {row['Screen Size']}\n" + \
           f"- Battery: {row['Battery Capacity']}\n" + \
           f"- Weight: {row['Mobile Weight']}\n" + \
           f"- Back Camera: {row['Back Camera']}\n" + \
           f"- Front Camera: {row['Front Camera']}\n" + \
           f"- Launch Year: {row['Launched Year']}"

if __name__ == "__main__":
    # Example usage
    csv_file = "attached_assets/Mobiles Dataset (2025).csv"
    jsonl_file = "attached_assets/formatted_dataset.jsonl"
    convert_csv_to_jsonl(csv_file, jsonl_file)