import re

def find_months_and_years(text):
    # Mapping full month names and abbreviations
    full_to_abbr = {
        "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
        "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
        "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec"
    }
    # Reverse mapping abbreviations to full names
    abbr_to_full = {v: k for k, v in full_to_abbr.items()}

    month_pattern = r"\b(" \
                    r"January|February|March|April|May|June|July|August|September|October|November|December|" \
                    r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec" \
                    r")\b"
    year_pattern = r"\b(19|20)\d{2}\b"

    months_found = re.findall(month_pattern, text, re.IGNORECASE)
    full_years = re.findall(r"\b((?:19|20)\d{2})\b", text)

    processed_months = []
    seen = set()

    for m in months_found:
        m_cap = m.capitalize()
        if m_cap in full_to_abbr:
            full = m_cap
            abbr = full_to_abbr[full]
            # Add both full and abbr if not seen before
            if full not in seen:
                processed_months.append(full)
                seen.add(full)
            if abbr not in seen:
                processed_months.append(abbr)
                seen.add(abbr)
        elif m_cap in abbr_to_full:
            abbr = m_cap
            full = abbr_to_full[abbr]
            # Add both abbr and full if not seen before
            if abbr not in seen:
                processed_months.append(abbr)
                seen.add(abbr)
            if full not in seen:
                processed_months.append(full)
                seen.add(full)
        else:
            # Numeric month or unmatched
            if m not in seen:
                processed_months.append(m)
                seen.add(m)

    return processed_months, full_years