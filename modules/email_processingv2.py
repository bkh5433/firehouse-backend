import re


def parser(email_content, metadata=None):
    # Split the email into lines
    lines = email_content.split("\n")

    # Initialize dictionaries to store the parsed data
    incident_data = {}
    units = []
    event_comments = []

    # Extract metadata if not provided
    # if not metadata:
    #     metadata = {
    #         "subject": lines[1].split(": ", 1)[1],
    #         "date": lines[2].split(": ", 1)[1],
    #         "from": lines[3].split(": ", 1)[1].strip(),
    #         "to": lines[4].split(": ", 1)[1]
    #     }

    # Determine the type of email
    email_type = None
    if "CLEAR" in email_content.upper():
        email_type = "CLEAR"
    elif "DISPATCH" in email_content.upper():
        email_type = "DISPATCH"

    # Iterate through the lines to parse information
    for i, line in enumerate(lines):
        # Parsing incident related details
        if "INCIDENT:" in line:
            incident_data["incident_number"] = line.split(":")[-1].strip()
        elif "Incident Received:" in line:
            incident_data["received"] = line.split(":")[1].split("Call")[0].strip()
            incident_data["source"] = line.split(":")[-1].strip()
        elif "Incident Closed:" in line:
            incident_data["closed"] = line.split(":")[-1].strip()
        elif "First Unit Onscene:" in line:
            incident_data["first_unit_onscene"] = line.split(":")[-1].strip()
        elif "Time In Service:" in line:
            incident_data["time_in_service"] = line.split(":")[-1].strip()
        elif "CODE:" in line:
            incident_data["code"] = line.split("CODE:")[-1].strip()
        elif re.match(r"\d{4} .+", line):
            # This regex matches an address pattern (e.g., 1444 PEPPER RD)
            incident_data["location"] = line.strip()
        elif "Cross Street:" in line:
            incident_data["cross_street"] = line.split(":")[-1].strip()
        elif "Map:" in line:
            details = line.split()
            if len(details) >= 5:  # Ensure we have enough details before extracting
                incident_data["map"] = details[1]
                incident_data["esz"] = details[4]
                incident_data["mun"] = details[6]
        elif "UNIT DISPATCH" in line:
            j = i + 2  # Move to the next line after the header
            while j < len(lines) and lines[j] and not lines[j].startswith("Event Comments:"):
                unit_data = lines[j].strip().split()
                if len(unit_data) >= 7:  # Ensure enough data exists before extracting
                    unit = {
                        "unit": unit_data[0],
                        "dispatch": unit_data[1],
                        "respond": unit_data[2],
                        "on_scene": unit_data[3],
                        "transport": unit_data[4],
                        "at_hosp": unit_data[5],
                        "available_miles": unit_data[6],

                    }
                    units.append(unit)
                j += 1
        elif "Event Comments:" in line:
            j = i + 1  # Move to the next line
            while j < len(lines) and lines[j]:
                parts = lines[j].strip().split(maxsplit=1)
                if len(parts) < 2:
                    print(f"Warning: Unexpected format in line {j}: {lines[j]}")
                    j += 1
                    continue
                time, comment = parts
                event_comments.append({
                    "time": time,
                    "comment": comment
                })
                j += 1

    # Combine all data into the desired JSON structure
    result = {
        "type": email_type,
        "metadata": metadata,
        "incident": incident_data,
        "units": units,
        "event_comments": event_comments
    }

    return result
