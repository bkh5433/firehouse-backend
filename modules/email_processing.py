import re


def processed_mcpds_email(email_content):
    # Split the email into lines
    lines = email_content.split("\n")

    # Initialize a dictionary to store the parsed data
    parsed_data = {}

    # Extract key information using string functions and regular expressions
    for i, line in enumerate(lines):
        if "INCIDENT:" in line:
            parsed_data["Incident Number"] = line.split("INCIDENT:")[-1].strip()
        elif "Incident Received:" in line:
            parsed_data["Incident Received Date and Time"] = line.split(":")[-1].strip()
        elif "Call Source:" in line:
            parsed_data["Call Source"] = line.split(":")[-1].strip()
        elif "Incident Closed:" in line:
            parsed_data["Incident Closed Status"] = line.split(":")[-1].strip()
        elif "First Unit Onscene:" in line:
            parsed_data["First Unit Onscene Time"] = line.split(":")[-1].strip()
        elif "Time In Service:" in line:
            parsed_data["Time In Service"] = line.split(":")[-1].strip()
        elif "CODE:" in line:
            parsed_data["Code and Description"] = line.split("CODE:")[-1].strip()
        elif re.match(r"\d{4} .+", line):
            # This regex matches an address pattern (e.g., 1444 PEPPER RD)
            parsed_data["Address"] = line.strip()
        elif "UNIT DISPATCH" in line:
            # Start of the Units Dispatched section
            units_dispatched = []
            j = i + 1  # Move to the next line
            while j < len(lines) and lines[j] and not lines[j].startswith("Event Comments:"):
                units_dispatched.append(lines[j].strip())
                j += 1
            parsed_data["Units Dispatched"] = units_dispatched
        elif "Event Comments:" in line:
            # Start of the Event Comments section
            event_comments = []
            j = i + 1  # Move to the next line
            while j < len(lines) and lines[j]:
                event_comments.append(lines[j].strip())
                j += 1
            parsed_data["Event Comments"] = event_comments

    return parsed_data
