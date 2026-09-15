# printer.py

import textwrap

def generate_bill_receipt_text(invoice_no, date_str, mobile, cart_items, subtotal, disc_pct, discount_amount, grand_total, payment_mode="CASH"):
    receipt = []
    receipt.append("========================================")
    receipt.append("               MERA STORE               ")
    receipt.append("========================================")
    receipt.append(f"Inv No : {invoice_no}")
    receipt.append(f"Date   : {date_str}")
    receipt.append(f"Mobile : {mobile}")
    
    # Handle long mixed payment strings nicely
    if "MIXED" in payment_mode:
        receipt.append(f"Payment: MIXED")
        parts = payment_mode.replace("MIXED (", "").replace(")", "").split(", ")
        for p in parts:
            receipt.append(f"  - {p}")
    else:
        receipt.append(f"Payment: {payment_mode}")
        
    receipt.append("----------------------------------------")
    receipt.append(f"{'Item Name':<18} {'Qty':<4} {'Rate':<8} {'Total':<8}")
    receipt.append("----------------------------------------")
    
    for item in cart_items:
        name = item['name']
        qty = int(item['qty'])
        rate = int(item['rate'])
        tot = int(qty * rate)
        
        wrapped_lines = textwrap.wrap(name, width=18)
        if not wrapped_lines:
            wrapped_lines = [""]
            
        for line in wrapped_lines[:-1]:
            receipt.append(f"{line:<18}")
            
        last_line = wrapped_lines[-1]
        receipt.append(f"{last_line:<18} {qty:<4} {rate:<8} {tot:<8}")
        
    receipt.append("----------------------------------------")
    receipt.append(f"Subtotal: Rs.{subtotal:.2f}")
    receipt.append(f"Discount ({disc_pct}%): -Rs.{discount_amount:.2f}")
    receipt.append(f"GRAND TOTAL: Rs.{grand_total:.2f}")
    receipt.append("========================================")
    receipt.append("         Thank You, Visit Again!        ")
    receipt.append("========================================")
    
    return "\n".join(receipt)