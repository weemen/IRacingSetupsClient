import json

def flatten_json(y, prefix=''):
    out = {}
    if isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{prefix}.{k}" if prefix else k
            out.update(flatten_json(v, new_key))
    elif isinstance(y, list):
        for idx, v in enumerate(y):
            new_key = f"{prefix}.{idx}"
            out.update(flatten_json(v, new_key))
    else:
        out[prefix] = y
    return out

# Load your JSON data
# with open('./sample_data/sample.json', 'r') as f:
#     data = json.load(f)

# Flatten the JSON
# flat = flatten_json(data)

# Write to a .properties file
with open('c:\Temp\session_tracking.properties', 'w+') as f:
    for key, value in flat.items():
        f.write(f"{key}={value}\n")
