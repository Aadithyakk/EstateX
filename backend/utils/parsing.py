from datetime import datetime
import re


def parse_storey_mid(storey_range: str):
    if not storey_range:
        return None
    # Example: "01 TO 03"
    nums = re.findall(r"\d+", storey_range)
    if not nums:
        return None
    nums = list(map(int, nums))
    return sum(nums) / len(nums)


def parse_remaining_lease(lease_str: str):
    if not lease_str:
        return None
    # formats like "99 years", "78"
    nums = re.findall(r"\d+", lease_str)
    if not nums:
        return None
    return int(nums[0])


def derive_dates(lease_commence_date: str, txn_date: str = None):
    # lease_commence_date can be YYYY, YYYY-MM-DD, or YYYYMMDD format
    start_year = None
    if lease_commence_date:
        try:
            # try parsing as ISO date first (YYYY-MM-DD)
            if "-" in lease_commence_date or len(lease_commence_date) > 4:
                d = datetime.fromisoformat(lease_commence_date)
                start_year = d.year
            else:
                # assume YYYY
                start_year = int(lease_commence_date)
        except Exception:
            try:
                # try extracting first 4 digits as year
                start_year = int(lease_commence_date[:4])
            except Exception:
                start_year = None
    
    txn_year = txn_month = txn_quarter = None
    if txn_date:
        try:
            d = datetime.fromisoformat(txn_date)
            txn_year = d.year
            txn_month = d.month
            txn_quarter = (d.month - 1) // 3 + 1
        except Exception:
            try:
                # try extracting first 4 digits as year
                txn_year = int(txn_date[:4])
            except Exception:
                pass
    
    return start_year, txn_year, txn_month, txn_quarter
